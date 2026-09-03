"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

This generated migration is reviewed source code. Keep schema changes small,
reversible, and paired with application compatibility during rollout.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

revision: str = ${repr(up_revision)}
down_revision: Union[str, Sequence[str], None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    """Apply the generated schema change."""
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """Reverse the generated schema change."""
    ${downgrades if downgrades else "pass"}
