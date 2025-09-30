import json

from pathlib import Path
from datetime import datetime
from tqdm import tqdm
from colorama import Fore, Style, init
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