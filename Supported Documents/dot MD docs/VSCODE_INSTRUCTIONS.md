# 🚀 VS Code Instructions - Run Everything with F5!

## 📦 Initial Setup (One-Time Only)

### Method 1: Open Workspace File (RECOMMENDED)
1. **Open VS Code**
2. **File → Open Workspace from File...**
3. **Select: `sabpaisa-reports-api.code-workspace`**
4. VS Code will automatically configure everything!

### Method 2: Open Folder
1. **Open VS Code**
2. **File → Open Folder...**
3. **Select the `sabpaisa-reports-api` folder**

## 🎯 Quick Start - Just Press F5!

### 🟢 STEP 1: First-Time Setup
1. Open the workspace in VS Code
2. **Press `Ctrl+Shift+D`** to open Debug panel
3. Select **"📦 Setup & Migrate"** from dropdown
4. **Press F5** - This will:
   - ✅ Create virtual environment
   - ✅ Install all packages
   - ✅ Create .env file
   - ✅ Setup directories
   - ✅ Run migrations

### 🟢 STEP 2: Update Database Configuration
1. Open `.env` file in VS Code
2. Update these settings with your MySQL credentials:
```env
DB_PRIMARY_NAME=sabpaisa2_stage_sabpaisa
DB_PRIMARY_USER=your_mysql_user
DB_PRIMARY_PASSWORD=your_mysql_password
DB_PRIMARY_HOST=localhost
```

### 🟢 STEP 3: Run the Server
1. Select **"🚀 Run Django Server (F5)"** from dropdown
2. **Press F5**
3. Server starts automatically at http://13.127.244.103:8000

## 🎮 VS Code Keyboard Shortcuts

| Action | Shortcut | Description |
|--------|----------|-------------|
| **F5** | Run/Debug | Start selected configuration |
| **Shift+F5** | Stop | Stop running server |
| **Ctrl+F5** | Run without Debug | Run faster without debugging |
| **F9** | Toggle Breakpoint | Set/remove breakpoint |
| **Ctrl+Shift+D** | Debug Panel | Open debug sidebar |
| **Ctrl+Shift+P** | Command Palette | All VS Code commands |
| **Ctrl+`** | Terminal | Open/close terminal |
| **Ctrl+B** | Sidebar | Toggle sidebar |

## 📋 Available Run Configurations

### From Debug Panel (Ctrl+Shift+D), Select and Press F5:

#### 🚀 Main Configurations
- **🚀 Run Django Server (F5)** - Main development server
- **📦 Setup & Migrate** - First-time setup
- **🚀 Run Full Stack** - Django + Celery + Beat

#### 🛠️ Setup & Management
- **🔄 Run Migrations** - Apply database migrations
- **👤 Create Superuser** - Create admin account
- **🎯 Django Shell Plus** - Interactive Django shell

#### ⚡ Celery (Background Tasks)
- **⚡ Celery Worker** - Process async tasks
- **⏰ Celery Beat** - Scheduled tasks
- **🌸 Celery Flower** - Monitor Celery tasks

#### 📊 Testing & Database
- **📊 Run Tests** - Execute test suite
- **🗄️ DB Shell** - Database command line

## 🔧 VS Code Features Configured

### ✅ Auto-Configured Features:
- **Python Interpreter** - Automatically uses `.venv`
- **Linting** - Pylint with Django support
- **Formatting** - Black formatter on save
- **Import Sorting** - isort on save
- **Django Support** - Template syntax, debugging
- **IntelliSense** - Full code completion
- **Git Integration** - Source control built-in

### 📁 Project Structure in VS Code:
```
sabpaisa-reports-api/
├── 📁 .vscode/           # VS Code settings
├── 📁 apps/              # Django applications
│   ├── authentication/   # Login/JWT
│   ├── transactions/     # Main APIs
│   ├── settlements/      # Settlement APIs
│   └── reports/         # Excel/CSV
├── 📁 config/           # Django settings
├── 📄 .env              # Your configuration
├── 📄 manage.py         # Django management
└── 📄 run_server.py     # Quick runner
```

## 🎯 Common Tasks in VS Code

### Create Superuser (Admin Account)
1. **Ctrl+Shift+D** → Select **"👤 Create Superuser"**
2. **Press F5**
3. Enter username, email, password

### Run with Celery (Background Tasks)
1. **Ctrl+Shift+D** → Select **"🚀 Run Full Stack"**
2. **Press F5**
3. Opens 3 terminals: Django, Celery Worker, Celery Beat

### Open Django Shell
1. **Ctrl+Shift+D** → Select **"🎯 Django Shell Plus"**
2. **Press F5**
3. Interactive Python with Django models loaded

### View API Documentation
1. Run server with F5
2. Open browser: http://13.127.244.103:8000/api/docs/

## 🔍 Troubleshooting in VS Code

### If F5 doesn't work:
1. **Check Python Extension**:
   - Ctrl+Shift+X → Search "Python" → Install Microsoft Python extension

2. **Select Python Interpreter**:
   - Ctrl+Shift+P → "Python: Select Interpreter"
   - Choose `.venv\Scripts\python.exe`

3. **Install Dependencies Manually**:
   - Ctrl+` (Open Terminal)
   - Run: `.venv\Scripts\activate`
   - Run: `pip install -r requirements.txt`

### Database Connection Issues:
1. Check `.env` file has correct credentials
2. Ensure MySQL service is running
3. Create databases if they don't exist:
```sql
CREATE DATABASE sabpaisa2_stage_sabpaisa;
CREATE DATABASE sabpaisa2_stage_legacy;
CREATE DATABASE spclientonboard;
```

### Port 8000 Already in Use:
1. Stop other Django servers
2. Or change port in launch.json to 8001

## 📱 API Testing in VS Code

### Using Thunder Client Extension:
1. Install Thunder Client extension (already recommended)
2. Click Thunder Client icon in sidebar
3. Create new request
4. Set URL: http://13.127.244.103:8000/api/v1/...
5. Add headers: `Authorization: Bearer <token>`

### Login to Get Token:
```
POST http://13.127.244.103:8000/api/v1/auth/login/
{
    "username": "admin",
    "password": "your_password"
}
```

## 🌟 VS Code Tips

1. **Multi-Cursor Editing**: Alt+Click to add cursors
2. **Quick File Open**: Ctrl+P, type filename
3. **Go to Definition**: F12 on any function/class
4. **Find References**: Shift+F12
5. **Rename Symbol**: F2
6. **Format Document**: Shift+Alt+F
7. **Toggle Comments**: Ctrl+/
8. **Duplicate Line**: Shift+Alt+Down

## 🎉 You're All Set!

Just remember:
- **F5** = Run Server
- **Shift+F5** = Stop Server
- **Ctrl+Shift+D** = Debug Panel
- **Ctrl+`** = Terminal

Everything is configured to work with a single F5 press!

---

**Need Help?**
- Check output in Terminal (Ctrl+`)
- View Problems panel (Ctrl+Shift+M)
- Check Debug Console during debugging