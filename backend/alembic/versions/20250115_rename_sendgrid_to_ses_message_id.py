"""rename sendgrid_message_id to ses_message_id

Revision ID: 20250115_rename_ses_id
Revises: 5190413f17b0
Create Date: 2025-01-15 12:00:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '20250115_rename_ses_id'
down_revision = '5190413f17b0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Rename column from sendgrid_message_id to ses_message_id
    op.alter_column('email_logs', 'sendgrid_message_id', new_column_name='ses_message_id')


def downgrade() -> None:
    # Revert column name back to sendgrid_message_id
    op.alter_column('email_logs', 'ses_message_id', new_column_name='sendgrid_message_id')

