"""add email_preview to tasks

Revision ID: 20250116_add_email_preview
Revises: 20250115_rename_ses_id
Create Date: 2025-01-16 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250116_add_email_preview'
down_revision = '20250115_rename_ses_id'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add email_preview JSON column to tasks table
    op.add_column('tasks', sa.Column('email_preview', postgresql.JSON(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    # Remove email_preview column
    op.drop_column('tasks', 'email_preview')

