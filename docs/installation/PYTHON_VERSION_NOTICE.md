# Python Version Compatibility Notice

## Supported Python Versions

**TerminalAI requires Python 3.10, 3.11, or 3.12**

```
Python 3.10: ✅ Fully Supported
Python 3.11: ✅ Fully Supported (Recommended)
Python 3.12: ✅ Fully Supported
Python 3.13: ❌ Not Compatible (see below)
```

## Recommended Version

**Python 3.11** is recommended for best compatibility and stability.

## Python 3.13 Compatibility Issue

**Current Status:** Python 3.13 is **not compatible** with TerminalAI due to dependency issues.

**Issue:** Some AI dependencies (basicsr, facexlib) have installation problems on Python 3.13 due to breaking changes in Python's build system.

**Error:**
```
KeyError: '__version__'
error: metadata-generation-failed
```

## If You Have Python 3.13

You have two options:

### Option 1: Install Python 3.11 (Recommended)

**Windows:**
```bash
winget install Python.Python.3.11
```

**Linux:**
```bash
sudo apt install python3.11 python3.11-venv
```

**macOS:**
```bash
brew install python@3.11
```

### Option 2: Create Python 3.11 Virtual Environment

If you want to keep Python 3.13 as your system default:

**Windows:**
```bash
# Download and install Python 3.11 alongside 3.13
winget install Python.Python.3.11

# Create virtual environment with Python 3.11
py -3.11 -m venv venv_terminalai

# Activate
venv_terminalai\Scripts\activate

# Install TerminalAI
pip install -e .
```

**Linux:**
```bash
# Install Python 3.11
sudo apt install python3.11 python3.11-venv

# Create virtual environment
python3.11 -m venv venv_terminalai

# Activate
source venv_terminalai/bin/activate

# Install TerminalAI
pip install -e .
```

**macOS:**
```bash
# Install Python 3.11
brew install python@3.11

# Create virtual environment
python3.11 -m venv venv_terminalai

# Activate
source venv_terminalai/bin/activate

# Install TerminalAI
pip install -e .
```

## Verify Python Version

```bash
python --version
```

Should show: `Python 3.10.x`, `Python 3.11.x`, or `Python 3.12.x`

## Why Python 3.13 Doesn't Work

Python 3.13 introduced changes to the build system and metadata handling that break some older packages:

1. **basicsr** (face restoration dependency) has hardcoded version detection that fails
2. **facexlib** has similar issues
3. These packages haven't been updated yet for Python 3.13

## When Will Python 3.13 Be Supported?

TerminalAI will support Python 3.13 once all dependencies are updated:

- Waiting for basicsr to fix setup.py (tracked upstream)
- Waiting for facexlib compatibility updates
- Expected timeline: Q1-Q2 2025

## Check Your Python Version

Before installing, verify your Python version:

```bash
python --version
```

If you see `Python 3.13.x`, follow the instructions above to install Python 3.11.

## Installed on Python 3.13 by Mistake?

If you already tried installing on Python 3.13 and got errors:

1. Create a Python 3.11 virtual environment (see above)
2. Activate the environment
3. Install TerminalAI: `pip install -e .`
4. Use the virtual environment whenever running TerminalAI

## Summary

**Use Python 3.11 for best results.**

```bash
# Check version
python --version

# If Python 3.13, create 3.11 venv
py -3.11 -m venv venv_terminalai  # Windows
python3.11 -m venv venv_terminalai  # Linux/Mac

# Activate
venv_terminalai\Scripts\activate  # Windows
source venv_terminalai/bin/activate  # Linux/Mac

# Install
pip install -e .
```
