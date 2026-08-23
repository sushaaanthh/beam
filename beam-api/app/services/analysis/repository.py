"""Database access for analysis sessions. Ownership is enforced here so no
endpoint can ever return another user's analysis."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.analysis_input import AnalysisInput
from app.models.analysis_session import AnalysisSession
from app.schemas.analysis import AnalysisStatus


def create_session_with_input(
    db: Session,
    *,
    user_id: UUID,
    text: str,
    source_type: str,
    title: str | None,
) -> tuple[AnalysisSession, AnalysisInput]:
    session = AnalysisSession(
        user_id=user_id,
        source_type=source_type,
        title=title,
        status=AnalysisStatus.PENDING.value,
    )
    db.add(session)
    db.flush()

    analysis_input = AnalysisInput(session_id=session.id, raw_text=text)
    db.add(analysis_input)
    db.flush()

    return session, analysis_input


def get_owned_session(
    db: Session,
    *,
    session_id: UUID,
    user_id: UUID,
) -> AnalysisSession | None:
    stmt = (
        select(AnalysisSession)
        .where(AnalysisSession.id == session_id, AnalysisSession.user_id == user_id)
        .options(
            selectinload(AnalysisSession.input),
            selectinload(AnalysisSession.prediction),
            selectinload(AnalysisSession.behavior_metric),
            selectinload(AnalysisSession.explanation),
        )
    )
    return db.scalar(stmt)


def list_user_sessions(
    db: Session,
    *,
    user_id: UUID,
    page: int,
    page_size: int,
    search: str | None,
    status: AnalysisStatus | None,
    sort_desc: bool,
) -> tuple[list[AnalysisSession], int]:
    base_filter = AnalysisSession.user_id == user_id
    if status is not None:
        base_filter = base_filter & (AnalysisSession.status == status.value)

    if search:
        pattern = f"%{search.lower()}%"
        base_filter = base_filter & (
            or_(
                func.lower(AnalysisSession.title).like(pattern),
                func.lower(AnalysisSession.source_type).like(pattern),
                AnalysisSession.id.in_(
                    select(AnalysisInput.session_id).where(
                        func.lower(AnalysisInput.raw_text).like(pattern)
                    )
                ),
            )
        )

    total = db.scalar(select(func.count()).select_from(AnalysisSession).where(base_filter)) or 0

    order_by = (
        AnalysisSession.created_at.desc() if sort_desc else AnalysisSession.created_at.asc()
    )
    stmt = (
        select(AnalysisSession)
        .where(base_filter)
        .order_by(order_by, AnalysisSession.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .options(
            selectinload(AnalysisSession.input),
            selectinload(AnalysisSession.prediction),
        )
    )
    items = list(db.scalars(stmt).all())
    return items, int(total)


def delete_session(db: Session, session: AnalysisSession) -> None:
    # ORM cascades remove input/prediction/metrics/explanation rows.
    db.delete(session)
    db.flush()
