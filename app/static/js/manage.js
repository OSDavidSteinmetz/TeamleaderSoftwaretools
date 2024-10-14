/**
 * Startet den Download der CSV-Datei.
 */
function downloadCSV() {
    window.location.href = '/download_times_csv';
}

/**
 * Sendet die ausgewählte ID an den Python-Backend und verarbeitet die Antwort.
 */
function sendSelectedIdToPython() {
    const user = document.getElementById('avatar-initials').innerHTML;
    if (user === "JK") {
        document.getElementById('audiofile').play();
    }

    updateUIBeforeSending();

    const teamSelect = document.getElementById('teamSelect');
    const selectedOption = teamSelect.options[teamSelect.selectedIndex];
    const teamName = selectedOption.innerHTML;
    const selectedId = selectedOption.getAttribute('id');
    const monthValue = document.getElementById('month').value;

    const dates = calculateDates(monthValue, selectedId);

    const requestBody = {
        selectedId: selectedId,
        selectedOption: selectedOption.value,
        team_name: teamName,
        selectedMonth: monthValue,
        ...dates
    };

    fetch('/manage-times.html', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
    })
    .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.text();
    })
    .then(data => {
        // DOMParser zum Parsen des zurückgegebenen HTML-Strings verwenden
        const parser = new DOMParser();
        const doc = parser.parseFromString(data, 'text/html');

        // Den neuen Inhalt für den "box-content"-Bereich aus dem zurückgegebenen HTML holen
        const newBoxContent = doc.getElementById('box-container').innerHTML;

        // Nur den alten "box-content" mit dem neuen Inhalt ersetzen
        document.getElementById('box-container').innerHTML = newBoxContent;

        // Optional: Ladeanimation beenden, falls benötigt
        loader.className = "loaded";
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

/**
 * Aktualisiert die UI-Elemente vor dem Senden der Anfrage.
 */
function updateUIBeforeSending() {
    const loader = document.getElementById('loader');
    loader.className = "loading";

    const confirmButton = document.getElementById('confirmbutton');
    confirmButton.disabled = true;

    try {
        const membersTable = document.getElementById('membersTable');
        if (membersTable) membersTable.className = 'hidden';
    } catch (error) {
        console.error('Error hiding members table:', error);
    }

    const downloadButtons = document.querySelectorAll('button.download-button');
    downloadButtons.forEach(button => button.disabled = true);
}

/**
 * Berechnet die erforderlichen Datumsangaben basierend auf dem ausgewählten Monat.
 * @param {string} monthValue - Der ausgewählte Monat im Format "YYYY-MM"
 * @returns {Object} Ein Objekt mit den berechneten Datumsangaben
 */
function calculateDates(monthValue, selectedId) {
    let firstBlockDate, secondBlockDate, thirdBlockDate, fourthBlockDate, endDate;

    if (selectedId === "-2") {
        // Calculate dates for the range 16th of previous month to 15th of current month
        const currentDate = new Date(monthValue + "-01T00:00:00+02:00");
        const previousMonth = new Date(currentDate);
        previousMonth.setMonth(previousMonth.getMonth() - 1);

        firstBlockDate = new Date(previousMonth.getFullYear(), previousMonth.getMonth(), 16);
        secondBlockDate = new Date(previousMonth.getFullYear(), previousMonth.getMonth(), 26);
        thirdBlockDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), 5);
        endDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), 16);
    } else {
        // Original logic for other cases
        firstBlockDate = new Date(monthValue + "-01T00:00:00+02:00");
        secondBlockDate = addDays(firstBlockDate, 10);
        thirdBlockDate = addDays(firstBlockDate, 20);
        endDate = new Date(firstBlockDate);
        endDate.setMonth(endDate.getMonth() + 1);
    }

    const dates = {
        first_tmstmp: formatDate(firstBlockDate),
        second_tmstmp: formatDate(secondBlockDate),
        third_tmstmp: formatDate(thirdBlockDate),
        end_tmstmp: formatDate(endDate)
    };

    // Check if we need to add a fourth timestamp
    if (selectedId === "-2") {
        // For the special case, we don't add a fourth timestamp
    } else if ([0, 2, 4, 6, 7, 9, 11].includes(firstBlockDate.getMonth())) {
        dates.fourth_tmstmp = formatDate(new Date(monthValue + "-31T00:00:00+02:00"));
    }

    return dates;
}

/**
 * Fügt einer gegebenen Anzahl von Tagen zu einem Datum hinzu.
 * @param {Date} date - Das Ausgangsdatum
 * @param {number} days - Die Anzahl der hinzuzufügenden Tage
 * @returns {Date} Das resultierende Datum
 */
function addDays(date, days) {
    const result = new Date(date);
    result.setDate(result.getDate() + days);
    return result;
}

/**
 * Formatiert ein Datum in den gewünschten String.
 * @param {Date} date - Das zu formatierende Datum
 * @returns {string} Das formatierte Datum
 */
function formatDate(date) {
    return date.toISOString().slice(0, 19) + "+02:00";
}

/**
 * Setzt das Datum um einen Monat nach vorne.
 */
function setDateForward() {
    const dateInput = document.getElementById('month');
    const teamSelect = document.getElementById('teamSelect');
    const teamName = teamSelect.options[teamSelect.selectedIndex].innerHTML;

    if (updateDate(dateInput, 1) && teamName !== "Team auswählen") {
        sendSelectedIdToPython();
    }
}

/**
 * Setzt das Datum um einen Monat zurück.
 */
function setDateBackward() {
    const dateInput = document.getElementById('month');
    const teamSelect = document.getElementById('teamSelect');
    const teamName = teamSelect.options[teamSelect.selectedIndex].innerHTML;

    if (updateDate(dateInput, -1) && teamName !== "Team auswählen") {
        sendSelectedIdToPython();
    }
}

/**
 * Aktualisiert das Datum im Eingabefeld.
 * @param {HTMLInputElement} dateInput - Das Datumseingabefeld
 * @param {number} monthsToAdd - Die Anzahl der hinzuzufügenden (oder abzuziehenden) Monate
 * @returns {boolean} True, wenn das Update erfolgreich war, sonst false
 */
function updateDate(dateInput, monthsToAdd) {
    const inputValue = dateInput.value;
    if (/^\d{4}-\d{2}$/.test(inputValue)) {
        const [year, month] = inputValue.split('-').map(Number);
        let currentDate = new Date(year, month - 1, 1);
        currentDate.setMonth(currentDate.getMonth() + monthsToAdd);
        dateInput.value = `${currentDate.getFullYear()}-${('0' + (currentDate.getMonth() + 1)).slice(-2)}`;
        return true;
    } else {
        console.error('Invalid date format. Expected YYYY-MM.');
        return false;
    }
}

/**
 * Aktiviert oder deaktiviert den Bestätigungsbutton basierend auf der Auswahl.
 */
function toggleConfirmButton() {
    const teamSelect = document.getElementById('teamSelect');
    const date = document.getElementById('month');
    const confirmButton = document.getElementById('confirmbutton');
    var shortInfo = document.getElementById('short_info');

    confirmButton.disabled = !(teamSelect.value && date.value);

    if (teamSelect.value === 'option14') {
        shortInfo.style.display = 'block';
    } else {
        shortInfo.style.display = 'none';
    }
}