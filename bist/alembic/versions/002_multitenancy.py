"""Phase 4 — multi-tenancy, billing, and SSO tables.

Adds:
  tenants, api_keys, usage_events, stripe_subscriptions,
  sso_sessions, saml_configs

Extends test_runs with tenant_id (nullable, FK → tenants.id).

Revision ID: 002
Revises: 001
Create Date: 2026-04-17
"""
import sqlalchemy as sa
from alembic import op

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── tenants ───────────────────────────────────────────────────────────────
    op.create_table(
        "tenants",
        sa.Column("id",         sa.Integer(),    nullable=False, autoincrement=True),
        sa.Column("name",       sa.Text(),       nullable=False),
        sa.Column("tier",       sa.String(20),   nullable=False, server_default="free"),
        sa.Column("created_at", sa.Float(),      nullable=False),
        sa.Column("active",     sa.Integer(),    nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── api_keys ──────────────────────────────────────────────────────────────
    op.create_table(
        "api_keys",
        sa.Column("id",         sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("tenant_id",  sa.Integer(), nullable=False),
        sa.Column("key_hash",   sa.Text(),    nullable=False),
        sa.Column("key_prefix", sa.Text(),    nullable=False),
        sa.Column("label",      sa.Text(),    nullable=True,  server_default=""),
        sa.Column("created_at", sa.Float(),   nullable=False),
        sa.Column("last_used",  sa.Float(),   nullable=True),
        sa.Column("active",     sa.Integer(), nullable=False, server_default="1"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key_hash"),
    )

    # ── usage_events ──────────────────────────────────────────────────────────
    op.create_table(
        "usage_events",
        sa.Column("id",          sa.Integer(),  nullable=False, autoincrement=True),
        sa.Column("tenant_id",   sa.Integer(),  nullable=False),
        sa.Column("event_type",  sa.Text(),     nullable=False),
        sa.Column("quantity",    sa.Integer(),  nullable=False, server_default="1"),
        sa.Column("metadata",    sa.Text(),     nullable=True,  server_default="{}"),
        sa.Column("recorded_at", sa.Float(),    nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_usage_events_tenant_type", "usage_events", ["tenant_id", "event_type"])

    # ── stripe_subscriptions ──────────────────────────────────────────────────
    op.create_table(
        "stripe_subscriptions",
        sa.Column("id",                     sa.Integer(),  nullable=False, autoincrement=True),
        sa.Column("tenant_id",              sa.Integer(),  nullable=False),
        sa.Column("stripe_customer_id",     sa.Text(),     nullable=False),
        sa.Column("stripe_subscription_id", sa.Text(),     nullable=False),
        sa.Column("tier",                   sa.String(20), nullable=False, server_default="free"),
        sa.Column("status",                 sa.String(20), nullable=False, server_default="active"),
        sa.Column("current_period_start",   sa.Float(),    nullable=True),
        sa.Column("current_period_end",     sa.Float(),    nullable=True),
        sa.Column("updated_at",             sa.Float(),    nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id"),
    )

    # ── sso_sessions ──────────────────────────────────────────────────────────
    op.create_table(
        "sso_sessions",
        sa.Column("id",         sa.Integer(),   nullable=False, autoincrement=True),
        sa.Column("tenant_id",  sa.Integer(),   nullable=True),
        sa.Column("state",      sa.Text(),      nullable=False),
        sa.Column("provider",   sa.String(20),  nullable=False, server_default="oauth2"),
        sa.Column("created_at", sa.Float(),     nullable=False),
        sa.Column("expires_at", sa.Float(),     nullable=False),
        sa.Column("user_info",  sa.Text(),      nullable=True,  server_default="{}"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("state"),
    )

    # ── saml_configs ──────────────────────────────────────────────────────────
    op.create_table(
        "saml_configs",
        sa.Column("id",              sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("tenant_id",       sa.Integer(), nullable=False),
        sa.Column("idp_entity_id",   sa.Text(),    nullable=False),
        sa.Column("idp_sso_url",     sa.Text(),    nullable=False),
        sa.Column("idp_cert",        sa.Text(),    nullable=False),
        sa.Column("sp_entity_id",    sa.Text(),    nullable=True,  server_default=""),
        sa.Column("attribute_email", sa.Text(),    nullable=False, server_default="email"),
        sa.Column("attribute_name",  sa.Text(),    nullable=False, server_default="displayName"),
        sa.Column("created_at",      sa.Float(),   nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id"),
    )

    # ── Extend test_runs with tenant_id ───────────────────────────────────────
    op.add_column("test_runs", sa.Column("tenant_id", sa.Integer(), nullable=True))
    try:
        op.create_foreign_key(
            "fk_test_runs_tenant_id", "test_runs", "tenants", ["tenant_id"], ["id"]
        )
    except Exception:
        pass  # SQLite doesn't enforce FKs via DDL; skip gracefully

    op.create_index("ix_test_runs_tenant_id", "test_runs", ["tenant_id"])


def downgrade() -> None:
    op.drop_index("ix_test_runs_tenant_id", "test_runs")
    op.drop_column("test_runs", "tenant_id")
    op.drop_table("saml_configs")
    op.drop_table("sso_sessions")
    op.drop_table("stripe_subscriptions")
    op.drop_index("ix_usage_events_tenant_type", "usage_events")
    op.drop_table("usage_events")
    op.drop_table("api_keys")
    op.drop_table("tenants")
