"""allow duplicate client emails

Revision ID: 20251101_allow_dup_emails
Revises: 9632c8ae555a
Create Date: 2025-11-01 23:45:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '20251101_allow_dup_emails'
down_revision = '9632c8ae555a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop unique index on clients.email to allow duplicates
    op.drop_index('ix_clients_email', table_name='clients')
    # Recreate a non-unique index on email for performance (optional)
    op.create_index('ix_clients_email', 'clients', ['email'], unique=False)


def downgrade() -> None:
    # Recreate the unique constraint if downgrading
    op.drop_index('ix_clients_email', table_name='clients')
    op.create_index('ix_clients_email', 'clients', ['email'], unique=True)

