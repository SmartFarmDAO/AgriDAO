# Production Authentication Setup Guide

## Overview

AgriDAO now includes a production-ready authentication system with:
- Multi-provider email service (Gmail, SendGrid, Mailgun)
- Rate limiting (3 requests per minute per email)
- Automatic fallback between email providers
- Secure OTP generation and verification
- Production environment configuration

## Quick Setup

### 1. Configure Email Provider

Choose one or more email providers:

#### Option A: Gmail SMTP (Recommended for small scale)
```bash
# In .env.production
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # Generate at https://myaccount.google.com/apppasswords
FROM_EMAIL=your-email@gmail.com
FROM_NAME=AgriDAO
```

#### Option B: SendGrid (Recommended for production)
```bash
# In .env.production
SENDGRID_API_KEY=your-sendgrid-api-key
SENDGRID_FROM_EMAIL=noreply@yourdomain.com
SENDGRID_FROM_NAME=AgriDAO
```

#### Option C: Mailgun (Alternative)
```bash
# In .env.production
MAILGUN_API_KEY=your-mailgun-api-key
MAILGUN_DOMAIN=yourdomain.com
MAILGUN_FROM_EMAIL=noreply@yourdomain.com
MAILGUN_FROM_NAME=AgriDAO
```

### 2. Set Environment to Production
```bash
# In .env.production
ENVIRONMENT=production
```

### 3. Deploy
```bash
# Copy and configure production environment
cp .env.production.example .env.production
# Edit .env.production with your settings

# Run deployment script
./scripts/deploy-production.sh
```

## Email Provider Setup Instructions

### Gmail Setup
1. Enable 2-Factor Authentication on your Google account
2. Go to https://myaccount.google.com/apppasswords
3. Generate an app password for "Mail"
4. Use the 16-character password in `SMTP_PASSWORD`

### SendGrid Setup
1. Sign up at https://sendgrid.com
2. Create an API key with "Mail Send" permissions
3. Verify your sender email/domain
4. Use the API key in `SENDGRID_API_KEY`

### Mailgun Setup
1. Sign up at https://mailgun.com
2. Add and verify your domain
3. Get your API key from the dashboard
4. Use the API key and domain in configuration

## Production vs Development Behavior

### Development Mode (`ENVIRONMENT=development`)
- Shows `dev_code` in API responses when email fails
- Allows authentication with dev_code
- More verbose error messages
- Suitable for testing

### Production Mode (`ENVIRONMENT=production`)
- No `dev_code` in API responses
- Requires actual email delivery for authentication
- Generic error messages for security
- Rate limiting enforced
- Suitable for real users

## Rate Limiting

- 3 OTP requests per minute per email address
- Prevents abuse and spam
- Returns error message when limit exceeded
- Automatically resets after 1 minute

## Security Features

- Secure 6-digit OTP generation using `secrets` module
- 5-minute OTP expiration
- Maximum 3 verification attempts per OTP
- Rate limiting to prevent brute force attacks
- Production environment removes debug information

## Monitoring

Monitor these metrics in production:
- Email delivery success rate
- OTP verification success rate
- Rate limiting triggers
- Authentication failures

## Troubleshooting

### Email Not Sending
1. Check email provider configuration
2. Verify API keys/passwords are correct
3. Check provider account status and limits
4. Review backend logs for specific errors

### Rate Limiting Issues
- Users hitting rate limits too frequently
- Consider adjusting limits in `otp_service.py`
- Monitor for potential abuse

### Authentication Failures
- Check OTP expiration (5 minutes)
- Verify attempt limits (3 attempts)
- Ensure email delivery is working

## Testing

Test the complete flow:
```bash
# Request OTP
curl -X POST https://yourdomain.com/api/auth/otp/request \
  -H "Content-Type: application/json" \
  -d '{"email": "test@yourdomain.com"}'

# Check email and verify OTP
curl -X POST https://yourdomain.com/api/auth/otp/verify \
  -H "Content-Type: application/json" \
  -d '{"email": "test@yourdomain.com", "code": "123456"}'
```

## Support

For issues or questions:
1. Check application logs: `docker-compose logs backend`
2. Verify email provider status
3. Test with different email addresses
4. Check rate limiting status

The system is now ready for production use with real users!
