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
 * Ändert die Ansicht basierend auf der ausgewählten Option (Tag, Woche, Monat).
 */
function changeView() {
    const today = new Date();
    const currentYear = today.getFullYear();
    const currentMonth = (today.getMonth() + 1).toString().padStart(2, '0');
    const currentDay = today.getDate().toString().padStart(2, '0');
    const viewSelect = document.getElementById("viewSelect");
    const selectedOption = viewSelect.options[viewSelect.selectedIndex].value;
    const dateInput = document.getElementById("date");

    switch (selectedOption) {
        case "day":
            dateInput.type = "date";
            dateInput.value = `${currentYear}-${currentMonth}-${currentDay}`;
            break;
        case "week":
            dateInput.type = "week";
            dateInput.value = `${currentYear}-W${getISOWeek(today).toString().padStart(2, '0')}`;
            break;
        case "month":
            dateInput.type = "month";
            dateInput.value = `${currentYear}-${currentMonth}`;
            break;
        default:
            dateInput.type = "date";
            dateInput.value = `${currentYear}-${currentMonth}-${currentDay}`;
            break;
    }
}

/**
 * Zeigt nur den ausgewählten Tag an und versteckt die anderen.
 * @param {string} selectedDay - Das ausgewählte Datum im Format 'YYYY-MM-DD'.
 */
function showCurrentDay(selectedDay) {
    const selDate = new Date(selectedDay);
    const dayNames = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"];
    const currentDayName = dayNames[selDate.getDay()];

    const days = document.querySelectorAll('.day');
    days.forEach(day => {
        day.style.display = day.id === currentDayName ? "block" : "none";
    });
}

/**
 * Zeigt alle Tage der aktuellen Woche an.
 */
function showCurrentWeek() {
    const days = document.querySelectorAll('.day');
    days.forEach(day => {
        day.style.display = "block";
    });
}

/**
 * Überprüft die Abwesenheit für das ausgewählte Datum und aktualisiert die Ansicht.
 */
function checkAbsenceForDate() {
    const loader = document.getElementById('loader');
    const table = document.getElementById('calendar');
    const confirmButton = document.getElementById('confirmbutton');
    const dateInput = document.getElementById("date");

    loader.className = "loading";
    table.className = 'hidden';
    confirmButton.disabled = true;

    fetch('/absence.html', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            date: dateInput.value,
            inputType: dateInput.type
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

        // Optional: Ladeanimation beenden, falls benötigt
        loader.className = "loaded";
        confirmButton.disabled = false;
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
    const viewSelect = document.getElementById("viewSelect");
    const selectedOption = viewSelect.options[viewSelect.selectedIndex].value;
    let currentDate = new Date(dateInput.value);

    if (/^\d{4}-W\d{2}$/.test(dateInput.value)) {
        handleWeekForward(currentDate, selectedOption, dateInput);
    } else {
        handleDateForward(currentDate, selectedOption, dateInput);
    }

    checkAbsenceForDate();
}

/**
 * Setzt das Datum um einen Tag oder eine Woche zurück.
 */
function setDateBackward() {
    const dateInput = document.getElementById('date');
    const viewSelect = document.getElementById("viewSelect");
    const selectedOption = viewSelect.options[viewSelect.selectedIndex].value;
    let currentDate = new Date(dateInput.value);

    if (/^\d{4}-W\d{2}$/.test(dateInput.value)) {
        handleWeekBackward(currentDate, selectedOption, dateInput);
    } else {
        handleDateBackward(currentDate, selectedOption, dateInput);
    }

    checkAbsenceForDate();
}

/**
 * Hilfsfunktion für setDateForward bei Wochenansicht.
 * @param {Date} currentDate - Das aktuelle Datum.
 * @param {string} selectedOption - Die ausgewählte Ansichtsoption.
 * @param {HTMLInputElement} dateInput - Das Datumseingabefeld.
 */
function handleWeekForward(currentDate, selectedOption, dateInput) {
    let [year, week] = dateInput.value.split('-W').map(Number);
    currentDate = new Date(year, 0, (week - 1) * 7 + 1);
    adjustToWeekStart(currentDate);

    if (selectedOption === "week") {
        currentDate.setDate(currentDate.getDate() + 7);
    } else {
        currentDate.setDate(currentDate.getDate() + 1);
    }

    let newWeekNum = getISOWeek(currentDate);
    let newYear = currentDate.getFullYear();

    // Überprüfen, ob wir ins nächste Jahr wechseln müssen
    if (week === 52 && newWeekNum === 53) {
        newYear++;
        newWeekNum = 1;
    }

    dateInput.value = `${newYear}-W${('0' + newWeekNum).slice(-2)}`;
}

/**
 * Hilfsfunktion für setDateBackward bei Wochenansicht.
 * @param {Date} currentDate - Das aktuelle Datum.
 * @param {string} selectedOption - Die ausgewählte Ansichtsoption.
 * @param {HTMLInputElement} dateInput - Das Datumseingabefeld.
 */
function handleWeekBackward(currentDate, selectedOption, dateInput) {
    let [year, week] = dateInput.value.split('-W').map(Number);
    currentDate = new Date(year, 0, (week - 1) * 7 + 1);
    adjustToWeekStart(currentDate);

    if (selectedOption === "week") {
        currentDate.setDate(currentDate.getDate() - 7);
    } else {
        currentDate.setDate(currentDate.getDate() - 1);
    }

    let newWeekNum = getISOWeek(currentDate);
    let newYear = currentDate.getFullYear();

    // Überprüfen, ob wir ins vorherige Jahr wechseln müssen
    if (newWeekNum === 53) {
        newWeekNum = 1;
        newYear++;
    }

    dateInput.value = `${newYear}-W${('0' + newWeekNum).slice(-2)}`;
}

/**
 * Hilfsfunktion für setDateForward bei Tagesansicht.
 * @param {Date} currentDate - Das aktuelle Datum.
 * @param {string} selectedOption - Die ausgewählte Ansichtsoption.
 * @param {HTMLInputElement} dateInput - Das Datumseingabefeld.
 */
function handleDateForward(currentDate, selectedOption, dateInput) {
    if (selectedOption === "week") {
        currentDate.setDate(currentDate.getDate() + 7);
    } else {
        currentDate.setDate(currentDate.getDate() + 1);
    }
    dateInput.value = currentDate.toISOString().split('T')[0];
}

/**
 * Hilfsfunktion für setDateBackward bei Tagesansicht.
 * @param {Date} currentDate - Das aktuelle Datum.
 * @param {string} selectedOption - Die ausgewählte Ansichtsoption.
 * @param {HTMLInputElement} dateInput - Das Datumseingabefeld.
 */
function handleDateBackward(currentDate, selectedOption, dateInput) {
    if (selectedOption === "week") {
        currentDate.setDate(currentDate.getDate() - 7);
    } else {
        currentDate.setDate(currentDate.getDate() - 1);
    }
    dateInput.value = currentDate.toISOString().split('T')[0];
}

/**
 * Passt das Datum auf den Beginn der Woche an.
 * @param {Date} date - Das anzupassende Datum.
 */
function adjustToWeekStart(date) {
    if (date.getDay() <= 4) {
        date.setDate(date.getDate() - date.getDay() + 1);
    } else {
        date.setDate(date.getDate() + 8 - date.getDay());
    }
}

document.addEventListener('keydown', function(event) {
    if (event.key === 'F5') {
        event.preventDefault(); // Verhindert das Standard-Verhalten (Seite neu laden)
        checkAbsenceForDate(); // Ruft stattdessen die checkAbsenceForDate-Funktion auf
    }
});
