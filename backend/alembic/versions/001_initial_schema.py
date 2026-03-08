"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-03-07

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Use raw SQL so every statement is safe to re-run against a DB that was
    # created before Alembic was introduced (no alembic_version row yet).

    op.execute("""
        DO $$ BEGIN
            CREATE TYPE userrole AS ENUM ('super_admin', 'company_admin', 'lab_admin', 'member');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id UUID PRIMARY KEY,
            name VARCHAR NOT NULL,
            created_at TIMESTAMP NOT NULL
        )
    """)
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_companies_name ON companies (name)")

    op.execute("""
        CREATE TABLE IF NOT EXISTS labs (
            id UUID PRIMARY KEY,
            company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
            name VARCHAR NOT NULL,
            created_at TIMESTAMP NOT NULL
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY,
            lab_id UUID REFERENCES labs(id) ON DELETE CASCADE,
            username VARCHAR NOT NULL,
            password_hash VARCHAR NOT NULL,
            role userrole NOT NULL,
            created_at TIMESTAMP NOT NULL
        )
    """)
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username ON users (username)")

    op.execute("""
        CREATE TABLE IF NOT EXISTS designs (
            id UUID PRIMARY KEY,
            lab_id UUID NOT NULL REFERENCES labs(id) ON DELETE CASCADE,
            created_by UUID NOT NULL REFERENCES users(id),
            name VARCHAR NOT NULL,
            description VARCHAR,
            nodes JSONB NOT NULL,
            edges JSONB NOT NULL,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL
        )
    """)


def downgrade():
    op.drop_table("designs")
    op.execute("DROP INDEX IF EXISTS ix_users_username")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS userrole")
    op.drop_table("labs")
    op.execute("DROP INDEX IF EXISTS ix_companies_name")
    op.drop_table("companies")
