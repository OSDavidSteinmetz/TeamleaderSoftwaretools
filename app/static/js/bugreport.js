 const errorBubble = document.getElementById('errorBubble');
    const errorForm = document.getElementById('errorForm');
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('errorImages');
    const imagePreview = document.getElementById('imagePreview');

    function toggleBubble() {
        if (errorBubble.style.display === 'block') {
            hideBubble();
        } else {
            showBubble();
        }
    }

    function showBubble() {
        errorBubble.style.display = 'block';
    }

    function hideBubble() {
        errorBubble.style.display = 'none';
        resetForm();
    }

    function resetForm() {
        errorForm.reset();
        imagePreview.innerHTML = '';
    }

    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        handleFiles(e.dataTransfer.files);
    });

    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });

    document.addEventListener('paste', (e) => {
        const items = e.clipboardData.items;
        for (let i = 0; i < items.length; i++) {
            if (items[i].type.indexOf('image') !== -1) {
                const blob = items[i].getAsFile();
                handleFiles([blob]);
            }
        }
    });

function handleFiles(files) {
    for (let i = 0; i < files.length; i++) {
        if (files[i].type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const img = document.createElement('img');
                img.src = e.target.result;
                imagePreview.appendChild(img);
            };
            reader.readAsDataURL(files[i]);
        }
    }
}


errorForm.addEventListener('submit', function(e) {
    e.preventDefault();

    const title = document.getElementById('errorTitle').value;
    const text = document.getElementById('errorText').value;
    const images = imagePreview.getElementsByTagName('img');

    const formData = new FormData();
    formData.append('title', title);
    formData.append('text', text);

    const imageFiles = fileInput.files; // Use file input files directly
    for (let i = 0; i < imageFiles.length; i++) {
        formData.append('images', imageFiles[i], imageFiles[i].name);
    }

    fetch('/create_ticket', {
        method: 'POST',
        body: formData
    }).then(response => {
        if (response.ok) {
            showMessage('Ein Ticket mit dem Fehler wurde angelegt!', 'success');
            hideBubble();
        } else {
            showMessage('Das Ticket konnte nicht angelegt werden!', 'error');
        }
    }).catch(error => {
        console.error('Error:', error);
            showMessage('Das Ticket konnte nicht angelegt werden!', 'error');
    });
});

function showMessage(message, type) {
  const messageContainer = document.getElementById("message-container");
  const messageElement = document.createElement("div");
  messageElement.className = `message ${type}-message show`;
  messageElement.innerText = message;
  messageContainer.appendChild(messageElement);

  setTimeout(() => {
    messageElement.classList.remove("show");
    setTimeout(() => {
      messageContainer.removeChild(messageElement);
    }, 500);
  }, 2000);
}

