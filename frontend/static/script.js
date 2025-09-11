document.getElementById('extraction-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const pat = document.getElementById('pat').value;
    const statusDiv = document.getElementById('status-message');
    const submitButton = document.getElementById('submit-button');

    // Show loading state
    statusDiv.textContent = 'Starting workflow...';
    statusDiv.classList.add('show');
    submitButton.disabled = true;

    const requestBody = {
        username: username,
        pat: pat
    };

    try {
        const response = await fetch('/api/start_extraction', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody),
        });

        const result = await response.json();

        if (response.ok) {
            statusDiv.textContent = `Workflow started successfully! Workflow ID: ${result.workflow_id}`;
            statusDiv.style.backgroundColor = '#d4edda';
            statusDiv.style.color = '#155724';
        } else {
            statusDiv.textContent = `Error: ${result.error}`;
            statusDiv.style.backgroundColor = '#f8d7da';
            statusDiv.style.color = '#721c24';
        }
    } catch (error) {
        statusDiv.textContent = `An unexpected error occurred: ${error}`;
        statusDiv.style.backgroundColor = '#f8d7da';
        statusDiv.style.color = '#721c24';
    } finally {
        submitButton.disabled = false;
        setTimeout(() => {
            statusDiv.classList.remove('show');
        }, 10000);
    }
});