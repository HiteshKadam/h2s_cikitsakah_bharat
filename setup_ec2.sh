#!/bin/bash

# EC2 Setup Script for Cikitsakh Application
# Run this script on a fresh Ubuntu 22.04 EC2 instance

set -e

echo "=========================================="
echo "Cikitsakh EC2 Setup Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    print_error "Please do not run as root. Run as ubuntu user."
    exit 1
fi

# Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
print_status "Installing Python and dependencies..."
sudo apt install -y python3-pip python3-dev python3-venv

# Install Nginx
print_status "Installing Nginx..."
sudo apt install -y nginx

# Install Node.js
print_status "Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install PostgreSQL
print_status "Installing PostgreSQL..."
sudo apt install -y postgresql postgresql-contrib

# Install other utilities
print_status "Installing utilities..."
sudo apt install -y git curl wget

# Install Angular CLI
print_status "Installing Angular CLI..."
sudo npm install -g @angular/cli

# Create application directory
print_status "Creating application directory..."
sudo mkdir -p /var/www/cikitsakh
sudo chown -R $USER:$USER /var/www/cikitsakh

# Prompt for database credentials
print_warning "Database Setup"
read -p "Enter database name [cikitsakh_db]: " DB_NAME
DB_NAME=${DB_NAME:-cikitsakh_db}

read -p "Enter database user [cikitsakh_user]: " DB_USER
DB_USER=${DB_USER:-cikitsakh_user}

read -sp "Enter database password: " DB_PASSWORD
echo

# Setup PostgreSQL
print_status "Setting up PostgreSQL database..."
sudo -u postgres psql <<EOF
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
ALTER ROLE $DB_USER SET client_encoding TO 'utf8';
ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';
ALTER ROLE $DB_USER SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF

print_status "PostgreSQL setup completed!"

# Prompt for deployment method
print_warning "Code Deployment"
echo "How would you like to deploy your code?"
echo "1) Clone from Git repository"
echo "2) I will upload manually via SCP"
read -p "Enter choice [1 or 2]: " DEPLOY_METHOD

if [ "$DEPLOY_METHOD" == "1" ]; then
    read -p "Enter Git repository URL: " GIT_REPO
    print_status "Cloning repository..."
    cd /var/www/cikitsakh
    git clone $GIT_REPO .
else
    print_warning "Please upload your code to /var/www/cikitsakh/ using SCP"
    print_warning "Command: scp -i your-key.pem -r /local/path ubuntu@$HOSTNAME:/var/www/cikitsakh/"
    read -p "Press Enter when upload is complete..."
fi

# Setup Python virtual environment
if [ -d "/var/www/cikitsakh/cikitsakh_backend" ]; then
    print_status "Setting up Python virtual environment..."
    cd /var/www/cikitsakh/cikitsakh_backend
    python3 -m venv venv
    source venv/bin/activate
    
    print_status "Installing Python dependencies..."
    pip install --upgrade pip
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
    
    pip install gunicorn psycopg2-binary python-decouple
    
    # Create .env file
    print_status "Creating environment file..."
    cat > .env <<EOF
DJANGO_SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=False
DATABASE_NAME=$DB_NAME
DATABASE_USER=$DB_USER
DATABASE_PASSWORD=$DB_PASSWORD
DATABASE_HOST=localhost
DATABASE_PORT=5432
ALLOWED_HOSTS=localhost,127.0.0.1
EOF
    
    # Collect static files
    print_status "Collecting static files..."
    python manage.py collectstatic --noinput || print_warning "Static files collection failed (may need manual intervention)"
    
    deactivate
else
    print_error "Backend directory not found at /var/www/cikitsakh/cikitsakh_backend"
fi

# Create Gunicorn service
print_status "Creating Gunicorn service..."
sudo tee /etc/systemd/system/gunicorn.service > /dev/null <<EOF
[Unit]
Description=Gunicorn daemon for Cikitsakh Django Backend
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=/var/www/cikitsakh/cikitsakh_backend
Environment="PATH=/var/www/cikitsakh/cikitsakh_backend/venv/bin"
EnvironmentFile=/var/www/cikitsakh/cikitsakh_backend/.env
ExecStart=/var/www/cikitsakh/cikitsakh_backend/venv/bin/gunicorn \\
          --workers 3 \\
          --bind 127.0.0.1:8000 \\
          cikitsakh_backend.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

# Start Gunicorn
print_status "Starting Gunicorn..."
sudo systemctl start gunicorn
sudo systemctl enable gunicorn

# Build Angular frontend
if [ -d "/var/www/cikitsakh/cikitsakh-frontend" ]; then
    print_status "Building Angular frontend..."
    cd /var/www/cikitsakh/cikitsakh-frontend
    
    print_status "Installing npm dependencies..."
    npm install
    
    print_status "Building for production..."
    ng build --configuration production
    
    # Copy to Nginx directory
    print_status "Deploying frontend..."
    sudo mkdir -p /var/www/html/cikitsakh
    sudo cp -r dist/cikitsakh-frontend/browser/* /var/www/html/cikitsakh/
    sudo chown -R www-data:www-data /var/www/html/cikitsakh
else
    print_error "Frontend directory not found at /var/www/cikitsakh/cikitsakh-frontend"
fi

# Get server IP
SERVER_IP=$(curl -s http://checkip.amazonaws.com)

# Configure Nginx
print_status "Configuring Nginx..."
sudo tee /etc/nginx/sites-available/cikitsakh > /dev/null <<EOF
server {
    listen 80;
    server_name $SERVER_IP localhost;

    # Frontend - Angular
    location / {
        root /var/www/html/cikitsakh;
        try_files \$uri \$uri/ /index.html;
        
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend - Django API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Django static files
    location /static/ {
        alias /var/www/cikitsakh/cikitsakh_backend/staticfiles/;
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
EOF

# Enable site
print_status "Enabling Nginx site..."
sudo ln -sf /etc/nginx/sites-available/cikitsakh /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
print_status "Testing Nginx configuration..."
sudo nginx -t

# Restart Nginx
print_status "Restarting Nginx..."
sudo systemctl restart nginx
sudo systemctl enable nginx

# Create deployment script
print_status "Creating deployment script..."
cat > /var/www/cikitsakh/deploy.sh <<'EOF'
#!/bin/bash
echo "Starting deployment..."
cd /var/www/cikitsakh
git pull origin main

# Backend
echo "Deploying backend..."
cd cikitsakh_backend
source venv/bin/activate
pip install -r requirements.txt
python manage.py collectstatic --noinput
deactivate
sudo systemctl restart gunicorn

# Frontend
echo "Deploying frontend..."
cd ../cikitsakh-frontend
npm install
ng build --configuration production
sudo rm -rf /var/www/html/cikitsakh/*
sudo cp -r dist/cikitsakh-frontend/browser/* /var/www/html/cikitsakh/
sudo chown -R www-data:www-data /var/www/html/cikitsakh
sudo systemctl restart nginx

echo "Deployment completed!"
EOF

chmod +x /var/www/cikitsakh/deploy.sh

# Setup firewall
print_status "Configuring firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# Print summary
echo ""
echo "=========================================="
print_status "Setup Complete!"
echo "=========================================="
echo ""
echo "Application URL: http://$SERVER_IP"
echo ""
echo "Service Status:"
sudo systemctl status gunicorn --no-pager | grep Active
sudo systemctl status nginx --no-pager | grep Active
sudo systemctl status postgresql --no-pager | grep Active
echo ""
echo "Useful Commands:"
echo "  - View Gunicorn logs: sudo journalctl -u gunicorn -f"
echo "  - View Nginx logs: sudo tail -f /var/log/nginx/error.log"
echo "  - Restart services: sudo systemctl restart gunicorn nginx"
echo "  - Deploy updates: /var/www/cikitsakh/deploy.sh"
echo ""
print_warning "Next Steps:"
echo "  1. Update ALLOWED_HOSTS in Django settings with your domain"
echo "  2. Update API URL in Angular if using a domain"
echo "  3. Setup SSL certificate with: sudo certbot --nginx"
echo "  4. Configure database backups"
echo ""
print_status "Deployment guide available at: DEPLOYMENT_GUIDE.md"
echo "=========================================="
