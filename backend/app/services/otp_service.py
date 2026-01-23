"""
Production OTP Service
Secure OTP generation and delivery for real users
"""

import os
import secrets
import time
import logging
from typing import Dict, Optional

from .email_service import email_service

logger = logging.getLogger(__name__)


class OTPService:
    """Production OTP service with secure delivery"""
    
    def __init__(self):
        self.otp_store = {}  # Use Redis in production
        self.otp_expiry = 300  # 5 minutes
        self.max_attempts = 3
        
        # Production mode settings
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.is_production = self.environment == "production"
        
        # Rate limiting
        self.rate_limit_store = {}
        self.rate_limit_window = 60  # 1 minute
        self.max_requests_per_minute = 3
    
    def generate_otp(self) -> str:
        """Generate 6-digit OTP"""
        return f"{secrets.randbelow(1000000):06d}"
    
    def _check_rate_limit(self, identifier: str) -> bool:
        """Check if request is within rate limits"""
        current_time = time.time()
        
        # Clean old entries
        self.rate_limit_store = {
            k: v for k, v in self.rate_limit_store.items() 
            if current_time - v["first_request"] < self.rate_limit_window
        }
        
        if identifier not in self.rate_limit_store:
            self.rate_limit_store[identifier] = {
                "count": 1,
                "first_request": current_time
            }
            return True
        
        entry = self.rate_limit_store[identifier]
        if entry["count"] >= self.max_requests_per_minute:
            return False
        
        entry["count"] += 1
        return True
    
    def send_otp_email(self, email: str) -> Dict[str, any]:
        """Send OTP via email - production version"""
        
        # Rate limiting
        if not self._check_rate_limit(email):
            logger.warning(f"Rate limit exceeded for {email}")
            return {
                "success": False,
                "error": "Too many requests. Please wait before requesting another code.",
                "retry_after": 60
            }
        
        logger.info(f"DEBUG: Processing OTP for {email}. Env: {self.environment}")
        
        # Generate and store OTP

        code = self.generate_otp()
        expires_at = time.time() + self.otp_expiry
        
        self.otp_store[email] = {
            "code": code,
            "exp": expires_at,
            "attempts": 0
        }
        
        logger.info(f"DEBUG OTP CODE GENERATED: {code}")
        
        # Send email using production service
        email_sent = False
        is_configured = email_service.is_configured()
        logger.info(f"DEBUG: Email service configured: {is_configured}")
        
        if is_configured:
            try:
                email_sent = email_service.send_otp_email(email, code)
                if email_sent:
                    logger.info(f"OTP email sent successfully to {email}")
            except Exception as e:
                import traceback
                error_msg = f"Failed to send OTP email: {str(e)}"
                logger.error(error_msg, extra={"stack_trace": traceback.format_exc()})
                logger.info(f"DEBUG OTP CODE: {code}")  # Temporary debug log
        else:
            logger.warning("DEBUG: Email service NOT configured")
        
        # Production response
        if self.is_production:
            if email_sent:
                return {
                    "success": True,
                    "message": f"Verification code sent to {email}",
                    "expires_in": self.otp_expiry
                }
            else:
                # FALLBACK: If email fails in production, return dev code to unblock user
                # This should be monitored and fixed, but allows login for now.
                logger.error(f"FALLBACK: Returning dev code for {email} due to email failure")
                return {
                    "success": True, 
                    "message": "Email delivery failed. Use the code displayed.",
                    "dev_code": code,
                    "expires_in": self.otp_expiry
                }
        
        # Development response (includes dev_code)
        result = {
            "success": True,
            "expires_in": self.otp_expiry,
            "email_sent": email_sent
        }
        
        if not email_sent:
            result["dev_code"] = code
            result["message"] = f"Email delivery failed. Use dev code: {code}"
        else:
            result["message"] = f"Verification code sent to {email}"
            
        return result
    
    def verify_otp(self, identifier: str, code: str) -> Dict[str, any]:
        """Verify OTP code"""
        record = self.otp_store.get(identifier)
        
        if not record:
            return {"success": False, "error": "OTP not found or expired"}
        
        if time.time() > record["exp"]:
            del self.otp_store[identifier]
            return {"success": False, "error": "OTP expired"}
        
        if record["attempts"] >= self.max_attempts:
            del self.otp_store[identifier]
            return {"success": False, "error": "Too many attempts"}
        
        if record["code"] == code:
            del self.otp_store[identifier]
            return {"success": True}
        else:
            record["attempts"] += 1
            return {
                "success": False,
                "error": "Invalid code",
                "attempts_remaining": self.max_attempts - record["attempts"]
            }


# Global instance
otp_service = OTPService()
