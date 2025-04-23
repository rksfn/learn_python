# Setup Guide

This guide will help you set up your environment for the Python Debugging & Code Review Masterclass.

## 1. Python Installation

Ensure you have Python 3.7+ installed:

```bash
python --version
# or
python3 --version
```

If needed, download from [python.org](https://www.python.org/downloads/).

## 2. Virtual Environment Setup

Creating a virtual environment is recommended to keep dependencies isolated:

```bash
# Navigate to the course directory
cd path/to/learn_python

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

Your terminal prompt should now show the environment name, e.g., `(venv)`.

## 3. Required Packages

With your virtual environment activated, install required packages:

```bash
pip install ipython pytest
```

## 4. VS Code Setup (Recommended)

Visual Studio Code provides excellent debugging tools for Python:

1. Download and install VS Code from [code.visualstudio.com](https://code.visualstudio.com/)
2. Install the Python extension:
   - Open VS Code
   - Go to Extensions (Ctrl+Shift+X / Cmd+Shift+X)
   - Search for "Python" and install the Microsoft extension

3. Configure VS Code for Python debugging:
   - Open the command palette (Ctrl+Shift+P / Cmd+Shift+P)
   - Type "Python: Select Interpreter" and select your virtual environment

## 5. Debugging Tools Overview

This course covers several debugging approaches:

- **Print debugging**: Strategic use of print statements
- **Python Debugger (pdb)**: Built-in interactive debugger
- **VS Code Debugger**: GUI-based debugging
- **pytest**: For test-driven debugging

## 6. Git & GitHub (Optional)

If you want to track your progress or contribute:

1. Install Git from [git-scm.com](https://git-scm.com/)
2. Create a GitHub account if you don't have one
3. Fork this repository to your account
4. Clone your fork:
   ```bash
   git clone https://github.com/your-username/python-debugging-masterclass.git
   ```

## 7. Testing Your Setup

To confirm your setup is working:

1. Make sure your virtual environment is activated
2. Navigate to the `exercises/01_intro_debugging` directory
3. Run the setup verification script:
   ```bash
   python check_setup.py
   ```

If successful, you'll see a confirmation message.

## Troubleshooting

- **Python not found**: Ensure Python is in your PATH
- **Package installation issues**: Try `pip install --upgrade pip` before installing packages
- **Virtual environment problems**: Check you're using the correct activation command for your OS

You're now ready to begin the course! Start with the first module in the `lessons` directory.
