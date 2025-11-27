"""
Free and Open Source OTP Service
Supports multiple email and SMS providers without paid services
"""

import os
import secrets
import time
import logging
from typing import Dict, Optional, Literal

logger = logging.getLogger(__name__)


class OTPService:
    """Service for OTP generation and delivery using free/open-source tools"""
    
    def __init__(self):
        self.otp_store = {}  # Use Redis in production
        self.otp_expiry = 300  # 5 minutes
        self.max_attempts = 3
        
        # Email configuration
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "465"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "smartfarmdao@gmail.com")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "smartfarmdao@gmail.com")
        self.from_name = os.getenv("FROM_NAME", "AgriDAO")
        
        # SMS configuration
        self.sms_provider = os.getenv("SMS_PROVIDER", "none")
        self.android_api_url = os.getenv("ANDROID_SMS_API_URL", "")
        self.android_api_key = os.getenv("ANDROID_SMS_API_KEY", "")
        self.playsms_api_url = os.getenv("PLAYSMS_API_URL", "")
        self.playsms_username = os.getenv("PLAYSMS_USERNAME", "")
        self.playsms_api_key = os.getenv("PLAYSMS_API_KEY", "")
    
    def generate_otp(self) -> str:
        """Generate 6-digit OTP"""
        return f"{secrets.randbelow(1000000):06d}"
    
    def send_otp_email(self, email: str) -> Dict[str, any]:
        """Send OTP via email"""
        code = self.generate_otp()
        expires_at = time.time() + self.otp_expiry
        
        # Store OTP
        self.otp_store[email] = {
            "code": code,
            "exp": expires_at,
            "attempts": 0
        }
        
        # Send email
        try:
            success = self._send_email(email, code)
            return {
                "success": success,
                "expires_in": self.otp_expiry
            }
        except Exception as e:
            logger.error(f"Failed to send OTP email: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_otp_sms(self, phone: str) -> Dict[str, any]:
        """Send OTP via SMS"""
        code = self.generate_otp()
        expires_at = time.time() + self.otp_expiry
        
        # Store OTP
        self.otp_store[phone] = {
            "code": code,
            "exp": expires_at,
            "attempts": 0
        }
        
        # Send SMS
        message = f"Your AgriDAO verification code is: {code}. Valid for 5 minutes."
        try:
            success = self._send_sms(phone, message)
            return {
                "success": success,
                "expires_in": self.otp_expiry
            }
        except Exception as e:
            logger.error(f"Failed to send OTP SMS: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
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
    
    def _send_email(self, email: str, code: str) -> bool:
        """Send OTP email using Gmail SMTP"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            subject = "Your AgriDAO Verification Code"
            
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; }}
                    .header {{ background: linear-gradient(to right, #1e40af, #059669); padding: 30px 20px; text-align: center; }}
                    .logo-container {{ display: flex; align-items: center; justify-content: center; gap: 8px; }}
                    .leaf-icon {{ font-size: 32px; line-height: 1; }}
                    .logo-text {{ font-size: 28px; font-weight: bold; color: white; }}
                    .content {{ padding: 30px; }}
                    .code {{ 
                        font-size: 36px; 
                        font-weight: bold; 
                        color: #22c55e; 
                        letter-spacing: 8px; 
                        text-align: center; 
                        padding: 20px; 
                        background: #f3f4f6; 
                        border-radius: 8px;
                        margin: 20px 0;
                    }}
                    .footer {{ 
                        text-align: center; 
                        padding: 20px; 
                        color: #6b7280; 
                        font-size: 12px; 
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <div class="logo-container">
                        <span class="leaf-icon">🌱</span>
                        <span class="logo-text">AgriDAO</span>
                    </div>
                </div>
                <div class="content">
                    <h2>Verify Your Email</h2>
                    <p>Enter this code to complete your verification:</p>
                    <div class="code">{code}</div>
                    <p><strong>This code expires in 5 minutes.</strong></p>
                    <p>If you didn't request this code, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>© 2025 AgriDAO - Agricultural Marketplace</p>
                    <p>This is an automated message, please do not reply.</p>
                </div>
            </body>
            </html>
            """
            
            text_body = f"""
            AgriDAO - Email Verification
            
            Your verification code is: {code}
            
            This code expires in 5 minutes.
            
            If you didn't request this code, please ignore this email.
            
            © 2025 AgriDAO
            """
            
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = email
            
            msg.attach(MIMEText(text_body, "plain"))
            msg.attach(MIMEText(html_body, "html"))
            
            # Use Gmail SMTP with SSL
            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as server:
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"OTP email sent successfully to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def _send_sms(self, phone: str, message: str) -> bool:
        """Send SMS using configured provider"""
        
        if self.sms_provider == "gammu":
            return self._send_sms_gammu(phone, message)
        elif self.sms_provider == "android":
            return self._send_sms_android(phone, message)
        elif self.sms_provider == "playsms":
            return self._send_sms_playsms(phone, message)
        elif self.sms_provider == "none":
            logger.warning(f"SMS provider not configured. Would send: {message}")
            return False
        else:
            logger.error(f"Unknown SMS provider: {self.sms_provider}")
            return False
    
    def _send_sms_gammu(self, phone: str, message: str) -> bool:
        """Send SMS via Gammu (USB GSM modem)"""
        try:
            import gammu
            sm = gammu.StateMachine()
            sm.ReadConfig()
            sm.Init()
            
            message_data = {
                'Text': message,
                'SMSC': {'Location': 1},
                'Number': phone,
            }
            sm.SendSMS(message_data)
            logger.info(f"SMS sent via Gammu to {phone}")
            return True
        except ImportError:
            logger.error("Gammu library not installed. Install: pip install python-gammu")
            return False
        except Exception as e:
            logger.error(f"Gammu SMS failed: {e}")
            return False
    
    def _send_sms_android(self, phone: str, message: str) -> bool:
        """Send SMS via Android Gateway"""
        try:
            import requests
            
            if not self.android_api_url or not self.android_api_key:
                logger.error("Android SMS Gateway not configured")
                return False
            
            response = requests.post(
                f"{self.android_api_url}/api/send",
                json={"phone": phone, "message": message},
                headers={"Authorization": f"Bearer {self.android_api_key}"},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"SMS sent via Android Gateway to {phone}")
                return True
            else:
                logger.error(f"Android Gateway returned {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Android SMS failed: {e}")
            return False
    
    def _send_sms_playsms(self, phone: str, message: str) -> bool:
        """Send SMS via PlaySMS"""
        try:
            import requests
            
            if not self.playsms_api_url or not self.playsms_api_key:
                logger.error("PlaySMS not configured")
                return False
            
            response = requests.get(
                f"{self.playsms_api_url}/index.php",
                params={
                    "app": "ws",
                    "u": self.playsms_username,
                    "h": self.playsms_api_key,
                    "op": "pv",
                    "to": phone,
                    "msg": message
                },
                timeout=10
            )
            
            if "OK" in response.text:
                logger.info(f"SMS sent via PlaySMS to {phone}")
                return True
            else:
                logger.error(f"PlaySMS returned: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"PlaySMS failed: {e}")
            return False


# Global instance
otp_service = OTPService()
