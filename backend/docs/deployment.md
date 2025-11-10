# Production Deployment Guide

**Project**: 大学向けコミュニケーションツール Backend
**Version**: v3
**Last Updated**: 2025-11-10

---

## Overview

This guide covers deploying the FastAPI backend to a production environment. It includes configuration, security hardening, and operational procedures.

### Deployment Options

1. **Docker Compose** (Recommended for small to medium deployments)
2. **Kubernetes** (For large-scale deployments)
3. **Traditional VPS** (Ubuntu/RHEL)

This guide focuses on Docker Compose deployment.

---

## Prerequisites

### System Requirements

**Minimum**:
- 2 CPU cores
- 4GB RAM
- 20GB SSD storage
- Ubuntu 20.04+ or similar Linux distribution

**Recommended**:
- 4+ CPU cores
- 8GB+ RAM
- 50GB+ SSD storage
- Load balancer (nginx/traefik)

### Software Requirements

- Docker 24.0+
- Docker Compose 2.0+
- Git
- (Optional) nginx for reverse proxy

---

## Deployment Steps

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

### 2. Clone Repository

```bash
# Create deployment directory
sudo mkdir -p /opt/university-communication
cd /opt/university-communication

# Clone repository
git clone <repository-url> .

# Navigate to backend
cd backend
```

### 3. Environment Configuration

Create production `.env` file:

```bash
# Create .env file
nano .env
```

**Production `.env` template**:

```bash
# ==================
# Database Configuration
# ==================
DATABASE_URL=postgresql://postgres:STRONG_PASSWORD_HERE@db:5432/university_communication

# ==================
# JWT Configuration
# ==================
# CRITICAL: Generate a strong SECRET_KEY
# Use: openssl rand -hex 32
SECRET_KEY=your-very-strong-secret-key-min-64-characters-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# ==================
# Application Configuration
# ==================
DEBUG=false  # MUST be false in production
ENVIRONMENT=production

# ==================
# PostgreSQL Configuration
# ==================
POSTGRES_USER=postgres
POSTGRES_PASSWORD=STRONG_PASSWORD_HERE
POSTGRES_DB=university_communication

# ==================
# CORS Configuration
# ==================
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# ==================
# Logging
# ==================
LOG_LEVEL=INFO
```

**⚠️ SECURITY WARNINGS**:
1. **NEVER use default passwords in production**
2. **Generate a strong SECRET_KEY**: `openssl rand -hex 32`
3. **Set DEBUG=false**
4. **Restrict ALLOWED_ORIGINS** to your actual domain
5. **Keep .env file secret** (add to .gitignore)

### 4. Production Dockerfile

**Dockerfile.prod**:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run with gunicorn (NOT uvicorn --reload)
CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "--access-logfile", "-", "--error-logfile", "-"]
```

**Key Changes from Development**:
- ❌ Removed `--reload` flag
- ✅ Using `gunicorn` with multiple workers
- ✅ Running as non-root user
- ✅ Production-grade WSGI server

### 5. Docker Compose Configuration

**docker-compose.prod.yml**:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: university_db
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backup:/backup
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - backend_network

  backend:
    build:
      context: .
      dockerfile: Dockerfile.prod
    container_name: university_backend
    environment:
      DATABASE_URL: ${DATABASE_URL}
      SECRET_KEY: ${SECRET_KEY}
      ALGORITHM: ${ALGORITHM}
      ACCESS_TOKEN_EXPIRE_MINUTES: ${ACCESS_TOKEN_EXPIRE_MINUTES}
      DEBUG: ${DEBUG}
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - backend_network
    volumes:
      - ./logs:/app/logs

volumes:
  postgres_data:

networks:
  backend_network:
    driver: bridge
```

### 6. Build and Deploy

```bash
# Build production image
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f

# Verify services
docker-compose -f docker-compose.prod.yml ps
```

### 7. Database Migration

```bash
# Run migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Verify migration
docker-compose -f docker-compose.prod.yml exec db psql -U postgres -d university_communication -c "\dt"
```

---

## Reverse Proxy (nginx)

### nginx Configuration

**`/etc/nginx/sites-available/university-communication`**:

```nginx
upstream backend_api {
    server localhost:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Proxy Configuration
    location / {
        proxy_pass http://backend_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;

    # Logging
    access_log /var/log/nginx/university_api_access.log;
    error_log /var/log/nginx/university_api_error.log;
}
```

### SSL Certificate (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d api.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

---

## Security Hardening

### 1. Firewall Configuration

```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Deny direct access to backend port
sudo ufw deny 8000/tcp

# Check status
sudo ufw status
```

### 2. Environment Variables Security

```bash
# Set restrictive permissions
chmod 600 .env

# Never commit .env to git
echo ".env" >> .gitignore
```

### 3. Database Security

```bash
# Change default PostgreSQL password
docker-compose -f docker-compose.prod.yml exec db psql -U postgres
ALTER USER postgres WITH PASSWORD 'new_strong_password';
\q

# Update .env with new password
```

### 4. Application Security Checklist

- [x] DEBUG=false
- [x] Strong SECRET_KEY (64+ characters)
- [x] HTTPS enabled
- [x] CORS restricted to actual domains
- [x] Rate limiting configured
- [x] Security headers enabled
- [x] Running as non-root user
- [x] Database password changed
- [x] Firewall configured
- [x] Regular security updates

---

## Backup Strategy

### Automated Backup Script

**`/opt/university-communication/scripts/backup.sh`**:

```bash
#!/bin/bash

BACKUP_DIR="/opt/university-communication/backend/backup"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql"

# Create backup
docker-compose -f /opt/university-communication/backend/docker-compose.prod.yml exec -T db \
    pg_dump -U postgres university_communication > "$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_FILE"

# Delete backups older than 30 days
find "$BACKUP_DIR" -name "backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

### Cron Job for Daily Backups

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /opt/university-communication/scripts/backup.sh >> /var/log/backup.log 2>&1
```

### Restore from Backup

```bash
# Stop backend service
docker-compose -f docker-compose.prod.yml stop backend

# Restore database
gunzip -c backup/backup_20251110_020000.sql.gz | \
    docker-compose -f docker-compose.prod.yml exec -T db \
    psql -U postgres university_communication

# Restart services
docker-compose -f docker-compose.prod.yml start backend
```

---

## Monitoring and Logging

### Health Check Endpoints

```bash
# Check application health
curl https://api.yourdomain.com/health

# Expected response:
{"status": "healthy"}
```

### Log Management

```bash
# View backend logs
docker-compose -f docker-compose.prod.yml logs -f backend

# View database logs
docker-compose -f docker-compose.prod.yml logs -f db

# View nginx logs
sudo tail -f /var/log/nginx/university_api_access.log
sudo tail -f /var/log/nginx/university_api_error.log
```

### Log Rotation

**`/etc/logrotate.d/university-communication`**:

```
/var/log/nginx/university_api_*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        [ -f /var/run/nginx.pid ] && kill -USR1 `cat /var/run/nginx.pid`
    endscript
}
```

---

## Scaling Strategies

### Horizontal Scaling

**Update docker-compose.prod.yml**:

```yaml
backend:
  deploy:
    replicas: 3
    update_config:
      parallelism: 1
      delay: 10s
    restart_policy:
      condition: on-failure
```

### Vertical Scaling

```yaml
backend:
  deploy:
    resources:
      limits:
        cpus: '2.0'
        memory: 4G
      reservations:
        cpus: '1.0'
        memory: 2G
```

---

## Maintenance Procedures

### Zero-Downtime Deployment

```bash
# Build new image
docker-compose -f docker-compose.prod.yml build backend

# Rolling update
docker-compose -f docker-compose.prod.yml up -d --no-deps --build backend

# Verify health
curl https://api.yourdomain.com/health
```

### Database Migration in Production

```bash
# 1. Create backup FIRST
./scripts/backup.sh

# 2. Test migration on backup (optional but recommended)
# ...

# 3. Apply migration
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# 4. Verify
docker-compose -f docker-compose.prod.yml exec backend alembic current

# 5. If issues, rollback
docker-compose -f docker-compose.prod.yml exec backend alembic downgrade -1
```

---

## Troubleshooting

### Common Issues

#### 1. Backend Not Starting

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs backend

# Common causes:
# - Database not ready (check db logs)
# - Invalid DATABASE_URL
# - Missing SECRET_KEY
# - Port 8000 already in use
```

#### 2. Database Connection Error

```bash
# Verify database is running
docker-compose -f docker-compose.prod.yml ps db

# Test connection
docker-compose -f docker-compose.prod.yml exec db psql -U postgres -d university_communication -c "SELECT 1;"

# Check DATABASE_URL format
echo $DATABASE_URL
```

#### 3. 502 Bad Gateway (nginx)

```bash
# Check backend health
docker-compose -f docker-compose.prod.yml ps backend

# Check nginx configuration
sudo nginx -t

# Restart services
docker-compose -f docker-compose.prod.yml restart backend
sudo systemctl restart nginx
```

---

## Performance Tuning

### PostgreSQL Tuning

**Edit `postgresql.conf`** (inside container or via docker volume):

```conf
# Connections
max_connections = 100

# Memory
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 16MB
maintenance_work_mem = 64MB

# Checkpoints
checkpoint_completion_target = 0.9
wal_buffers = 16MB

# Query Planner
random_page_cost = 1.1  # For SSD
effective_io_concurrency = 200
```

### Gunicorn Workers

Rule of thumb: `(2 x $num_cores) + 1`

```bash
# For 4 cores:
CMD ["gunicorn", "main:app", "-w", "9", "-k", "uvicorn.workers.UvicornWorker", ...]
```

---

## Rollback Procedure

### Emergency Rollback

```bash
# 1. Stop current deployment
docker-compose -f docker-compose.prod.yml down

# 2. Restore database from backup
gunzip -c backup/backup_TIMESTAMP.sql.gz | docker-compose -f docker-compose.prod.yml exec -T db psql -U postgres university_communication

# 3. Checkout previous version
git checkout <previous-commit>

# 4. Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build

# 5. Verify
curl https://api.yourdomain.com/health
```

---

## Checklist for Production Deployment

### Pre-Deployment

- [ ] All tests passing
- [ ] Code reviewed
- [ ] Database migrations tested
- [ ] .env file configured with production values
- [ ] SECRET_KEY generated
- [ ] DEBUG=false
- [ ] SSL certificates obtained
- [ ] Firewall configured
- [ ] Backup system in place
- [ ] Monitoring configured

### During Deployment

- [ ] Database backup created
- [ ] Services built successfully
- [ ] Migrations applied
- [ ] Health checks passing
- [ ] Logs monitored
- [ ] Performance verified

### Post-Deployment

- [ ] Smoke tests performed
- [ ] Documentation updated
- [ ] Team notified
- [ ] Rollback plan confirmed
- [ ] Monitoring dashboard reviewed

---

## Support and Resources

### Documentation Links

- [README.md](../README.md)
- [Database Schema](database_schema.md)
- [Code Review Report](../REVIEW.md)

### Monitoring

- Uptime: https://uptimerobot.com
- Application Performance: Consider New Relic, DataDog, or open-source alternatives

### Contacts

- Infrastructure Issues: infrastructure-team@example.com
- Application Issues: backend-team@example.com
- Security Issues: security@example.com

---

**Last Updated**: 2025-11-10
**Maintained By**: Backend Team
