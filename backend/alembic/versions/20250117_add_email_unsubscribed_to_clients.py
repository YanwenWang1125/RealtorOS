"""Add email_unsubscribed field to clients

Revision ID: 20250117_add_email_unsubscribed
Revises: b4d7875e7f62
Create Date: 2025-01-17 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20250117_add_email_unsubscribed'
down_revision = 'b4d7875e7f62'
branch_labels = None
depends_on = None


def upgrade():
    # Add email_unsubscribed column to clients table
    op.add_column('clients', sa.Column('email_unsubscribed', sa.Boolean(), nullable=False, server_default='false'))
    # Create index for email_unsubscribed
    op.create_index('ix_clients_email_unsubscribed', 'clients', ['email_unsubscribed'])


def downgrade():
    # Drop index
    op.drop_index('ix_clients_email_unsubscribed', table_name='clients')
    # Drop column
    op.drop_column('clients', 'email_unsubscribed')

