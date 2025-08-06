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
        const parser = new DOMParser();
        const doc = parser.parseFromString(data, 'text/html');
        const newBoxContent = doc.getElementById('box-container').innerHTML;
        document.getElementById('box-container').innerHTML = newBoxContent;
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
        const currentDate = new Date(monthValue + "-01T23:59:00+02:00");
        const previousMonth = new Date(currentDate);
        previousMonth.setMonth(previousMonth.getMonth() - 1);

        firstBlockDate = new Date(previousMonth.getFullYear(), previousMonth.getMonth(), 16);
        secondBlockDate = new Date(previousMonth.getFullYear(), previousMonth.getMonth(), 26);
        thirdBlockDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), 5);
        endDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), 16);
    } else {
        firstBlockDate = new Date(monthValue + "-01T23:59:00+02:00");
        secondBlockDate = addDays(firstBlockDate, 10);
        thirdBlockDate = addDays(firstBlockDate, 20);
        endDate = new Date(firstBlockDate);
        endDate.setMonth(endDate.getMonth() + 1);
    }

    // firstBlockDate um einen Tag nach vorne schieben
    const adjustedFirstBlockDate = new Date(firstBlockDate);
    adjustedFirstBlockDate.setDate(adjustedFirstBlockDate.getDate() - 1);

    const dates = {
        first_tmstmp: formatDate(adjustedFirstBlockDate),
        second_tmstmp: formatDate(secondBlockDate),
        third_tmstmp: formatDate(thirdBlockDate),
        end_tmstmp: formatDate(endDate)
    };

    dates.end_tmstmp = dates.end_tmstmp.replace(/T23:59:00/, 'T00:00:00');
    
    if (selectedId === "-2") {
    } else if ([0, 2, 4, 6, 7, 9, 11].includes(firstBlockDate.getMonth())) {
        // Auch hier 00:00:00 Uhr verwenden statt 23:59:00
        const lastDayOfMonth = new Date(monthValue + "-31T00:00:00+02:00");
        dates.fourth_tmstmp = formatDate(lastDayOfMonth);
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
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}T23:59:00+02:00`;
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

    if (teamSelect.value === 'option16') {
        shortInfo.style.display = 'block';
    } else {
        shortInfo.style.display = 'none';
    }
}