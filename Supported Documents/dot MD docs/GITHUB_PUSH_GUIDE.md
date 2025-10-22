# GitHub Push Guide - SabPaisa Reports API

**Date**: October 15, 2025
**Purpose**: Guide for pushing Django application to GitHub

---

## 🚨 CRITICAL: Files You MUST NOT Push

### ❌ NEVER push these files (contain sensitive data):

1. **`.env`** - Contains database passwords, secret keys
2. **`*.pyc`** - Python compiled files
3. **`__pycache__/`** - Python cache directories
4. **`*.log`** - Log files may contain sensitive data
5. **`logs/`** - Log directory
6. **`exports/`** - Exported reports (may contain customer data)
7. **`reports/`** - Generated reports
8. **`media/`** - Uploaded files
9. **`staticfiles/`** - Collected static files
10. **`.vscode/`** - VS Code settings (personal)
11. **`db.sqlite3`** - Database file (if using SQLite for testing)
12. **`.pytest_cache/`** - Test cache

---

## ✅ Files You MUST Push

### Essential Files:

1. **`manage.py`** - Django management script
2. **`requirements.txt`** - Python dependencies
3. **`requirements_windows.txt`** - Windows-specific requirements
4. **`.gitignore`** - Git ignore file (CRITICAL!)
5. **`.env.example`** - Template for environment variables (without real passwords)
6. **`README.md`** - Project documentation

### Application Code:

7. **`apps/`** - All your Django apps (transactions, settlements, etc.)
8. **`config/`** - Django configuration
9. **`scripts/`** - Utility scripts
10. **`static/`** - Static files (CSS, JS, images)

### Documentation Files:

11. **`API_DOCUMENTATION.md`**
12. **`FEATURE_ENHANCEMENTS_DOCUMENTATION.md`**
13. **`TESTING_GUIDE.md`**
14. **`JWT_TOKEN_UPDATE_SUMMARY.md`**
15. **`RBI_PCIDSS_AUDIT_COMPLIANCE_GUIDE.md`**
16. **`EXECUTIVE_SUMMARY_AUDIT_COMPLIANCE.md`**
17. **`AUDIT_QUICK_REFERENCE.md`**
18. **`AUDIT_BENEFITS_SIMPLE_GUIDE.md`**
19. **`PAYMENT_MODE_FILTER_FIX.md`**
20. **`GITHUB_PUSH_GUIDE.md`** (this file)

### Optional Scripts:

21. **`run_server.py`** - Server runner script
22. **`run_server_safe.py`** - Safe server runner
23. **`setup_test_users.py`** - Test user setup script
24. **`setup_vscode.py`** - VS Code setup script

---

## 📋 Step-by-Step Push Instructions

### Step 1: Create/Update .gitignore in Git Repository

```bash
cd D:\Hackathon-Project-new\RepositoryHackathonCode\sabpaisa-report-api
```

Create `.gitignore` file with this content:

```gitignore
# Python
*.py[cod]
*$py.class
*.so
__pycache__/
*.pyc
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
/media/
/staticfiles/
/static/collected/

# Environment variables (CRITICAL!)
.env
.env.local
.env.*.local

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Project specific
logs/
*.log
exports/
reports/
media/

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.mypy_cache/
.dmypy.json
dmypy.json

# Virtual Environment
venv/
env/
ENV/
env.bak/
venv.bak/

# Windows
Thumbs.db
ehthumbs.db
Desktop.ini

# Workspace files (optional - personal preference)
*.code-workspace

# Batch files for local setup (optional)
install_*.bat
verify_*.bat
```

---

### Step 2: Copy Files from Source to Git Repository

**From**: `D:\Hackathon-Project-new\Cleaned_SabPaisa_Report_Solution\sabpaisa-reports-api`
**To**: `D:\Hackathon-Project-new\RepositoryHackathonCode\sabpaisa-report-api`

#### Method 1: Manual Copy (Recommended for first time)

Copy these folders/files:
```
✅ apps/
✅ config/
✅ scripts/
✅ static/
✅ manage.py
✅ requirements.txt
✅ requirements_windows.txt
✅ .env.example
✅ .gitignore
✅ All documentation .md files
✅ run_server.py
✅ run_server_safe.py
✅ setup_test_users.py
✅ setup_vscode.py
```

**DO NOT COPY**:
```
❌ .env (contains passwords!)
❌ logs/
❌ exports/
❌ reports/
❌ media/
❌ staticfiles/
❌ __pycache__/
❌ *.pyc
❌ .vscode/
❌ .pytest_cache/
❌ *.log
```

#### Method 2: Using Command Line (Faster)

```bash
# Navigate to source directory
cd D:\Hackathon-Project-new\Cleaned_SabPaisa_Report_Solution\sabpaisa-reports-api

# Copy essential files (PowerShell)
xcopy /E /I /Y apps D:\Hackathon-Project-new\RepositoryHackathonCode\sabpaisa-report-api\apps
xcopy /E /I /Y config D:\Hackathon-Project-new\RepositoryHackathonCode\sabpaisa-report-api\config
xcopy /E /I /Y scripts D:\Hackathon-Project-new\RepositoryHackathonCode\sabpaisa-report-api\scripts
xcopy /E /I /Y static D:\Hackathon-Project-new\RepositoryHackathonCode\sabpaisa-report-api\static

# Copy individual files
copy manage.py D:\Hackathon-Project-new\RepositoryHackathonCode\sabpaisa-report-api\
copy requirements.txt D:\Hackathon-Project-new\RepositoryHackathonCode\sabpaisa-report-api\
copy requirements_windows.txt D:\Hackathon-Project-new\RepositoryHackathonCode\sabpaisa-report-api\
copy .env.example D:\Hackathon-Project-new\RepositoryHackathonCode\sabpaisa-report-api\
copy .gitignore D:\Hackathon-Project-new\RepositoryHackathonCode\sabpaisa-report-api\
copy *.md D:\Hackathon-Project-new\RepositoryHackathonCode\sabpaisa-report-api\
copy run_*.py D:\Hackathon-Project-new\RepositoryHackathonCode\sabpaisa-report-api\
copy setup_*.py D:\Hackathon-Project-new\RepositoryHackathonCode\sabpaisa-report-api\
```

---

### Step 3: Verify .env is NOT in Git Repository

```bash
cd D:\Hackathon-Project-new\RepositoryHackathonCode\sabpaisa-report-api

# Check that .env is NOT there (should show error "File Not Found")
dir .env
```

**Expected**: File Not Found ✅

If .env exists, DELETE it immediately:
```bash
del .env
```

---

### Step 4: Update README.md

Edit the README.md in your git repository with installation instructions:

```markdown
# SabPaisa Reports API

Django REST API for managing transaction reports, settlements, and analytics.

## Features

- Transaction Management (240M+ records)
- Settlement Reports
- Real-time Analytics
- RBI & PCI DSS Compliant
- JWT Authentication
- Role-based Access Control (Admin/Merchant)

## Installation

### Prerequisites

- Python 3.12+
- MySQL 8.0+
- Redis (optional, for caching)

### Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd sabpaisa-report-api
```

2. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
# Copy the example file
copy .env.example .env

# Edit .env and add your database credentials
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Run the server:
```bash
python manage.py runserver
```

## API Documentation

See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for complete API reference.

## Compliance

- **RBI Compliance**: 95% (See [AUDIT_COMPLIANCE.md](./RBI_PCIDSS_AUDIT_COMPLIANCE_GUIDE.md))
- **PCI DSS Compliance**: 85%
- **Overall**: 90% Audit Ready

## License

Proprietary - SabPaisa
```

---

### Step 5: Git Commands to Push

```bash
# Navigate to git repository
cd D:\Hackathon-Project-new\RepositoryHackathonCode\sabpaisa-report-api

# Check status
git status

# Add all files (gitignore will automatically exclude sensitive files)
git add .

# Verify what will be committed (make sure .env is NOT in the list!)
git status

# Commit
git commit -m "Initial commit: Django Reports API with RBI/PCI DSS compliance"

# Push to GitHub
git push origin main
# OR if your branch is named master:
git push origin master
```

---

## 🔒 Security Checklist Before Push

- [ ] `.env` file is NOT in git repository
- [ ] `.gitignore` file is present in git repository
- [ ] `.env.example` has NO real passwords (only placeholder values)
- [ ] `logs/` directory is NOT in git repository
- [ ] `exports/` directory is NOT in git repository
- [ ] `media/` directory is NOT in git repository
- [ ] Database passwords are NOT in any committed file
- [ ] `SECRET_KEY` in committed files is a placeholder
- [ ] Run `git status` and verify no sensitive files are staged

---

## 📝 .env.example Template

Your `.env.example` should look like this (with fake credentials):

```ini
# Database Configuration - UPDATE THESE WITH YOUR MYSQL CREDENTIALS
DB_PRIMARY_NAME=your_database_name
DB_PRIMARY_USER=your_mysql_user
DB_PRIMARY_PASSWORD=your_secure_password
DB_PRIMARY_HOST=localhost
DB_PRIMARY_PORT=3306

DB_LEGACY_NAME=your_legacy_db
DB_LEGACY_USER=your_mysql_user
DB_LEGACY_PASSWORD=your_secure_password
DB_LEGACY_HOST=localhost
DB_LEGACY_PORT=3306

# Add other configs similarly with placeholder values
```

---

## ⚠️ What to Do If You Accidentally Push Sensitive Data

If you accidentally pushed `.env` or passwords:

1. **Immediately** change all passwords in your database
2. **Immediately** change your Django SECRET_KEY
3. Remove the file from git history:
```bash
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

git push origin --force --all
```
4. Notify your team
5. Rotate all API keys and secrets

---

## 📊 Expected File Structure in GitHub

```
sabpaisa-report-api/
├── .git/
├── .gitignore          ✅ MUST HAVE
├── README.md           ✅ Updated
├── .env.example        ✅ Safe template
├── manage.py
├── requirements.txt
├── apps/
│   ├── transactions/
│   ├── settlements/
│   ├── core/
│   └── ...
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── scripts/
├── static/
└── Documentation files (.md)
```

**NOT in GitHub**:
```
❌ .env
❌ logs/
❌ exports/
❌ media/
❌ __pycache__/
❌ *.pyc
❌ .vscode/
```

---

## 🎯 Quick Commands Summary

```bash
# 1. Copy .gitignore to git repo
copy D:\Hackathon-Project-new\Cleaned_SabPaisa_Report_Solution\sabpaisa-reports-api\.gitignore D:\Hackathon-Project-new\RepositoryHackathonCode\sabpaisa-report-api\

# 2. Copy all safe files (use xcopy or manually copy)

# 3. Navigate to git repo
cd D:\Hackathon-Project-new\RepositoryHackathonCode\sabpaisa-report-api

# 4. Verify .env is NOT there
dir .env  # Should give error

# 5. Git add, commit, push
git add .
git status  # Verify no sensitive files
git commit -m "Initial commit: Django Reports API"
git push origin main
```

---

## ✅ Final Verification

After pushing, check on GitHub:

1. ✅ No `.env` file visible
2. ✅ `.gitignore` file is present
3. ✅ `.env.example` has placeholder values only
4. ✅ All source code files are present
5. ✅ Documentation files are present
6. ✅ No log files visible
7. ✅ No export/media files visible

---

**Document Version**: 1.0
**Last Updated**: October 15, 2025
**Status**: Ready for GitHub Push
