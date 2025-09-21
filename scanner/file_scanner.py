import re
from .utils import match_feature

def scan_file(file_path, baseline_features, max_nonbaseline_display=20, min_word_length=3):
    """Scan a single file for baseline and non-baseline features."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception:
        return file_path, [], []

    # Detect baseline features
    baseline_matches = [f for f in baseline_features if match_feature(content, f)]

    # Extract words (alphabetic only, min length)
    pattern = rf"\b[a-zA-Z]{{{min_word_length},}}\b"
    words = set(re.findall(pattern, content))
    
    # Non-baseline matches
    non_baseline_matches = list(words - set(baseline_matches))

    # Limit display
    non_baseline_display = non_baseline_matches[:max_nonbaseline_display]

    return file_path, baseline_matches, non_baseline_display
