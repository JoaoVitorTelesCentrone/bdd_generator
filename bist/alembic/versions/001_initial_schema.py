"""Initial BIST schema.

Revision ID: 001
Revises:
Create Date: 2026-04-16
"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "test_runs",
        sa.Column("id",           sa.Integer(),    nullable=False, autoincrement=True),
        sa.Column("started_at",   sa.Float(),      nullable=False),
        sa.Column("env_url",      sa.Text(),       nullable=False),
        sa.Column("status",       sa.String(20),   nullable=False),
        sa.Column("duration_ms",  sa.Integer(),    nullable=True,  server_default="0"),
        sa.Column("feature_path", sa.Text(),       nullable=True,  server_default=""),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "scenarios",
        sa.Column("id",          sa.Integer(),   nullable=False, autoincrement=True),
        sa.Column("run_id",      sa.Integer(),   nullable=False),
        sa.Column("name",        sa.Text(),      nullable=False),
        sa.Column("status",      sa.String(20),  nullable=False),
        sa.Column("duration_ms", sa.Integer(),   nullable=True, server_default="0"),
        sa.Column("error",       sa.Text(),      nullable=True, server_default=""),
        sa.Column("video_path",  sa.Text(),      nullable=True, server_default=""),
        sa.ForeignKeyConstraint(["run_id"], ["test_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "steps",
        sa.Column("id",              sa.Integer(),  nullable=False, autoincrement=True),
        sa.Column("scenario_id",     sa.Integer(),  nullable=False),
        sa.Column("step_text",       sa.Text(),     nullable=False),
        sa.Column("status",          sa.String(20), nullable=False),
        sa.Column("duration_ms",     sa.Integer(),  nullable=True, server_default="0"),
        sa.Column("screenshot_path", sa.Text(),     nullable=True, server_default=""),
        sa.ForeignKeyConstraint(["scenario_id"], ["scenarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "selector_cache",
        sa.Column("id",            sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("step_pattern",  sa.Text(),    nullable=False),
        sa.Column("selector",      sa.Text(),    nullable=False),
        sa.Column("success_count", sa.Integer(), nullable=True, server_default="1"),
        sa.Column("last_used",     sa.Float(),   nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("step_pattern", "selector"),
    )
    op.create_table(
        "healing_log",
        sa.Column("id",              sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("scenario_id",     sa.Integer(), nullable=True),
        sa.Column("step_text",       sa.Text(),    nullable=False),
        sa.Column("failed_selector", sa.Text(),    nullable=False),
        sa.Column("healed_selector", sa.Text(),    nullable=False),
        sa.Column("timestamp",       sa.Float(),   nullable=False),
        sa.ForeignKeyConstraint(["scenario_id"], ["scenarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_test_runs_started_at", "test_runs", ["started_at"])
    op.create_index("ix_scenarios_run_id",     "scenarios", ["run_id"])
    op.create_index("ix_steps_scenario_id",    "steps",     ["scenario_id"])


def downgrade() -> None:
    op.drop_table("healing_log")
    op.drop_table("selector_cache")
    op.drop_table("steps")
    op.drop_table("scenarios")
    op.drop_table("test_runs")
