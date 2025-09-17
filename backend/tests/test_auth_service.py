import pytest
from datetime import datetime, timedelta
from sqlmodel import Session, select

from app.models import User, UserSession, TokenBlacklist, UserRole, UserStatus
from app.services.auth import TokenManager
from app.database import engine


@pytest.fixture
def token_manager():
    return TokenManager()


@pytest.fixture
def test_user():
    with Session(engine) as session:
        user = User(
            role=UserRole.BUYER,
            name="Test User",
            email="test@example.com",
            email_verified=True,
            status=UserStatus.ACTIVE
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        user_id = user.id
        
    yield user
    
    # Cleanup - remove all sessions and blacklisted tokens for this user
    with Session(engine) as session:
        # Delete user sessions
        user_sessions = session.exec(
            select(UserSession).where(UserSession.user_id == user_id)
        ).all()
        for us in user_sessions:
            session.delete(us)
        
        # Delete blacklisted tokens (cleanup all for simplicity in tests)
        blacklisted_tokens = session.exec(select(TokenBlacklist)).all()
        for bt in blacklisted_tokens:
            session.delete(bt)
        
        # Delete user
        user_to_delete = session.get(User, user_id)
        if user_to_delete:
            session.delete(user_to_delete)
        
        session.commit()


class TestTokenManager:
    
    def test_create_tokens(self, token_manager, test_user):
        """Test token creation with user session storage."""
        result = token_manager.create_tokens(
            test_user, 
            user_agent="test-agent", 
            ip_address="127.0.0.1"
        )
        
        assert "access_token" in result
        assert "refresh_token" in result
        assert result["token_type"] == "bearer"
        assert result["expires_in"] == 15 * 60  # 15 minutes
        assert result["user"]["id"] == test_user.id
        assert result["user"]["email"] == test_user.email
        
        # Verify session was created
        with Session(engine) as session:
            user_session = session.exec(
                select(UserSession).where(UserSession.user_id == test_user.id)
            ).first()
            assert user_session is not None
            assert user_session.user_agent == "test-agent"
            assert user_session.ip_address == "127.0.0.1"
    
    def test_validate_access_token(self, token_manager, test_user):
        """Test access token validation."""
        result = token_manager.create_tokens(test_user)
        access_token = result["access_token"]
        
        payload = token_manager.validate_token(access_token, "access")
        assert payload is not None
        assert payload["sub"] == str(test_user.id)
        assert payload["role"] == test_user.role.value
        assert payload["type"] == "access"
    
    def test_validate_refresh_token(self, token_manager, test_user):
        """Test refresh token validation."""
        result = token_manager.create_tokens(test_user)
        refresh_token = result["refresh_token"]
        
        payload = token_manager.validate_token(refresh_token, "refresh")
        assert payload is not None
        assert payload["sub"] == str(test_user.id)
        assert payload["type"] == "refresh"
    
    def test_refresh_access_token(self, token_manager, test_user):
        """Test access token refresh."""
        result = token_manager.create_tokens(test_user)
        refresh_token = result["refresh_token"]
        
        new_result = token_manager.refresh_access_token(refresh_token)
        assert new_result is not None
        assert "access_token" in new_result
        assert new_result["token_type"] == "bearer"
        
        # Verify new access token is valid
        new_access_token = new_result["access_token"]
        payload = token_manager.validate_token(new_access_token, "access")
        assert payload is not None
        assert payload["sub"] == str(test_user.id)
    
    def test_refresh_with_invalid_token(self, token_manager):
        """Test refresh with invalid token."""
        result = token_manager.refresh_access_token("invalid_token")
        assert result is None
    
    def test_revoke_token(self, token_manager, test_user):
        """Test token revocation."""
        result = token_manager.create_tokens(test_user)
        access_token = result["access_token"]
        
        # Token should be valid initially
        payload = token_manager.validate_token(access_token, "access")
        assert payload is not None
        original_jti = payload["jti"]
        
        # Revoke token
        revoked = token_manager.revoke_token(access_token)
        assert revoked is True
        
        # Token should be invalid after revocation
        payload_after_revoke = token_manager.validate_token(access_token, "access")
        assert payload_after_revoke is None
        
        # Verify token is in blacklist
        with Session(engine) as session:
            blacklisted = session.exec(
                select(TokenBlacklist).where(TokenBlacklist.token_jti == original_jti)
            ).first()
            assert blacklisted is not None
    
    def test_revoke_all_user_sessions(self, token_manager, test_user):
        """Test revoking all user sessions."""
        # Create multiple sessions
        result1 = token_manager.create_tokens(test_user)
        result2 = token_manager.create_tokens(test_user)
        
        # Both tokens should be valid
        assert token_manager.validate_token(result1["access_token"], "access") is not None
        assert token_manager.validate_token(result2["access_token"], "access") is not None
        
        # Revoke all sessions
        revoked = token_manager.revoke_all_user_sessions(test_user.id)
        assert revoked is True
        
        # Both tokens should be invalid
        assert token_manager.validate_token(result1["access_token"], "access") is None
        assert token_manager.validate_token(result2["access_token"], "access") is None
        
        # Verify sessions are deleted
        with Session(engine) as session:
            sessions = session.exec(
                select(UserSession).where(UserSession.user_id == test_user.id)
            ).all()
            assert len(sessions) == 0
    
    def test_cleanup_expired_sessions(self, token_manager, test_user):
        """Test cleanup of expired sessions."""
        # Clean up any existing sessions first
        with Session(engine) as session:
            existing_sessions = session.exec(
                select(UserSession).where(UserSession.user_id == test_user.id)
            ).all()
            for es in existing_sessions:
                session.delete(es)
            session.commit()
        
        # Create a session
        result = token_manager.create_tokens(test_user)
        
        # Manually expire the session
        with Session(engine) as session:
            user_session = session.exec(
                select(UserSession).where(UserSession.user_id == test_user.id)
            ).first()
            user_session.expires_at = datetime.utcnow() - timedelta(days=1)
            session.add(user_session)
            session.commit()
        
        # Run cleanup
        count = token_manager.cleanup_expired_sessions()
        assert count >= 1
        
        # Verify session is deleted
        with Session(engine) as session:
            sessions = session.exec(
                select(UserSession).where(UserSession.user_id == test_user.id)
            ).all()
            assert len(sessions) == 0
    
    def test_session_limit(self, token_manager, test_user):
        """Test that old sessions are cleaned up when limit is exceeded."""
        # Create 6 sessions (limit is 5)
        for i in range(6):
            token_manager.create_tokens(test_user)
        
        # Should only have 5 sessions
        with Session(engine) as session:
            sessions = session.exec(
                select(UserSession).where(UserSession.user_id == test_user.id)
            ).all()
            assert len(sessions) == 5
    
    def test_wrong_token_type_validation(self, token_manager, test_user):
        """Test validation fails with wrong token type."""
        result = token_manager.create_tokens(test_user)
        access_token = result["access_token"]
        refresh_token = result["refresh_token"]
        
        # Access token should not validate as refresh token
        payload = token_manager.validate_token(access_token, "refresh")
        assert payload is None
        
        # Refresh token should not validate as access token
        payload = token_manager.validate_token(refresh_token, "access")
        assert payload is None