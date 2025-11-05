# ADR 002: Security Enhancements

## Status
Accepted

## Context
The application handles sensitive healthcare data and requires robust security measures to protect patient information and prevent common web vulnerabilities.

## Decision
We will implement comprehensive security measures:
1. **Argon2 Password Hashing** - Replace PBKDF2 with Argon2id for stronger password security
2. **Flask-Talisman** - Enforce security headers (CSP, HSTS, X-Frame-Options, etc.)
3. **Flask-Limiter** - Rate limiting to prevent brute-force attacks
4. **Field-Level Encryption** - Encrypt sensitive PII fields in MongoDB
5. **JWT Authentication** - Token-based authentication for API endpoints
6. **Comprehensive Input Validation** - Prevent SQL injection, XSS, and other attacks

## Consequences

### Positive
- Stronger password security with Argon2
- Protection against common web vulnerabilities
- Rate limiting prevents brute-force attacks
- Field-level encryption protects sensitive data at rest
- JWT enables stateless API authentication

### Negative
- Additional dependencies
- Slightly increased complexity
- Performance overhead from encryption/decryption

## Implementation
- Integrated Argon2 via `argon2-cffi`
- Added Flask-Talisman for security headers
- Implemented rate limiting with Flask-Limiter
- Created encryption service for field-level encryption
- Added JWT support for API authentication

## References
- OWASP Top 10
- Argon2 specification
- JWT RFC 7519

