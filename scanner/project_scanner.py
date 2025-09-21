import os
import time
from tqdm import tqdm
from .filters import should_skip
from .file_scanner import scan_file

ALLOWED_EXT = {".py", ".js", ".json", ".html", ".css", ".md"}

def valid_file(path):
    return os.path.splitext(path)[1] in ALLOWED_EXT and not should_skip(path)

def walk_project(root):
    """Yield folder and valid files in it."""
    for current_dir, dirs, files in os.walk(root):
        # This is more efficient than the previous implementation
        dirs[:] = [d for d in dirs if not should_skip(os.path.join(current_dir, d))]
        
        folder_files = [os.path.join(current_dir, f) for f in files if valid_file(os.path.join(current_dir, f))]
        if folder_files:
            yield current_dir, folder_files

def scan_project_folderwise(root, baseline_features):
    """Scan project folder by folder, showing progress bar reaching 100% for each folder."""
    results = []

    # Use a list comprehension to get all folders and files first to have a better overall progress
    project_folders = list(walk_project(root))
    
    print(f"📂 Starting scan of project: {root}")
    with tqdm(total=len(project_folders), desc="Overall Progress", unit="folder", ncols=100) as pbar_total:
        for folder, files in project_folders:
            pbar_total.set_description(f"📂 Scanning folder: {os.path.basename(folder)}")
            num_files = len(files)
            
            with tqdm(total=num_files, desc=f"Folder: {os.path.basename(folder)}", unit="file", ncols=100, leave=False) as pbar_folder:
                for f in files:
                    results.append(scan_file(f, baseline_features))
                    pbar_folder.update(1)
                    time.sleep(0.05)  # small delay for smooth progress bar

            pbar_total.update(1)
        
    print("✅ Completed scanning all folders.")
    return results