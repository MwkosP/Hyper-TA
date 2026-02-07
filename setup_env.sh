#!/usr/bin/env bash
# setup_env.sh - Create and activate a virtual environment, then install dependencies

# Exit if any command fails
set -e

# Create virtual environment
python -m venv venv

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Upgrade pip
pip install --upgrade pip

# Install dependencies
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
fi

echo "✅ Virtual environment created and dependencies installed."
