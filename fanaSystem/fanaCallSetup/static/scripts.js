document.getElementById('setup-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const formData = new FormData(this);

    fetch('/setup/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': formData.get('csrfmiddlewaretoken')
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('response').innerText = data.status === 'success' ? 'Setup completed successfully!' : `Error: ${data.message}`;
    })
    .catch(error => {
        document.getElementById('response').innerText = `Error: ${error}`;
    });
});
