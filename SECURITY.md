# Security Guidelines for AutomateIQ

## 🔒 Environment Variables & Secrets Management

### Critical Security Rules

1. **NEVER commit secrets to version control**
   - All sensitive data should be in `.env` files (which are gitignored)
   - Use `.env.example` as a template without real values
   - Rotate secrets regularly in production

2. **Required Environment Variables**
   ```bash
   # Critical secrets that MUST be changed in production
   JWT_SECRET=                    # Minimum 32 characters, cryptographically secure
   MONGODB_URI=                   # Use strong passwords and connection strings
   OPENAI_API_KEY=               # Keep secure, monitor usage
   STRIPE_SECRET_KEY=            # Production keys for payments
   SMTP_PASS=                    # App-specific passwords for email
   ```

3. **Secret Generation**
   ```bash
   # Generate secure JWT secret
   node -e "console.log(require('crypto').randomBytes(64).toString('hex'))"
   
   # Generate secure session secret
   openssl rand -base64 32
   ```

## 🛡️ Production Security Checklist

### Environment Setup
- [ ] Change all default passwords
- [ ] Use environment-specific `.env` files
- [ ] Enable SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Set up VPN access for sensitive operations
- [ ] Enable audit logging
- [ ] Configure backup encryption

### Database Security
- [ ] Use strong MongoDB passwords
- [ ] Enable MongoDB authentication
- [ ] Configure MongoDB SSL/TLS
- [ ] Set up database backups with encryption
- [ ] Implement database connection pooling
- [ ] Enable MongoDB audit logging

### API Security
- [ ] Implement rate limiting
- [ ] Use HTTPS only in production
- [ ] Configure CORS properly
- [ ] Implement request validation
- [ ] Set up API key rotation
- [ ] Enable request/response logging

### Authentication & Authorization
- [ ] Implement strong password policies
- [ ] Enable multi-factor authentication (MFA)
- [ ] Set up session management
- [ ] Configure JWT token expiration
- [ ] Implement role-based access control (RBAC)
- [ ] Set up account lockout policies

### File Upload Security
- [ ] Validate file types and sizes
- [ ] Scan uploaded files for malware
- [ ] Store files outside web root
- [ ] Implement file access controls
- [ ] Set up file encryption at rest

### AI/ML Security
- [ ] Secure OpenAI API keys
- [ ] Implement AI usage monitoring
- [ ] Set up content filtering
- [ ] Monitor AI model outputs
- [ ] Implement usage quotas

## 🔐 Secret Management Best Practices

### Development Environment
```bash
# Use .env files (never commit these)
cp .env.example .env
# Edit .env with your development secrets
```

### Production Environment
```bash
# Use environment variables or secret management services
export JWT_SECRET="$(openssl rand -base64 64)"
export MONGODB_URI="mongodb+srv://user:password@cluster.mongodb.net/db"

# Or use cloud secret managers
# AWS Secrets Manager
# Google Secret Manager
# Azure Key Vault
# HashiCorp Vault
```

### Docker Secrets
```yaml
# docker-compose.yml
services:
  backend:
    environment:
      - JWT_SECRET_FILE=/run/secrets/jwt_secret
    secrets:
      - jwt_secret

secrets:
  jwt_secret:
    file: ./secrets/jwt_secret.txt
```

## 🚨 Security Monitoring

### Logging & Monitoring
- Monitor failed login attempts
- Track API usage patterns
- Log all administrative actions
- Monitor file upload activities
- Track AI API usage and costs

### Alerting
- Set up alerts for suspicious activities
- Monitor for unusual API usage
- Alert on failed authentication attempts
- Monitor database connection failures
- Track error rates and performance

### Incident Response
1. **Immediate Actions**
   - Rotate compromised secrets
   - Block suspicious IP addresses
   - Disable affected user accounts
   - Review access logs

2. **Investigation**
   - Analyze security logs
   - Identify scope of breach
   - Document timeline of events
   - Assess data exposure

3. **Recovery**
   - Patch security vulnerabilities
   - Update security policies
   - Notify affected users
   - Implement additional safeguards

## 🔧 Security Configuration

### Nginx Security Headers
```nginx
# Security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### Express Security Middleware
```javascript
// Security middleware configuration
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"],
    },
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
  }
}));
```

### MongoDB Security
```javascript
// Connection with security options
const mongoOptions = {
  useNewUrlParser: true,
  useUnifiedTopology: true,
  ssl: true,
  sslValidate: true,
  authSource: 'admin',
  retryWrites: true,
  w: 'majority'
};
```

## 📋 Security Audit Checklist

### Regular Security Tasks
- [ ] Review and rotate API keys monthly
- [ ] Update dependencies regularly
- [ ] Scan for security vulnerabilities
- [ ] Review user access permissions
- [ ] Audit file upload activities
- [ ] Monitor AI usage patterns
- [ ] Review error logs for security issues
- [ ] Test backup and recovery procedures

### Quarterly Security Reviews
- [ ] Penetration testing
- [ ] Security policy updates
- [ ] Access control review
- [ ] Incident response plan testing
- [ ] Security training for team
- [ ] Third-party security assessment

## 🆘 Security Incident Contacts

### Internal Team
- **Security Lead**: security@automateiq.com
- **DevOps Team**: devops@automateiq.com
- **Legal Team**: legal@automateiq.com

### External Resources
- **Cloud Provider Support**: [Provider-specific contact]
- **Security Consultant**: [External security firm]
- **Legal Counsel**: [Law firm contact]

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Node.js Security Checklist](https://blog.risingstack.com/node-js-security-checklist/)
- [MongoDB Security Checklist](https://docs.mongodb.com/manual/administration/security-checklist/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [AWS Security Best Practices](https://aws.amazon.com/architecture/security-identity-compliance/)

---

**Remember**: Security is an ongoing process, not a one-time setup. Regularly review and update your security measures as your application grows and evolves.