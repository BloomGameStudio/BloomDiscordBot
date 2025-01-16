"""Remove yes_count from ongoing_votes

Revision ID: remove_yes_count
Revises: 
Create Date: 2024-01-25 06:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'remove_yes_count'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Drop the yes_count column from ongoing_votes table
    op.drop_column('ongoing_votes', 'yes_count')


def downgrade():
    # Add back the yes_count column if we need to rollback
    op.add_column('ongoing_votes',
        sa.Column('yes_count', sa.Integer(), nullable=True)
    ) 