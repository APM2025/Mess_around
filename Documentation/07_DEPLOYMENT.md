# Deployment Guide

## Overview

This document provides comprehensive instructions for deploying the UK Childhood Immunisation Coverage Data Insights Tool in different environments.

---

## Table of Contents

1. [Local Development Setup](#local-development-setup)
2. [Database Initialization](#database-initialization)
3. [Running the Application](#running-the-application)
4. [Testing Deployment](#testing-deployment)
5. [Production Deployment](#production-deployment)
6. [Configuration Management](#configuration-management)
7. [Monitoring and Logging](#monitoring-and-logging)
8. [Troubleshooting](#troubleshooting)

---

## Local Development Setup

### Prerequisites

**Required Software:**
- Python 3.12 or higher
- pip (Python package manager)
- Git
- Web browser (Chrome, Firefox, Edge, Safari)

**Recommended:**
- Virtual environment tool (venv)
- Code editor (VS Code, PyCharm, etc.)

### Step-by-Step Installation

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd Mess_around
```

#### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Verify Activation:**
```bash
# You should see (venv) at the start of your command prompt
which python  # macOS/Linux
where python  # Windows
```

#### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Verify Installation:**
```bash
pip list
# Should show: Flask, SQLAlchemy, pandas, matplotlib, pytest, etc.
```

#### 4. Verify Project Structure

```bash
# Ensure all directories exist
ls -la  # macOS/Linux
dir     # Windows

# Expected structure:
# - src/
# - tests/
# - data/
# - templates/
# - static/
# - Documentation/
# - main.py
# - requirements.txt
```

---

## Database Initialization

### Option 1: Automatic Initialization (Recommended)

The application automatically initializes the database on first run:

```bash
python main.py
```

**What Happens:**
1. Checks if `immunisation_data.db` exists
2. If not, runs `create_database.py` automatically
3. Loads all CSV files from `data/` directory
4. Creates all tables and relationships
5. Starts Flask web server

**Expected Output:**
```
Database not found. Creating and loading data...
Loading reference data...
Loading national coverage data...
Loading local authority data...
Loading regional time series...
Loading England time series...
Loading special programs data...
Database created and populated successfully!
 * Running on http://127.0.0.1:5000
```

### Option 2: Manual Database Creation

If you need to rebuild the database:

```bash
# Delete existing database (if any)
rm immunisation_data.db  # macOS/Linux
del immunisation_data.db  # Windows

# Create fresh database
python create_database.py
```

**Verify Database Creation:**
```bash
# Check file exists and has reasonable size
ls -lh immunisation_data.db  # macOS/Linux
dir immunisation_data.db     # Windows

# Should be several MB in size
```

### Data Files Required

**Location:** `data/` directory

**Required Files:**
1. `reference_data.csv` - Vaccines, areas, cohorts, years
2. `Table 1 - UK coverage by country.csv` - National data
3. `Table 4 - Local authority data for UTLA.csv` - UTLA data
4. `Table 5 - HepB and BCG.csv` - Special programs
5. `Table 6 - Regional time series.csv` - Regional trends
6. `Table 7 - England time series.csv` - Historical England data

**Data Validation:**
```bash
# Check all required files exist
ls data/*.csv  # macOS/Linux
dir data\*.csv # Windows
```

---

## Running the Application

### Development Mode

**Start the Application:**
```bash
python main.py
```

**Expected Behavior:**
- Web server starts on port 5000
- Browser automatically opens to http://localhost:5000
- Console shows Flask startup messages

**Manual Browser Access:**
```
http://localhost:5000
```

### Command Line Options

```bash
# Default: Development mode, port 5000
python main.py

# Specify custom port (not currently supported, requires code change)
# Edit main.py to change: app.run(debug=True, port=8080)
```

### Development Server Features

**Automatic Reloading:**
- Flask detects code changes
- Server automatically restarts
- No need to manually restart

**Debug Mode:**
- Detailed error messages
- Interactive debugger in browser
- Stack traces visible

**Warning:** Never use development server in production!

---

## Testing Deployment

### Running Tests

**Full Test Suite:**
```bash
pytest tests/ -v
```

**Expected Output:**
```
======================== test session starts ========================
tests/layer0_data_ingestion/test_csv_cleaner.py::test_... PASSED
tests/layer1_database/test_database.py::test_... PASSED
tests/layer2_business_logic/test_crud.py::test_... PASSED
tests/layer3_presentation/test_flask_app.py::test_... PASSED
...
======================== 324 passed in 7.23s ========================
```

**Quick Smoke Test:**
```bash
# Test each layer separately
pytest tests/layer0_data_ingestion/ -v  # Data loading
pytest tests/layer1_database/ -v        # Database layer
pytest tests/layer2_business_logic/ -v  # Business logic
pytest tests/layer3_presentation/ -v    # API endpoints
```

**Test with Coverage:**
```bash
pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
```

**View Coverage Report:**
```bash
# Windows
start htmlcov/index.html

# macOS
open htmlcov/index.html

# Linux
xdg-open htmlcov/index.html
```

### Integration Testing

**Test API Endpoints:**
```bash
# Ensure app is running first (python main.py)

# Test vaccines endpoint
curl http://localhost:5000/api/crud/vaccines

# Test areas endpoint
curl http://localhost:5000/api/areas

# Test table endpoint
curl -X POST http://localhost:5000/api/tables/table1 \
  -H "Content-Type: application/json" \
  -d '{"cohort_name": "24 months", "year": 2024}'
```

**Expected Responses:**
- 200 OK status codes
- Valid JSON responses
- Correct data structure

---

## Production Deployment

### Production Checklist

**Before Deployment:**
- [ ] All tests passing (324/324)
- [ ] Code coverage acceptable (>70%)
- [ ] Security tests passing
- [ ] Dependencies documented
- [ ] Environment variables configured
- [ ] Production database configured
- [ ] Secrets not in code
- [ ] Logging configured
- [ ] Backup strategy implemented
- [ ] Monitoring set up

### Production WSGI Server

**Option 1: Gunicorn (Linux/macOS)**

Install:
```bash
pip install gunicorn
```

Run:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 main:app

# -w 4: 4 worker processes
# -b 0.0.0.0:8000: Bind to all interfaces, port 8000
```

Configuration file (`gunicorn_config.py`):
```python
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 120
keepalive = 5

# Logging
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"

# Security
limit_request_line = 4096
limit_request_fields = 100
```

Run with config:
```bash
gunicorn -c gunicorn_config.py main:app
```

**Option 2: uWSGI**

Install:
```bash
pip install uwsgi
```

Configuration file (`uwsgi.ini`):
```ini
[uwsgi]
module = main:app
master = true
processes = 4
socket = 0.0.0.0:8000
chmod-socket = 660
vacuum = true
die-on-term = true

# Logging
logto = logs/uwsgi.log
```

Run:
```bash
uwsgi --ini uwsgi.ini
```

**Option 3: Waitress (Windows/Cross-platform)**

Install:
```bash
pip install waitress
```

Run:
```python
# In main.py, replace app.run() with:
from waitress import serve
serve(app, host='0.0.0.0', port=8000)
```

### Reverse Proxy Configuration

**Nginx Configuration:**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files
    location /static {
        alias /path/to/Mess_around/static;
        expires 30d;
    }

    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
}
```

**Apache Configuration:**

```apache
<VirtualHost *:80>
    ServerName your-domain.com

    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/

    # Security headers
    Header always set X-Content-Type-Options "nosniff"
    Header always set X-Frame-Options "DENY"
    Header always set X-XSS-Protection "1; mode=block"

    # Rate limiting (requires mod_ratelimit)
    <Location />
        SetOutputFilter RATE_LIMIT
        SetEnv rate-limit 400
    </Location>
</VirtualHost>
```

### HTTPS/SSL Configuration

**Using Let's Encrypt (Certbot):**

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

**Nginx HTTPS Configuration:**
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # ... rest of configuration
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

---

## Configuration Management

### Environment Variables

**Create `.env` file:**
```bash
# Database
DATABASE_URL=sqlite:///immunisation_data.db

# Flask
FLASK_ENV=production
FLASK_SECRET_KEY=your-secret-key-here

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Security
MAX_CONTENT_LENGTH=16777216  # 16MB
```

**Load in Application:**
```python
# In main.py or config.py
import os
from dotenv import load_dotenv

load_dotenv()

app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH'))
```

**Install python-dotenv:**
```bash
pip install python-dotenv
```

### Configuration Files

**Development Config (`config_dev.py`):**
```python
DEBUG = True
TESTING = False
DATABASE_URL = 'sqlite:///immunisation_data.db'
LOG_LEVEL = 'DEBUG'
```

**Production Config (`config_prod.py`):**
```python
DEBUG = False
TESTING = False
DATABASE_URL = os.getenv('DATABASE_URL')
LOG_LEVEL = 'INFO'
SECRET_KEY = os.getenv('SECRET_KEY')
```

**Load Config:**
```python
# In main.py
import os
env = os.getenv('FLASK_ENV', 'development')

if env == 'production':
    app.config.from_object('config_prod')
else:
    app.config.from_object('config_dev')
```

---

## Monitoring and Logging

### Application Logging

**Configure Logging:**
```python
import logging
from logging.handlers import RotatingFileHandler

# Create logs directory
os.makedirs('logs', exist_ok=True)

# Configure logger
handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=10485760,  # 10MB
    backupCount=10
)
handler.setFormatter(logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
))

app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)
```

**Log Locations:**
- Application logs: `logs/app.log`
- Activity logs: `logs/user_actions.log`
- Error logs: `logs/error.log`
- Access logs: `logs/access.log` (if using Gunicorn/uWSGI)

### Log Monitoring

**View Real-Time Logs:**
```bash
# Application logs
tail -f logs/app.log

# Activity logs
tail -f logs/user_actions.log

# Error logs only
tail -f logs/error.log | grep ERROR
```

**Log Rotation:**
```bash
# Configure logrotate (Linux)
sudo nano /etc/logrotate.d/immunisation-app

# Content:
/path/to/Mess_around/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
}
```

### Performance Monitoring

**Basic Monitoring Script:**
```python
# monitor.py
import psutil
import time

while True:
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    print(f"CPU: {cpu}% | Memory: {memory}% | Disk: {disk}%")

    if cpu > 80 or memory > 80:
        print("WARNING: High resource usage!")

    time.sleep(60)
```

**Run Monitoring:**
```bash
python monitor.py &
```

---

## Database Management

### Backup Strategy

**Automatic Backup Script:**
```bash
#!/bin/bash
# backup_db.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups"
DB_FILE="immunisation_data.db"

mkdir -p $BACKUP_DIR

# Create backup
cp $DB_FILE "$BACKUP_DIR/immunisation_data_$DATE.db"

# Keep only last 30 days
find $BACKUP_DIR -name "*.db" -mtime +30 -delete

echo "Backup completed: $DATE"
```

**Schedule with Cron:**
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /path/to/backup_db.sh >> logs/backup.log 2>&1
```

**Manual Backup:**
```bash
# Create backup
cp immunisation_data.db immunisation_data_backup_$(date +%Y%m%d).db

# Restore from backup
cp immunisation_data_backup_20241210.db immunisation_data.db
```

### Database Migrations

**For Future Schema Changes:**

```bash
# Install Alembic
pip install alembic

# Initialize migrations
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Add new table"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

---

## Troubleshooting

### Common Issues

**1. Database Locked Error**
```
Error: database is locked
```

**Solution:**
```bash
# Check for other processes using database
lsof immunisation_data.db  # macOS/Linux

# Close Flask app properly
# Restart application
```

**2. Port Already in Use**
```
Error: Address already in use
```

**Solution:**
```bash
# Find process using port 5000
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows

# Kill process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

**3. Module Import Errors**
```
ImportError: No module named 'flask'
```

**Solution:**
```bash
# Verify virtual environment is activated
which python

# Reinstall dependencies
pip install -r requirements.txt
```

**4. Database Not Found**
```
Error: no such table: vaccines
```

**Solution:**
```bash
# Recreate database
rm immunisation_data.db
python create_database.py
```

**5. CSV File Not Found**
```
FileNotFoundError: data/reference_data.csv
```

**Solution:**
```bash
# Verify data files exist
ls data/*.csv

# Check file permissions
chmod 644 data/*.csv  # macOS/Linux
```

### Performance Issues

**Slow Queries:**
```python
# Enable query logging
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

**Memory Usage:**
```bash
# Monitor Python process
top -p $(pgrep -f "python main.py")

# Check database size
du -h immunisation_data.db
```

### Debugging Tips

**Enable Debug Mode:**
```python
# In main.py
app.run(debug=True)
```

**Check Application Health:**
```bash
# Test basic connectivity
curl http://localhost:5000/api/crud/vaccines

# Check response time
time curl http://localhost:5000/api/crud/vaccines
```

**Verbose Logging:**
```python
# In main.py
import logging
app.logger.setLevel(logging.DEBUG)
```

---

## Health Checks

### Endpoint Health Check

```python
# Add to flask_app.py
@app.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Test database connection
        vaccine_count = session.query(Vaccine).count()
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'vaccine_count': vaccine_count
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500
```

**Test Health Check:**
```bash
curl http://localhost:5000/health
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] All tests passing
- [ ] Code coverage > 70%
- [ ] Security tests passing
- [ ] Dependencies documented
- [ ] Configuration files created
- [ ] Environment variables set
- [ ] Database backup created
- [ ] Logging configured

### Deployment

- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Database initialized
- [ ] Application starts successfully
- [ ] Health checks passing
- [ ] API endpoints responding
- [ ] Static files serving

### Post-Deployment

- [ ] Monitor logs for errors
- [ ] Test all major functionality
- [ ] Verify performance metrics
- [ ] Check resource usage
- [ ] Set up monitoring alerts
- [ ] Document deployment date
- [ ] Create backup schedule

---

## Support and Maintenance

### Regular Maintenance Tasks

**Daily:**
- Monitor application logs
- Check health endpoint
- Review error rates

**Weekly:**
- Review performance metrics
- Check disk space
- Verify backups

**Monthly:**
- Update dependencies
- Review security advisories
- Performance optimization
- Database optimization

**Quarterly:**
- Security audit
- Code review
- Documentation updates
- Disaster recovery test

---

## Resources

**Documentation:**
- [Flask Deployment](https://flask.palletsprojects.com/en/3.0.x/deploying/)
- [Gunicorn Docs](https://docs.gunicorn.org/)
- [Nginx Configuration](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/)

**Tools:**
- [Certbot](https://certbot.eff.org/)
- [PM2 Process Manager](https://pm2.keymetrics.io/)
- [Docker](https://www.docker.com/)

---

**Version:** 1.0.0
**Last Updated:** December 2024
**Deployment Status:** ✅ Ready for Production
