document.getElementById('project-form').addEventListener('submit', function (event) {
  event.preventDefault();

  const formData = new FormData(this);
  const uploadForm = document.getElementById('upload-form');
  const loadingDiv = document.getElementById('loading');
  const statusMessage = document.getElementById('status-message');

  // Show loading spinner
  uploadForm.style.display = 'none';
  loadingDiv.style.display = 'block';
  statusMessage.textContent = 'Uploading files...';

  fetch('/upload', {
    method: 'POST',
    body: formData
  })
    .then(async response => {
      // Check if response is OK
      if (!response.ok) {
        // Try parsing JSON error, else fallback to text
        let errorText;
        try {
          const errJson = await response.json();
          errorText = errJson.error || JSON.stringify(errJson);
        } catch {
          errorText = await response.text();
        }
        throw new Error(`Server returned ${response.status}: ${errorText}`);
      }
      // Parse JSON if response is OK
      return response.json();
    })
    .then(data => {
      if (data.task_id) {
        statusMessage.textContent = 'Scan in progress...';
        const source = new EventSource(`/task_status/${data.task_id}`);

        source.onmessage = function (event) {
          const status = event.data;
          if (status === 'SUCCESS') {
            source.close();
            window.location.href = `/results/${data.task_id}`;
          } else if (status === 'FAILURE') {
            source.close();
            alert('The scan failed. Check server logs for details.');
            uploadForm.style.display = 'block';
            loadingDiv.style.display = 'none';
          } else {
            statusMessage.textContent = `Status: ${status}`;
          }
        };

        source.onerror = function () {
          alert('Connection lost to status stream. Try again.');
          source.close();
          uploadForm.style.display = 'block';
          loadingDiv.style.display = 'none';
        };
      } else {
        alert('Error starting scan: ' + (data.error || 'Unknown server error'));
        uploadForm.style.display = 'block';
        loadingDiv.style.display = 'none';
      }
    })
    .catch(error => {
      console.error('Fetch Error:', error);
      alert('Could not connect to the server. Error: ' + error.message);
      uploadForm.style.display = 'block';
      loadingDiv.style.display = 'none';
    });
});
