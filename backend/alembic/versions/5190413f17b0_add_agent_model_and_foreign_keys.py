"""
Revision script.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '5190413f17b0'
down_revision = '20251101_allow_dup_emails'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create agents table first
    op.create_table(
        'agents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('google_sub', sa.String(length=255), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('auth_provider', sa.String(length=20), nullable=False, server_default='email'),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('title', sa.String(length=100), nullable=True),
        sa.Column('company', sa.String(length=200), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for agents table
    op.create_index('ix_agents_id', 'agents', ['id'], unique=False)
    op.create_index('ix_agents_email', 'agents', ['email'], unique=True)
    op.create_index('ix_agents_google_sub', 'agents', ['google_sub'], unique=True)
    op.create_index('ix_agents_is_active', 'agents', ['is_active'], unique=False)
    op.create_index('ix_agents_email_active', 'agents', ['email', 'is_active'], unique=False)
    op.create_index('ix_agents_google_sub_active', 'agents', ['google_sub', 'is_active'], unique=False)
    
    # Create a default "System Agent" for existing data
    op.execute("""
        INSERT INTO agents (email, name, auth_provider, is_active, created_at, updated_at)
        VALUES ('system@realtoros.com', 'System Agent', 'email', true, NOW(), NOW())
    """)
    
    # Add agent_id columns (nullable first)
    op.add_column('clients', sa.Column('agent_id', sa.Integer(), nullable=True))
    op.add_column('tasks', sa.Column('agent_id', sa.Integer(), nullable=True))
    op.add_column('email_logs', sa.Column('agent_id', sa.Integer(), nullable=True))
    op.add_column('email_logs', sa.Column('from_name', sa.String(length=200), nullable=True))
    op.add_column('email_logs', sa.Column('from_email', sa.String(length=255), nullable=True))
    
    # Update existing records to use system agent
    op.execute("""
        UPDATE clients 
        SET agent_id = (SELECT id FROM agents WHERE email = 'system@realtoros.com')
        WHERE agent_id IS NULL
    """)
    op.execute("""
        UPDATE tasks 
        SET agent_id = (SELECT id FROM agents WHERE email = 'system@realtoros.com')
        WHERE agent_id IS NULL
    """)
    op.execute("""
        UPDATE email_logs 
        SET agent_id = (SELECT id FROM agents WHERE email = 'system@realtoros.com')
        WHERE agent_id IS NULL
    """)
    
    # Make agent_id NOT NULL
    op.alter_column('clients', 'agent_id', nullable=False)
    op.alter_column('tasks', 'agent_id', nullable=False)
    op.alter_column('email_logs', 'agent_id', nullable=False)
    
    # Add foreign keys
    op.create_foreign_key('fk_clients_agent_id', 'clients', 'agents', ['agent_id'], ['id'])
    op.create_foreign_key('fk_tasks_agent_id', 'tasks', 'agents', ['agent_id'], ['id'])
    op.create_foreign_key('fk_email_logs_agent_id', 'email_logs', 'agents', ['agent_id'], ['id'])
    
    # Add indexes
    op.create_index('ix_clients_agent_id', 'clients', ['agent_id'], unique=False)
    op.create_index('ix_tasks_agent_id', 'tasks', ['agent_id'], unique=False)
    op.create_index('ix_email_logs_agent_id', 'email_logs', ['agent_id'], unique=False)
    
    # Add composite index for clients (agent_id + stage)
    op.create_index('ix_clients_agent_stage', 'clients', ['agent_id', 'stage'], unique=False)


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('ix_clients_agent_stage', table_name='clients')
    op.drop_index('ix_email_logs_agent_id', table_name='email_logs')
    op.drop_index('ix_tasks_agent_id', table_name='tasks')
    op.drop_index('ix_clients_agent_id', table_name='clients')
    
    # Drop foreign keys
    op.drop_constraint('fk_email_logs_agent_id', 'email_logs', type_='foreignkey')
    op.drop_constraint('fk_tasks_agent_id', 'tasks', type_='foreignkey')
    op.drop_constraint('fk_clients_agent_id', 'clients', type_='foreignkey')
    
    # Remove columns
    op.drop_column('email_logs', 'from_email')
    op.drop_column('email_logs', 'from_name')
    op.drop_column('email_logs', 'agent_id')
    op.drop_column('tasks', 'agent_id')
    op.drop_column('clients', 'agent_id')
    
    # Drop agents table indexes
    op.drop_index('ix_agents_google_sub_active', table_name='agents')
    op.drop_index('ix_agents_email_active', table_name='agents')
    op.drop_index('ix_agents_is_active', table_name='agents')
    op.drop_index('ix_agents_google_sub', table_name='agents')
    op.drop_index('ix_agents_email', table_name='agents')
    op.drop_index('ix_agents_id', table_name='agents')
    
    # Drop agents table
    op.drop_table('agents')
