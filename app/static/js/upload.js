/**
 * Startet den Download der Vorlage.
 */
function downloadTemplate() {
    window.location.href = '/download-template';
}

/**
 * Sendet das Formular ab.
 */
function submitForm() {
    document.getElementById('uploadForm').submit();
}

/**
 * Leitet zur Teamleader-Autorisierungsseite weiter.
 */
function redirectToTeamleader() {
    window.location.href = '/authorize-teamleader';
}

/**
 * Initiiert den Upload zu Teamleader und zeigt den Ladevorgang an.
 */
function uploadToTeamleader() {
    const confirmButton = document.getElementById('confirm-btn');
    const cancelButton = document.getElementById('cancel-btn');
    const loader = document.getElementById('loader');

    confirmButton.disabled = true;
    cancelButton.disabled = true;
    loader.className = "loading";

    window.location.href = '/upload-to-teamleader';
}

/**
 * Löscht die Daten und setzt die Benutzeroberfläche zurück.
 */
function clearData() {
    fetch('/clear-data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            resetUI();
        } else {
            console.error('Fehler beim Löschen der Daten:', data.message);
        }
    })
    .catch(error => console.error('Fehler:', error));
}

/**
 * Setzt die Benutzeroberfläche zurück.
 */
function resetUI() {
    const csvContentDiv = document.getElementById('csvContent');
    const fileInput = document.getElementById('csvFile');
    const clearButton = document.querySelector('.clear-button');
    const uploadButton = document.getElementById('uploadButton');

    csvContentDiv.innerHTML = '';
    fileInput.value = '';
    clearButton.disabled = true;
    uploadButton.disabled = true;
    document.getElementById('uploadForm').reset();
}

/**
 * Öffnet das Modal.
 */
function openModal() {
    document.getElementById('myModal').style.display = 'flex';
}

/**
 * Schließt das Modal.
 */
function closeModal() {
    document.getElementById('myModal').style.display = 'none';
}

/**
 * Lädt Zeiten hoch und zeigt eine Erfolgsmeldung an.
 */
function uploadTimes() {
    clearData();
    closeModal();
    document.getElementById('csvContent').innerHTML = '<p class="success-message">Die Zeiten wurden erfolgreich hochgeladen!</p>';
}

/**
 * Überprüft die Sichtbarkeit der Tabelle und aktualisiert den Zustand der Buttons.
 */
function checkTableVisibility() {
    const csvContentDiv = document.getElementById('csvContent');
    const tableExists = csvContentDiv.querySelector('table') !== null;
    const clearButton = document.querySelector('.clear-button');
    const uploadButton = document.getElementById('uploadButton');

    clearButton.disabled = !tableExists;
    uploadButton.disabled = !tableExists;
}