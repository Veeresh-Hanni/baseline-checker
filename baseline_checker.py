import json
from pathlib import Path
from tqdm import tqdm
from rich.console import Console
from reports.report_generator import save_csv, save_json, save_pdf, save_word

console = Console()

# Folders to skip during scanning
SKIP_FOLDERS = {"node_modules", ".git", "dist", "build", ".vscode", "__pycache__","$Recycle.Bin"}

def load_features(file_path="config/baseline_data.json"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        features_dict = data.get("features", {})
        console.print(f"[green][INFO][/green] Loaded {len(features_dict)} features")
        return features_dict
    except FileNotFoundError:
        console.print("[red][ERROR][/red] baseline_data.json not found!")
        return {}


def scan_file(file_path, all_features):
    """Scan a single file and return features found. Skip if inaccessible."""
    found = set()
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read().lower()
        for feat in all_features:
            if feat.lower() in content:
                found.add(feat)
    except Exception:
        pass  # silently skip unreadable files
    return found


def scan_folder(folder_path, all_features):
    """Scan all files in a folder recursively, skipping unnecessary folders"""
    folder_path = Path(folder_path)
    found_features = set()

    if not folder_path.exists():
        return found_features

    try:
        files = list(folder_path.rglob("*.*"))
    except Exception:
        return found_features  # skip inaccessible folder

    console.print(f"\n[cyan][INFO][/cyan] Scanning folder: {folder_path} ({len(files)} files)")

    for file in tqdm(files, desc="Files", unit="file", ncols=80, colour="green"):
        # Skip files inside unwanted folders
        if any(skip in file.parts for skip in SKIP_FOLDERS):
            continue
        found_features.update(scan_file(file, all_features))

    return found_features


def analyze_features(found_features, baseline_features):
    """Separate baseline and non-baseline features"""
    baseline_used = sorted([f for f in found_features if f in baseline_features])
    non_baseline_used = sorted([f for f in found_features if f not in baseline_features])
    return baseline_used, non_baseline_used


def main(scan_path, features_file="config/baseline_data.json", generate_json=False,
         generate_csv=False, generate_word=False, generate_pdf=False):
    
    features_dict = load_features(features_file)

    baseline_features = {
        name for name, info in features_dict.items()
        if info.get("status", {}).get("baseline") in ("high", "low")
    }
    all_feature_names = set(features_dict.keys())

    scan_path = Path(scan_path)
    if not scan_path.exists():
        console.print(f"[red][ERROR][/red] Path {scan_path} does not exist. Exiting.")
        return

    total_files_scanned = 0
    cumulative_baseline = set()
    cumulative_non_baseline = set()

    try:
        for folder in scan_path.iterdir():
            if folder.is_dir() and folder.name not in SKIP_FOLDERS:
                found_features = scan_folder(folder, all_feature_names)
                baseline_used, non_baseline_used = analyze_features(found_features, baseline_features)

                total_files_scanned += len(list(folder.rglob("*.*")))
                cumulative_baseline.update(baseline_used)
                cumulative_non_baseline.update(non_baseline_used)

                console.print(f"[green]✅ Baseline features used ({len(baseline_used)}):[/green] {', '.join(baseline_used)}")
                console.print(f"[red]❌ Non-Baseline features used ({len(non_baseline_used)}):[/red] {', '.join(non_baseline_used)}")
        
    except KeyboardInterrupt:
        console.print("\n[yellow][INFO][/yellow] Scan interrupted!")
        choice = input("Do you want to stop scanning? (y/n): ").strip().lower()
        if choice == "y":
            console.print("[red][INFO][/red] Scanning stopped by user.")
            r_choice = input("Do you want to save partial json report? (y/n): ").strip().lower()
            if r_choice == "y":
                partial_report = {
                "total_files_scanned": total_files_scanned,
                "baseline_features": sorted(cumulative_baseline),
                "non_baseline_features": sorted(cumulative_non_baseline)
            }

                save_json(partial_report)
                console.print("[yellow][INFO][/yellow] Partial report saved as baseline_report.json")
                return
        else:
            console.print("[green][INFO][/green] Resuming scan...")
            main(scan_path, features_file, generate_json, generate_csv, generate_word, generate_pdf)


        

    report_data = {
        "total_files_scanned": total_files_scanned,
        "baseline_features": sorted(cumulative_baseline),
        "non_baseline_features": sorted(cumulative_non_baseline)
    }

    if generate_json:
        save_json(report_data)
    if generate_csv:
        save_csv(report_data)
    if generate_word:
        save_word(report_data)
    if generate_pdf:
        save_pdf(report_data)


if __name__ == "__main__":
    
    import argparse
    
    import logging

    logging.basicConfig(
        filename="baseline_checker.log",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    logging.info("Scan started...")


    parser = argparse.ArgumentParser(description="Baseline Compatibility Scanner")
    parser.add_argument("path", help="Path to the project folder to scan")
    parser.add_argument("--features", default="config/baseline_data.json", help="Path to baseline features JSON")
    parser.add_argument("--json", action="store_true", help="Generate a JSON report")
    parser.add_argument("--csv", action="store_true", help="Generate a CSV report")
    parser.add_argument("--docx", action="store_true", help="Generate a Word (docx) report")
    parser.add_argument("--pdf", action="store_true", help="Generate a PDF report")

    args = parser.parse_args()

    main(
        scan_path=args.path,
        features_file=args.features,
        generate_json=args.json,
        generate_csv=args.csv,
        generate_word=args.docx,
        generate_pdf=args.pdf
    )