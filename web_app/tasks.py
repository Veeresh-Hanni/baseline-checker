import sys
import os
from celery import Celery
from pathlib import Path

# Add parent directory to path to import the original checker script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from baseline_checker import scan_folder
from reports.report_generator import save_json, save_csv, save_word, save_pdf


# Configure the Celery app to connect to the Redis broker
celery = Celery(
    'tasks',
    broker=os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0'),
    backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')
)

@celery.task(bind=True)
def run_scan_task(self, scan_path_str, features_file="config/baseline_data.json"):
    """
    Celery task that runs the baseline scan in the background.
    It updates its state, which the web app can monitor.
    """
    self.update_state(state='PROGRESS', meta={'status': 'Scanning project files...'})
    
    scan_path = Path(scan_path_str)
    report_data = scan_folder(scan_path=scan_path, features_file=features_file)

    # Add the upload_path to the report_data so we can clean it up later
    report_data['upload_path'] = scan_path_str
    
    # The return value of the task is the final result, stored in the backend
    return report_data