# Teamleader Softwaretools

**Teamleader Softwaretools** ist eine umfassende Plattform für Teammanagement und Produktivität, entwickelt mit Python und Flask. Die Anwendung läuft auf einem **SAP Business Technology Platform (BTP)** Server und bietet verschiedene Module zur Unterstützung von Teamleitern und Mitarbeitern bei der effizienten Organisation ihrer täglichen Aufgaben.

## Hauptfunktionen

- **Zeitbuchung erfassen**: Einfache Massenerfassung von per CSV-Dateiupload.
- **Zeitbuchung einsehen**: Überblick über die erfassten Zeiten der Mitarbeiter im PDF-Format.
- **Abwesenheiten einsehen**: Übersicht von Urlaub, Krankheit, Homeoffice und anderen Abwesenheiten.
- **Krankheitsstunden einsehen**: Tracking von krankheitsbedingten Ausfallzeiten über einen kompletten Monat.
- **Geburtstage**: Übersicht über Geburtstage im Team.
- **Projektübersicht**: Zentraler Überblick über laufende Projekte.
- **Mitarbeiter verwalten**: Verwaltung von Mitarbeiterdaten und -rechten.
- **Ticketsystem**: Integriertes System zur Verwaltung von Anfragen und Problemen im Bezug auf die Website.

## Technische Details

- **Backend**: Python mit Flask-Framework
- **Hosting**: SAP Business Technology Platform (BTP)
- **Datenbankverwaltung**: Derzeit noch mit JSON-Files, zukünftig gerne mit einer Datenbankanbindung, falls das in der BTP möglich ist.
- **Frontend**: Basic HTML, JS und CSS 

## Benutzeroberfläche

Jede App wird als einzelne kachel im Homescreen angezeigt. Die Apps können für einzelne User ausgeblendet werden, in dem man Ihnen die Berechtigung hierfür entzieht oder wieder erteilt.

## Zugriff und Sicherheit

- Webbasierter Zugriff über gängige Browser bevorzugt mit Chromium, da Firefox bspw. bei der Abwesenheitsübersicht im Wochenformat den Wocheinput nicht unterstützt.
- Sicheres Login-System über die Teamleader Focus Seite

## Ticketsystem

Das integrierte Ticketsystem ermöglicht:

- Erstellung und Verwaltung von Tickets (Fehler, die beim System sichtbar sind)
- Verbesserungsvorschläge für die einzelnen Apps/Funktionen

## Zielgruppe

Teamleader Softwaretools richtet sich primär an:

- Teamleiter und Heads
- Mitarbeiter in Teams

## Installation und Einrichtung

- .env-Datei erzeugen und mit den korrekten Informationen befüllen
- die Pfade von /static auf /app/static ändern.
- Port richtig angeben

## Systemanforderungen

- Hostingmöglichkeit
- Webbrowser (empfohlen: Microsoft Edge, Google Chrome, andere Chromiumbasierte Browser)

## Support und Wartung

Der Code ist gut dokumentiert und übersichtlich aufgebaut. Sollte daher gut verständlich sein und man kann sich gut einarbeiten.
Durch die relativ simple Bauweise mit Python, Flask, HTML, JS und CSS ist der Code auch nochmal leichter zu verstehen.

---