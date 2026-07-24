"""initial domain schema

Revision ID: a1b2c3d4e5f6
Revises: 
Create Date: 2026-07-24 00:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "a1b2c3d4e5f6"
down_revision = None
branch_labels = None
depends_on = None


UUID_TYPE = postgresql.UUID(as_uuid=True)


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", UUID_TYPE, primary_key=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("username", sa.String(length=50), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_table(
        "model_versions",
        sa.Column("id", UUID_TYPE, primary_key=True, nullable=False),
        sa.Column("model_name", sa.String(length=255), nullable=False),
        sa.Column("model_version", sa.String(length=100), nullable=False),
        sa.Column("training_dataset", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("model_name", "model_version", name="uq_model_versions_model_name_model_version"),
    )
    op.create_index("ix_model_versions_model_name", "model_versions", ["model_name"])

    op.create_table(
        "analysis_sessions",
        sa.Column("id", UUID_TYPE, primary_key=True, nullable=False),
        sa.Column("user_id", UUID_TYPE, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_type", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_analysis_sessions_user_id", "analysis_sessions", ["user_id"])
    op.create_index("ix_analysis_sessions_source_type", "analysis_sessions", ["source_type"])
    op.create_index("ix_analysis_sessions_status", "analysis_sessions", ["status"])

    op.create_table(
        "analysis_inputs",
        sa.Column("id", UUID_TYPE, primary_key=True, nullable=False),
        sa.Column(
            "session_id",
            UUID_TYPE,
            sa.ForeignKey("analysis_sessions.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("cleaned_text", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_table(
        "emotion_predictions",
        sa.Column("id", UUID_TYPE, primary_key=True, nullable=False),
        sa.Column(
            "session_id",
            UUID_TYPE,
            sa.ForeignKey("analysis_sessions.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("primary_emotion", sa.String(length=100), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("model_name", sa.String(length=255), nullable=False),
        sa.Column("inference_time_ms", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_emotion_predictions_primary_emotion", "emotion_predictions", ["primary_emotion"])
    op.create_index("ix_emotion_predictions_model_name", "emotion_predictions", ["model_name"])

    op.create_table(
        "behavior_metrics",
        sa.Column("id", UUID_TYPE, primary_key=True, nullable=False),
        sa.Column(
            "session_id",
            UUID_TYPE,
            sa.ForeignKey("analysis_sessions.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("positivity_score", sa.Float(), nullable=True),
        sa.Column("negativity_score", sa.Float(), nullable=True),
        sa.Column("engagement_score", sa.Float(), nullable=True),
        sa.Column("linguistic_complexity", sa.Float(), nullable=True),
        sa.Column("emotional_variance", sa.Float(), nullable=True),
        sa.Column("posting_frequency", sa.Float(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_table(
        "explanations",
        sa.Column("id", UUID_TYPE, primary_key=True, nullable=False),
        sa.Column(
            "session_id",
            UUID_TYPE,
            sa.ForeignKey("analysis_sessions.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("explanation_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("important_keywords", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", UUID_TYPE, primary_key=True, nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("endpoint", sa.String(length=255), nullable=False),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "user_id",
            UUID_TYPE,
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_endpoint", "audit_logs", ["endpoint"])
    op.create_index("ix_audit_logs_timestamp", "audit_logs", ["timestamp"])
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_audit_logs_user_id", table_name="audit_logs")
    op.drop_index("ix_audit_logs_timestamp", table_name="audit_logs")
    op.drop_index("ix_audit_logs_endpoint", table_name="audit_logs")
    op.drop_index("ix_audit_logs_action", table_name="audit_logs")
    op.drop_table("audit_logs")
    op.drop_table("explanations")
    op.drop_table("behavior_metrics")
    op.drop_index("ix_emotion_predictions_model_name", table_name="emotion_predictions")
    op.drop_index("ix_emotion_predictions_primary_emotion", table_name="emotion_predictions")
    op.drop_table("emotion_predictions")
    op.drop_table("analysis_inputs")
    op.drop_index("ix_analysis_sessions_status", table_name="analysis_sessions")
    op.drop_index("ix_analysis_sessions_source_type", table_name="analysis_sessions")
    op.drop_index("ix_analysis_sessions_user_id", table_name="analysis_sessions")
    op.drop_table("analysis_sessions")
    op.drop_index("ix_model_versions_model_name", table_name="model_versions")
    op.drop_table("model_versions")
    op.drop_table("users")
