# Quick Fix - PowerShell Execution Policy

## Problem
PowerShell is blocking script execution. Here are **3 easy solutions**:

## Solution 1: Use Batch File (Easiest) ✅

**Double-click `START_APP.bat`** or run:
```cmd
START_APP.bat
```

This uses `activate.bat` instead of PowerShell scripts - no policy changes needed!

## Solution 2: Use activate.bat Directly

```cmd
venv\Scripts\activate.bat
python run.py
```

## Solution 3: Skip Activation (Works Too!)

Since the virtual environment is already set up, you can run directly:

```powershell
.\venv\Scripts\python.exe run.py
```

Or:
```powershell
python run.py
```

(Windows will use the venv Python automatically if you're in the project directory)

## Solution 4: Fix PowerShell Policy (If Needed)

If you want to use PowerShell scripts:

```powershell
# Check current policy
Get-ExecutionPolicy -List

# Set policy for current user
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

# Then activate
.\venv\Scripts\Activate.ps1
```

## Recommended: Use START_APP.bat

Just double-click `START_APP.bat` - it handles everything automatically!

---

**The application should now be running at http://localhost:5000**

