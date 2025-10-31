"""init

Revision ID: 9632c8ae555a
Revises: 
Create Date: 2025-01-14 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '9632c8ae555a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create clients table first (no dependencies)
    op.create_table(
        'clients',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('property_address', sa.String(length=200), nullable=False),
        sa.Column('property_type', sa.String(length=50), nullable=False),
        sa.Column('stage', sa.String(length=50), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('custom_fields', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_contacted', sa.DateTime(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_clients_email', 'clients', ['email'], unique=True)
    op.create_index('ix_clients_id', 'clients', ['id'], unique=False)
    op.create_index('ix_clients_is_deleted', 'clients', ['is_deleted'], unique=False)
    op.create_index('ix_clients_stage', 'clients', ['stage'], unique=False)
    op.create_index('ix_clients_email_is_deleted', 'clients', ['email', 'is_deleted'], unique=False)
    op.create_index('ix_clients_stage_is_deleted', 'clients', ['stage', 'is_deleted'], unique=False)

    # Create tasks table without email_sent_id FK first (to break circular dependency)
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('client_id', sa.Integer(), nullable=False),
        sa.Column('email_sent_id', sa.Integer(), nullable=True),
        sa.Column('followup_type', sa.String(length=50), nullable=False),
        sa.Column('scheduled_for', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('priority', sa.String(length=20), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tasks_client_id', 'tasks', ['client_id'], unique=False)
    op.create_index('ix_tasks_id', 'tasks', ['id'], unique=False)
    op.create_index('ix_tasks_scheduled_for', 'tasks', ['scheduled_for'], unique=False)
    op.create_index('ix_tasks_status', 'tasks', ['status'], unique=False)
    op.create_index('ix_tasks_client_status', 'tasks', ['client_id', 'status'], unique=False)
    op.create_index('ix_tasks_scheduled_status', 'tasks', ['scheduled_for', 'status'], unique=False)

    # Create email_logs table with FK to tasks (now that tasks exists)
    op.create_table(
        'email_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('client_id', sa.Integer(), nullable=False),
        sa.Column('to_email', sa.String(length=255), nullable=False),
        sa.Column('subject', sa.String(length=200), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('sendgrid_message_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('opened_at', sa.DateTime(), nullable=True),
        sa.Column('clicked_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('webhook_events', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_email_logs_client_id', 'email_logs', ['client_id'], unique=False)
    op.create_index('ix_email_logs_created_at', 'email_logs', ['created_at'], unique=False)
    op.create_index('ix_email_logs_id', 'email_logs', ['id'], unique=False)
    op.create_index('ix_email_logs_sendgrid_message_id', 'email_logs', ['sendgrid_message_id'], unique=False)
    op.create_index('ix_email_logs_status', 'email_logs', ['status'], unique=False)
    op.create_index('ix_email_logs_status_client', 'email_logs', ['status', 'client_id'], unique=False)

    # Now add the FK constraint from tasks.email_sent_id to email_logs.id
    op.create_foreign_key('tasks_email_sent_id_fkey', 'tasks', 'email_logs', ['email_sent_id'], ['id'])


def downgrade() -> None:
    # Drop FK first
    op.drop_constraint('tasks_email_sent_id_fkey', 'tasks', type_='foreignkey')
    
    # Drop tables in reverse order
    op.drop_index('ix_email_logs_status_client', table_name='email_logs')
    op.drop_index('ix_email_logs_status', table_name='email_logs')
    op.drop_index('ix_email_logs_sendgrid_message_id', table_name='email_logs')
    op.drop_index('ix_email_logs_id', table_name='email_logs')
    op.drop_index('ix_email_logs_created_at', table_name='email_logs')
    op.drop_index('ix_email_logs_client_id', table_name='email_logs')
    op.drop_table('email_logs')

    op.drop_index('ix_tasks_scheduled_status', table_name='tasks')
    op.drop_index('ix_tasks_client_status', table_name='tasks')
    op.drop_index('ix_tasks_status', table_name='tasks')
    op.drop_index('ix_tasks_scheduled_for', table_name='tasks')
    op.drop_index('ix_tasks_id', table_name='tasks')
    op.drop_index('ix_tasks_client_id', table_name='tasks')
    op.drop_table('tasks')

    op.drop_index('ix_clients_stage_is_deleted', table_name='clients')
    op.drop_index('ix_clients_email_is_deleted', table_name='clients')
    op.drop_index('ix_clients_stage', table_name='clients')
    op.drop_index('ix_clients_is_deleted', table_name='clients')
    op.drop_index('ix_clients_id', table_name='clients')
    op.drop_index('ix_clients_email', table_name='clients')
    op.drop_table('clients')

