# CI/CD Deployment Guide - SabPaisa Reports API

**Date**: October 15, 2025
**Purpose**: Complete guide for setting up CI/CD pipelines for Staging and Production deployment

---

## 📋 Table of Contents

1. [Git Branch Strategy](#git-branch-strategy)
2. [Environment Setup](#environment-setup)
3. [GitHub Actions Pipeline](#github-actions-pipeline)
4. [Deployment Architecture](#deployment-architecture)
5. [Database Migration Strategy](#database-migration-strategy)
6. [Security Considerations](#security-considerations)
7. [Rollback Strategy](#rollback-strategy)
8. [Monitoring & Health Checks](#monitoring--health-checks)

---

## 🌳 Git Branch Strategy

### Branch Structure

```
main (production)
  ↑
  |
staging (staging environment)
  ↑
  |
develop (development - integration)
  ↑
  |
feature/* (feature branches)
```

### Branch Policies

#### 1. **main** (Production)
- **Protected**: Yes
- **Direct Push**: ❌ Not allowed
- **Merge From**: staging only
- **Requires**: Pull Request + 2 approvals + All tests passing
- **Auto-Deploy**: Production server
- **Tag**: Create git tag on every merge (v1.0.0, v1.0.1, etc.)

#### 2. **staging** (Staging Environment)
- **Protected**: Yes
- **Direct Push**: ❌ Not allowed
- **Merge From**: develop only
- **Requires**: Pull Request + 1 approval + All tests passing
- **Auto-Deploy**: Staging server
- **Purpose**: QA testing, client review

#### 3. **develop** (Development)
- **Protected**: Yes
- **Direct Push**: Limited (only for hotfixes)
- **Merge From**: feature/* branches
- **Requires**: Pull Request + Tests passing
- **Auto-Deploy**: Dev server (optional)
- **Purpose**: Integration testing

#### 4. **feature/*** (Feature Branches)
- **Protected**: No
- **Created From**: develop
- **Naming**: feature/payment-mode-filter, feature/audit-reports, etc.
- **Lifetime**: Delete after merge to develop

---

## 🔧 Environment Setup

### Environment Variables Structure

Create separate `.env` files for each environment (NEVER commit these to git):

#### Development (.env.development)
```ini
ENVIRONMENT=development
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_PRIMARY_NAME=sabpaisa_dev
DB_PRIMARY_USER=dev_user
DB_PRIMARY_PASSWORD=dev_password
DB_PRIMARY_HOST=localhost
DB_PRIMARY_PORT=3306

SECRET_KEY=dev-secret-key-change-in-production
```

#### Staging (.env.staging)
```ini
ENVIRONMENT=staging
DEBUG=False
ALLOWED_HOSTS=staging.sabpaisa.com,staging-api.sabpaisa.com

DB_PRIMARY_NAME=sabpaisa_staging
DB_PRIMARY_USER=staging_user
DB_PRIMARY_PASSWORD=STAGING_SECURE_PASSWORD
DB_PRIMARY_HOST=staging-db.sabpaisa.com
DB_PRIMARY_PORT=3306

SECRET_KEY=staging-secret-key-very-secure-random-string
SENTRY_DSN=https://your-sentry-dsn-staging
```

#### Production (.env.production)
```ini
ENVIRONMENT=production
DEBUG=False
ALLOWED_HOSTS=api.sabpaisa.com,sabpaisa.com

DB_PRIMARY_NAME=sabpaisa_production
DB_PRIMARY_USER=prod_user
DB_PRIMARY_PASSWORD=PRODUCTION_SUPER_SECURE_PASSWORD
DB_PRIMARY_HOST=prod-db.sabpaisa.com
DB_PRIMARY_PORT=3306

SECRET_KEY=production-secret-key-extremely-secure-random-string-256-chars
SENTRY_DSN=https://your-sentry-dsn-production
```

### Store Secrets in GitHub Secrets

Go to: **GitHub Repository → Settings → Secrets and variables → Actions**

Add these secrets:

**Staging Secrets:**
- `STAGING_DB_HOST`
- `STAGING_DB_NAME`
- `STAGING_DB_USER`
- `STAGING_DB_PASSWORD`
- `STAGING_SECRET_KEY`
- `STAGING_SERVER_HOST`
- `STAGING_SERVER_USER`
- `STAGING_SSH_KEY`

**Production Secrets:**
- `PROD_DB_HOST`
- `PROD_DB_NAME`
- `PROD_DB_USER`
- `PROD_DB_PASSWORD`
- `PROD_SECRET_KEY`
- `PROD_SERVER_HOST`
- `PROD_SERVER_USER`
- `PROD_SSH_KEY`

---

## 🚀 GitHub Actions Pipeline

### Directory Structure

Create these files in your repository:

```
.github/
  workflows/
    ├── test.yml                    # Run tests on every PR
    ├── deploy-staging.yml          # Deploy to staging
    ├── deploy-production.yml       # Deploy to production
    └── rollback.yml                # Rollback workflow
```

### 1. Test Workflow (.github/workflows/test.yml)

```yaml
name: Run Tests

on:
  pull_request:
    branches: [develop, staging, main]
  push:
    branches: [develop, staging, main]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: test_password
          MYSQL_DATABASE: test_db
        ports:
          - 3306:3306
        options: >-
          --health-cmd="mysqladmin ping"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=3

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Cache pip dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-django pytest-cov

      - name: Create test .env file
        run: |
          echo "DEBUG=True" > .env
          echo "SECRET_KEY=test-secret-key-for-ci" >> .env
          echo "DB_PRIMARY_NAME=test_db" >> .env
          echo "DB_PRIMARY_USER=root" >> .env
          echo "DB_PRIMARY_PASSWORD=test_password" >> .env
          echo "DB_PRIMARY_HOST=127.0.0.1" >> .env
          echo "DB_PRIMARY_PORT=3306" >> .env

      - name: Run migrations
        run: |
          python manage.py migrate --noinput

      - name: Run tests
        run: |
          pytest --cov=apps --cov-report=xml --cov-report=html

      - name: Upload coverage reports
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: false

      - name: Check code quality (flake8)
        run: |
          pip install flake8
          flake8 apps/ config/ --max-line-length=120 --exclude=migrations
        continue-on-error: true

      - name: Security check (bandit)
        run: |
          pip install bandit
          bandit -r apps/ config/ -f json -o bandit-report.json
        continue-on-error: true
```

### 2. Deploy to Staging (.github/workflows/deploy-staging.yml)

```yaml
name: Deploy to Staging

on:
  push:
    branches:
      - staging

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: staging

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup SSH
        uses: webfactory/ssh-agent@v0.7.0
        with:
          ssh-private-key: ${{ secrets.STAGING_SSH_KEY }}

      - name: Create .env file
        run: |
          cat > .env << EOF
          ENVIRONMENT=staging
          DEBUG=False
          ALLOWED_HOSTS=${{ secrets.STAGING_ALLOWED_HOSTS }}
          DB_PRIMARY_NAME=${{ secrets.STAGING_DB_NAME }}
          DB_PRIMARY_USER=${{ secrets.STAGING_DB_USER }}
          DB_PRIMARY_PASSWORD=${{ secrets.STAGING_DB_PASSWORD }}
          DB_PRIMARY_HOST=${{ secrets.STAGING_DB_HOST }}
          DB_PRIMARY_PORT=3306
          SECRET_KEY=${{ secrets.STAGING_SECRET_KEY }}
          JWT_ACCESS_TOKEN_LIFETIME=1440
          JWT_REFRESH_TOKEN_LIFETIME=10080
          EOF

      - name: Create deployment package
        run: |
          tar -czf deploy.tar.gz \
            --exclude='.git' \
            --exclude='__pycache__' \
            --exclude='*.pyc' \
            --exclude='.vscode' \
            --exclude='logs' \
            --exclude='exports' \
            --exclude='media' \
            .

      - name: Copy files to server
        run: |
          scp -o StrictHostKeyChecking=no deploy.tar.gz \
            ${{ secrets.STAGING_SERVER_USER }}@${{ secrets.STAGING_SERVER_HOST }}:/tmp/

      - name: Deploy on server
        run: |
          ssh -o StrictHostKeyChecking=no \
            ${{ secrets.STAGING_SERVER_USER }}@${{ secrets.STAGING_SERVER_HOST }} << 'ENDSSH'

          # Backup current deployment
          if [ -d /var/www/sabpaisa-api ]; then
            sudo cp -r /var/www/sabpaisa-api /var/www/sabpaisa-api-backup-$(date +%Y%m%d-%H%M%S)
          fi

          # Extract new deployment
          sudo mkdir -p /var/www/sabpaisa-api
          sudo tar -xzf /tmp/deploy.tar.gz -C /var/www/sabpaisa-api
          cd /var/www/sabpaisa-api

          # Create virtual environment if not exists
          if [ ! -d "venv" ]; then
            python3 -m venv venv
          fi

          # Activate virtual environment and install dependencies
          source venv/bin/activate
          pip install --upgrade pip
          pip install -r requirements.txt

          # Run migrations
          python manage.py migrate --noinput

          # Collect static files
          python manage.py collectstatic --noinput

          # Restart services
          sudo systemctl restart gunicorn-sabpaisa
          sudo systemctl restart nginx

          # Health check
          sleep 5
          curl -f http://localhost:8000/api/v1/system/health/ || exit 1

          echo "Deployment successful!"
          ENDSSH

      - name: Send Slack notification
        if: always()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'Staging Deployment: ${{ job.status }}'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}

      - name: Create deployment tag
        run: |
          git tag -a "staging-$(date +%Y%m%d-%H%M%S)" -m "Staging deployment"
          git push origin --tags
```

### 3. Deploy to Production (.github/workflows/deploy-production.yml)

```yaml
name: Deploy to Production

on:
  push:
    branches:
      - main
  workflow_dispatch:  # Allow manual trigger

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://api.sabpaisa.com

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Run tests before deployment
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-django
          # Run critical tests only
          pytest tests/critical/ -v

      - name: Setup SSH
        uses: webfactory/ssh-agent@v0.7.0
        with:
          ssh-private-key: ${{ secrets.PROD_SSH_KEY }}

      - name: Create .env file
        run: |
          cat > .env << EOF
          ENVIRONMENT=production
          DEBUG=False
          ALLOWED_HOSTS=${{ secrets.PROD_ALLOWED_HOSTS }}
          DB_PRIMARY_NAME=${{ secrets.PROD_DB_NAME }}
          DB_PRIMARY_USER=${{ secrets.PROD_DB_USER }}
          DB_PRIMARY_PASSWORD=${{ secrets.PROD_DB_PASSWORD }}
          DB_PRIMARY_HOST=${{ secrets.PROD_DB_HOST }}
          DB_PRIMARY_PORT=3306
          SECRET_KEY=${{ secrets.PROD_SECRET_KEY }}
          JWT_ACCESS_TOKEN_LIFETIME=1440
          JWT_REFRESH_TOKEN_LIFETIME=10080
          SENTRY_DSN=${{ secrets.PROD_SENTRY_DSN }}
          EOF

      - name: Create deployment package
        run: |
          tar -czf deploy.tar.gz \
            --exclude='.git' \
            --exclude='__pycache__' \
            --exclude='*.pyc' \
            --exclude='.vscode' \
            --exclude='logs' \
            --exclude='exports' \
            --exclude='media' \
            .

      - name: Backup production database
        run: |
          ssh -o StrictHostKeyChecking=no \
            ${{ secrets.PROD_SERVER_USER }}@${{ secrets.PROD_SERVER_HOST }} \
            "mysqldump -h ${{ secrets.PROD_DB_HOST }} \
             -u ${{ secrets.PROD_DB_USER }} \
             -p'${{ secrets.PROD_DB_PASSWORD }}' \
             ${{ secrets.PROD_DB_NAME }} | \
             gzip > /backups/db-backup-\$(date +%Y%m%d-%H%M%S).sql.gz"

      - name: Copy files to server
        run: |
          scp -o StrictHostKeyChecking=no deploy.tar.gz \
            ${{ secrets.PROD_SERVER_USER }}@${{ secrets.PROD_SERVER_HOST }}:/tmp/

      - name: Deploy on server (Blue-Green)
        run: |
          ssh -o StrictHostKeyChecking=no \
            ${{ secrets.PROD_SERVER_USER }}@${{ secrets.PROD_SERVER_HOST }} << 'ENDSSH'

          # Blue-Green deployment
          BLUE_DIR="/var/www/sabpaisa-api-blue"
          GREEN_DIR="/var/www/sabpaisa-api-green"
          CURRENT_LINK="/var/www/sabpaisa-api-current"

          # Determine which is currently active
          if [ "$(readlink $CURRENT_LINK)" = "$BLUE_DIR" ]; then
            NEW_DIR="$GREEN_DIR"
            OLD_DIR="$BLUE_DIR"
          else
            NEW_DIR="$BLUE_DIR"
            OLD_DIR="$GREEN_DIR"
          fi

          echo "Deploying to: $NEW_DIR"

          # Extract to new directory
          sudo mkdir -p $NEW_DIR
          sudo tar -xzf /tmp/deploy.tar.gz -C $NEW_DIR
          cd $NEW_DIR

          # Setup virtual environment
          python3 -m venv venv
          source venv/bin/activate
          pip install --upgrade pip
          pip install -r requirements.txt

          # Run migrations (on current DB)
          python manage.py migrate --noinput

          # Collect static files
          python manage.py collectstatic --noinput

          # Test the new deployment
          python manage.py check --deploy

          # Switch to new deployment
          sudo ln -sfn $NEW_DIR $CURRENT_LINK

          # Reload services
          sudo systemctl reload gunicorn-sabpaisa

          # Health check
          sleep 5
          for i in {1..5}; do
            if curl -f http://localhost:8000/api/v1/system/health/; then
              echo "Health check passed!"
              break
            fi
            if [ $i -eq 5 ]; then
              echo "Health check failed! Rolling back..."
              sudo ln -sfn $OLD_DIR $CURRENT_LINK
              sudo systemctl reload gunicorn-sabpaisa
              exit 1
            fi
            sleep 2
          done

          echo "Production deployment successful!"
          ENDSSH

      - name: Create release tag
        run: |
          git tag -a "v$(date +%Y.%m.%d-%H%M)" -m "Production release $(date)"
          git push origin --tags

      - name: Send notifications
        if: always()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: '🚀 Production Deployment: ${{ job.status }}'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}

      - name: Send email notification
        if: success()
        uses: dawidd6/action-send-mail@v3
        with:
          server_address: smtp.gmail.com
          server_port: 465
          username: ${{ secrets.EMAIL_USERNAME }}
          password: ${{ secrets.EMAIL_PASSWORD }}
          subject: Production Deployment Successful
          to: tech-team@sabpaisa.com
          from: DevOps <devops@sabpaisa.com>
          body: |
            Production deployment completed successfully!

            Branch: ${{ github.ref }}
            Commit: ${{ github.sha }}
            Deployed by: ${{ github.actor }}
            Time: $(date)
```

### 4. Rollback Workflow (.github/workflows/rollback.yml)

```yaml
name: Rollback Deployment

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to rollback'
        required: true
        type: choice
        options:
          - staging
          - production
      backup_timestamp:
        description: 'Backup timestamp (YYYYMMDD-HHMMSS) or "previous"'
        required: true
        default: 'previous'

jobs:
  rollback:
    runs-on: ubuntu-latest

    steps:
      - name: Setup SSH
        uses: webfactory/ssh-agent@v0.7.0
        with:
          ssh-private-key: ${{ inputs.environment == 'production' && secrets.PROD_SSH_KEY || secrets.STAGING_SSH_KEY }}

      - name: Rollback deployment
        run: |
          SERVER_USER=${{ inputs.environment == 'production' && secrets.PROD_SERVER_USER || secrets.STAGING_SERVER_USER }}
          SERVER_HOST=${{ inputs.environment == 'production' && secrets.PROD_SERVER_HOST || secrets.STAGING_SERVER_HOST }}

          ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_HOST << 'ENDSSH'

          CURRENT_LINK="/var/www/sabpaisa-api-current"
          BLUE_DIR="/var/www/sabpaisa-api-blue"
          GREEN_DIR="/var/www/sabpaisa-api-green"

          # Switch to other deployment
          if [ "$(readlink $CURRENT_LINK)" = "$BLUE_DIR" ]; then
            sudo ln -sfn $GREEN_DIR $CURRENT_LINK
          else
            sudo ln -sfn $BLUE_DIR $CURRENT_LINK
          fi

          # Reload services
          sudo systemctl reload gunicorn-sabpaisa

          echo "Rollback completed!"
          ENDSSH

      - name: Send notification
        uses: 8398a7/action-slack@v3
        with:
          status: 'success'
          text: '⚠️ Rollback performed on ${{ inputs.environment }}'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## 🏗️ Deployment Architecture

### Server Setup Requirements

#### Staging Server
- **OS**: Ubuntu 22.04 LTS
- **Python**: 3.12+
- **Web Server**: Nginx
- **Application Server**: Gunicorn
- **Database**: MySQL 8.0 (separate server)
- **Cache**: Redis (optional)
- **Resources**: 4 CPU, 8GB RAM, 100GB SSD

#### Production Server (Recommended)
- **OS**: Ubuntu 22.04 LTS
- **Python**: 3.12+
- **Web Server**: Nginx (with SSL)
- **Application Server**: Gunicorn (4-8 workers)
- **Database**: MySQL 8.0 (RDS or separate server with replication)
- **Cache**: Redis cluster
- **Load Balancer**: AWS ELB / Nginx
- **Resources**: 8 CPU, 16GB RAM, 200GB SSD
- **Backup**: Daily automated backups
- **Monitoring**: Sentry, DataDog, or New Relic

### Service Configuration Files

#### Gunicorn Service (/etc/systemd/system/gunicorn-sabpaisa.service)

```ini
[Unit]
Description=Gunicorn daemon for SabPaisa Reports API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/sabpaisa-api-current
Environment="PATH=/var/www/sabpaisa-api-current/venv/bin"
ExecStart=/var/www/sabpaisa-api-current/venv/bin/gunicorn \
    --workers 4 \
    --bind unix:/run/gunicorn-sabpaisa.sock \
    --timeout 120 \
    --access-logfile /var/log/gunicorn/access.log \
    --error-logfile /var/log/gunicorn/error.log \
    --log-level info \
    config.wsgi:application

[Install]
WantedBy=multi-user.target
```

#### Nginx Configuration (/etc/nginx/sites-available/sabpaisa-api)

```nginx
upstream sabpaisa_api {
    server unix:/run/gunicorn-sabpaisa.sock fail_timeout=0;
}

server {
    listen 80;
    server_name api.sabpaisa.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.sabpaisa.com;

    ssl_certificate /etc/letsencrypt/live/api.sabpaisa.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.sabpaisa.com/privkey.pem;

    client_max_body_size 50M;

    access_log /var/log/nginx/sabpaisa-api-access.log;
    error_log /var/log/nginx/sabpaisa-api-error.log;

    location /static/ {
        alias /var/www/sabpaisa-api-current/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/sabpaisa-api-current/media/;
        expires 7d;
    }

    location / {
        proxy_pass http://sabpaisa_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;

        # Timeouts
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
}
```

---

## 🗄️ Database Migration Strategy

### Migration Workflow

1. **Development**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   git add apps/*/migrations/
   git commit -m "Add migration for [feature]"
   ```

2. **Staging** (Automatic via CI/CD)
   - Migrations run automatically during deployment
   - Test thoroughly on staging before production

3. **Production** (Automatic with backup)
   - Database backup taken before deployment
   - Migrations run automatically
   - If migration fails, deployment stops (rollback)

### Zero-Downtime Migrations

For production, follow these best practices:

```python
# Good - Backward compatible
class Migration(migrations.Migration):
    operations = [
        # 1. Add new field as nullable
        migrations.AddField(
            model_name='transaction',
            name='new_field',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]

# Later migration - Make it required after data backfill
class Migration(migrations.Migration):
    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='new_field',
            field=models.CharField(max_length=100),
        ),
    ]
```

---

## 🔒 Security Considerations

### Pre-Deployment Security Checklist

- [ ] All secrets stored in GitHub Secrets (not in code)
- [ ] `.env` files excluded from git
- [ ] DEBUG=False in production
- [ ] ALLOWED_HOSTS properly configured
- [ ] SECRET_KEY is strong and unique per environment
- [ ] Database passwords are strong and unique
- [ ] SSH keys are passwordless for automation
- [ ] SSL certificates are valid
- [ ] Security headers configured in Nginx
- [ ] CORS settings properly configured
- [ ] Rate limiting enabled
- [ ] SQL injection protection (Django ORM used correctly)
- [ ] XSS protection enabled
- [ ] CSRF protection enabled

### Post-Deployment Security

- [ ] Run security scan (bandit, safety)
- [ ] Check for dependency vulnerabilities
- [ ] Monitor error logs for security issues
- [ ] Review access logs for suspicious activity
- [ ] Verify backup encryption

---

## 🔄 Rollback Strategy

### Automatic Rollback Triggers

1. **Health check failure** after deployment
2. **Critical error rate** spike (>10% in 5 minutes)
3. **Database migration failure**
4. **Service start failure**

### Manual Rollback Process

1. **Immediate** - Switch symlink (blue-green deployment)
   ```bash
   ln -sfn /var/www/sabpaisa-api-green /var/www/sabpaisa-api-current
   systemctl reload gunicorn-sabpaisa
   ```

2. **Database** - Restore from backup if needed
   ```bash
   mysql -u user -p database < backup.sql
   ```

3. **Notification** - Alert team via Slack/Email

---

## 📊 Monitoring & Health Checks

### Health Check Endpoints

Already implemented:
- `GET /api/v1/system/health/` - Overall health
- `GET /api/v1/system/metrics/` - System metrics
- `GET /api/v1/system/status/` - Detailed status
- `GET /api/v1/system/database-status/` - Database health

### Monitoring Tools to Integrate

1. **Sentry** - Error tracking
   ```python
   # config/settings.py
   import sentry_sdk

   if not DEBUG:
       sentry_sdk.init(
           dsn=config('SENTRY_DSN'),
           environment=config('ENVIRONMENT'),
       )
   ```

2. **New Relic / DataDog** - APM
3. **CloudWatch / Grafana** - Metrics & logs
4. **UptimeRobot** - Uptime monitoring

### Key Metrics to Monitor

- Response time (p50, p95, p99)
- Error rate (4xx, 5xx)
- Database query performance
- API endpoint availability
- Server CPU, Memory, Disk usage
- Active database connections
- Queue length (if using Celery)

---

## 📝 Deployment Checklist

### Before First Deployment

- [ ] Setup staging and production servers
- [ ] Install and configure Nginx, Gunicorn
- [ ] Setup MySQL databases (staging, production)
- [ ] Configure firewall rules
- [ ] Setup SSL certificates
- [ ] Create GitHub secrets
- [ ] Setup monitoring tools
- [ ] Configure backup automation
- [ ] Test SSH access from GitHub Actions
- [ ] Create deployment documentation

### For Each Deployment

- [ ] All tests passing
- [ ] Code review completed
- [ ] Database migrations reviewed
- [ ] .env.example updated if needed
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Staging deployment successful
- [ ] QA testing completed on staging
- [ ] Stakeholder approval (for production)
- [ ] Backup verified
- [ ] Off-hours deployment scheduled (production)

---

## 🎯 Quick Start Commands

### Setup GitHub Secrets
```bash
# Navigate to: GitHub Repo → Settings → Secrets and variables → Actions
# Add all required secrets listed in "Environment Setup" section
```

### Create Workflow Files
```bash
mkdir -p .github/workflows
# Copy the workflow YAML files provided above
```

### Test Workflow Locally (using act)
```bash
# Install act: https://github.com/nektos/act
act -j test
```

### Manual Deployment Trigger
```bash
# Go to: GitHub Repo → Actions → Deploy to Production → Run workflow
```

---

## 📞 Support & Troubleshooting

### Common Issues

1. **Deployment fails at migration**
   - Check database connectivity
   - Review migration logs
   - Rollback and fix migration

2. **Health check fails after deployment**
   - Check application logs: `/var/log/gunicorn/error.log`
   - Verify environment variables
   - Check database connection

3. **GitHub Actions timeout**
   - Increase timeout in workflow
   - Check server SSH connectivity
   - Review network/firewall rules

### Logs Locations

- **GitHub Actions**: GitHub Repo → Actions → Workflow run
- **Application**: `/var/log/gunicorn/error.log`
- **Nginx**: `/var/log/nginx/sabpaisa-api-error.log`
- **System**: `/var/log/syslog`

---

## ✅ Summary

### Deployment Flow

```
Developer Push → feature/branch
       ↓
   Pull Request → develop
       ↓
   CI Tests Run
       ↓
   Merge to develop
       ↓
   Pull Request → staging
       ↓
   Deploy to Staging (Auto)
       ↓
   QA Testing
       ↓
   Pull Request → main
       ↓
   Deploy to Production (Auto)
       ↓
   Monitoring & Alerts
```

### Next Steps

1. ✅ Push code to GitHub (with .gitignore)
2. ✅ Create branch structure (main, staging, develop)
3. ✅ Add GitHub secrets
4. ✅ Create workflow files
5. ✅ Setup staging server
6. ✅ Test staging deployment
7. ✅ Setup production server
8. ✅ Configure monitoring
9. ✅ Test production deployment
10. ✅ Document team process

---

**Document Version**: 1.0
**Last Updated**: October 15, 2025
**Status**: Ready for Implementation
