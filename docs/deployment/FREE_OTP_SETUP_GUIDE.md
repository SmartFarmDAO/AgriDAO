# 🆓 Free & Open Source OTP Setup Guide

## Complete Self-Hosted Solution (No Paid Services)

This guide shows you how to enable OTP sending using **100% free and open-source tools** without any paid services.

## 📧 Email OTP - Free Options

### **Option 1: MailHog (Development/Testing) ⭐ RECOMMENDED FOR DEV**

MailHog is a fake SMTP server that captures emails for testing.

#### **Setup with Docker**

```yaml
# Add to docker-compose.yml
services:
  mailhog:
    image: mailhog/mailhog:latest
    ports:
      - "1025:1025"  # SMTP server
      - "8025:8025"  # Web UI
    networks:
      - agridao-dev
```

#### **Configuration**

```bash
# backend/.env
SMTP_HOST=mailhog
SMTP_PORT=1025
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_USE_TLS=false
FROM_EMAIL=noreply@agridao.local
FROM_NAME=AgriDAO
```

#### **Access**
- Web UI: http://localhost:8025
- All emails are captured and viewable in the browser
- Perfect for development and testing

---

### **Option 2: Postal (Production Self-Hosted) ⭐ RECOMMENDED FOR PRODUCTION**

Postal is a complete, self-hosted email platform (like Mailgun/SendGrid).

#### **Features**
- ✅ Full-featured SMTP server
- ✅ Web interface for monitoring
- ✅ Webhook support
- ✅ Bounce handling
- ✅ Click/open tracking
- ✅ Multiple domains


#### **Installation**

```bash
# Install Postal using Docker
git clone https://github.com/postalserver/postal.git
cd postal

# Initialize
docker-compose up -d

# Create admin user
docker-compose run postal postal initialize

# Access web interface
# http://localhost:5000
```

#### **Configuration**

```bash
# backend/.env
SMTP_HOST=postal
SMTP_PORT=25
SMTP_USERNAME=your-postal-api-key
SMTP_PASSWORD=your-postal-api-key
SMTP_USE_TLS=true
FROM_EMAIL=noreply@yourdomain.com
FROM_NAME=AgriDAO
```

---

### **Option 3: Gmail Free Tier (Limited)**

Gmail allows 500 emails/day for free with app passwords.

#### **Setup**

1. Enable 2FA on your Google account
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use the generated password

```bash
# backend/.env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
SMTP_USE_TLS=true
FROM_EMAIL=your-email@gmail.com
FROM_NAME=AgriDAO
```

**Limitations:**
- 500 emails/day limit
- May be flagged as spam
- Not recommended for production

---

### **Option 4: Mailu (Complete Email Server)**

Mailu is a simple, full-featured mail server.

#### **Docker Compose Setup**

```yaml
# docker-compose.mailu.yml
version: '3.7'

services:
  mailu:
    image: mailu/admin:latest
    restart: always
    env_file: mailu.env
    ports:
      - "25:25"     # SMTP
      - "465:465"   # SMTPS
      - "587:587"   # Submission
      - "143:143"   # IMAP
      - "993:993"   # IMAPS
      - "8080:80"   # Web admin
    volumes:
      - mailu-data:/data
      - mailu-mail:/mail

volumes:
  mailu-data:
  mailu-mail:
```

#### **Configuration**

```bash
# mailu.env
SECRET_KEY=your-secret-key
DOMAIN=yourdomain.com
HOSTNAMES=mail.yourdomain.com
POSTMASTER=admin
```

---

## 📱 SMS OTP - Free Options

### **Option 1: Gammu + USB Modem (Completely Free)**

Use a USB GSM modem to send SMS directly.

#### **Hardware Needed**
- USB GSM Modem (~$20-50 one-time cost)
- SIM card with SMS plan

#### **Installation**

```bash
# Install Gammu
apt-get install gammu gammu-smsd python3-gammu

# Configure
gammu-config
```

#### **Python Integration**

```python
# backend/app/services/sms_gammu.py

import gammu

class GammuSMSService:
    def __init__(self):
        self.state_machine = gammu.StateMachine()
        self.state_machine.ReadConfig()
        self.state_machine.Init()
    
    def send_sms(self, phone_number: str, message: str) -> bool:
        try:
            message_data = {
                'Text': message,
                'SMSC': {'Location': 1},
                'Number': phone_number,
            }
            self.state_machine.SendSMS(message_data)
            return True
        except Exception as e:
            print(f"Failed to send SMS: {e}")
            return False
```

#### **Configuration**

```bash
# /etc/gammurc
[gammu]
device = /dev/ttyUSB0
connection = at
```

---

### **Option 2: Android Phone as SMS Gateway**

Use an old Android phone as an SMS gateway.

#### **Setup**

1. **Install SMS Gateway App**
   - Download: https://github.com/android-sms-gateway/android-sms-gateway
   - Free and open source

2. **Configure API**

```python
# backend/app/services/sms_android.py

import requests

class AndroidSMSGateway:
    def __init__(self):
        self.api_url = os.getenv("ANDROID_SMS_API_URL", "http://192.168.1.100:8080")
        self.api_key = os.getenv("ANDROID_SMS_API_KEY", "")
    
    def send_sms(self, phone_number: str, message: str) -> bool:
        try:
            response = requests.post(
                f"{self.api_url}/api/send",
                json={
                    "phone": phone_number,
                    "message": message
                },
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Failed to send SMS: {e}")
            return False
```

---

### **Option 3: PlaySMS (Self-Hosted SMS Gateway)**

PlaySMS is an open-source SMS gateway platform.

#### **Installation**

```bash
# Install PlaySMS
git clone https://github.com/playsms/playsms.git
cd playsms
./install-playsms.sh

# Access web interface
# http://localhost/playsms
```

#### **Python Integration**

```python
# backend/app/services/sms_playsms.py

import requests

class PlaySMSService:
    def __init__(self):
        self.api_url = os.getenv("PLAYSMS_API_URL", "http://localhost/playsms")
        self.username = os.getenv("PLAYSMS_USERNAME", "admin")
        self.api_key = os.getenv("PLAYSMS_API_KEY", "")
    
    def send_sms(self, phone_number: str, message: str) -> bool:
        try:
            response = requests.get(
                f"{self.api_url}/index.php",
                params={
                    "app": "ws",
                    "u": self.username,
                    "h": self.api_key,
                    "op": "pv",
                    "to": phone_number,
                    "msg": message
                }
            )
            return "OK" in response.text
        except Exception as e:
            print(f"Failed to send SMS: {e}")
            return False
```

---

### **Option 4: Kannel (SMS Gateway)**

Kannel is a powerful open-source SMS gateway.

#### **Docker Setup**

```yaml
# docker-compose.kannel.yml
services:
  kannel:
    image: docker.io/thibaultbustarret/kannel:latest
    ports:
      - "13013:13013"  # Admin
      - "13000:13000"  # SMS
    volumes:
      - ./kannel.conf:/etc/kannel/kannel.conf
```

#### **Configuration**

```ini
# kannel.conf
group = core
admin-port = 13000
smsbox-port = 13001
admin-password = admin
log-level = 0

group = smsc
smsc = at
modemtype = auto
device = /dev/ttyUSB0
```

---

## 🔧 Complete Implementation

### **1. Update Docker Compose**

```yaml
# docker-compose.yml
services:
  # ... existing services ...

  mailhog:
    image: mailhog/mailhog:latest
    ports:
      - "1025:1025"
      - "8025:8025"
    networks:
      - agridao-dev

  # Optional: Add Postal for production
  postal:
    image: ghcr.io/postalserver/postal:latest
    ports:
      - "25:25"
      - "5000:5000"
    volumes:
      - postal-data:/opt/postal
    networks:
      - agridao-dev

volumes:
  postal-data:
```

### **2. Create OTP Service**

```python
# backend/app/services/otp_service.py

import os
import secrets
import time
from typing import Dict, Optional, Literal
from .notification_service import NotificationService

class OTPService:
    def __init__(self):
        self.notification_service = NotificationService()
        self.otp_store = {}  # Use Redis in production
        self.otp_expiry = 300  # 5 minutes
    
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
        result = self.notification_service._send_otp_email(email, code)
        
        return {
            "success": result.get("success", False),
            "expires_in": self.otp_expiry
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
        result = self._send_sms(phone, message)
        
        return {
            "success": result,
            "expires_in": self.otp_expiry
        }
    
    def verify_otp(self, identifier: str, code: str) -> Dict[str, any]:
        """Verify OTP code"""
        record = self.otp_store.get(identifier)
        
        if not record:
            return {"success": False, "error": "OTP not found"}
        
        if time.time() > record["exp"]:
            del self.otp_store[identifier]
            return {"success": False, "error": "OTP expired"}
        
        if record["attempts"] >= 3:
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
                "attempts_remaining": 3 - record["attempts"]
            }
    
    def _send_sms(self, phone: str, message: str) -> bool:
        """Send SMS using configured provider"""
        provider = os.getenv("SMS_PROVIDER", "none")
        
        if provider == "gammu":
            return self._send_sms_gammu(phone, message)
        elif provider == "android":
            return self._send_sms_android(phone, message)
        elif provider == "playsms":
            return self._send_sms_playsms(phone, message)
        else:
            print(f"SMS provider not configured. Message: {message}")
            return False
    
    def _send_sms_gammu(self, phone: str, message: str) -> bool:
        """Send SMS via Gammu"""
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
            return True
        except Exception as e:
            print(f"Gammu SMS failed: {e}")
            return False
    
    def _send_sms_android(self, phone: str, message: str) -> bool:
        """Send SMS via Android Gateway"""
        try:
            import requests
            api_url = os.getenv("ANDROID_SMS_API_URL")
            api_key = os.getenv("ANDROID_SMS_API_KEY")
            
            response = requests.post(
                f"{api_url}/api/send",
                json={"phone": phone, "message": message},
                headers={"Authorization": f"Bearer {api_key}"}
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Android SMS failed: {e}")
            return False
    
    def _send_sms_playsms(self, phone: str, message: str) -> bool:
        """Send SMS via PlaySMS"""
        try:
            import requests
            api_url = os.getenv("PLAYSMS_API_URL")
            username = os.getenv("PLAYSMS_USERNAME")
            api_key = os.getenv("PLAYSMS_API_KEY")
            
            response = requests.get(
                f"{api_url}/index.php",
                params={
                    "app": "ws",
                    "u": username,
                    "h": api_key,
                    "op": "pv",
                    "to": phone,
                    "msg": message
                }
            )
            return "OK" in response.text
        except Exception as e:
            print(f"PlaySMS failed: {e}")
            return False


# Global instance
otp_service = OTPService()
```

### **3. Update Auth Router**

```python
# backend/app/routers/auth.py

from ..services.otp_service import otp_service

@router.post("/otp/request")
def request_otp(payload: OTPRequest):
    """Request OTP via email or SMS"""
    
    if payload.email:
        result = otp_service.send_otp_email(payload.email)
    elif payload.phone:
        result = otp_service.send_otp_sms(payload.phone)
    else:
        raise HTTPException(400, "Email or phone required")
    
    if result["success"]:
        return {
            "sent": True,
            "expires_in": result["expires_in"]
        }
    else:
        raise HTTPException(500, "Failed to send OTP")

@router.post("/otp/verify")
def verify_otp(request: Request, payload: OTPVerify):
    """Verify OTP code"""
    
    identifier = payload.email or payload.phone
    result = otp_service.verify_otp(identifier, payload.code)
    
    if not result["success"]:
        raise HTTPException(400, result.get("error", "Invalid OTP"))
    
    # Create user session
    with Session(engine) as session:
        user = session.exec(
            select(User).where(User.email == identifier)
        ).first()
        
        if not user:
            user = User(
                role=UserRole.BUYER,
                name=identifier.split("@")[0],
                email=identifier,
                email_verified=True
            )
            session.add(user)
            session.commit()
            session.refresh(user)
    
    return token_manager.create_tokens(user, request.headers.get("user-agent"), 
                                      request.client.host if request.client else None)
```

### **4. Add Email Template**

```python
# backend/app/services/notification_service.py

def _send_otp_email(self, email: str, code: str) -> Dict[str, Any]:
    """Send OTP code via email"""
    
    subject = "Your AgriDAO Verification Code"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; }}
            .header {{ background: #22c55e; color: white; padding: 20px; text-align: center; }}
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
            <h1>🌾 AgriDAO</h1>
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
    
    try:
        msg = MimeMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{self.from_name} <{self.from_email}>"
        msg["To"] = email
        
        msg.attach(MimeText(text_body, "plain"))
        msg.attach(MimeText(html_body, "html"))
        
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            if self.smtp_use_tls:
                server.starttls()
            if self.smtp_username and self.smtp_password:
                server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
        
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### **5. Environment Configuration**

```bash
# backend/.env

# Email Configuration (Choose one)
# Option 1: MailHog (Development)
SMTP_HOST=mailhog
SMTP_PORT=1025
SMTP_USE_TLS=false

# Option 2: Postal (Production)
# SMTP_HOST=postal
# SMTP_PORT=25
# SMTP_USERNAME=your-api-key
# SMTP_PASSWORD=your-api-key
# SMTP_USE_TLS=true

# Option 3: Gmail (Limited)
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USERNAME=your-email@gmail.com
# SMTP_PASSWORD=your-app-password
# SMTP_USE_TLS=true

FROM_EMAIL=noreply@agridao.local
FROM_NAME=AgriDAO

# SMS Configuration (Choose one)
# Option 1: Gammu
SMS_PROVIDER=gammu

# Option 2: Android Gateway
# SMS_PROVIDER=android
# ANDROID_SMS_API_URL=http://192.168.1.100:8080
# ANDROID_SMS_API_KEY=your-api-key

# Option 3: PlaySMS
# SMS_PROVIDER=playsms
# PLAYSMS_API_URL=http://localhost/playsms
# PLAYSMS_USERNAME=admin
# PLAYSMS_API_KEY=your-api-key
```

---

## 🚀 Quick Start

### **Development Setup (MailHog)**

```bash
# 1. Start services
docker-compose up -d

# 2. Access MailHog UI
open http://localhost:8025

# 3. Test OTP
curl -X POST http://localhost:8000/auth/otp/request \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# 4. Check MailHog UI for the email with OTP code
```

### **Production Setup (Postal)**

```bash
# 1. Install Postal
git clone https://github.com/postalserver/postal.git
cd postal
docker-compose up -d

# 2. Initialize
docker-compose run postal postal initialize

# 3. Configure DNS records for your domain

# 4. Update backend/.env with Postal credentials

# 5. Start AgriDAO
docker-compose up -d
```

---

## 📊 Comparison Table

| Solution | Cost | Complexity | Reliability | Best For |
|----------|------|------------|-------------|----------|
| **MailHog** | Free | ⭐ Easy | Dev only | Development |
| **Postal** | Free | ⭐⭐⭐ Medium | ⭐⭐⭐⭐⭐ High | Production |
| **Gmail** | Free* | ⭐ Easy | ⭐⭐⭐ Medium | Small scale |
| **Mailu** | Free | ⭐⭐⭐ Medium | ⭐⭐⭐⭐ High | Self-hosted |
| **Gammu** | $20-50 | ⭐⭐⭐⭐ Hard | ⭐⭐⭐ Medium | SMS (hardware) |
| **Android** | Free | ⭐⭐ Easy | ⭐⭐⭐ Medium | SMS (mobile) |
| **PlaySMS** | Free | ⭐⭐⭐ Medium | ⭐⭐⭐⭐ High | SMS (gateway) |

*Gmail: 500 emails/day limit

---

## ✅ Recommended Setup

### **For Development:**
```
MailHog (Email) + Console logging (SMS)
```

### **For Production:**
```
Postal (Email) + Android Gateway or PlaySMS (SMS)
```

### **For Budget Production:**
```
Gmail (Email) + Android Phone (SMS)
```

---

## 🎯 Next Steps

1. **Choose your email provider** (MailHog for dev, Postal for prod)
2. **Choose your SMS provider** (Android Gateway is easiest)
3. **Update docker-compose.yml** with chosen services
4. **Configure environment variables**
5. **Test OTP flow**
6. **Deploy to production**

All solutions are **100% free and open source**! 🎉
