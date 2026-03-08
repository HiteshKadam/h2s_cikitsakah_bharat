# AWS EC2 Deployment Guide - Django + Angular

## Architecture Overview

```
EC2 Instance (Ubuntu)
├── Nginx (Port 80/443)
│   ├── Frontend: / → Angular (Static Files)
│   └── Backend: /api → Django (Gunicorn on Port 8000)
├── PostgreSQL/MySQL (Database)
├── Gunicorn (WSGI Server for Django)
└── PM2 (Optional: Process Manager)
```

## Prerequisites

- AWS Account
- EC2 Instance (Ubuntu 22.04 LTS recommended)
- Domain name (optional, for SSL)
- Security Group configured (Ports: 22, 80, 443)

---

## Step 1: Launch EC2 Instance

### 1.1 Create EC2 Instance
```bash
# Instance Type: t2.medium or t3.medium (minimum)
# OS: Ubuntu 22.04 LTS
# Storage: 20GB minimum
# Security Group: Allow ports 22, 80, 443
```

### 1.2 Configure Security Group
```
Inbound Rules:
- SSH (22) - Your IP
- HTTP (80) - 0.0.0.0/0
- HTTPS (443) - 0.0.0.0/0
- Custom TCP (8000) - 127.0.0.1/32 (localhost only)
```

### 1.3 Connect to Instance
```bash
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

---

## Step 2: Initial Server Setup

### 2.1 Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 2.2 Install Required Packages
```bash
# Python and dependencies
sudo apt install -y python3-pip python3-dev python3-venv

# Nginx
sudo apt install -y nginx

# Node.js and npm (for Angular build)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Database (PostgreSQL)
sudo apt install -y postgresql postgresql-contrib

# Other utilities
sudo apt install -y git curl wget
```

### 2.3 Install Angular CLI
```bash
sudo npm install -g @angular/cli
```

---

## Step 3: Setup Database

### 3.1 Configure PostgreSQL
```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE cikitsakh_db;
CREATE USER cikitsakh_user WITH PASSWORD 'your_strong_password';
ALTER ROLE cikitsakh_user SET client_encoding TO 'utf8';
ALTER ROLE cikitsakh_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE cikitsakh_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE cikitsakh_db TO cikitsakh_user;
\q
```

### 3.2 Update PostgreSQL Authentication (if needed)
```bash
sudo nano /etc/postgresql/14/main/pg_hba.conf

# Change peer to md5 for local connections
# local   all             all                                     md5

sudo systemctl restart postgresql
```

---

## Step 4: Deploy Django Backend

### 4.1 Create Application Directory
```bash
sudo mkdir -p /var/www/cikitsakh
sudo chown -R $USER:$USER /var/www/cikitsakh
cd /var/www/cikitsakh
```

### 4.2 Clone or Upload Your Code
```bash
# Option 1: Clone from Git
git clone https://github.com/your-repo/h2s_cikitsakah_bharat.git .

# Option 2: Upload via SCP from local machine
# scp -i your-key.pem -r /path/to/project ubuntu@your-ec2-ip:/var/www/cikitsakh/
```

### 4.3 Setup Python Virtual Environment
```bash
cd /var/www/cikitsakh/cikitsakh_backend
python3 -m venv venv
source venv/bin/activate
```

### 4.4 Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### 4.5 Create/Update Django Settings for Production
```bash
nano cikitsakh_backend/settings.py
```

Add production settings:
```python
import os
from pathlib import Path

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'your-secret-key-here')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['your-domain.com', 'your-ec2-ip', 'localhost']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'cikitsakh_db',
        'USER': 'cikitsakh_user',
        'PASSWORD': 'your_strong_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://your-domain.com",
    "https://your-domain.com",
]

# Security settings
SECURE_SSL_REDIRECT = False  # Set to True when using HTTPS
SESSION_COOKIE_SECURE = False  # Set to True when using HTTPS
CSRF_COOKIE_SECURE = False  # Set to True when using HTTPS
```

### 4.6 Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 4.7 Run Migrations (if using managed models)
```bash
python manage.py migrate
```

### 4.8 Create Gunicorn Service
```bash
sudo nano /etc/systemd/system/gunicorn.service
```

Add:
```ini
[Unit]
Description=Gunicorn daemon for Cikitsakh Django Backend
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/cikitsakh/cikitsakh_backend
Environment="PATH=/var/www/cikitsakh/cikitsakh_backend/venv/bin"
ExecStart=/var/www/cikitsakh/cikitsakh_backend/venv/bin/gunicorn \
          --workers 3 \
          --bind 127.0.0.1:8000 \
          cikitsakh_backend.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 4.9 Start Gunicorn
```bash
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl status gunicorn
```

---

## Step 5: Deploy Angular Frontend

### 5.1 Navigate to Frontend Directory
```bash
cd /var/www/cikitsakh/cikitsakh-frontend
```

### 5.2 Install Dependencies
```bash
npm install
```

### 5.3 Update API URL for Production
```bash
nano src/app/services/api.service.ts
```

Update:
```typescript
export class ApiService {
  private baseUrl = '/api';  // Use relative URL for same domain
  // OR
  // private baseUrl = 'https://your-domain.com/api';
}
```

### 5.4 Build Angular for Production
```bash
ng build --configuration production
```

This creates optimized files in `dist/cikitsakh-frontend/browser/`

### 5.5 Copy Build to Nginx Directory
```bash
sudo mkdir -p /var/www/html/cikitsakh
sudo cp -r dist/cikitsakh-frontend/browser/* /var/www/html/cikitsakh/
sudo chown -R www-data:www-data /var/www/html/cikitsakh
```

---

## Step 6: Configure Nginx

### 6.1 Create Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/cikitsakh
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;  # Or use EC2 IP

    # Frontend - Angular
    location / {
        root /var/www/html/cikitsakh;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend - Django API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers (if needed)
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization' always;
        
        if ($request_method = 'OPTIONS') {
            return 204;
        }
    }

    # Django static files
    location /static/ {
        alias /var/www/cikitsakh/cikitsakh_backend/staticfiles/;
    }

    # Django media files (if any)
    location /media/ {
        alias /var/www/cikitsakh/cikitsakh_backend/media/;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;
}
```

### 6.2 Enable Site and Test Configuration
```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/cikitsakh /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

---

## Step 7: Setup SSL with Let's Encrypt (Optional but Recommended)

### 7.1 Install Certbot
```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 7.2 Obtain SSL Certificate
```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### 7.3 Auto-renewal
```bash
# Test renewal
sudo certbot renew --dry-run

# Certbot automatically sets up a cron job for renewal
```

### 7.4 Update Django Settings for HTTPS
```python
# In settings.py
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
```

---

## Step 8: Environment Variables (Recommended)

### 8.1 Create Environment File
```bash
sudo nano /var/www/cikitsakh/cikitsakh_backend/.env
```

Add:
```env
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=False
DATABASE_NAME=cikitsakh_db
DATABASE_USER=cikitsakh_user
DATABASE_PASSWORD=your_strong_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,your-ec2-ip
```

### 8.2 Update Django Settings to Use .env
```bash
pip install python-decouple
```

In `settings.py`:
```python
from decouple import config

SECRET_KEY = config('DJANGO_SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS').split(',')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DATABASE_NAME'),
        'USER': config('DATABASE_USER'),
        'PASSWORD': config('DATABASE_PASSWORD'),
        'HOST': config('DATABASE_HOST'),
        'PORT': config('DATABASE_PORT'),
    }
}
```

### 8.3 Update Gunicorn Service
```bash
sudo nano /etc/systemd/system/gunicorn.service
```

Add environment file:
```ini
[Service]
EnvironmentFile=/var/www/cikitsakh/cikitsakh_backend/.env
```

Restart:
```bash
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
```

---

## Step 9: Monitoring and Logs

### 9.1 View Logs
```bash
# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Gunicorn logs
sudo journalctl -u gunicorn -f

# Django logs (if configured)
tail -f /var/www/cikitsakh/cikitsakh_backend/logs/django.log
```

### 9.2 Check Service Status
```bash
sudo systemctl status nginx
sudo systemctl status gunicorn
sudo systemctl status postgresql
```

---

## Step 10: Deployment Script (Automation)

Create a deployment script for easy updates:

```bash
nano /var/www/cikitsakh/deploy.sh
```

Add:
```bash
#!/bin/bash

echo "Starting deployment..."

# Navigate to project directory
cd /var/www/cikitsakh

# Pull latest code
git pull origin main

# Backend deployment
echo "Deploying backend..."
cd cikitsakh_backend
source venv/bin/activate
pip install -r requirements.txt
python manage.py collectstatic --noinput
# python manage.py migrate  # Uncomment if using migrations
deactivate

# Restart Gunicorn
sudo systemctl restart gunicorn

# Frontend deployment
echo "Deploying frontend..."
cd ../cikitsakh-frontend
npm install
ng build --configuration production
sudo rm -rf /var/www/html/cikitsakh/*
sudo cp -r dist/cikitsakh-frontend/browser/* /var/www/html/cikitsakh/
sudo chown -R www-data:www-data /var/www/html/cikitsakh

# Restart Nginx
sudo systemctl restart nginx

echo "Deployment completed!"
```

Make executable:
```bash
chmod +x /var/www/cikitsakh/deploy.sh
```

Run deployment:
```bash
./deploy.sh
```

---

## Troubleshooting

### Issue: 502 Bad Gateway
```bash
# Check Gunicorn is running
sudo systemctl status gunicorn

# Check Gunicorn logs
sudo journalctl -u gunicorn -n 50

# Restart Gunicorn
sudo systemctl restart gunicorn
```

### Issue: Static files not loading
```bash
# Collect static files again
cd /var/www/cikitsakh/cikitsakh_backend
source venv/bin/activate
python manage.py collectstatic --noinput

# Check permissions
sudo chown -R www-data:www-data /var/www/cikitsakh/cikitsakh_backend/staticfiles
```

### Issue: CORS errors
```bash
# Update Django settings.py
CORS_ALLOWED_ORIGINS = [
    "http://your-domain.com",
    "https://your-domain.com",
]

# Restart Gunicorn
sudo systemctl restart gunicorn
```

### Issue: Database connection error
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U cikitsakh_user -d cikitsakh_db -h localhost
```

---

## Performance Optimization

### 1. Enable Nginx Caching
```nginx
# Add to nginx config
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=1g inactive=60m;

location /api/ {
    proxy_cache api_cache;
    proxy_cache_valid 200 10m;
    proxy_cache_bypass $http_cache_control;
    add_header X-Cache-Status $upstream_cache_status;
    # ... rest of proxy settings
}
```

### 2. Increase Gunicorn Workers
```bash
# Rule of thumb: (2 x CPU cores) + 1
sudo nano /etc/systemd/system/gunicorn.service

# Update workers
--workers 5
```

### 3. Setup Redis for Caching (Optional)
```bash
sudo apt install redis-server
pip install django-redis

# In Django settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

---

## Backup Strategy

### Database Backup Script
```bash
nano /home/ubuntu/backup_db.sh
```

Add:
```bash
#!/bin/bash
BACKUP_DIR="/home/ubuntu/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

pg_dump -U cikitsakh_user cikitsakh_db > $BACKUP_DIR/db_backup_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -name "db_backup_*.sql" -mtime +7 -delete
```

Setup cron:
```bash
crontab -e

# Add daily backup at 2 AM
0 2 * * * /home/ubuntu/backup_db.sh
```

---

## Cost Estimation

### EC2 Instance (t3.medium)
- Instance: ~$30/month
- Storage (20GB): ~$2/month
- Data Transfer: ~$9/GB (first 10GB free)

### Total: ~$35-50/month

---

## Security Checklist

- [ ] Change default SSH port
- [ ] Setup firewall (UFW)
- [ ] Disable root login
- [ ] Use SSH keys only (disable password auth)
- [ ] Setup fail2ban
- [ ] Enable HTTPS with SSL certificate
- [ ] Regular security updates
- [ ] Database backups
- [ ] Monitor logs regularly
- [ ] Use strong passwords
- [ ] Setup AWS CloudWatch monitoring

---

## Quick Commands Reference

```bash
# Restart all services
sudo systemctl restart gunicorn nginx postgresql

# View all logs
sudo journalctl -u gunicorn -f
sudo tail -f /var/log/nginx/error.log

# Check disk space
df -h

# Check memory usage
free -m

# Check running processes
ps aux | grep gunicorn
ps aux | grep nginx
```

---

## Support

For issues or questions:
1. Check logs first
2. Verify all services are running
3. Test database connection
4. Check firewall rules
5. Review Nginx configuration

---

**Deployment Complete! 🚀**

Access your application at: `http://your-domain.com` or `http://your-ec2-ip`
