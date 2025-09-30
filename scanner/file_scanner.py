
import os
import time
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
from colorama import Fore, Style, init
from .utils import *

# ---------------- Scan File ----------------
def scan_file(file_path, all_features):
    found = set()
    ext = Path(file_path).suffix.lower()
    if ext in SKIP_FILES or ext not in FRONTEND_EXTENSIONS:
        return found
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read().lower()
        for feat in all_features:
            if feat.lower() in content:
                found.add(feat)
    except PermissionError:
        logging.warning(f"Permission denied: {file_path}")
    except Exception as e:
        logging.warning(f"Could not read file {file_path}: {e}")
    return found

# ---------------- Scan Folder ----------------
def scan_folder(folder_path, all_features, baseline_features, print_console=False):
    files_list = []
    for root, dirs, files in os.walk(folder_path):
        # Skip unwanted folders completely
        dirs[:] = [d for d in dirs if d not in SKIP_FOLDERS]
        for file in files:
            if Path(file).suffix.lower() in SKIP_FILES:
                continue
            files_list.append(os.path.join(root, file))

    total_files = len(files_list)
    print(f"\n{Fore.CYAN}[INFO]{Style.RESET_ALL}{Fore.MAGENTA} Scanning folder: {Fore.YELLOW}{folder_path}{Style.RESET_ALL} ({Fore.GREEN}{total_files} files{Style.RESET_ALL})")

    found_features = set()
    start_time = time.time()
    bar_format = Fore.MAGENTA + "{l_bar}" + Fore.GREEN + "{bar}" + Fore.RESET + "{r_bar}"
    for file in tqdm(files_list, desc=f"{Fore.YELLOW}Files{Style.RESET_ALL}", unit="file", ncols=90, bar_format=bar_format):
        found_features.update(scan_file(file, all_features))

    elapsed = time.time() - start_time
    speed = total_files / elapsed if elapsed > 0 else 0
    print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL}{Fore.BLUE} Scanned {Fore.GREEN}{total_files}{Style.RESET_ALL} files in {Fore.YELLOW}{elapsed:.2f}s{Style.RESET_ALL} ({Fore.MAGENTA}{speed:.2f} files/s{Style.RESET_ALL})\n")
    logging.info(f"Scanned {total_files} files in {elapsed:.2f}s ({speed:.2f} files/s) for folder {folder_path}")

    baseline_used = sorted([f for f in found_features if f in baseline_features])
    non_baseline_used = sorted([f for f in found_features if f not in baseline_features])

    if print_console:
        print(f"{Fore.GREEN}✅ Baseline features used ({len(baseline_used)}):{Style.RESET_ALL} {', '.join(baseline_used) if baseline_used else 'None'}")
        print(f"{Fore.RED}❌ Non-Baseline features used ({len(non_baseline_used)}):{Style.RESET_ALL} {', '.join(non_baseline_used) if non_baseline_used else 'None'}\n")

    return baseline_used, non_baseline_used, total_files