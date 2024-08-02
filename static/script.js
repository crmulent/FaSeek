const fileInput = document.getElementById('fileInput');
const dropArea = document.getElementById('dropArea');
const imagePreview = document.getElementById('imagePreview');
let imageDataUrl = ''; // Variable to hold the image data URL


function processImage() {
    if (!imageDataUrl) {
        alert('No image to process!');
        return;
    }

    var form = document.createElement('form');
    form.method = 'POST';
    form.action = '/process_image';
    form.style.display = 'none';

    var input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'image_data';
    input.value = imageDataUrl.split(',')[1];
    form.appendChild(input);

    document.body.appendChild(form);
    form.submit();
}

document.onpaste = function (event) {
    var items = (event.clipboardData || event.originalEvent.clipboardData).items;
    for (var index in items) {
        var item = items[index];
        if (item.kind === 'file') {
            var blob = item.getAsFile();
            var reader = new FileReader();
            reader.onload = function (event) {
                imageDataUrl = event.target.result;
                displayImage(imageDataUrl);
            };
            reader.readAsDataURL(blob);
        }
    }
};

function displayImage(imageDataUrl) {
    var imgElement = document.getElementById('pasted-image');
    imgElement.src = imageDataUrl;
}

// Function to display image and set the imageDataUrl
function displayImage(imageDataUrl) {
    imagePreview.src = imageDataUrl;
    imagePreview.style.display = 'block';
}

// Function to handle image file and convert it to data URL
function handleImageFile(file) {
    const reader = new FileReader();
    reader.onload = function (event) {
        imageDataUrl = event.target.result; // Set the image data URL
        displayImage(imageDataUrl);
    };
    reader.readAsDataURL(file);
}

// Handle file input change event
fileInput.addEventListener('change', (event) => {
    const file = event.target.files[0];
    if (file) {
        handleImageFile(file);
    }
});

// Handle paste event
document.onpaste = function (event) {
    const items = (event.clipboardData || event.originalEvent.clipboardData).items;
    for (const index in items) {
        const item = items[index];
        if (item.kind === 'file') {
            const blob = item.getAsFile();
            handleImageFile(blob);
        }
    }
};

// Handle drop event
dropArea.addEventListener('drop', (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file) {
        handleImageFile(file);
    }
});

// Prevent default behavior for dragover
dropArea.addEventListener('dragover', (event) => {
    event.preventDefault();
});

function sidebar() {
    var x = document.getElementById("right-container");
    var computedStyle = window.getComputedStyle(x);

    if (computedStyle.display === "none") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }
}

function downloadAllImages() {
    fetch('/download_all_images')
        .then(response => {
            if (response.ok) {
                return response.blob();
            } else {
                throw new Error('Failed to download images');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}