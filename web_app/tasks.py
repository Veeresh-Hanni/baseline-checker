import sys
import os
from celery import Celery
from pathlib import Path
# Add parent directory to path to import the original checker script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import scan_folder

# Configure the Celery app to connect to the Redis broker
celery = Celery(
    'tasks',
    broker=os.environ.get('CELERY_BROKER_URL', 'redis://127.0.0.1:6379/0'),
    backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://127.0.0.1:6379/0')
)


@celery.task(bind=True)
def run_scan_task(self, scan_path_str, features_file="config/baseline_data.json"):
    """
    Celery task that runs the baseline scan in the background.
    It updates its state, which the web app can monitor.
    """
    try:
        self.update_state(state='PROGRESS', meta={'status': 'Scanning project files...'})
        scan_path = Path(scan_path_str)
        # The scan_folder should return a dict-like report with keys:
        # baseline_features, non_baseline_features, total_files_scanned, etc.
        report_data = scan_folder(scan_path=scan_path, features_file=features_file)
        # Add the upload_path to the report_data so the web app can use it
        report_data['upload_path'] = scan_path_str
        # Optionally save an interim report
        # You can set more update_state calls during the scan if scan_folder reports progress
        return report_data
    except Exception as exc:
        # Provide failure info for debugging in the UI (shortened)
        return {'error': str(exc)}
