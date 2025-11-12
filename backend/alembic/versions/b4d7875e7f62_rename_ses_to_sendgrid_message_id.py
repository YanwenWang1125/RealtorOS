"""rename_ses_to_sendgrid_message_id

Revision ID: b4d7875e7f62
Revises: 20250116_add_email_preview
Create Date: 2025-11-12 05:35:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b4d7875e7f62'
down_revision = '20250116_add_email_preview'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if ses_message_id exists and rename it, or add sendgrid_message_id
    # Using raw SQL to check and handle both cases
    conn = op.get_bind()
    
    # Check if ses_message_id column exists
    result = conn.execute(sa.text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='email_logs' AND column_name='ses_message_id'
    """))
    has_ses = result.fetchone() is not None
    
    # Check if sendgrid_message_id column exists
    result = conn.execute(sa.text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='email_logs' AND column_name='sendgrid_message_id'
    """))
    has_sendgrid = result.fetchone() is not None
    
    if has_ses and not has_sendgrid:
        # Rename ses_message_id to sendgrid_message_id
        op.alter_column('email_logs', 'ses_message_id', new_column_name='sendgrid_message_id')
        # Drop old index if it exists (using raw SQL to avoid transaction issues)
        conn.execute(sa.text("""
            DROP INDEX IF EXISTS ix_email_logs_ses_message_id
        """))
        # Create new index only if it doesn't exist
        conn.execute(sa.text("""
            CREATE INDEX IF NOT EXISTS ix_email_logs_sendgrid_message_id ON email_logs (sendgrid_message_id)
        """))
    elif not has_sendgrid:
        # Add sendgrid_message_id column if it doesn't exist
        op.add_column('email_logs', sa.Column('sendgrid_message_id', sa.String(length=255), nullable=True))
        # Create index only if it doesn't exist
        conn.execute(sa.text("""
            CREATE INDEX IF NOT EXISTS ix_email_logs_sendgrid_message_id ON email_logs (sendgrid_message_id)
        """))
    # If sendgrid_message_id already exists, do nothing


def downgrade() -> None:
    # Reverse: rename sendgrid_message_id back to ses_message_id
    conn = op.get_bind()
    
    # Check if sendgrid_message_id exists
    result = conn.execute(sa.text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='email_logs' AND column_name='sendgrid_message_id'
    """))
    has_sendgrid = result.fetchone() is not None
    
    if has_sendgrid:
        op.alter_column('email_logs', 'sendgrid_message_id', new_column_name='ses_message_id')
        conn.execute(sa.text("""
            DROP INDEX IF EXISTS ix_email_logs_sendgrid_message_id
        """))
        conn.execute(sa.text("""
            CREATE INDEX IF NOT EXISTS ix_email_logs_ses_message_id ON email_logs (ses_message_id)
        """))
