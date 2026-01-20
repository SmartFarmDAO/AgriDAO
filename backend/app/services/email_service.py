"""
Production Email Service
Supports multiple email providers with fallback mechanisms
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional, List
import requests
import json

logger = logging.getLogger(__name__)


class EmailProvider:
    """Base class for email providers"""
    
    def __init__(self, name: str):
        self.name = name
        self.enabled = False
    
    def send_email(self, to_email: str, subject: str, html_body: str, text_body: str) -> bool:
        """Send email - to be implemented by subclasses"""
        raise NotImplementedError


class GmailProvider(EmailProvider):
    """Gmail SMTP provider"""
    
    def __init__(self):
        super().__init__("Gmail")
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.username = os.getenv("SMTP_USERNAME", "")
        self.password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "")
        self.from_name = os.getenv("FROM_NAME", "AgriDAO")
        
        self.enabled = bool(self.username and self.password)
    
    def send_email(self, to_email: str, subject: str, html_body: str, text_body: str) -> bool:
        if not self.enabled:
            return False
            
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email
            
            msg.attach(MIMEText(text_body, "plain"))
            msg.attach(MIMEText(html_body, "html"))
            
            if self.smtp_port == 465:
                # SSL connection
                with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as server:
                    server.login(self.username, self.password)
                    server.send_message(msg)
            else:
                # TLS connection (port 587)
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.username, self.password)
                    server.send_message(msg)
            
            logger.info(f"Email sent successfully via Gmail to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Gmail send failed: {e}")
            return False


class SendGridProvider(EmailProvider):
    """SendGrid API provider"""
    
    def __init__(self):
        super().__init__("SendGrid")
        self.api_key = os.getenv("SENDGRID_API_KEY", "")
        self.from_email = os.getenv("SENDGRID_FROM_EMAIL", "")
        self.from_name = os.getenv("SENDGRID_FROM_NAME", "AgriDAO")
        
        self.enabled = bool(self.api_key and self.from_email)
    
    def send_email(self, to_email: str, subject: str, html_body: str, text_body: str) -> bool:
        if not self.enabled:
            return False
            
        try:
            data = {
                "personalizations": [{
                    "to": [{"email": to_email}],
                    "subject": subject
                }],
                "from": {
                    "email": self.from_email,
                    "name": self.from_name
                },
                "content": [
                    {"type": "text/plain", "value": text_body},
                    {"type": "text/html", "value": html_body}
                ]
            }
            
            response = requests.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=data,
                timeout=10
            )
            
            if response.status_code == 202:
                logger.info(f"Email sent successfully via SendGrid to {to_email}")
                return True
            else:
                logger.error(f"SendGrid API returned {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"SendGrid send failed: {e}")
            return False


class MailgunProvider(EmailProvider):
    """Mailgun API provider"""
    
    def __init__(self):
        super().__init__("Mailgun")
        self.api_key = os.getenv("MAILGUN_API_KEY", "")
        self.domain = os.getenv("MAILGUN_DOMAIN", "")
        self.from_email = os.getenv("MAILGUN_FROM_EMAIL", "")
        self.from_name = os.getenv("MAILGUN_FROM_NAME", "AgriDAO")
        
        self.enabled = bool(self.api_key and self.domain)
    
    def send_email(self, to_email: str, subject: str, html_body: str, text_body: str) -> bool:
        if not self.enabled:
            return False
            
        try:
            response = requests.post(
                f"https://api.mailgun.net/v3/{self.domain}/messages",
                auth=("api", self.api_key),
                data={
                    "from": f"{self.from_name} <{self.from_email}>",
                    "to": to_email,
                    "subject": subject,
                    "text": text_body,
                    "html": html_body
                },
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Email sent successfully via Mailgun to {to_email}")
                return True
            else:
                logger.error(f"Mailgun API returned {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Mailgun send failed: {e}")
            return False


class ProductionEmailService:
    """Production email service with multiple providers and fallback"""
    
    def __init__(self):
        # Initialize providers in order of preference
        self.providers: List[EmailProvider] = [
            GmailProvider(),
            SendGridProvider(),
            MailgunProvider()
        ]
        
        # Filter enabled providers
        self.enabled_providers = [p for p in self.providers if p.enabled]
        
        if not self.enabled_providers:
            logger.warning("No email providers configured")
        else:
            provider_names = [p.name for p in self.enabled_providers]
            logger.info(f"Email providers enabled: {', '.join(provider_names)}")
    
    def send_otp_email(self, email: str, otp_code: str) -> bool:
        """Send OTP email using available providers with fallback"""
        
        subject = "Your AgriDAO Verification Code"
        
        # HTML email template
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
                <div class="code">{otp_code}</div>
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
        
        # Plain text version
        text_body = f"""
        AgriDAO - Email Verification
        
        Your verification code is: {otp_code}
        
        This code expires in 5 minutes.
        
        If you didn't request this code, please ignore this email.
        
        © 2025 AgriDAO
        """
        
        # Try each provider until one succeeds
        for provider in self.enabled_providers:
            try:
                if provider.send_email(email, subject, html_body, text_body):
                    return True
            except Exception as e:
                logger.error(f"Provider {provider.name} failed: {e}")
                continue
        
        logger.error(f"All email providers failed for {email}")
        return False
    
    def is_configured(self) -> bool:
        """Check if any email provider is configured"""
        return len(self.enabled_providers) > 0


# Global instance
email_service = ProductionEmailService()
