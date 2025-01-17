#!/usr/bin/env python3
import os
import subprocess

# Set environment variables
os.environ["DB_USER"] = "bloom"
os.environ["DB_PASSWORD"] = "bloom"
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "5432"
os.environ["DB_NAME"] = "bloombot"

# Run alembic upgrade
try:
    subprocess.run(["alembic", "upgrade", "head"], check=True)
except subprocess.CalledProcessError as e:
    print(f"Error running migration: {e}")
    exit(1)
