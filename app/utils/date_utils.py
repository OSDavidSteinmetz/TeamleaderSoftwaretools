from datetime import datetime
from typing import Dict, Union

# Mapping von englischen zu deutschen Wochentag-Abkürzungen
WEEKDAY_MAPPING: Dict[str, str] = {
    "Mon": "Mo",
    "Tue": "Di",
    "Wed": "Mi",
    "Thu": "Do",
    "Fri": "Fr",
    "Sat": "Sa",
    "Sun": "So",
}

def calculate_total_hours(start_time: str, end_time: str) -> Union[float, None]:
    """
    Berechnet die Gesamtstunden zwischen zwei Zeitpunkten.

    Args:
        start_time (str): Startzeit im Format "HH:MM".
        end_time (str): Endzeit im Format "HH:MM".

    Returns:
        Union[float, None]: Gesamtstunden als Float auf zwei Dezimalstellen gerundet,
                            oder None bei ungültigen Eingaben.

    Raises:
        ValueError: Wenn das Zeitformat ungültig ist.
    """
    try:
        start = datetime.strptime(start_time, "%H:%M")
        end = datetime.strptime(end_time, "%H:%M")

        if end < start:
            raise ValueError("Endzeit kann nicht vor Startzeit liegen.")

        delta = end - start
        total_hours = delta.total_seconds() / 3600.0  # Umrechnung von Sekunden in Stunden
        return round(total_hours, 2)  # Runden auf zwei Dezimalstellen

    except ValueError as e:
        print(f"Fehler bei der Zeitberechnung: {e}")
        return None

def get_german_weekday(date_str: str) -> Union[str, None]:
    """
    Konvertiert ein Datum in die deutsche Wochentag-Abkürzung.

    Args:
        date_str (str): Datum im Format "DD.MM.YYYY".

    Returns:
        Union[str, None]: Deutsche Wochentag-Abkürzung oder None bei ungültiger Eingabe.

    Raises:
        ValueError: Wenn das Datumsformat ungültig ist.
    """
    try:
        date_obj = datetime.strptime(date_str, "%d.%m.%Y")
        english_weekday = date_obj.strftime("%a")
        return WEEKDAY_MAPPING.get(english_weekday, english_weekday)
    except ValueError as e:
        print(f"Fehler bei der Datumskonvertierung: {e}")
        return None