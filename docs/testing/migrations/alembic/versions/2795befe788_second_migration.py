"""Second Migration

Revision ID: 2795befe788
Revises: 523c20aa695
Create Date: 2015-11-04 12:16:04.467765

"""

# revision identifiers, used by Alembic.
revision = '2795befe788'
down_revision = '523c20aa695'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.create_table('roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Unicode(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('addresses')
    op.add_column(
        'employees', sa.Column('number_of_pets', sa.Integer(), nullable=False)
    )
    op.add_column(
        'employees', sa.Column('role_id', sa.Integer(), nullable=False)
    )
    op.create_index(
        op.f('ix_employees_name'), 'employees', ['name'], unique=True
    )
    op.drop_index('name', table_name='employees')
    op.create_foreign_key(
        'fk_employees_roles', 'employees', 'roles', ['role_id'], ['id']
    )
    op.drop_column('employees', 'favourite_meal')
    op.alter_column(
        'phone_numbers',
        'number',
        existing_type=mysql.VARCHAR(length=40),
        nullable=False
    )


def downgrade():
    op.alter_column(
        'phone_numbers',
        'number',
        existing_type=mysql.VARCHAR(length=40),
        nullable=True
    )
    op.add_column(
        'employees',
        sa.Column(
            'favourite_meal',
            mysql.ENUM('meat', 'vegan', 'vegetarian'),
            nullable=False
        )
    )
    op.drop_constraint('fk_employees_roles', 'employees', type_='foreignkey')
    op.create_index('name', 'employees', ['name'], unique=True)
    op.drop_index(op.f('ix_employees_name'), table_name='employees')
    op.drop_column('employees', 'role_id')
    op.drop_column('employees', 'number_of_pets')
    op.create_table('addresses',
        sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
        sa.Column('address', mysql.VARCHAR(length=200), nullable=True),
        sa.Column('zip_code', mysql.VARCHAR(length=20), nullable=True),
        sa.Column('city', mysql.VARCHAR(length=100), nullable=True),
        sa.Column('country', mysql.VARCHAR(length=3), nullable=True),
        sa.Column(
            'person_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=False
        ),
        sa.ForeignKeyConstraint(
            ['person_id'], ['employees.id'], name='fk_addresses_employees'
        ),
        sa.PrimaryKeyConstraint('id'),
        mysql_default_charset='utf8',
        mysql_engine='InnoDB'
    )
    op.drop_table('roles')
