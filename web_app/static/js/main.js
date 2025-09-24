// document.getElementById('project-form').addEventListener('submit', function (event) {
//     event.preventDefault();

//     // Explicitly define the API URL for the server
//     const apiUrl = "http://127.0.0.1:5000";

//     const formData = new FormData(this);
//     const uploadForm = document.getElementById('upload-form');
//     const loadingDiv = document.getElementById('loading');
//     const statusMessage = document.getElementById('status-message');

//     uploadForm.style.display = 'none';
//     loadingDiv.style.display = 'block';
//     statusMessage.textContent = 'Uploading files...';

//     fetch(`${apiUrl}/upload`, {
//         method: 'POST',
//         body: formData
//     })
//         .then(response => {
//             if (!response.ok) {
//                 // If the server returns an error, we can handle it here
//                 return response.json().then(err => { throw new Error(err.error || 'Server error'); });
//             }
//             return response.json();
//         })
//         .then(data => {
//             if (data.task_id) {
//                 statusMessage.textContent = 'Scan in progress...';
//                 // Listen for Server-Sent Events for status updates
//                 const source = new EventSource(`${apiUrl}/task_status/${data.task_id}`);

//                 source.onmessage = function (event) {
//                     const status = event.data;
//                     if (status === 'SUCCESS') {
//                         source.close();
//                         // Redirect to the results page when the scan is complete
//                         window.location.href = `${apiUrl}/results/${data.task_id}`;
//                     } else if (status === 'FAILURE') {
//                         source.close();
//                         alert('The scan failed. Please check the server logs for more details.');
//                         uploadForm.style.display = 'block';
//                         loadingDiv.style.display = 'none';
//                     } else {
//                         // Update the status message on the page
//                         statusMessage.textContent = `Status: ${status}`;
//                     }
//                 };

//                 source.onerror = function () {
//                     alert('Connection to the status stream failed. The server may have restarted. Please try again.');
//                     source.close();
//                     uploadForm.style.display = 'block';
//                     loadingDiv.style.display = 'none';
//                 };

//             } else {
//                 alert('Error starting scan: ' + (data.error || 'Unknown error from server'));
//                 uploadForm.style.display = 'block';
//                 loadingDiv.style.display = 'none';
//             }
//         })
//         .catch(error => {
//             console.error('Fetch Error:', error);
//             alert('Could not connect to the server. Please ensure it is running and accessible. Error: ' + error.message);
//             uploadForm.style.display = 'block';
//             loadingDiv.style.display = 'none';
//         });
// });


document.getElementById('project-form').addEventListener('submit', function (event) {
    event.preventDefault();

    const formData = new FormData(this);
    const uploadForm = document.getElementById('upload-form');
    const loadingDiv = document.getElementById('loading');
    const statusMessage = document.getElementById('status-message');

    uploadForm.style.display = 'none';
    loadingDiv.style.display = 'block';
    statusMessage.textContent = 'Uploading files...';

    // Use a relative URL. The browser will automatically use the correct host and port.
    // This is the correct way for production.
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
        .then(response => {
            if (!response.ok) {
                // If the server returns an error, we can handle it here
                return response.json().then(err => { throw new Error(err.error || 'Server error'); });
            }
            return response.json();
        })
        .then(data => {
            if (data.task_id) {
                statusMessage.textContent = 'Scan in progress...';
                // Listen for Server-Sent Events for status updates, also using a relative URL.
                const source = new EventSource(`/task_status/${data.task_id}`);

                source.onmessage = function (event) {
                    const status = event.data;
                    if (status === 'SUCCESS') {
                        source.close();
                        // Redirect to the results page when the scan is complete
                        window.location.href = `/results/${data.task_id}`;
                    } else if (status === 'FAILURE') {
                        source.close();
                        alert('The scan failed. Please check the server logs for more details.');
                        uploadForm.style.display = 'block';
                        loadingDiv.style.display = 'none';
                    } else {
                        // Update the status message on the page
                        statusMessage.textContent = `Status: ${status}`;
                    }
                };

                source.onerror = function () {
                    alert('Connection to the status stream failed. The server may have restarted. Please try again.');
                    source.close();
                    uploadForm.style.display = 'block';
                    loadingDiv.style.display = 'none';
                };

            } else {
                alert('Error starting scan: ' + (data.error || 'Unknown error from server'));
                uploadForm.style.display = 'block';
                loadingDiv.style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Fetch Error:', error);
            alert('Could not connect to the server. Please ensure it is running correctly. Error: ' + error.message);
            uploadForm.style.display = 'block';
            loadingDiv.style.display = 'none';
        });
});

