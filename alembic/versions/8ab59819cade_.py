"""empty message

Revision ID: 8ab59819cade
Revises: 
Create Date: 2020-10-10 01:08:26.803140

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "8ab59819cade"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "link",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("first_time_seen", sa.DateTime(), nullable=False),
        sa.Column("last_time_scraped", sa.DateTime(), nullable=True),
        sa.Column("is_closed", sa.Integer(), nullable=True),
        sa.Column("link_type", sa.String(length=10), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("url"),
    )
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("olx_user_slug", sa.String(length=100), nullable=True),
        sa.Column("on_olx_since", sa.DateTime(), nullable=True),
        sa.Column("phone_number", sa.String(length=20), nullable=True),
        sa.Column("agency_otodom_id", sa.Integer(), nullable=True),
        sa.Column("agency_name", sa.String(length=100), nullable=True),
        sa.Column("agency_address", sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "advertisement",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("link_id", sa.Integer(), nullable=True),
        sa.Column("scraped_time", sa.DateTime(), nullable=True),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Unicode(length=50000), nullable=True),
        sa.Column("private_business", sa.String(length=30), nullable=True),
        sa.Column("floor", sa.String(), nullable=True),
        sa.Column("builttype", sa.String(), nullable=True),
        sa.Column("room_no", sa.String(), nullable=True),
        sa.Column("furniture", sa.String(), nullable=True),
        sa.Column("price", sa.Float(precision=10), nullable=False),
        sa.Column("size_m2", sa.Float(), nullable=False),
        sa.Column("build_year", sa.Integer(), nullable=True),
        sa.Column("location", sa.String(length=1000), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("olx_id", sa.Integer(), nullable=True),
        sa.Column("otodom_id", sa.Integer(), nullable=True),
        sa.Column("added_time", sa.DateTime(), nullable=True),
        sa.Column("views_number", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["link_id"],
            ["link.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("advertisement")
    op.drop_table("user")
    op.drop_table("link")
    # ### end Alembic commands ###
