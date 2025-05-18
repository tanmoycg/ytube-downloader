import os
import shutil
import time
from pathlib import Path

def cleanup_create(directory: str) -> None:
    """Ensures clean download directory exists."""
    directory_path = Path.cwd() / directory
    try:
        if directory_path.exists():
            shutil.rmtree(directory_path)
            print(f"Removed existing directory: {directory_path}")
            time.sleep(1)
        directory_path.mkdir(exist_ok=True)
        print(f"Created fresh directory: {directory_path}")
    except Exception as e:
        print(f"Directory handling failed: {e}")
        raise