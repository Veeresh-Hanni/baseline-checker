# import json
# from pathlib import Path
# import os
# import sys
# import time
# from tqdm import tqdm
# from colorama import Fore, Style, Back, init
# from reports.report_generator import save_csv, save_json, save_pdf, save_word, save_html
# import logging

# # Initialize colorama
# init(autoreset=True)
# console = Fore  # For backward compatibility in coloring

# # ---------------- Config ----------------
# SKIP_FOLDERS = {"node_modules", ".git", "dist", "build", ".vscode", "__pycache__", "$RECYCLE.BIN"}
# SKIP_FILES = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".mp4", ".mp3", ".zip", ".rar", ".exe"}
# FRONTEND_EXTENSIONS = {".html", ".css", ".scss", ".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte"}

# # Logging setup
# logging.basicConfig(
#     filename="baseline_checker.log",
#     level=logging.INFO,
#     format="%(asctime)s [%(levelname)s] %(message)s"
# )

# PRINT_CONSOLE = True

# # ---------------- Load Features ----------------
# def load_features(file_path="config/baseline_data.json"):
#     try:
#         with open(file_path, "r", encoding="utf-8") as f:
#             data = json.load(f)
#         features_dict = data.get("features", {})
#         if PRINT_CONSOLE:
#             print(f"{Fore.GREEN}[INFO]{Style.RESET_ALL} Loaded {len(features_dict)} features")
#         logging.info(f"Loaded {len(features_dict)} features from {file_path}")
#         return features_dict
#     except FileNotFoundError:
#         print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} baseline_data.json not found!")
#         logging.error(f"Features file not found: {file_path}")
#         return {}

# # ---------------- Scan File ----------------
# def scan_file(file_path, all_features):
#     found = set()
#     ext = Path(file_path).suffix.lower()
#     if ext in SKIP_FILES or ext not in FRONTEND_EXTENSIONS:
#         return found
#     try:
#         with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
#             content = f.read().lower()
#         for feat in all_features:
#             if feat.lower() in content:
#                 found.add(feat)
#         if found:
#             logging.debug(f"Found {len(found)} features in {file_path}")
#     except PermissionError:
#         logging.warning(f"Permission denied: {file_path}")
#     except Exception as e:
#         logging.warning(f"Could not read file {file_path}: {e}")
#     return found

# # ---------------- Scan Folder ----------------
# def scan_folder(folder_path, all_features, baseline_features, print_console=True):
#     files_list = []
#     for root, _, files in os.walk(folder_path):
#         for file in files:
#             files_list.append(os.path.join(root, file))
#     total_files = len(files_list)

#     print(f"\n{Fore.CYAN}[INFO]{Style.RESET_ALL}{Fore.MAGENTA} Scanning folder: {Fore.YELLOW}{folder_path}{Style.RESET_ALL} ({Fore.GREEN}{total_files} files{Style.RESET_ALL})")

#     found_features = set()
#     start_time = time.time()

#     # Colored progress bar
#     bar_format = Fore.MAGENTA + "{l_bar}" + Fore.GREEN + "{bar}" + Fore.RESET + "{r_bar}"
#     for file in tqdm(files_list, desc=f"{Fore.YELLOW}Files{Style.RESET_ALL}", unit="file", ncols=90, bar_format=bar_format):
#         if any(skip in Path(file).parts for skip in SKIP_FOLDERS) or Path(file).suffix.lower() in SKIP_FILES:
#             continue
#         found_features.update(scan_file(file, all_features))

#     elapsed = time.time() - start_time
#     speed = total_files / elapsed if elapsed > 0 else 0

#     print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL}{Fore.BLUE} Scanned {Fore.GREEN}{total_files}{Style.RESET_ALL} files in {Fore.YELLOW}{elapsed:.2f}s{Style.RESET_ALL} ({Fore.MAGENTA}{speed:.2f} files/s{Style.RESET_ALL})\n")
#     logging.info(f"Scanned {total_files} files in {elapsed:.2f}s ({speed:.2f} files/s) for folder {folder_path}")

#     baseline_used = sorted([f for f in found_features if f in baseline_features])
#     non_baseline_used = sorted([f for f in found_features if f not in baseline_features])

#     if print_console:
#         print(f"{Fore.GREEN}✅ Baseline features used ({len(baseline_used)}):{Style.RESET_ALL} {', '.join(baseline_used) if baseline_used else 'None'}")
#         print(f"{Fore.RED}❌ Non-Baseline features used ({len(non_baseline_used)}):{Style.RESET_ALL} {', '.join(non_baseline_used) if non_baseline_used else 'None'}\n")

#     return baseline_used, non_baseline_used, total_files

# # ---------------- Detect Frontend ----------------
# def detect_frontend_framework(folder_path: Path) -> bool:
#     for file in folder_path.rglob("*"):
#         if file.suffix.lower() in {".vue", ".svelte"}:
#             return True
#         if file.name == "package.json":
#             try:
#                 data = json.loads(file.read_text(encoding="utf-8"))
#                 deps = data.get("dependencies", {})
#                 dev_deps = data.get("devDependencies", {})
#                 all_deps = {**deps, **dev_deps}
#                 for fw in ("react", "vue", "@angular/core", "svelte"):
#                     if fw in all_deps:
#                         return True
#             except Exception:
#                 continue
#         if file.suffix.lower() in {".js", ".jsx", ".ts", ".tsx,","css","scss"}:
#             content = file.read_text(encoding="utf-8", errors="ignore").lower()
#             if any(k in content for k in ["import react", "reactdom.render", "new vue(", "@component"]):
#                 return True
#     return False

# # ---------------- Main ----------------
# def main(scan_path, features_file="config/baseline_data.json",
#          generate_json=True, generate_csv=True, generate_word=True,
#          generate_pdf=True, generate_html=True):

#     features_dict = load_features(features_file)
#     baseline_features = {name for name, info in features_dict.items() if info.get("status", {}).get("baseline") in ("high", "low")}
#     all_feature_names = set(features_dict.keys())

#     scan_path = Path(scan_path)
#     if not scan_path.exists():
#         print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Path {scan_path} does not exist. Exiting.")
#         logging.error(f"Scan path does not exist: {scan_path}")
#         return

#     total_files_scanned = 0
#     cumulative_baseline = set()
#     cumulative_non_baseline = set()
#     folder_reports = []

#     try:
#         for folder in scan_path.iterdir():
#             if folder.is_dir() and folder.name not in SKIP_FOLDERS:
#                 if detect_frontend_framework(folder):
#                     baseline_used, non_baseline_used, files_scanned = scan_folder(
#                         folder, all_feature_names, baseline_features, print_console=PRINT_CONSOLE
#                     )
#                     cumulative_baseline.update(baseline_used)
#                     cumulative_non_baseline.update(non_baseline_used)
#                     total_files_scanned += files_scanned
#                     folder_reports.append({
#                         "name": folder.name,
#                         "files_scanned": files_scanned,
#                         "baseline_features": baseline_used,
#                         "non_baseline_features": non_baseline_used
#                     })

#     except KeyboardInterrupt:
#         print(f"\n{Fore.YELLOW}[INFO]{Style.RESET_ALL} Scan interrupted!")
#         logging.warning("Scan interrupted by user")
#         choice = input(f"{Fore.YELLOW}Do you want to stop scanning? (y/n): {Style.RESET_ALL}").strip().lower()
#         if choice == "y":
#             partial_report = {
#                 "total_files_scanned": total_files_scanned,
#                 "baseline_features": sorted(cumulative_baseline),
#                 "non_baseline_features": sorted(cumulative_non_baseline),
#                 "folders": folder_reports
#             }
#             save_json(partial_report)
#             print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Partial report saved as baseline_report.json")
#             return

#     # Final report
#     report_data = {
#         "total_files_scanned": total_files_scanned,
#         "baseline_features": sorted(cumulative_baseline),
#         "non_baseline_features": sorted(cumulative_non_baseline),
#         "folders": folder_reports
#     }

#     if generate_json:
#         save_json(report_data)
#         logging.info("JSON report generated")
#     if generate_csv:
#         save_csv(report_data)
#         logging.info("CSV report generated")
#     if generate_word:
#         save_word(report_data)
#         logging.info("Word report generated")
#     if generate_pdf:
#         save_pdf(report_data)
#         logging.info("PDF report generated")
#     if generate_html:
#         save_html(report_data)
#         logging.info("HTML report generated")

#     print(f"\n{Fore.GREEN}[INFO]{Style.RESET_ALL} Scan completed! Total files scanned: {Fore.YELLOW}{total_files_scanned}")
#     print(f"{Fore.GREEN}✅ Total Baseline features used: {len(cumulative_baseline)}{Style.RESET_ALL}")
#     print(f"{Fore.RED}❌ Total Non-Baseline features used: {len(cumulative_non_baseline)}{Style.RESET_ALL}")

# # ---------------- Entry Point ----------------
# if __name__ == "__main__":
#     import argparse
#     logging.info("="*60)
#     logging.info("CLI SCAN INITIATED")

#     parser = argparse.ArgumentParser(description="Baseline Compatibility Scanner")
#     parser.add_argument("path", help="Path to the project folder to scan")
#     parser.add_argument("--features", default="config/baseline_data.json", help="Path to baseline features JSON")
#     parser.add_argument("--json", action="store_true", help="Generate JSON report")
#     parser.add_argument("--csv", action="store_true", help="Generate CSV report")
#     parser.add_argument("--docx", action="store_true", help="Generate Word report")
#     parser.add_argument("--pdf", action="store_true", help="Generate PDF report")
#     parser.add_argument("--html", action="store_true", help="Generate HTML report")
#     parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
#     args = parser.parse_args()

#     PRINT_CONSOLE = input(f"{Fore.CYAN}Do you want to print each folder's report on console? (y/n): {Style.RESET_ALL}").strip().lower() == "y"

#     try:
#         main(
#             scan_path=args.path,
#             features_file=args.features,
#             generate_json=args.json,
#             generate_csv=args.csv,
#             generate_word=args.docx,
#             generate_pdf=args.pdf,
#             generate_html=args.html
#         )
#         logging.info("CLI SCAN COMPLETED SUCCESSFULLY")
#     except Exception as e:
#         print(f"{Fore.RED}An unexpected error occurred: {e}{Style.RESET_ALL}")
#         logging.critical(f"An unhandled exception occurred: {e}", exc_info=True)
#         sys.exit(1)
#     finally:
#         logging.info("="*60 + "\n")



import json
from pathlib import Path
import os
import sys
import time
from tqdm import tqdm
from colorama import Fore, Style, init
from .reports.report_generator import save_csv, save_json, save_pdf, save_word, save_html
import logging

# Initialize colorama
init(autoreset=True)

# ---------------- Config ----------------
SKIP_FOLDERS = {"node_modules", ".git", "dist", "build", ".vscode", "__pycache__", "$RECYCLE.BIN"}
SKIP_FILES = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".mp4", ".mp3", ".zip", ".rar", ".exe"}
FRONTEND_EXTENSIONS = {".html", ".css", ".scss", ".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte"}

# Logging setup
import os
import sys
import logging
from datetime import datetime
from pathlib import Path


# Determine base folder for logs
if getattr(sys, 'frozen', False):  # running as PyInstaller exe
    base_dir = Path(sys.executable).parent
else:
    base_dir = Path.cwd()

log_folder = base_dir / "logs"
log_folder.mkdir(exist_ok=True)

log_file = log_folder / f"baseline_checker_{datetime.now():%Y%m%d_%H%M%S}.log"

# Only log to file, no console output for INFO
logging.basicConfig(
    level=logging.DEBUG,  # developer logs
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(log_file, encoding="utf-8")]
)

# Optional: print to console only for WARN/ERROR
# console_handler = logging.StreamHandler()
# console_handler.setLevel(logging.WARNING)  # only warnings or errors appear on console
# console_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
# console_handler.setFormatter(console_formatter)
# logging.getLogger().addHandler(console_handler)

logging.debug("Log file created at: %s", log_file)  # developer log



PRINT_CONSOLE = True

# ---------------- Load Features ----------------
import pkg_resources

def load_features(file_path=None):
    try:
        if file_path is None:
            # Load baseline_data.json from the package
            file_path = pkg_resources.resource_filename("baseline_checker", "config/baseline_data.json")
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
    for root, _, files in os.walk(folder_path):
        for file in files:
            files_list.append(os.path.join(root, file))
    total_files = len(files_list)

    print(f"\n{Fore.CYAN}[INFO]{Style.RESET_ALL}{Fore.MAGENTA} Scanning folder: {Fore.YELLOW}{folder_path}{Style.RESET_ALL} ({Fore.GREEN}{total_files} files{Style.RESET_ALL})")

    found_features = set()
    start_time = time.time()

    bar_format = Fore.MAGENTA + "{l_bar}" + Fore.GREEN + "{bar}" + Fore.RESET + "{r_bar}"
    for file in tqdm(files_list, desc=f"{Fore.YELLOW}Files{Style.RESET_ALL}", unit="file", ncols=90, bar_format=bar_format):
        if any(skip in Path(file).parts for skip in SKIP_FOLDERS) or Path(file).suffix.lower() in SKIP_FILES:
            continue
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

# ---------------- Detect Frontend ----------------
def detect_frontend_framework(folder_path: Path) -> bool:
    for file in folder_path.rglob("*"):
        if file.suffix.lower() in {".vue", ".svelte"}:
            return True
        if file.name == "package.json":
            try:
                data = json.loads(file.read_text(encoding="utf-8"))
                deps = data.get("dependencies", {})
                dev_deps = data.get("devDependencies", {})
                all_deps = {**deps, **dev_deps}
                for fw in ("react", "vue", "@angular/core", "svelte"):
                    if fw in all_deps:
                        return True
            except Exception:
                continue
        if file.suffix.lower() in {".js", ".jsx", ".ts", ".tsx", ".css", ".scss"}:
            content = file.read_text(encoding="utf-8", errors="ignore").lower()
            if any(k in content for k in ["import react", "reactdom.render", "new vue(", "@component"]):
                return True
    return False

# ---------------- Main ----------------
def main(scan_path, features_file="config/baseline_data.json",
         generate_json=True, generate_csv=True, generate_word=True,
         generate_pdf=True, generate_html=True):

    features_dict = load_features(features_file)
    baseline_features = {name for name, info in features_dict.items() if info.get("status", {}).get("baseline") in ("high", "low")}
    all_feature_names = set(features_dict.keys())

    scan_path = Path(scan_path)
    if not scan_path.exists():
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Path {scan_path} does not exist. Exiting.")
        logging.error(f"Scan path does not exist: {scan_path}")
        return

    total_files_scanned = 0
    cumulative_baseline = set()
    cumulative_non_baseline = set()
    folder_reports = []

    try:
        for folder in scan_path.rglob("*"):
            if folder.is_dir() and folder.name not in SKIP_FOLDERS:
                try:
                    if detect_frontend_framework(folder):
                        baseline_used, non_baseline_used, files_scanned = scan_folder(
                            folder, all_feature_names, baseline_features, print_console=PRINT_CONSOLE
                        )
                        cumulative_baseline.update(baseline_used)
                        cumulative_non_baseline.update(non_baseline_used)
                        total_files_scanned += files_scanned
                        folder_reports.append({
                            "name": str(folder),
                            "files_scanned": files_scanned,
                            "baseline_features": baseline_used,
                            "non_baseline_features": non_baseline_used
                        })
                except PermissionError:
                    logging.warning(f"Permission denied: {folder}")
                    print(f"{Fore.YELLOW}[WARN]{Style.RESET_ALL} Skipping folder (Permission denied): {folder}")
                except Exception as e:
                    logging.warning(f"Error scanning folder {folder}: {e}")
                    print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Skipping folder due to error: {folder}")


    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[INFO]{Style.RESET_ALL} Scan interrupted!")
        logging.warning("Scan interrupted by user")
        choice = input(f"{Fore.YELLOW}Do you want to stop scanning? (y/n): {Style.RESET_ALL}").strip().lower()
        if choice == "y":
            partial_report = {
                "total_files_scanned": total_files_scanned,
                "baseline_features": sorted(cumulative_baseline),
                "non_baseline_features": sorted(cumulative_non_baseline),
                "folders": folder_reports
            }
            save_pdf(partial_report)
            print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Partial report saved as baseline_report.pdf")
            return

    # Final report
    report_data = {
        "total_files_scanned": total_files_scanned,
        "baseline_features": sorted(cumulative_baseline),
        "non_baseline_features": sorted(cumulative_non_baseline),
        "folders": folder_reports
    }

    if generate_json:
        save_json(report_data)
        logging.info("JSON report generated")
    if generate_csv:
        save_csv(report_data)
        logging.info("CSV report generated")
    if generate_word:
        save_word(report_data)
        logging.info("Word report generated")
    if generate_pdf:
        save_pdf(report_data)
        logging.info("PDF report generated")
    if generate_html:
        save_html(report_data)
        logging.info("HTML report generated")

    print(f"\n{Fore.GREEN}[INFO]{Style.RESET_ALL} Scan completed! Total files scanned: {Fore.YELLOW}{total_files_scanned}")
    print(f"{Fore.GREEN}✅ Total Baseline features used: {len(cumulative_baseline)}{Style.RESET_ALL}")
    print(f"{Fore.RED}❌ Total Non-Baseline features used: {len(cumulative_non_baseline)}{Style.RESET_ALL}")

# ---------------- Entry Point ----------------
def run():
    import argparse
    logging.info("="*60)
    logging.info("CLI SCAN INITIATED")
    global PRINT_CONSOLE
    parser = argparse.ArgumentParser(description="Baseline Compatibility Scanner")
    parser.add_argument("path", help="Path to the project folder to scan")
    parser.add_argument("--features", default=None, help="Path to baseline features JSON")
    parser.add_argument("--json", action="store_true", help="Generate JSON report")
    parser.add_argument("--csv", action="store_true", help="Generate CSV report")
    parser.add_argument("--docx", action="store_true", help="Generate Word report")
    parser.add_argument("--pdf", action="store_true", help="Generate PDF report")
    parser.add_argument("--html", action="store_true", help="Generate HTML report")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    PRINT_CONSOLE = input(f"{Fore.CYAN}Do you want to print each folder's report on console? (y/n): {Style.RESET_ALL}").strip().lower() == "y"

    try:
        main(
            scan_path=args.path,
            features_file=args.features,
            generate_json=args.json,
            generate_csv=args.csv,
            generate_word=args.docx,
            generate_pdf=args.pdf,
            generate_html=args.html
        )

        logging.info("CLI SCAN COMPLETED SUCCESSFULLY")
    except Exception as e:
        print(f"{Fore.RED}An unexpected error occurred: {e}{Style.RESET_ALL}")
        logging.critical(f"An unhandled exception occurred: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logging.info("="*60 + "\n")

if __name__ == "__main__":
    run()