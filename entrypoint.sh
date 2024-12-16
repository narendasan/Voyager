#!/bin/sh

# Navigate to the mounted directory
cd /data

# Install dependencies
pip install --no-cache-dir --upgrade pip
pip install --no-cache-dir -r requirements.txt -c constraints.txt

# Run the application
exec python -m __main__