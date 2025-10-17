from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_create_orders'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    with op.batch_alter_table('orders', schema=None) as batch_op:
        pass

    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('city', sa.String(length=120), nullable=False),
        sa.Column('street', sa.String(length=160), nullable=False),
        sa.Column('apartment', sa.String(length=30), nullable=True),
        sa.Column('floor', sa.Integer(), nullable=True),
        sa.Column('entrance', sa.String(length=30), nullable=True),
        sa.Column('bottles', sa.Integer(), nullable=False),
        sa.Column('comment', sa.String(length=500), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='В процессе'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(op.f('ix_orders_id'), 'orders', ['id'], unique=False)
    op.create_index(op.f('ix_orders_city'), 'orders', ['city'], unique=False)
    op.create_index(op.f('ix_orders_created_at'), 'orders', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_orders_created_at'), table_name='orders')
    op.drop_index(op.f('ix_orders_city'), table_name='orders')
    op.drop_index(op.f('ix_orders_id'), table_name='orders')
    op.drop_table('orders')
