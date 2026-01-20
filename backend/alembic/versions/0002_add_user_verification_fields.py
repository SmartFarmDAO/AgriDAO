"""Add email_verified and phone_verified to user table

Revision ID: 0002_user_verify
Revises: d0e34b587fc7
Create Date: 2025-11-20
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0002_user_verify'
down_revision: Union[str, None] = 'd0e34b587fc7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add email_verified column if it doesn't exist
    op.execute("""
        DO $$ 
        BEGIN 
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='user' AND column_name='email_verified'
            ) THEN
                ALTER TABLE "user" ADD COLUMN email_verified BOOLEAN DEFAULT FALSE NOT NULL;
            END IF;
        END $$;
    """)
    
    # Add phone_verified column if it doesn't exist
    op.execute("""
        DO $$ 
        BEGIN 
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='user' AND column_name='phone_verified'
            ) THEN
                ALTER TABLE "user" ADD COLUMN phone_verified BOOLEAN DEFAULT FALSE NOT NULL;
            END IF;
        END $$;
    """)
    
    # Add profile_image_url column if it doesn't exist
    op.execute("""
        DO $$ 
        BEGIN 
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='user' AND column_name='profile_image_url'
            ) THEN
                ALTER TABLE "user" ADD COLUMN profile_image_url VARCHAR;
            END IF;
        END $$;
    """)
    
    # Add status column if it doesn't exist
    op.execute("""
        DO $$ 
        BEGIN 
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='user' AND column_name='status'
            ) THEN
                ALTER TABLE "user" ADD COLUMN status VARCHAR DEFAULT 'active' NOT NULL;
            END IF;
        END $$;
    """)
    
    # Add updated_at column if it doesn't exist
    op.execute("""
        DO $$ 
        BEGIN 
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='user' AND column_name='updated_at'
            ) THEN
                ALTER TABLE "user" ADD COLUMN updated_at TIMESTAMP;
            END IF;
        END $$;
    """)


def downgrade() -> None:
    # Remove columns if they exist
    op.execute("""
        DO $$ 
        BEGIN 
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='user' AND column_name='email_verified'
            ) THEN
                ALTER TABLE "user" DROP COLUMN email_verified;
            END IF;
        END $$;
    """)
    
    op.execute("""
        DO $$ 
        BEGIN 
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='user' AND column_name='phone_verified'
            ) THEN
                ALTER TABLE "user" DROP COLUMN phone_verified;
            END IF;
        END $$;
    """)
    
    op.execute("""
        DO $$ 
        BEGIN 
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='user' AND column_name='profile_image_url'
            ) THEN
                ALTER TABLE "user" DROP COLUMN profile_image_url;
            END IF;
        END $$;
    """)
    
    op.execute("""
        DO $$ 
        BEGIN 
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='user' AND column_name='status'
            ) THEN
                ALTER TABLE "user" DROP COLUMN status;
            END IF;
        END $$;
    """)
    
    op.execute("""
        DO $$ 
        BEGIN 
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='user' AND column_name='updated_at'
            ) THEN
                ALTER TABLE "user" DROP COLUMN updated_at;
            END IF;
        END $$;
    """)
