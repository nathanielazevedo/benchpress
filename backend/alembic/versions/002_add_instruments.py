"""add instruments table

Revision ID: 002
Revises: 001
Create Date: 2026-03-08

"""
from alembic import op

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE instrumentstatus AS ENUM ('online', 'offline');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS instruments (
            id UUID PRIMARY KEY,
            instrument_id VARCHAR NOT NULL,
            name VARCHAR NOT NULL,
            lab_id UUID REFERENCES labs(id) ON DELETE SET NULL,
            status instrumentstatus NOT NULL,
            last_seen_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP NOT NULL
        )
    """)
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_instruments_instrument_id ON instruments (instrument_id)")


def downgrade():
    op.execute("DROP INDEX IF EXISTS ix_instruments_instrument_id")
    op.drop_table("instruments")
    op.execute("DROP TYPE IF EXISTS instrumentstatus")
