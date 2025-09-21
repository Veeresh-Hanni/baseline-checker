# scanner/utils.py
import re
from rich.console import Console

console = Console()

def match_feature(content, feature_name):
    """Return True if feature_name exists in content"""
    return bool(re.search(rf"\b{re.escape(feature_name)}\b", content))
