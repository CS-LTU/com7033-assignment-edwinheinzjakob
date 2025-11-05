# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |

## Security Features

This application implements multiple security measures:

### Authentication & Authorization
- Argon2 password hashing
- Session-based authentication with Flask-Login
- Role-based access control (RBAC)
- JWT token authentication for API
- Account lockout after failed login attempts

### Input Validation & Sanitization
- Email format validation
- Username format validation
- Patient data field validation
- XSS prevention through input sanitization
- SQL injection prevention (parameterized queries)
- NoSQL injection prevention (MongoDB query validation)

### Security Headers
- Content Security Policy (CSP)
- Strict Transport Security (HSTS)
- X-Frame-Options
- X-Content-Type-Options
- X-XSS-Protection

### Rate Limiting
- Authentication endpoints: 5 requests/minute
- CRUD operations: 100 requests/hour
- Search operations: 30 requests/minute
- API endpoints: 1000 requests/hour

### Data Protection
- Field-level encryption for sensitive PII data
- Secure session cookies (HttpOnly, SameSite)
- CSRF protection on all forms
- Secure password storage

### Logging & Monitoring
- Structured JSON logging
- Audit logging for user actions
- Failed login attempt tracking
- Sentry integration for error monitoring

## Reporting a Vulnerability

If you discover a security vulnerability, please do NOT create a public issue.

Instead, please email the security team at:
- **Module Leader**: x.lu@leedstrinity.ac.uk
- **Assessment Team**: assessment@leedstrinity.ac.uk

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will respond within 48 hours and work with you to address the issue.

## Security Best Practices

1. **Never commit secrets**: Use environment variables for sensitive data
2. **Keep dependencies updated**: Run `safety check` regularly
3. **Use strong passwords**: Minimum 8 characters with mixed case, numbers, and special characters
4. **Enable HTTPS**: Always use HTTPS in production
5. **Regular security audits**: Run `bandit` and `safety` checks regularly
6. **Monitor logs**: Check application logs for suspicious activity

## Threat Model

### High Priority Threats
- SQL/NoSQL Injection
- Cross-Site Scripting (XSS)
- Cross-Site Request Forgery (CSRF)
- Unauthorized access to patient data
- Password brute-force attacks

### Mitigations
- Parameterized queries (SQL injection prevention)
- Input sanitization (XSS prevention)
- CSRF tokens (CSRF prevention)
- Authentication and authorization (unauthorized access)
- Rate limiting and account lockout (brute-force prevention)

## Security Checklist

- [x] Password hashing (Argon2)
- [x] Input validation and sanitization
- [x] CSRF protection
- [x] XSS prevention
- [x] SQL injection prevention
- [x] Rate limiting
- [x] Secure session handling
- [x] Security headers
- [x] Audit logging
- [x] Field-level encryption (optional)
- [ ] OAuth2 integration (optional)
- [ ] reCAPTCHA (optional)

## Compliance

This application handles sensitive healthcare data and should comply with:
- GDPR (General Data Protection Regulation)
- HIPAA (if applicable)
- Local data protection laws

**Data Retention**: Patient data is retained according to healthcare regulations. Contact administrator for data deletion requests.

