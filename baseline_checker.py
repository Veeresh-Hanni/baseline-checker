# import json
# from pathlib import Path
# from tqdm import tqdm
# from rich.console import Console
# from reports.report_generator import save_csv, save_json, save_pdf, save_word

# console = Console()

# # Folders to skip during scanning
# SKIP_FOLDERS = {"node_modules", ".git", "dist", "build", ".vscode", "__pycache__","$Recycle.Bin"}

# def load_features(file_path="config/baseline_data.json"):
#     try:
#         with open(file_path, "r", encoding="utf-8") as f:
#             data = json.load(f)
#         features_dict = data.get("features", {})
#         console.print(f"[green][INFO][/green] Loaded {len(features_dict)} features")
#         return features_dict
#     except FileNotFoundError:
#         console.print("[red][ERROR][/red] baseline_data.json not found!")
#         return {}


# def scan_file(file_path, all_features):
#     """Scan a single file and return features found. Skip if inaccessible."""
#     found = set()
#     try:
#         with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
#             content = f.read().lower()
#         for feat in all_features:
#             if feat.lower() in content:
#                 found.add(feat)
#     except Exception:
#         pass  # silently skip unreadable files
#     return found


# def scan_folder(folder_path, all_features):
#     """Scan all files in a folder recursively, skipping unnecessary folders"""
#     folder_path = Path(folder_path)
#     found_features = set()

#     if not folder_path.exists():
#         return found_features

#     try:
#         files = list(folder_path.rglob("*.*"))
#     except Exception:
#         return found_features  # skip inaccessible folder

#     console.print(f"\n[cyan][INFO][/cyan] Scanning folder: {folder_path} ({len(files)} files)")

#     for file in tqdm(files, desc="Files", unit="file", ncols=80, colour="green"):
#         # Skip files inside unwanted folders
#         if any(skip in file.parts for skip in SKIP_FOLDERS):
#             continue
#         found_features.update(scan_file(file, all_features))

#     return found_features


# def analyze_features(found_features, baseline_features):
#     """Separate baseline and non-baseline features"""
#     baseline_used = sorted([f for f in found_features if f in baseline_features])
#     non_baseline_used = sorted([f for f in found_features if f not in baseline_features])
#     return baseline_used, non_baseline_used


# def main(scan_path, features_file="config/baseline_data.json", generate_json=False,
#          generate_csv=False, generate_word=False, generate_pdf=False):
    
#     features_dict = load_features(features_file)

#     baseline_features = {
#         name for name, info in features_dict.items()
#         if info.get("status", {}).get("baseline") in ("high", "low")
#     }
#     all_feature_names = set(features_dict.keys())

#     scan_path = Path(scan_path)
#     if not scan_path.exists():
#         console.print(f"[red][ERROR][/red] Path {scan_path} does not exist. Exiting.")
#         return

#     total_files_scanned = 0
#     cumulative_baseline = set()
#     cumulative_non_baseline = set()

#     try:
#         for folder in scan_path.iterdir():
#             if folder.is_dir() and folder.name not in SKIP_FOLDERS:
#                 found_features = scan_folder(folder, all_feature_names)
#                 baseline_used, non_baseline_used = analyze_features(found_features, baseline_features)

#                 total_files_scanned += len(list(folder.rglob("*.*")))
#                 cumulative_baseline.update(baseline_used)
#                 cumulative_non_baseline.update(non_baseline_used)

#                 console.print(f"[green]✅ Baseline features used ({len(baseline_used)}):[/green] {', '.join(baseline_used)}")
#                 console.print(f"[red]❌ Non-Baseline features used ({len(non_baseline_used)}):[/red] {', '.join(non_baseline_used)}")
        
#     except KeyboardInterrupt:
#         console.print("\n[yellow][INFO][/yellow] Scan interrupted!")
#         choice = input("Do you want to stop scanning? (y/n): ").strip().lower()
#         if choice == "y":
#             console.print("[red][INFO][/red] Scanning stopped by user.")
#             r_choice = input("Do you want to save partial json report? (y/n): ").strip().lower()
#             if r_choice == "y":
#                 partial_report = {
#                 "total_files_scanned": total_files_scanned,
#                 "baseline_features": sorted(cumulative_baseline),
#                 "non_baseline_features": sorted(cumulative_non_baseline)
#             }

#                 save_json(partial_report)
#                 console.print("[yellow][INFO][/yellow] Partial report saved as baseline_report.json")
#                 return
#         else:
#             console.print("[green][INFO][/green] Resuming scan...")
#             main(scan_path, features_file, generate_json, generate_csv, generate_word, generate_pdf)


        

#     report_data = {
#         "total_files_scanned": total_files_scanned,
#         "baseline_features": sorted(cumulative_baseline),
#         "non_baseline_features": sorted(cumulative_non_baseline)
#     }

#     if generate_json:
#         save_json(report_data)
#     if generate_csv:
#         save_csv(report_data)
#     if generate_word:
#         save_word(report_data)
#     if generate_pdf:
#         save_pdf(report_data)


# if __name__ == "__main__":
    
#     import argparse
    
#     import logging

#     logging.basicConfig(
#         filename="baseline_checker.log",
#         level=logging.INFO,
#         format="%(asctime)s [%(levelname)s] %(message)s"
#     )
#     logging.info("Scan started...")


#     parser = argparse.ArgumentParser(description="Baseline Compatibility Scanner")
#     parser.add_argument("path", help="Path to the project folder to scan")
#     parser.add_argument("--features", default="config/baseline_data.json", help="Path to baseline features JSON")
#     parser.add_argument("--json", action="store_true", help="Generate a JSON report")
#     parser.add_argument("--csv", action="store_true", help="Generate a CSV report")
#     parser.add_argument("--docx", action="store_true", help="Generate a Word (docx) report")
#     parser.add_argument("--pdf", action="store_true", help="Generate a PDF report")

#     args = parser.parse_args()

#     main(
#         scan_path=args.path,
#         features_file=args.features,
#         generate_json=args.json,
#         generate_csv=args.csv,
#         generate_word=args.docx,
#         generate_pdf=args.pdf
#     )

import json
from pathlib import Path
from tqdm import tqdm
from rich.console import Console
import argparse
import logging
import re

# This file is now designed to be used as a library by the web app,
# but can still be run as a command-line tool.

# --- Library Functions ---

def load_features(file_path="config/baseline_data.json"):
    """Loads feature data from the specified JSON file."""
    logging.debug(f"Attempting to load features from: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        features_dict = data.get("features", {})
        logging.info(f"Successfully loaded {len(features_dict)} features from {file_path}")
        return features_dict
    except FileNotFoundError:
        logging.error(f"Features file not found at {file_path}")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from {file_path}: {e}")
        return {}

def scan_folder(folder_path, all_features):
    """
    Scans all files in a folder recursively and returns a set of all features found
    along with the count of files scanned.
    This version is optimized for background tasks and does not print to console.
    """
    folder = Path(folder_path)
    found_features = set()
    files_scanned_count = 0
    skip_folders = {"node_modules", ".git", "dist", "build", ".vscode", "__pycache__", "$Recycle.Bin"}

    if not folder.is_dir():
        logging.warning(f"Scan path {folder_path} is not a directory. Skipping.")
        return found_features, 0

    logging.info(f"Starting scan of directory: {folder_path}")
    for file_path in folder.rglob("*.*"):
        if any(skip in file_path.parts for skip in skip_folders):
            logging.debug(f"Skipping ignored path: {file_path}")
            continue
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read().lower()
            files_scanned_count += 1
            for feat in all_features:
                if re.search(rf"\b{re.escape(feat.lower())}\b", content):
                    found_features.add(feat)
        except Exception as e:
            logging.warning(f"Could not read file {file_path}: {e}")
            continue
            
    logging.info(f"Finished scan of {folder_path}. Scanned {files_scanned_count} files. Found {len(found_features)} unique features.")
    return found_features, files_scanned_count

def analyze_features(found_features, features_dict):
    """Separates found features into baseline and non-baseline categories."""
    logging.debug("Starting feature analysis...")
    baseline_features_set = {
        name for name, info in features_dict.items()
        if info.get("status", {}).get("baseline") in ("high", "low")
    }
    
    baseline_used = sorted(list(found_features.intersection(baseline_features_set)))
    non_baseline_used = sorted(list(found_features.difference(baseline_features_set)))
    
    logging.info(f"Analysis complete. Found {len(baseline_used)} baseline features and {len(non_baseline_used)} non-baseline features.")
    return baseline_used, non_baseline_used

# --- Command-Line Interface (CLI) Functionality ---

def run_as_cli(scan_path_str, generate_json=False, generate_csv=False, generate_word=False, generate_pdf=False):
    """Runs the full scan and report generation process for the command line."""
    from reports.report_generator import save_csv, save_json, save_pdf, save_word
    console = Console()
    
    scan_path = Path(scan_path_str)
    if not scan_path.exists():
        console.print(f"[red][ERROR][/red] Path {scan_path} does not exist. Exiting.")
        logging.error(f"Scan path {scan_path} does not exist. Exiting CLI run.")
        return

    console.print("[green]Loading features...[/green]")
    features_dict = load_features()
    if not features_dict:
        console.print("[red]Could not load features. Exiting.[/red]")
        logging.error("Could not load features dictionary. Exiting CLI run.")
        return
        
    all_feature_names = set(features_dict.keys())

    console.print(f"[cyan]Scanning folder: {scan_path}...[/cyan]")
    
    # Use tqdm for a better user experience in the command line
    found_features, files_scanned_count = scan_folder(scan_path, all_feature_names)

    baseline_used, non_baseline_used = analyze_features(found_features, features_dict)
    
    report_data = {
        "total_files_scanned": files_scanned_count,
        "baseline_features": baseline_used,
        "non_baseline_features": non_baseline_used
    }
    
    console.print(f"\n[green]✅ Baseline features found ({len(baseline_used)}):[/green] {', '.join(baseline_used)}")
    console.print(f"[red]❌ Non-Baseline features found ({len(non_baseline_used)}):[/red] {', '.join(non_baseline_used)}")

    if generate_json:
        logging.info("Generating JSON report...")
        save_json(report_data)
    if generate_csv:
        logging.info("Generating CSV report...")
        save_csv(report_data)
    if generate_word:
        logging.info("Generating Word report...")
        save_word(report_data)
    if generate_pdf:
        logging.info("Generating PDF report...")
        save_pdf(report_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Baseline Compatibility Scanner")
    parser.add_argument("path", help="Path to the project folder to scan")
    parser.add_argument("--json", action="store_true", help="Generate a JSON report")
    parser.add_argument("--csv", action="store_true", help="Generate a CSV report")
    parser.add_argument("--docx", action="store_true", help="Generate a Word (docx) report")
    parser.add_argument("--pdf", action="store_true", help="Generate a PDF report")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose DEBUG logging")
    args = parser.parse_args()

    # Configure logging based on verbosity
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        filename="baseline_checker.log",
        level=log_level,
        format="%(asctime)s - %(levelname)-8s - %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S',
        filemode='a' # Append to the log file instead of overwriting
    )
    
    logging.info("="*50)
    logging.info("CLI SCAN INITIATED")
    logging.info(f"Arguments passed: {vars(args)}")

    run_as_cli(
        scan_path_str=args.path,
        generate_json=args.json,
        generate_csv=args.csv,
        generate_word=args.docx,
        generate_pdf=args.pdf
    )

    logging.info("CLI SCAN COMPLETED")
    logging.info("="*50 + "\n")

