#!/usr/bin/env python3
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

print("Testing imports...")
try:
    from src.api import app
    print("✓ API imported successfully")
except Exception as e:
    print(f"✗ Failed to import API: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nStarting server on port 8080...")
app.run(debug=True, host='0.0.0.0', port=8080)
