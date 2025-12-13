# ⚡ Quick Start Guide - AI Resume Analyzer

## 🚀 Fastest Way to Get Started

### Step 1: Prerequisites Check
- ✅ Python 3.9.12 installed
- ✅ MySQL installed and running
- ✅ Internet connection (for package downloads)

### Step 2: Run Setup (One Command!)
```bash
setup.bat
```

This will install everything automatically!

### Step 3: Create Database (One Command!)
```bash
create_database.bat
```

Or manually:
```bash
mysql -u root -p < database_setup.sql
```

### Step 4: Update Database Credentials (If Needed)
Edit `App/App.py` line 95 if your MySQL credentials are different:
```python
connection = pymysql.connect(
    host='localhost',
    user='root',                    # Your MySQL username
    password='root@MySQL4admin',    # Your MySQL password
    db='cv'
)
```

### Step 5: Run the Application!
```bash
run.bat
```

The app will open in your browser at `http://localhost:8501`

## 📋 Admin Login
- **Username**: `admin`
- **Password**: `admin@resume-analyzer`

## 🎯 That's It!

For detailed instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md)

---

**Need Help?** Check the troubleshooting section in SETUP_GUIDE.md

