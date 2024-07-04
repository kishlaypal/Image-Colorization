document.getElementById('fileInput').addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById('preview');
            preview.src = e.target.result;
            preview.style.display = 'block';


            const colorizedImage = document.getElementById('colorizedImage');
            colorizedImage.style.display = 'none';
            colorizedImage.src = '';

            const downloadButton = document.getElementById('downloadButton');
            downloadButton.style.display = 'none';
            downloadButton.href = '';
        };
        reader.readAsDataURL(file);
    }
});

document.getElementById('changeButton').addEventListener('click', function() {
    const fileInput = document.getElementById('fileInput');
    fileInput.click();
});

document.getElementById('colorizeButton').addEventListener('click', function() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    if (!file) {
        alert("Please select an image first.");
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    fetch('/colorize', {
        method: 'POST',
        body: formData
    })
    .then(response => response.blob())
    .then(blob => {
        const url = URL.createObjectURL(blob);
        const colorizedImage = document.getElementById('colorizedImage');
        colorizedImage.src = url;
        colorizedImage.style.display = 'block';

        const preview = document.getElementById('preview');
        preview.style.display = 'none';


        const downloadButton = document.getElementById('downloadButton');
        downloadButton.href = url;
        downloadButton.style.display = 'inline-block';
        downloadButton.setAttribute('download', 'colorized_image.jpg');
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
