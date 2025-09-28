# import sys
# import os
# import shutil
# import uuid
# from flask import Flask, render_template, request, url_for, jsonify, Response, stream_with_context
# from celery.result import AsyncResult

# # Add parent directory to path to import from the root
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# # Import the Celery app instance from the tasks module within the web_app package
# from web_app.tasks import celery, run_scan_task
# from werkzeug.utils import secure_filename

# app = Flask(__name__)
# # Use an environment variable for the secret key in production, with a fallback for development
# app.secret_key = os.environ.get("FLASK_SECRET_KEY", "a-default-dev-secret-key")
# app.config['UPLOAD_FOLDER'] = 'uploads'
# app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB upload limit

# @app.route('/', methods=['GET'])
# def index():
#     """Renders the main upload page."""
#     return render_template('index.html')

# @app.route('/upload', methods=['POST'])
# def upload():
#     """Handles folder uploads and starts the background scanning task."""
#     if 'project_files[]' not in request.files:
#         return jsonify({'error': 'No file part in the request.'}), 400
        
#     files = request.files.getlist('project_files[]')
#     if not files or not files[0].filename:
#         return jsonify({'error': 'No folder was selected.'}), 400

#     # Create a unique directory for this specific scan task
#     task_id = str(uuid.uuid4())
#     upload_path = os.path.join(app.config['UPLOAD_FOLDER'], task_id)
#     os.makedirs(upload_path, exist_ok=True)

#     for file in files:
#         if file and file.filename:
#             # Sanitize the relative path to prevent directory traversal attacks
#             relative_path = file.filename
#             path_parts = [secure_filename(part) for part in relative_path.split('/')]
#             safe_relative_path = os.path.join(*path_parts)
            
#             final_path = os.path.join(upload_path, safe_relative_path)
#             os.makedirs(os.path.dirname(final_path), exist_ok=True)
#             file.save(final_path)

#     # Start the background scan via Celery and get its task object
#     task = run_scan_task.delay(upload_path, task_id)
#     # Return the task ID to the client as JSON
#     return jsonify({'task_id': task.id})

# @app.route('/task_status/<task_id>')
# def task_status(task_id):
#     """Streams real-time status updates for a running task using Server-Sent Events."""
#     def generate():
#         task = AsyncResult(task_id, app=celery)
#         while task.state not in ['SUCCESS', 'FAILURE']:
#             status = task.info.get('status', task.state) if isinstance(task.info, dict) else task.state
#             yield f"data: {status}\n\n"
#             task = AsyncResult(task_id, app=celery)
        
#         yield f"data: {task.state}\n\n"

#         # Clean up uploaded files after the task is confirmed successful
#         if task.state == 'SUCCESS':
#             upload_path = os.path.join(app.config['UPLOAD_FOLDER'], task_id)
#             if os.path.exists(upload_path):
#                 shutil.rmtree(upload_path)
    
#     return Response(stream_with_context(generate()), mimetype='text/event-stream')

# @app.route('/results/<task_id>')
# def results(task_id):
#     """Renders the results page for a completed task."""
#     task = AsyncResult(task_id, app=celery)
#     if task.state == 'SUCCESS':
#         return render_template('results.html', report=task.info)
#     else:
#         # Provide a user-friendly message for other states
#         return "Task not found, is still running, or has failed.", 404

# if __name__ == '__main__':
#     # This block is only for local development (e.g., `py app.py`)
#     if not os.path.exists(app.config['UPLOAD_FOLDER']):
#         os.makedirs(app.config['UPLOAD_FOLDER'])
#     port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
#     app.run(host='0.0.0.0', port=port, debug=True)


import sys
import os
import shutil
import uuid
from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from celery.result import AsyncResult
from werkzeug.utils import secure_filename

# Add parent directory to path to import from the root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_app.tasks import celery, run_scan_task

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "a-default-dev-secret-key")
app.config['UPLOAD_FOLDER'] = 'uploads'
# Allow uploads up to 2 GB (adjust as needed)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024  # 2 GB

# -----------------------------
# Routes
# -----------------------------

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    """Handles folder uploads and starts the Celery task."""
    try:
        if 'project_files[]' not in request.files:
            return jsonify({'error': 'No file part in the request.'}), 400

        files = request.files.getlist('project_files[]')
        if not files or not files[0].filename:
            return jsonify({'error': 'No folder was selected.'}), 400

        task_id = str(uuid.uuid4())
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], task_id)
        os.makedirs(upload_path, exist_ok=True)

        for file in files:
            if file and file.filename:
                # Secure path
                safe_path = os.path.join(*[secure_filename(p) for p in file.filename.split('/')])
                final_path = os.path.join(upload_path, safe_path)
                os.makedirs(os.path.dirname(final_path), exist_ok=True)
                file.save(final_path)

        # Start Celery task
        task = run_scan_task.delay(upload_path)
        return jsonify({'task_id': task.id})
    except Exception as e:
        # Catch all errors and return JSON
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/task_status/<task_id>')
def task_status(task_id):
    """Streams real-time task status using Server-Sent Events."""
    def generate():
        try:
            task = AsyncResult(task_id, app=celery)
            while task.state not in ['SUCCESS', 'FAILURE']:
                status = task.info.get('status', task.state) if isinstance(task.info, dict) else task.state
                yield f"data: {status}\n\n"
                task = AsyncResult(task_id, app=celery)

            yield f"data: {task.state}\n\n"

            if task.state == 'SUCCESS':
                upload_path = os.path.join(app.config['UPLOAD_FOLDER'], task_id)
                if os.path.exists(upload_path):
                    shutil.rmtree(upload_path)
        except Exception as e:
            yield f"data: ERROR: {str(e)}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@app.route('/results/<task_id>')
def results(task_id):
    """Renders the results page."""
    try:
        task = AsyncResult(task_id, app=celery)
        if task.state == 'SUCCESS':
            return render_template('results.html', report=task.info)
        elif task.state == 'FAILURE':
            return jsonify({'error': 'Task failed. Check server logs.'}), 500
        else:
            return jsonify({'error': 'Task not finished yet.'}), 202
    except Exception as e:
        return jsonify({'error': f'Error fetching results: {str(e)}'}), 500

# -----------------------------
# Run Flask
# -----------------------------
if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    app.run(host='0.0.0.0', port=port, debug=True)
