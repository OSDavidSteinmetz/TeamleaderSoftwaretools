/**
 * Berechnet die ISO-Wochennummer für ein gegebenes Datum.
 * @param {Date} date - Das Datum, für das die Wochennummer berechnet werden soll.
 * @returns {number} Die ISO-Wochennummer.
 */
function getISOWeek(date) {
    const januaryFourth = new Date(date.getFullYear(), 0, 4);
    const millisecondsInDay = 86400000;
    return Math.ceil((((date - januaryFourth) / millisecondsInDay) + januaryFourth.getDay() + 1) / 7);
}

/**
 * Startet den Download der CSV-Datei.
 */
function downloadCSV() {
    window.location.href = '/download_illness_csv';
}

/**
 * Überprüft die Abwesenheit für das ausgewählte Datum und aktualisiert die Ansicht.
 */
function checkAbsenceForDate() {
    const loader = document.getElementById('loader');
    const table = document.getElementById('membersTable');
    const confirmButton = document.getElementById('confirmbutton');
    const dateInput = document.getElementById("date");
    const downloadButton = document.getElementById("download-button");
    const errorMessage = document.getElementById("error-message");

    loader.className = "loading";
    table.className = 'hidden';
    confirmButton.disabled = true;
    downloadButton.disabled = true;

    if (errorMessage) {
        errorMessage.className = 'hidden';
    }

    fetch('/illness.html', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            date: dateInput.value,
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.text();
    })
    .then(data => {
        // DOMParser zum Parsen des zurückgegebenen HTML-Strings verwenden
        const parser = new DOMParser();
        const doc = parser.parseFromString(data, 'text/html');

        // Den neuen Inhalt für den "box-content"-Bereich aus dem zurückgegebenen HTML holen
        const newBoxContent = doc.getElementById('box-content').innerHTML;

        // Nur den alten "box-content" mit dem neuen Inhalt ersetzen
        document.getElementById('box-content').innerHTML = newBoxContent;

        const membersTableBody = document.getElementById("membersTableBody");

        // Optional: Ladeanimation beenden, falls benötigt
        loader.className = "loaded";
        confirmButton.disabled = false;

        // Überprüfen, ob membersTableBody Kinder-Elemente hat
        if (membersTableBody.children.length > 0) {
            downloadButton.disabled = false;
        } else {
            downloadButton.disabled = true;
            errorMessage.classList.remove('hidden');
        }
    })
    .catch(error => {
        loader.className = "loaded";
        console.error('Error:', error);
    });
}

/**
 * Setzt das Datum um einen Tag oder eine Woche nach vorne.
 */
function setDateForward() {
    const dateInput = document.getElementById('date');
    let currentDate = new Date(dateInput.value);

    handleMonthForward(currentDate, dateInput);
}

/**
 * Setzt das Datum um einen Tag oder eine Woche zurück.
 */
function setDateBackward() {
    const dateInput = document.getElementById('date');
    let currentDate = new Date(dateInput.value);

    handleMonthBackward(currentDate, dateInput);
}

/**
 * Hilfsfunktion für setDateForward bei Monatsansicht.
 * @param {Date} currentDate - Das aktuelle Datum.
 * @param {string} selectedOption - Die ausgewählte Ansichtsoption.
 * @param {HTMLInputElement} dateInput - Das Datumseingabefeld.
 */
function handleMonthForward(currentDate, dateInput) {
    let [year, month] = dateInput.value.split('-').map(Number);
    currentDate = new Date(year, month - 1, 1);

    currentDate.setMonth(currentDate.getMonth() + 1);

    let newMonth = currentDate.getMonth() + 1; // JavaScript months are 0-indexed
    let newYear = currentDate.getFullYear();

    dateInput.value = `${newYear}-${('0' + newMonth).slice(-2)}`;
}

/**
 * Hilfsfunktion für setDateBackward bei Monatsansicht.
 * @param {Date} currentDate - Das aktuelle Datum.
 * @param {string} selectedOption - Die ausgewählte Ansichtsoption.
 * @param {HTMLInputElement} dateInput - Das Datumseingabefeld.
 */
function handleMonthBackward(currentDate, dateInput) {
    let [year, month] = dateInput.value.split('-').map(Number);
    currentDate = new Date(year, month - 1, 1);

    currentDate.setMonth(currentDate.getMonth() - 1);

    let newMonth = currentDate.getMonth() + 1; // JavaScript months are 0-indexed
    let newYear = currentDate.getFullYear();

    dateInput.value = `${newYear}-${('0' + newMonth).slice(-2)}`;
    };