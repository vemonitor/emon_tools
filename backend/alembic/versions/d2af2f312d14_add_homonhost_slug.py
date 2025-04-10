"""add homonHost slug

Revision ID: d2af2f312d14
Revises: b084d745a76b
Create Date: 2025-03-10 17:48:14.007904

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = 'd2af2f312d14'
down_revision: Union[str, None] = 'b084d745a76b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('archivefile', 'file_name',
               existing_type=mysql.VARCHAR(length=50),
               nullable=False)
    op.add_column('emonhost', sa.Column('slug', sqlmodel.sql.sqltypes.AutoString(length=40), nullable=False))
    op.alter_column('emonhost', 'name',
               existing_type=mysql.VARCHAR(length=255),
               type_=sqlmodel.sql.sqltypes.AutoString(length=40),
               existing_nullable=False)
    op.create_unique_constraint(None, 'emonhost', ['slug'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'emonhost', type_='unique')
    op.alter_column('emonhost', 'name',
               existing_type=sqlmodel.sql.sqltypes.AutoString(length=40),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=False)
    op.drop_column('emonhost', 'slug')
    op.alter_column('archivefile', 'file_name',
               existing_type=mysql.VARCHAR(length=50),
               nullable=True)
    # ### end Alembic commands ###
