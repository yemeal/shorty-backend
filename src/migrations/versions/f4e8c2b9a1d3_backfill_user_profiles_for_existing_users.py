"""backfill user_profiles for users created before the profile table

Revision ID: f4e8c2b9a1d3
Revises: 541e53335ee7
Create Date: 2026-04-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f4e8c2b9a1d3"
down_revision: Union[str, Sequence[str], None] = "541e53335ee7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Insert default profile rows for users that have none (e.g. prod users predating user_profiles)."""
    op.execute(
        sa.text(
            """
            INSERT INTO user_profiles (
                id,
                user_id,
                emoji_avatar,
                ui_theme,
                ui_language,
                bio,
                timezone,
                created_at,
                updated_at
            )
            SELECT
                gen_random_uuid(),
                u.id,
                '⚡️',
                'system',
                'en',
                NULL,
                NULL,
                NOW(),
                NULL
            FROM users u
            WHERE NOT EXISTS (
                SELECT 1 FROM user_profiles p WHERE p.user_id = u.id
            );
            """
        )
    )


def downgrade() -> None:
    """
    Not reversed automatically: rows are indistinguishable from manually created defaults.
    Restore from backup if you must undo this data migration.
    """
    pass
