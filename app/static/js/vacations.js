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

let sortState = {
    column: null,
    direction: null // 'asc' or 'desc'
};

function sortTable(columnIndex) {
    const table = document.getElementById('membersTable');
    const tbody = table.getElementsByTagName('tbody')[0];
    const rows = Array.from(tbody.getElementsByTagName('tr'));
    
    // Bestimme Sortierrichtung
    if (sortState.column === columnIndex) {
        // Gleiche Spalte - Richtung umkehren
        sortState.direction = sortState.direction === 'asc' ? 'desc' : 'asc';
    } else {
        // Neue Spalte - standardmäßig aufsteigend
        sortState.column = columnIndex;
        sortState.direction = 'asc';
    }
    
    // Sortiere die Zeilen
    rows.sort((a, b) => {
        const aValue = parseInt(a.cells[columnIndex].textContent.trim());
        const bValue = parseInt(b.cells[columnIndex].textContent.trim());
        
        if (sortState.direction === 'asc') {
            return aValue - bValue;
        } else {
            return bValue - aValue;
        }
    });
    
    // Entferne alle Zeilen und füge sie in neuer Reihenfolge hinzu
    rows.forEach(row => tbody.removeChild(row));
    rows.forEach(row => tbody.appendChild(row));
    
    // Aktualisiere Sort-Indikatoren
    updateSortIndicators();
}

function updateSortIndicators() {
    // Alle Indikatoren zurücksetzen
    const indicators = document.querySelectorAll('.sort-indicator');
    indicators.forEach(indicator => {
        indicator.className = 'sort-indicator';
    });
    
    // Aktiven Indikator setzen
    if (sortState.column !== null) {
        const activeIndicator = document.getElementById(`sort-indicator-${sortState.column}`);
        if (activeIndicator) {
            activeIndicator.className = `sort-indicator ${sortState.direction}`;
        }
    }
}