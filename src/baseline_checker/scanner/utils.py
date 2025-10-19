import json
import sys
import logging
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
from colorama import Fore, Style, init

import pkg_resources

# ---------------- Initialize ----------------
init(autoreset=True)
PRINT_CONSOLE = True

# ---------------- Config ----------------
SKIP_FOLDERS = {"node_modules", ".git", "dist", "build", ".vscode", "__pycache__", "$RECYCLE.BIN"}
SKIP_FILES = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".mp4", ".mp3", ".zip", ".rar", ".exe"}
FRONTEND_EXTENSIONS = {".html", ".css", ".scss", ".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte"}


# ---------------- Logging Setup ----------------
if getattr(sys, 'frozen', False):
    base_dir = Path(sys.executable).parent
else:
    base_dir = Path.cwd()

log_folder = base_dir / "logs"
log_folder.mkdir(exist_ok=True)
log_file = log_folder / f"baseline_checker_{datetime.now():%Y%m%d_%H%M%S}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(log_file, encoding="utf-8")]
)
logging.info("Log file created at: %s", log_file)

# ---------------- Load Features ----------------
def load_features(file_path=None):
    try:
        if file_path is None:
            file_path = pkg_resources.resource_filename(
                "baseline_checker", 
                "config/baseline_data.json"
            )
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        features_dict = data.get("features", {})
        if PRINT_CONSOLE:
            print(f"{Fore.GREEN}[INFO]{Style.RESET_ALL} Loaded {len(features_dict)} features")
        logging.info(f"Loaded {len(features_dict)} features from {file_path}")
        return features_dict
    except FileNotFoundError:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} baseline_data.json not found!")
        logging.error(f"Features file not found: {file_path}")
        return {}