# Quick Start - CI/CD Setup

**Purpose**: Quick reference for setting up CI/CD pipelines

---

## 🚀 Immediate Actions (Before First Push)

### Step 1: Create .gitignore in Git Repository

Create this file: `D:\Hackathon-Project-new\RepositoryHackathonCode\sabpaisa-report-api\.gitignore`

Copy from: `D:\Hackathon-Project-new\Cleaned_SabPaisa_Report_Solution\sabpaisa-reports-api\.gitignore`

**OR** Create manually with this content:

```gitignore
# Python
__pycache__/
*.pyc
*.pyo
*.egg-info/

# Django
*.log
db.sqlite3
/media/
/staticfiles/

# CRITICAL - Never commit!
.env
.env.*
!.env.example

# Project specific
logs/
exports/
reports/

# IDEs
.vscode/
.idea/

# Testing
.pytest_cache/
```

---

### Step 2: Verify .env.example (Safe for Git)

Edit: `D:\Hackathon-Project-new\Cleaned_SabPaisa_Report_Solution\sabpaisa-reports-api\.env.example`

Make sure it has **placeholder** values only:

```ini
# Database Configuration
DB_PRIMARY_NAME=your_database_name_here
DB_PRIMARY_USER=your_mysql_username
DB_PRIMARY_PASSWORD=your_secure_password_here
DB_PRIMARY_HOST=localhost
DB_PRIMARY_PORT=3306

# Django Settings
DEBUG=False
SECRET_KEY=your-secret-key-change-this-to-random-50-char-string
ALLOWED_HOSTS=localhost,127.0.0.1

# JWT Token Configuration
JWT_ACCESS_TOKEN_LIFETIME=1440
JWT_REFRESH_TOKEN_LIFETIME=10080
```

---

### Step 3: Copy Files to Git Repository

**Copy these files/folders:**

```bash
# From: D:\Hackathon-Project-new\Cleaned_SabPaisa_Report_Solution\sabpaisa-reports-api
# To:   D:\Hackathon-Project-new\RepositoryHackathonCode\sabpaisa-report-api

✅ apps/                  (entire folder)
✅ config/                (entire folder)
✅ scripts/               (entire folder)
✅ static/                (entire folder)
✅ manage.py
✅ requirements.txt
✅ requirements_windows.txt
✅ .env.example           (SAFE - no real passwords)
✅ .gitignore             (MUST HAVE)
✅ run_server.py
✅ run_server_safe.py
✅ setup_test_users.py
✅ All *.md files         (documentation)
```

**DO NOT COPY:**
```
❌ .env                   (contains real passwords!)
❌ logs/
❌ exports/
❌ reports/
❌ media/
❌ __pycache__/
❌ *.pyc
❌ .vscode/
❌ .pytest_cache/
```

---

### Step 4: First Git Push

```bash
# Navigate to git repository
cd D:\Hackathon-Project-new\RepositoryHackathonCode\sabpaisa-report-api

# Verify .env is NOT there (should fail)
dir .env
# Expected: "File Not Found" ✅

# Check git status
git status

# Add all files
git add .

# Verify no sensitive files are staged
git status
# Make sure .env is NOT in the list!

# Commit
git commit -m "Initial commit: Django Reports API with audit compliance"

# Push to GitHub
git push origin main
```

---

## 🌳 Branch Structure Setup (After First Push)

### Create Branches on GitHub

```bash
# Create develop branch
git checkout -b develop
git push origin develop

# Create staging branch
git checkout -b staging
git push origin staging

# Go back to main
git checkout main
```

### Protect Branches on GitHub

Go to: **GitHub → Settings → Branches → Add rule**

**For `main` branch:**
- ✅ Require pull request reviews before merging (2 approvals)
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date
- ✅ Do not allow bypassing the above settings

**For `staging` branch:**
- ✅ Require pull request reviews before merging (1 approval)
- ✅ Require status checks to pass before merging

**For `develop` branch:**
- ✅ Require status checks to pass before merging

---

## 🔐 GitHub Secrets Setup (Required for CI/CD)

Go to: **GitHub → Settings → Secrets and variables → Actions → New repository secret**

### Add These Secrets:

#### Staging Secrets
```
STAGING_DB_HOST = staging-db.sabpaisa.com
STAGING_DB_NAME = sabpaisa_staging
STAGING_DB_USER = staging_user
STAGING_DB_PASSWORD = [your-staging-db-password]
STAGING_SECRET_KEY = [random-50-char-string]
STAGING_ALLOWED_HOSTS = staging.sabpaisa.com,staging-api.sabpaisa.com
STAGING_SERVER_HOST = [staging-server-ip]
STAGING_SERVER_USER = ubuntu
STAGING_SSH_KEY = [private-ssh-key-content]
```

#### Production Secrets
```
PROD_DB_HOST = prod-db.sabpaisa.com
PROD_DB_NAME = sabpaisa_production
PROD_DB_USER = prod_user
PROD_DB_PASSWORD = [your-production-db-password]
PROD_SECRET_KEY = [random-50-char-string]
PROD_ALLOWED_HOSTS = api.sabpaisa.com,sabpaisa.com
PROD_SERVER_HOST = [production-server-ip]
PROD_SERVER_USER = ubuntu
PROD_SSH_KEY = [private-ssh-key-content]
PROD_SENTRY_DSN = [sentry-dsn-if-using]
```

#### Notification Secrets (Optional)
```
SLACK_WEBHOOK = [slack-webhook-url]
EMAIL_USERNAME = [smtp-username]
EMAIL_PASSWORD = [smtp-password]
```

---

## 📁 Create GitHub Actions Workflows

### Create Folder Structure

In your git repository:
```bash
mkdir -p .github/workflows
cd .github/workflows
```

### Create 4 Workflow Files

Copy content from `CICD_DEPLOYMENT_GUIDE.md`:

1. **test.yml** - Runs tests on every PR
2. **deploy-staging.yml** - Auto-deploy to staging
3. **deploy-production.yml** - Auto-deploy to production
4. **rollback.yml** - Manual rollback workflow

After creating, commit and push:
```bash
git add .github/
git commit -m "Add CI/CD workflows"
git push origin main
```

---

## 🎯 Development Workflow (Daily Use)

### For New Features

```bash
# 1. Create feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/payment-mode-filter

# 2. Make changes, commit
git add .
git commit -m "Add payment mode filter improvements"
git push origin feature/payment-mode-filter

# 3. Create Pull Request on GitHub
# From: feature/payment-mode-filter → To: develop

# 4. After approval and merge, delete feature branch
git checkout develop
git pull origin develop
git branch -d feature/payment-mode-filter
```

### Deploy to Staging

```bash
# 1. Create PR from develop to staging
# GitHub: develop → staging

# 2. After merge, auto-deploys to staging server
# Monitor: GitHub → Actions

# 3. Test on staging: https://staging.sabpaisa.com
```

### Deploy to Production

```bash
# 1. Create PR from staging to main
# GitHub: staging → main

# 2. Get 2 approvals from team

# 3. After merge, auto-deploys to production
# Monitor: GitHub → Actions

# 4. Verify: https://api.sabpaisa.com/api/v1/system/health/
```

---

## ✅ Pre-Deployment Checklist

### Before Pushing to GitHub (First Time)

- [ ] .gitignore file exists in git repo
- [ ] .env file is NOT in git repo
- [ ] .env.example has placeholder values only
- [ ] All passwords removed from committed files
- [ ] SECRET_KEY in code is placeholder
- [ ] Documentation files included

### Before Each Deployment

- [ ] All tests passing locally
- [ ] Code reviewed by peer
- [ ] Database migrations tested
- [ ] .env.example updated if needed
- [ ] Changelog updated
- [ ] No console.log or debug prints
- [ ] No commented code blocks

### Before Production Deployment

- [ ] Staging deployment successful
- [ ] QA team tested on staging
- [ ] Stakeholder approval received
- [ ] Database backup verified
- [ ] Rollback plan ready
- [ ] Team notified of deployment time
- [ ] Off-hours deployment scheduled

---

## 🚨 Emergency Procedures

### If You Accidentally Pushed .env

```bash
# 1. IMMEDIATELY change all passwords
# 2. Change SECRET_KEY
# 3. Remove from git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

git push origin --force --all

# 4. Notify team
```

### If Deployment Fails

```bash
# Option 1: Automatic rollback (built into workflows)
# Health checks will auto-rollback on failure

# Option 2: Manual rollback
# GitHub → Actions → Rollback Deployment → Run workflow
# Select environment and backup timestamp

# Option 3: Server-level rollback
ssh user@server
ln -sfn /var/www/sabpaisa-api-[blue|green] /var/www/sabpaisa-api-current
systemctl reload gunicorn-sabpaisa
```

---

## 📊 Monitoring After Deployment

### Check These Immediately

1. **Health Check**: https://api.sabpaisa.com/api/v1/system/health/
2. **Application Logs**: `/var/log/gunicorn/error.log`
3. **Nginx Logs**: `/var/log/nginx/sabpaisa-api-error.log`
4. **Database**: Check connection and query performance
5. **Error Rate**: Monitor Sentry/error tracking

### Monitor For Next 24 Hours

- Response times (should be <500ms)
- Error rates (should be <1%)
- Database connections (no leaks)
- Memory usage (no leaks)
- Disk space

---

## 📞 Quick Reference Commands

### Git Commands
```bash
# Check current branch
git branch

# Switch branch
git checkout staging

# Pull latest
git pull origin main

# Check what will be committed
git status

# View commit history
git log --oneline -10
```

### Server Commands
```bash
# Check service status
sudo systemctl status gunicorn-sabpaisa

# View logs
sudo tail -f /var/log/gunicorn/error.log

# Restart service
sudo systemctl restart gunicorn-sabpaisa

# Check disk space
df -h

# Check memory
free -h
```

### Health Checks
```bash
# Application health
curl http://localhost:8000/api/v1/system/health/

# Database health
curl http://localhost:8000/api/v1/system/database-status/

# Full system status
curl http://localhost:8000/api/v1/system/status/
```

---

## 📝 Summary

### What You Have Now

1. ✅ Complete CI/CD pipeline workflows
2. ✅ Branch strategy (main, staging, develop)
3. ✅ Auto-deployment to staging and production
4. ✅ Automated testing on every PR
5. ✅ Blue-green deployment (zero downtime)
6. ✅ Automatic rollback on failure
7. ✅ Health checks and monitoring

### Next Steps (In Order)

1. **Today**: Push code to GitHub with .gitignore
2. **This Week**: Setup branches and branch protection
3. **Next Week**: Add GitHub secrets
4. **Next Week**: Create workflow files
5. **Next 2 Weeks**: Setup staging server
6. **Next 3 Weeks**: Test staging deployment
7. **Next Month**: Setup production server
8. **Next Month**: First production deployment

---

## 🎯 Contact Points

**For Questions:**
- CI/CD Issues: Check `CICD_DEPLOYMENT_GUIDE.md`
- Git Issues: Check `GITHUB_PUSH_GUIDE.md`
- Application Issues: Check `API_DOCUMENTATION.md`

**For Emergencies:**
- Production Down: Follow rollback procedure
- Security Incident: Change passwords, notify team
- Database Issue: Contact DBA immediately

---

**Document Version**: 1.0
**Last Updated**: October 15, 2025
**Status**: Ready to Use
