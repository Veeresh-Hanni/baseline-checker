# scanner/filters.py

import os

# Folders we don’t want to scan
SKIP_DIRS = {"node_modules", "build", "dist", ".git", ".cache"}

# File types we don’t want to scan
SKIP_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico",
    ".mp4", ".mp3", ".zip", ".rar", ".exe"
}

def should_skip(path: str) -> bool:
    """Return True if this file/folder should be skipped."""
    parts = path.replace("\\", "/").split("/")
    if any(p in SKIP_DIRS for p in parts):
        return True
    if os.path.splitext(path)[1].lower() in SKIP_EXTS:
        return True
    return False
