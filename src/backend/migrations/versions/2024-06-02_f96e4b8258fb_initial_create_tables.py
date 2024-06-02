"""
Initial create tables

Revision ID: f96e4b8258fb
Revises:
Create Date: 2024-06-02 13:40:50.985287

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f96e4b8258fb"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Миграция на обновление"""

    op.execute("create schema if not exists content")
    op.create_table(
        "admin",
        sa.Column("username", sa.String(length=255), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
        schema="content",
    )
    op.create_table(
        "dining_table",
        sa.Column("table_number", sa.Integer(), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("table_number"),
        schema="content",
    )
    op.create_table(
        "dining_type",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="content",
    )
    op.create_table(
        "physician",
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("specialization", sa.String(length=255), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="content",
    )
    op.create_table(
        "room_type",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="content",
    )
    op.create_table(
        "user",
        sa.Column("first_name", sa.String(length=255), nullable=False),
        sa.Column("last_name", sa.String(length=255), nullable=False),
        sa.Column("passport_series", sa.Integer(), nullable=False),
        sa.Column("passport_number", sa.Integer(), nullable=False),
        sa.Column("medical_policy", sa.Integer(), nullable=False),
        sa.Column("birth_date", sa.Date(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="content",
    )
    op.create_table(
        "room",
        sa.Column("room_number", sa.Integer(), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column("type_id", sa.Uuid(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["type_id"],
            ["content.room_type.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("room_number"),
        schema="content",
    )
    op.create_table(
        "travel_package",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("room_type_id", sa.Uuid(), nullable=False),
        sa.Column("dining_type_id", sa.Uuid(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["dining_type_id"],
            ["content.dining_type.id"],
        ),
        sa.ForeignKeyConstraint(
            ["room_type_id"],
            ["content.room_type.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="content",
    )
    op.create_table(
        "registration",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("room_id", sa.Uuid(), nullable=False),
        sa.Column("dining_table_id", sa.Uuid(), nullable=False),
        sa.Column("physician_id", sa.Uuid(), nullable=False),
        sa.Column("travel_package_id", sa.Uuid(), nullable=False),
        sa.Column("check_in_date", sa.DateTime(), nullable=False),
        sa.Column("check_out_date", sa.DateTime(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["dining_table_id"],
            ["content.dining_table.id"],
        ),
        sa.ForeignKeyConstraint(
            ["physician_id"],
            ["content.physician.id"],
        ),
        sa.ForeignKeyConstraint(
            ["room_id"],
            ["content.room.id"],
        ),
        sa.ForeignKeyConstraint(
            ["travel_package_id"],
            ["content.travel_package.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["content.user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="content",
    )


def downgrade() -> None:
    """Миграция на удаление"""

    op.drop_table("registration", schema="content")
    op.drop_table("travel_package", schema="content")
    op.drop_table("room", schema="content")
    op.drop_table("user", schema="content")
    op.drop_table("room_type", schema="content")
    op.drop_table("physician", schema="content")
    op.drop_table("dining_type", schema="content")
    op.drop_table("dining_table", schema="content")
    op.drop_table("admin", schema="content")
    op.execute("drop schema content")
