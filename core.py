# ---------------- Main Scan ----------------
from pathlib import Path

from colorama import Fore, Style
from scanner.file_scanner import scan_folder
from scanner.filters import detect_frontend_framework
from scanner.utils import *
from reports.report_generator import *

def main(scan_path, features_file=None, generate_json=True, generate_csv=True, generate_word=True, generate_pdf=True, generate_html=True):
    features_dict = load_features(features_file)
    baseline_features = {name for name, info in features_dict.items() if info.get("status", {}).get("baseline") in ("high", "low")}
    all_feature_names = set(features_dict.keys())

    scan_path = Path(scan_path)
    if not scan_path.exists():
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Path {scan_path} does not exist.")
        logging.error(f"Scan path does not exist: {scan_path}")
        return

    total_files_scanned = 0
    cumulative_baseline = set()
    cumulative_non_baseline = set()
    folder_reports = []

    try:
        for folder in scan_path.iterdir():
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
                except Exception as e:
                    logging.warning(f"Error scanning folder {folder}: {e}")
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[INFO]{Style.RESET_ALL} Scan interrupted!")
        logging.warning("Scan interrupted by user")
        choice = input(f"{Fore.YELLOW}Stop scanning and save partial report? (y/n): {Style.RESET_ALL}").strip().lower()
        if choice == "y":
            report_data = {
                "total_files_scanned": total_files_scanned,
                "baseline_features": sorted(cumulative_baseline),
                "non_baseline_features": sorted(cumulative_non_baseline),
                "folders": folder_reports
            }
            save_json(report_data)
            save_word(report_data)
            print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Partial report saved as baseline_report.json and baseline_report.docx.")

    report_data = {
        "total_files_scanned": total_files_scanned,
        "baseline_features": sorted(cumulative_baseline),
        "non_baseline_features": sorted(cumulative_non_baseline),
        "folders": folder_reports
    }


    print(f"\n{Fore.GREEN}[INFO]{Style.RESET_ALL} Scan completed! Total files scanned: {Fore.YELLOW}{total_files_scanned}")
    print(f"{Fore.GREEN}✅ Baseline features used: {len(cumulative_baseline)}{Style.RESET_ALL}")
    print(f"{Fore.RED}❌ Non-Baseline features used: {len(cumulative_non_baseline)}{Style.RESET_ALL}\n")

    if generate_json: save_json(report_data)

    if generate_csv: save_csv(report_data)

    if generate_word: save_word(report_data)

    if generate_pdf: save_pdf(report_data)

    if generate_html: save_html(report_data)


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