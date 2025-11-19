# Gmail OTP Setup Guide

## ✅ Implementation Complete

Gmail SMTP has been configured for sending OTP emails via `smartfarmdao@gmail.com`.

## 🔑 Setup Gmail App Password

1. **Go to Google Account Settings**
   - Visit: https://myaccount.google.com/security
   - Sign in with `smartfarmdao@gmail.com`

2. **Enable 2-Step Verification** (if not already enabled)
   - Click "2-Step Verification"
   - Follow the setup process

3. **Generate App Password**
   - Go to: https://myaccount.google.com/apppasswords
   - Or navigate: Security → 2-Step Verification → App passwords
   - Select app: "Mail"
   - Select device: "Other (Custom name)" → Enter "AgriDAO Backend"
   - Click "Generate"
   - Copy the 16-character password (format: `xxxx xxxx xxxx xxxx`)

4. **Update Backend Configuration**
   - Open: `backend/.env`
   - Replace `your-app-password-here` with the generated password:
   ```bash
   SMTP_PASSWORD=abcd efgh ijkl mnop
   ```
   - Remove spaces: `SMTP_PASSWORD=abcdefghijklmnop`

## 📧 Configuration Details

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USERNAME=smartfarmdao@gmail.com
SMTP_PASSWORD=your-16-char-app-password
FROM_EMAIL=smartfarmdao@gmail.com
FROM_NAME=AgriDAO
```

## 🚀 How It Works

1. **User requests OTP** → Backend generates 6-digit code
2. **Email sent via Gmail SMTP** → Professional HTML email with branding
3. **User receives email** → Code valid for 5 minutes
4. **User enters code** → Backend verifies and authenticates

## 📊 Limits

- **500 emails/day** - Free Gmail account limit
- **No cost** - Completely free
- **Reliable delivery** - Gmail's infrastructure

## 🧪 Test OTP Email

```bash
# Start backend
cd backend
docker-compose up

# Test endpoint (use Postman or curl)
curl -X POST http://localhost:8000/api/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

## 🔒 Security Notes

- App password is separate from your Gmail password
- Can be revoked anytime without affecting Gmail access
- Only works with SMTP, not full Gmail access
- Store in `.env` file (never commit to git)

## 📝 Email Template

Users will receive a professional email with:
- AgriDAO branding (green header with 🌾)
- Large, easy-to-read 6-digit code
- 5-minute expiration notice
- Professional footer

## 🔄 Scaling Later

When you exceed 500 emails/day:
- Switch to **Resend** (3,000/month free)
- Or **SendGrid** (100/day free forever)
- Or **AWS SES** ($0.10 per 1,000 emails)

Migration is simple - just update SMTP settings in `.env`.

## ✅ Next Steps

1. Generate app password from Google Account
2. Update `SMTP_PASSWORD` in `backend/.env`
3. Restart backend: `docker-compose restart`
4. Test OTP sending
5. Ready for production! 🎉
