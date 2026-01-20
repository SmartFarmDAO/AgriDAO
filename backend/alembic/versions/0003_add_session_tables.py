"""Add UserSession and TokenBlacklist tables

Revision ID: 0003_session_tables
Revises: 0002_user_verify
Create Date: 2025-11-20
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0003_session_tables'
down_revision: Union[str, None] = '0002_user_verify'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create usersession table
    op.execute("""
        CREATE TABLE IF NOT EXISTS usersession (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES "user"(id),
            session_token VARCHAR NOT NULL UNIQUE,
            refresh_token VARCHAR NOT NULL UNIQUE,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_accessed TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            user_agent VARCHAR,
            ip_address VARCHAR
        );
    """)
    
    # Create tokenblacklist table
    op.execute("""
        CREATE TABLE IF NOT EXISTS tokenblacklist (
            id SERIAL PRIMARY KEY,
            token_jti VARCHAR NOT NULL UNIQUE,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Create indexes for better performance
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_usersession_user_id 
        ON usersession(user_id);
    """)
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_usersession_session_token 
        ON usersession(session_token);
    """)
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_usersession_refresh_token 
        ON usersession(refresh_token);
    """)
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_tokenblacklist_token_jti 
        ON tokenblacklist(token_jti);
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS tokenblacklist CASCADE;")
    op.execute("DROP TABLE IF EXISTS usersession CASCADE;")
