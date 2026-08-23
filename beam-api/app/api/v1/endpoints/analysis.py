from __future__ import annotations

import logging
from datetime import datetime, timezone
from math import ceil
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_database_session
from app.core.config import settings
from app.models.analysis_session import AnalysisSession
from app.models.user import User
from app.schemas.analysis import (
    AnalysisCreate,
    AnalysisCreatedResponse,
    AnalysisDetailResponse,
    AnalysisInputMetadata,
    AnalysisListResponse,
    AnalysisSessionSummary,
    AnalysisStatus,
    BehaviorMetricsPayload,
    ExplanationPayload,
    ModelInfo,
    PredictionPayload,
)
from app.services.analysis import get_analysis_service
from app.services.analysis.base import AnalysisService
from app.services.analysis import repository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analysis", tags=["analysis"])

_MODEL_NOTE = (
    "The B.E.A.M. transformer is not deployed yet; this session was completed "
    "by the placeholder service and contains no model predictions."
)


def _word_count(text: str) -> int:
    return len([w for w in text.split() if w])


@router.post("", response_model=AnalysisCreatedResponse, status_code=status.HTTP_201_CREATED)
def create_analysis(
    payload: AnalysisCreate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
    service: AnalysisService = Depends(get_analysis_service),
) -> AnalysisCreatedResponse:
    text = payload.text.strip()

    if not text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Text must not be empty",
        )
    if len(text) > settings.MAX_ANALYSIS_TEXT_CHARS:
        raise HTTPException(
            status_code=413,
            detail=(
                "Text exceeds the maximum allowed input size of "
                f"{settings.MAX_ANALYSIS_TEXT_CHARS} characters"
            ),
        )

    session, analysis_input = repository.create_session_with_input(
        db,
        user_id=current_user.id,
        text=text,
        source_type=payload.source_type or "text",
        title=payload.title,
    )

    try:
        outcome = service.run(db, session, analysis_input)
    except (SQLAlchemyError, Exception) as exc:
        db.rollback()
        logger.exception("Analysis inference failed for session %s", session.id)
        # Best-effort failure marker in a clean transaction.
        try:
            session.status = AnalysisStatus.FAILED.value
            session.completed_at = datetime.now(timezone.utc)
            db.add(session)
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            logger.exception("Could not persist failed status for session %s", session.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analysis could not be completed. Please try again later.",
        ) from exc

    if outcome.prediction is not None:
        db.add(outcome.prediction)
    if outcome.behavior_metric is not None:
        db.add(outcome.behavior_metric)
    if outcome.explanation is not None:
        db.add(outcome.explanation)
    if outcome.distribution and outcome.prediction is not None:
        outcome.prediction.emotion_distribution = outcome.distribution

    db.commit()
    return AnalysisCreatedResponse(session_id=session.id, status=AnalysisStatus(session.status))


@router.get("", response_model=AnalysisListResponse)
def list_analyses(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=settings.ANALYSIS_LIST_PAGE_SIZE_MAX),
    search: str | None = Query(default=None, max_length=255),
    status_filter: AnalysisStatus | None = Query(default=None, alias="status"),
    sort: str = Query(default="created_desc", pattern="^(created_desc|created_asc)$"),
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
) -> AnalysisListResponse:
    items, total = repository.list_user_sessions(
        db,
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        search=search.strip() if search else None,
        status=status_filter,
        sort_desc=sort == "created_desc",
    )
    pages = max(1, ceil(total / page_size)) if total else 1

    summaries = [_session_to_summary(s) for s in items]
    return AnalysisListResponse(
        items=summaries,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/{session_id}", response_model=AnalysisDetailResponse)
def get_analysis(
    session_id: UUID,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
) -> AnalysisDetailResponse:
    session = repository.get_owned_session(
        db, session_id=session_id, user_id=current_user.id
    )
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis session not found",
        )
    return _session_to_detail(session)


@router.delete("/{session_id}")
def delete_analysis(
    session_id: UUID,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    session = repository.get_owned_session(
        db, session_id=session_id, user_id=current_user.id
    )
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis session not found",
        )
    repository.delete_session(db, session)
    db.commit()
    return {"message": "Analysis deleted successfully"}


# --------------------------------------------------------------------------
# Mapping helpers
# --------------------------------------------------------------------------

def _prediction_from_session(session: AnalysisSession) -> PredictionPayload | None:
    prediction = session.prediction
    if prediction is None:
        return None
    return PredictionPayload(
        primary_emotion=prediction.primary_emotion,
        confidence=prediction.confidence,
        emotion_distribution=[
            {"label": str(item.get("label", "")), "score": float(item.get("score", 0.0))}
            for item in (prediction.emotion_distribution or [])
        ]
        or None,
        inference_time_ms=prediction.inference_time_ms,
    )


def _model_info(session: AnalysisSession) -> ModelInfo:
    prediction = session.prediction
    return ModelInfo(
        model_name=prediction.model_name if prediction else "beam-mock",
        model_version=None,
        deployed=False,
        note=_MODEL_NOTE,
    )


def _session_to_summary(session: AnalysisSession) -> AnalysisSessionSummary:
    prediction = session.prediction
    return AnalysisSessionSummary(
        session_id=session.id,
        status=AnalysisStatus(session.status),
        source_type=session.source_type,
        title=session.title,
        created_at=session.created_at,
        completed_at=session.completed_at,
        primary_emotion=prediction.primary_emotion if prediction else None,
        confidence=prediction.confidence if prediction else None,
        model_name=prediction.model_name if prediction else None,
    )


def _session_to_detail(session: AnalysisSession) -> AnalysisDetailResponse:
    analysis_input = session.input
    raw_text = analysis_input.raw_text if analysis_input else ""

    explanation_payload = None
    if session.explanation is not None:
        explanation_json = session.explanation.explanation_json or {}
        summary = explanation_json.get("summary")
        method = explanation_json.get("method")
        explanation_payload = ExplanationPayload(
            method=str(method) if isinstance(method, str) else None,
            summary=str(summary) if isinstance(summary, str) else None,
            important_keywords=session.explanation.important_keywords,
        )

    return AnalysisDetailResponse(
        session_id=session.id,
        status=AnalysisStatus(session.status),
        source_type=session.source_type,
        title=session.title,
        created_at=session.created_at,
        completed_at=session.completed_at,
        primary_emotion=session.prediction.primary_emotion if session.prediction else None,
        confidence=session.prediction.confidence if session.prediction else None,
        model_name=session.prediction.model_name if session.prediction else None,
        input=AnalysisInputMetadata(
            char_count=len(raw_text),
            word_count=_word_count(raw_text),
            raw_text=raw_text,
            created_at=analysis_input.created_at if analysis_input else session.created_at,
        ),
        prediction=_prediction_from_session(session),
        behavior_metrics=BehaviorMetricsPayload.model_validate(session.behavior_metric)
        if session.behavior_metric
        else None,
        explanation=explanation_payload,
        model_info=_model_info(session),
    )
