import os
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any

import jwt
from passlib.context import CryptContext
from sqlmodel import Session, select
from fastapi import HTTPException

from ..database import engine
from ..models import User, UserSession, TokenBlacklist
from .redis_service import redis_service


class TokenManager:
    """Manages JWT tokens with refresh token support and secure session handling."""
    
    def __init__(self):
        self.jwt_secret = os.getenv("JWT_SECRET", "devsecret")
        self.jwt_algorithm = "HS256"
        self.access_token_expire_minutes = 15
        self.refresh_token_expire_days = 7
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def create_tokens(self, user: User, user_agent: Optional[str] = None, ip_address: Optional[str] = None) -> Dict[str, Any]:
        """Create access and refresh token pair for a user."""
        now = datetime.utcnow()
        access_token_expires = now + timedelta(minutes=self.access_token_expire_minutes)
        refresh_token_expires = now + timedelta(days=self.refresh_token_expire_days)
        
        # Generate unique JTI for token tracking
        access_jti = str(uuid.uuid4())
        refresh_jti = str(uuid.uuid4())
        
        # Create access token
        access_payload = {
            "sub": str(user.id),
            "role": user.role.value,
            "email": user.email,
            "jti": access_jti,
            "type": "access",
            "iat": now,
            "exp": access_token_expires
        }
        
        # Create refresh token
        refresh_payload = {
            "sub": str(user.id),
            "jti": refresh_jti,
            "type": "refresh",
            "iat": now,
            "exp": refresh_token_expires
        }
        
        access_token = jwt.encode(access_payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        refresh_token = jwt.encode(refresh_payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        
        # Store session in database
        with Session(engine) as session:
            # Clean up old sessions for this user (keep only 5 most recent)
            old_sessions = session.exec(
                select(UserSession)
                .where(UserSession.user_id == user.id)
                .order_by(UserSession.created_at.desc())
                .offset(4)
            ).all()
            
            for old_session in old_sessions:
                session.delete(old_session)
            
            # Create new session
            user_session = UserSession(
                user_id=user.id,
                session_token=access_jti,
                refresh_token=refresh_jti,
                expires_at=refresh_token_expires,
                user_agent=user_agent,
                ip_address=ip_address
            )
            session.add(user_session)
            session.commit()
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.access_token_expire_minutes * 60,
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role.value,
                "name": user.name,
                "email_verified": user.email_verified
            }
        }
    
    def validate_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """Validate JWT token and return payload if valid."""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            
            # Check token type
            if payload.get("type") != token_type:
                return None
            
            # Check if token is blacklisted
            jti = payload.get("jti")
            if jti and self._is_token_blacklisted(jti):
                return None
            
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Generate new access token using refresh token."""
        payload = self.validate_token(refresh_token, "refresh")
        if not payload:
            return None
        
        user_id = int(payload.get("sub"))
        refresh_jti = payload.get("jti")
        
        with Session(engine) as session:
            # Verify refresh token exists in session store
            user_session = session.exec(
                select(UserSession)
                .where(UserSession.refresh_token == refresh_jti)
                .where(UserSession.user_id == user_id)
            ).first()
            
            if not user_session or user_session.expires_at < datetime.utcnow():
                return None
            
            # Get user
            user = session.get(User, user_id)
            if not user:
                return None
            
            # Update last accessed time and generate new access token
            user_session.last_accessed = datetime.utcnow()
            
            # Generate new access token (keep same refresh token)
            now = datetime.utcnow()
            access_token_expires = now + timedelta(minutes=self.access_token_expire_minutes)
            access_jti = str(uuid.uuid4())
            
            access_payload = {
                "sub": str(user.id),
                "role": user.role.value,
                "email": user.email,
                "jti": access_jti,
                "type": "access",
                "iat": now,
                "exp": access_token_expires
            }
            
            access_token = jwt.encode(access_payload, self.jwt_secret, algorithm=self.jwt_algorithm)
            
            # Update session token
            user_session.session_token = access_jti
            session.add(user_session)
            session.commit()
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": self.access_token_expire_minutes * 60
            }
    
    def revoke_token(self, token: str) -> bool:
        """Add token to blacklist."""
        payload = self.validate_token(token)
        if not payload:
            return False
        
        jti = payload.get("jti")
        exp = datetime.fromtimestamp(payload.get("exp", 0))
        
        with Session(engine) as session:
            blacklisted_token = TokenBlacklist(
                token_jti=jti,
                expires_at=exp
            )
            session.add(blacklisted_token)
            session.commit()
        
        return True
    
    def revoke_all_user_sessions(self, user_id: int) -> bool:
        """Revoke all sessions for a user."""
        with Session(engine) as session:
            # Get all user sessions
            user_sessions = session.exec(
                select(UserSession).where(UserSession.user_id == user_id)
            ).all()
            
            # Blacklist all tokens and delete sessions
            for user_session in user_sessions:
                # Check if tokens are already blacklisted to avoid duplicates
                existing_access = session.exec(
                    select(TokenBlacklist).where(TokenBlacklist.token_jti == user_session.session_token)
                ).first()
                
                if not existing_access:
                    access_blacklist = TokenBlacklist(
                        token_jti=user_session.session_token,
                        expires_at=user_session.expires_at
                    )
                    session.add(access_blacklist)
                
                existing_refresh = session.exec(
                    select(TokenBlacklist).where(TokenBlacklist.token_jti == user_session.refresh_token)
                ).first()
                
                if not existing_refresh:
                    refresh_blacklist = TokenBlacklist(
                        token_jti=user_session.refresh_token,
                        expires_at=user_session.expires_at
                    )
                    session.add(refresh_blacklist)
                
                # Delete session
                session.delete(user_session)
            
            session.commit()
        
        return True
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions and blacklisted tokens."""
        now = datetime.utcnow()
        count = 0
        
        with Session(engine) as session:
            # Remove expired sessions
            expired_sessions = session.exec(
                select(UserSession).where(UserSession.expires_at < now)
            ).all()
            
            for expired_session in expired_sessions:
                session.delete(expired_session)
                count += 1
            
            # Remove expired blacklisted tokens
            expired_blacklist = session.exec(
                select(TokenBlacklist).where(TokenBlacklist.expires_at < now)
            ).all()
            
            for expired_token in expired_blacklist:
                session.delete(expired_token)
                count += 1
            
            session.commit()
        
        return count
    
    async def store_session_in_redis(self, user_id: int, session_data: Dict[str, Any], 
                                   expire_seconds: int = 3600) -> bool:
        """Store session data in Redis."""
        session_key = f"user_session:{user_id}"
        return await redis_service.store_session(session_key, session_data, expire_seconds)
    
    async def get_session_from_redis(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get session data from Redis."""
        session_key = f"user_session:{user_id}"
        return await redis_service.get_session(session_key)
    
    async def delete_session_from_redis(self, user_id: int) -> bool:
        """Delete session from Redis."""
        session_key = f"user_session:{user_id}"
        return await redis_service.delete_session(session_key)
    
    async def is_token_blacklisted_redis(self, jti: str) -> bool:
        """Check if token is blacklisted using Redis."""
        blacklist_key = f"blacklist:{jti}"
        return await redis_service.exists(blacklist_key)
    
    async def blacklist_token_redis(self, jti: str, expire_seconds: int) -> bool:
        """Blacklist token in Redis."""
        blacklist_key = f"blacklist:{jti}"
        return await redis_service.set(blacklist_key, "1", expire_seconds)
    
    def _is_token_blacklisted(self, jti: str) -> bool:
        """Check if token JTI is blacklisted."""
        with Session(engine) as session:
            blacklisted = session.exec(
                select(TokenBlacklist).where(TokenBlacklist.token_jti == jti)
            ).first()
            return blacklisted is not None


# Global token manager instance
token_manager = TokenManager()