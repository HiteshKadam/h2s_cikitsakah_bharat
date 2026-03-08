# Quick Start Deployment Guide

## 🚀 Deploy in 5 Steps

### Step 1: Launch EC2 Instance
```
- Instance Type: t2.medium or t3.medium
- OS: Ubuntu 22.04 LTS
- Storage: 20GB
- Security Group: Ports 22, 80, 443
```

### Step 2: Connect and Upload Files
```bash
# Connect to EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# Upload setup script from local machine
scp -i your-key.pem setup_ec2.sh ubuntu@your-ec2-ip:~/

# Upload project files
scp -i your-key.pem -r h2s_cikitsakah_bharat ubuntu@your-ec2-ip:/tmp/
```

### Step 3: Run Setup Script
```bash
# On EC2 instance
chmod +x setup_ec2.sh
./setup_ec2.sh
```

The script will:
- ✅ Install all dependencies (Python, Node.js, Nginx, PostgreSQL)
- ✅ Setup database
- ✅ Configure Django backend with Gunicorn
- ✅ Build and deploy Angular frontend
- ✅ Configure Nginx as reverse proxy
- ✅ Setup firewall

### Step 4: Update Configuration

**Backend - Update ALLOWED_HOSTS:**
```bash
nano /var/www/cikitsakh/cikitsakh_backend/.env
```
Add your domain/IP:
```
ALLOWED_HOSTS=your-domain.com,your-ec2-ip,localhost
```

**Frontend - Update API URL (if using domain):**
```bash
nano /var/www/cikitsakh/cikitsakh-frontend/src/app/services/api.service.ts
```
```typescript
private baseUrl = '/api';  // For same domain
// OR
private baseUrl = 'https://your-domain.com/api';  // For different domain
```

Rebuild frontend:
```bash
cd /var/www/cikitsakh/cikitsakh-frontend
ng build --configuration production
sudo cp -r dist/cikitsakh-frontend/browser/* /var/www/html/cikitsakh/
```

### Step 5: Restart Services
```bash
sudo systemctl restart gunicorn nginx
```

## ✅ Access Your Application

**URL:** `http://your-ec2-ip` or `http://your-domain.com`

---

## 🔒 Optional: Setup SSL (HTTPS)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate (requires domain name)
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Update Django settings for HTTPS
nano /var/www/cikitsakh/cikitsakh_backend/.env
```
Add:
```
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

Restart:
```bash
sudo systemctl restart gunicorn
```

---

## 📊 Monitoring

### Check Service Status
```bash
sudo systemctl status gunicorn
sudo systemctl status nginx
sudo systemctl status postgresql
```

### View Logs
```bash
# Gunicorn logs
sudo journalctl -u gunicorn -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

---

## 🔄 Deploy Updates

```bash
# Use the deployment script
/var/www/cikitsakh/deploy.sh
```

Or manually:
```bash
cd /var/www/cikitsakh
git pull origin main

# Backend
cd cikitsakh_backend
source venv/bin/activate
pip install -r requirements.txt
python manage.py collectstatic --noinput
deactivate
sudo systemctl restart gunicorn

# Frontend
cd ../cikitsakh-frontend
npm install
ng build --configuration production
sudo cp -r dist/cikitsakh-frontend/browser/* /var/www/html/cikitsakh/
sudo systemctl restart nginx
```

---

## 🛠️ Troubleshooting

### 502 Bad Gateway
```bash
# Check Gunicorn
sudo systemctl status gunicorn
sudo journalctl -u gunicorn -n 50

# Restart
sudo systemctl restart gunicorn
```

### Frontend not loading
```bash
# Check Nginx
sudo nginx -t
sudo systemctl status nginx

# Check files exist
ls -la /var/www/html/cikitsakh/
```

### Database connection error
```bash
# Check PostgreSQL
sudo systemctl status postgresql

# Test connection
psql -U cikitsakh_user -d cikitsakh_db -h localhost
```

### API calls failing
```bash
# Check CORS settings in Django
# Check Nginx proxy configuration
sudo nano /etc/nginx/sites-available/cikitsakh

# Test backend directly
curl http://localhost:8000/api/
```

---

## 📁 File Structure on Server

```
/var/www/cikitsakh/
├── cikitsakh_backend/
│   ├── venv/
│   ├── cikitsakh_backend/
│   │   ├── settings.py
│   │   └── wsgi.py
│   ├── home/
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env
│   └── staticfiles/
├── cikitsakh-frontend/
│   ├── src/
│   ├── dist/
│   └── package.json
└── deploy.sh

/var/www/html/cikitsakh/
└── (Angular build files)

/etc/nginx/sites-available/
└── cikitsakh

/etc/systemd/system/
└── gunicorn.service
```

---

## 💰 Cost Estimate

**AWS EC2 (t3.medium):**
- Instance: ~$30/month
- Storage (20GB): ~$2/month
- Data Transfer: ~$9/GB (first 10GB free)

**Total: ~$35-50/month**

---

## 🔐 Security Checklist

- [ ] Change default SSH port
- [ ] Setup SSH key authentication only
- [ ] Configure firewall (UFW)
- [ ] Install fail2ban
- [ ] Setup SSL certificate
- [ ] Regular security updates
- [ ] Database backups
- [ ] Strong passwords
- [ ] Disable root login
- [ ] Monitor logs

---

## 📞 Support

**Common Issues:**
1. Check all services are running
2. Review logs for errors
3. Verify database connection
4. Check firewall rules
5. Test Nginx configuration

**Useful Links:**
- Django Deployment: https://docs.djangoproject.com/en/stable/howto/deployment/
- Nginx Documentation: https://nginx.org/en/docs/
- Let's Encrypt: https://letsencrypt.org/

---

## 🎉 Success!

Your application should now be live at:
- **Frontend:** `http://your-ec2-ip/`
- **Backend API:** `http://your-ec2-ip/api/`

For detailed instructions, see `DEPLOYMENT_GUIDE.md`
