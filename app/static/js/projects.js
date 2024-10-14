/**
 * Filtert die Projekttabelle basierend auf dem Suchfeld-Input.
 */
function filterTable() {
    const input = document.getElementById("searchField");
    const filter = input.value.toUpperCase();
    const table = document.getElementById("projectsTable");
    const rows = table.getElementsByTagName("tr");

    for (let i = 0; i < rows.length; i++) {
        const firstCell = rows[i].getElementsByTagName("td")[0];
        if (firstCell) {
            const textValue = firstCell.textContent || firstCell.innerText;
            rows[i].style.display = textValue.toUpperCase().indexOf(filter) > -1 ? "" : "none";
        }
    }
}

/**
 * Leert das Suchfeld und setzt die Tabellenansicht zurück.
 */
function clearSearch() {
    document.getElementById("searchField").value = "";
    filterTable();
}

/**
 * Sendet eine Anfrage zum Aktualisieren der Projekte und verarbeitet die Antwort.
 */
function updateProjects() {
    fetch('/update_projects', {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        handleUpdateResponse(data);
    })
    .catch((error) => {
        showMessage('Ein Fehler ist aufgetreten: ' + error, 'error');
        console.error('Error:', error);
    });
}

/**
 * Verarbeitet die Antwort der Projekt-Aktualisierung und zeigt eine entsprechende Nachricht an.
 * @param {Object} data - Die Antwortdaten vom Server
 */
function handleUpdateResponse(data) {
    switch(data.status) {
        case 'success':
            showMessage('Projekte erfolgreich aktualisiert', 'success');
            break;
        case 'info':
            showMessage('Es gab keine neuen Änderungen', 'info');
            break;
        default:
            showMessage('Fehler beim Aktualisieren der Projekte: ' + data.message, 'error');
    }
}

/**
 * Zeigt eine Nachricht an und leitet dann zur Projektseite weiter.
 * @param {string} message - Die anzuzeigende Nachricht
 * @param {string} type - Der Typ der Nachricht ('success', 'info', oder 'error')
 */
function showMessage(message, type) {
    const messageContainer = document.getElementById('message-container');
    const messageElement = document.createElement('div');
    messageElement.className = `message ${type}-message show`;
    messageElement.innerText = message;
    messageContainer.appendChild(messageElement);

    setTimeout(() => {
        messageElement.classList.remove('show');
        setTimeout(() => {
            messageContainer.removeChild(messageElement);
            window.location.href = '/projects.html';
        }, 500);
    }, 2000);
}

/**
 * Startet den Download der JSON-Datei.
 */
function downloadJson() {
    window.location.href = '/download-json';
}