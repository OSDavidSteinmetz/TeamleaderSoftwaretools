import csv
import io
import json
import locale
import os
import tempfile
import time
from datetime import date, datetime, timedelta

import requests
from config import Config
from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
)
from utils.csv_utils import group_by_date, parse_csv, save_illness_table_to_csv
from utils.date_utils import calculate_total_hours
from utils.teamleader_utils import (
    get_all_users,
    get_contact_info,
    get_number_of_absence_days,
    get_number_of_illness_days,
    get_projects,
    get_special_working_hours,
    get_teamleader_teams,
    get_teamleader_token,
    get_teamleader_user,
    get_teamleader_user_info,
    get_teamleader_user_times,
    get_user_absence,
    refresh_teamleader_token,
)
from utils.technical_utils import (
    download_file,
    refresh_token_code,
    update_flag_in_code_json,
    upload_file,
)
from werkzeug.utils import secure_filename

app = Flask(__name__)
port = int(os.environ.get("PORT", 3000))
app.secret_key = (
    Config.SECRET_KEY
)  # Setze einen geheimen Schlüssel für die Sitzungsverwaltung
locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")


def handle_token_refresh():
    username = session.get("username")
    initials = session.get("initials")
    try:
        refresh_teamleader_token(
            Config.CLIENT_ID, Config.CLIENT_SECRET, session.get("refresh_token")
        )
    except Exception as e:
        error_message = "Token ist abgelaufen. Melden Sie sich erneut an."
        return render_template(
            "error.html",
            error_message=error_message,
            username=username,
            initials=initials,
        )
    return None


def load_whitelist():
    with open("app/static/data/whitelist.json", "r", encoding="utf-8") as f:
        return json.load(f)


def load_worktype():
    with open("app/static/data/worktype.json", "r", encoding="utf-8") as f:
        return json.load(f)


@app.route("/")
def home():
    user_id = session.get("userId")

    if user_id:
        username = session.get("username")
        initials = session.get("initials")
        whitelist = load_whitelist()
        user_permissions = next(
            (user for user in whitelist if user["id"] == user_id), None
        )
        session["user_permissions"] = user_permissions

        if user_permissions:
            return render_template(
                "index.html",
                username=user_permissions["employee"],
                upload_times=user_permissions["upload_times"],
                manage_times=user_permissions["manage_times"],
                absence=user_permissions["absence"],
                illness=user_permissions["illness"],
                birthday=user_permissions["birthday"],
                projects=user_permissions["projects"],
                authorizations=user_permissions["authorizations"],
                initials=initials,
            )

    return render_template("index.html")


@app.route("/authorizations.html")
def authorizations():
    error_redirect = handle_token_refresh()
    if error_redirect:
        return error_redirect

    username = session.get("username")
    initials = session.get("initials")
    access_token = session.get("access_token")

    user_permissions = session.get("user_permissions", {})
    if not user_permissions.get("authorizations", False):
        return render_template("error.html", username=username, initials=initials)

    user_list = get_all_users(access_token)

    if user_list != None:
        with open("app/static/data/whitelist.json", "w", encoding="utf-8") as file:
            json.dump(user_list, file, ensure_ascii=False, indent=4)
    else:
        return render_template("error.html", username=username, initials=initials)

    return render_template(
        "authorizations.html", username=username, initials=initials, user_list=user_list
    )


@app.route("/error.html")
def error():
    username = session.get("username")
    initials = session.get("initials")
    return render_template("error.html", username=username, initials=initials)


@app.route("/projects.html")
def projects():
    error_redirect = handle_token_refresh()
    if error_redirect:
        return error_redirect

    username = session.get("username")
    initials = session.get("initials")

    user_permissions = session.get("user_permissions", {})
    if not user_permissions.get("authorizations", False):
        return render_template("error.html", username=username, initials=initials)

    # Loading whitelist data from whitelist.json
    with open("app/static/data/projects.json", "r", encoding="utf-8") as f:
        projects = json.load(f)

    return render_template(
        "projects.html", username=username, initials=initials, projects=projects
    )


@app.route("/update_projects", methods=["POST", "GET"])
def updateProjects():
    error_redirect = handle_token_refresh()
    if error_redirect:
        return error_redirect

    username = session.get("username")
    initials = session.get("initials")
    access_token = session.get("access_token")

    user_permissions = session.get("user_permissions", {})
    if not user_permissions.get("authorizations", False):
        return render_template("error.html", username=username, initials=initials)

    projects = get_projects(access_token)

    if projects == []:
        try:
            with open("app/static/data/projects.json", "w", encoding="utf-8") as file:
                json.dump(projects, file, ensure_ascii=False, indent=4)

            return jsonify({"status": "success"})

        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
    else:
        return jsonify({"status": "info"})


@app.route("/birthday.html", methods=["POST", "GET"])
def birthday():
    error_redirect = handle_token_refresh()
    if error_redirect:
        return error_redirect

    username = session.get("username")
    initials = session.get("initials")
    access_token = session.get("access_token")
    date = datetime.today().date().strftime("%d.%m.%Y")
    user_permissions = session.get("user_permissions", {})
    members = get_contact_info(access_token)

    if not user_permissions.get("birthday", False):
        return render_template("error.html", username=username, initials=initials)
    return render_template(
        "birthday.html",
        username=username,
        initials=initials,
        date=date,
        members=members,
    )


@app.route("/emergency.html", methods=["GET"])
def emergency():
    max_attempts = 3
    attempts = 0
    access_token = None
    
    while attempts < max_attempts:
        try:
            download_file()
            # Überprüfen, ob die Datei existiert
            if not os.path.exists("app/static/data/code.json"):
                raise FileNotFoundError("Die Datei code.json wurde nicht gefunden.")

            # code.json auslesen und das Flag überprüfen
            with open("app/static/data/code.json", "r", encoding="utf-8") as f:
                tokens = json.load(f)

            if tokens.get("flag") == True:
                # Wenn das Flag auf True steht, 10 Sekunden warten und die Schleife fortsetzen
                time.sleep(10)
                attempts += 1
                continue
            else:
                # Wenn das Flag auf False steht, kritischen Bereich mit try-finally absichern
                try:
                    # Flag auf True setzen
                    update_flag_in_code_json(True)
                    upload_file()
                    
                    try:
                        # Kritischer Bereich, der geschützt werden soll
                        refresh_token_code()
                        with open("app/static/data/code.json", "r", encoding="utf-8") as f:
                            tokens = json.load(f)
                        access_token = tokens["access_token"]
                        break  # Erfolgreich, Schleife verlassen
                    finally:
                        # Wird immer ausgeführt, auch bei Ausnahmen im try-Block
                        update_flag_in_code_json(False)
                        upload_file()
                        
                except Exception as inner_e:
                    print(f"Fehler im kritischen Bereich: {inner_e}")
                    # Wir sind hier, wenn ein Fehler beim Setzen/Zurücksetzen der Flag auftritt
                    # Die Flag sollte bereits zurückgesetzt sein, wenn nicht, versuchen wir es noch einmal
                    try:
                        update_flag_in_code_json(False)
                        upload_file()
                    except:
                        pass
                    attempts += 1
                    time.sleep(5)

        except Exception as e:
            print(f"Allgemeiner Fehler: {e}")
            attempts += 1
            if attempts >= max_attempts:
                break
            time.sleep(5)

    # Wenn wir keinen Access-Token haben nach den Versuchen oder bei Fehler
    if not access_token:
        error_redirect = handle_token_refresh()
        if error_redirect:
            return error_redirect
        access_token = session.get("access_token")

    username = session.get("username")
    initials = session.get("initials")

    holidays = set(
        [
            "Neujahr",
            "Heilige Drei Könige",
            "Karfreitag",
            "Ostermontag",
            "Tag der Arbeit",
            "Christi Himmelfahrt",
            "Pfingstmontag",
            "Fronleichnam",
            "Mariä Himmelfahrt",
            "Tag der Deutschen Einheit",
            "Allerheiligen",
            "Erster Weihnachtstag",
            "Zweiter Weihnachtstag",
        ]
    )

    # Heutiges Datum verwenden
    date_requested = datetime.today().date()
    startDate = date_requested - timedelta(days=1)
    endDate = date_requested + timedelta(days=1)

    week_dates = []
    formatted_day = date_requested.strftime("%d.%m.%Y")
    week_dates.append(formatted_day)

    # Loading whitelist data from whitelist.json
    with open("app/static/data/whitelist.json", "r", encoding="utf-8") as f:
        whitelist = json.load(f)

    # Prepare list for absences
    absences_list = []

    # Fetch absences for all users in whitelist
    for user_info in whitelist:
        name = user_info["employee"]

        try:
            absence_info = get_user_absence(
                access_token, user_info["id"], startDate, endDate
            )
            absences_list.append(
                {
                    "name": name,
                    "absence": absence_info,
                }
            )
        except Exception as e:
            # Bei Fehler für einzelnen User, trotzdem weitermachen
            print(f"Fehler beim Abrufen der Abwesenheit für {name}: {e}")
            absences_list.append(
                {
                    "name": name,
                    "absence": ["Fehler beim Laden"],
                }
            )

    # Sortiere die Liste alphabetisch nach Namen
    absences_list.sort(key=lambda x: x["name"])

    selected_date = date_requested.strftime("%Y-%m-%d")
    day_of_week = date_requested.strftime("%A")

    # Rendering the 'emergency.html' template and passing data
    return render_template(
        "emergency.html",
        username=username,
        initials=initials,
        absences=absences_list,
        today=selected_date,
        day=day_of_week,
        date=week_dates,
        holidays=holidays,
    )


@app.route("/absence.html", methods=["POST", "GET"])
def absence():
    max_attempts = 3
    attempts = 0
    access_token = None
    
    while attempts < max_attempts:
        try:
            download_file()
            # Überprüfen, ob die Datei existiert
            if not os.path.exists("app/static/data/code.json"):
                raise FileNotFoundError("Die Datei code.json wurde nicht gefunden.")

            # code.json auslesen und das Flag überprüfen
            with open("app/static/data/code.json", "r", encoding="utf-8") as f:
                tokens = json.load(f)
                print(tokens)

            if tokens.get("flag") == True:
                # Wenn das Flag auf True steht, 10 Sekunden warten und die Schleife fortsetzen
                time.sleep(10)
                attempts += 1
                continue
            else:
                # Wenn das Flag auf False steht, kritischen Bereich mit try-finally absichern
                try:
                    # Flag auf True setzen
                    update_flag_in_code_json(True)
                    upload_file()
                    
                    try:
                        # Kritischer Bereich, der geschützt werden soll
                        refresh_token_code()
                        with open("app/static/data/code.json", "r", encoding="utf-8") as f:
                            tokens = json.load(f)
                        access_token = tokens["access_token"]
                        break  # Erfolgreich, Schleife verlassen
                    finally:
                        # Wird immer ausgeführt, auch bei Ausnahmen im try-Block
                        update_flag_in_code_json(False)
                        upload_file()
                        
                except Exception as inner_e:
                    print(f"Fehler im kritischen Bereich: {inner_e}")
                    # Wir sind hier, wenn ein Fehler beim Setzen/Zurücksetzen der Flag auftritt
                    # Die Flag sollte bereits zurückgesetzt sein, wenn nicht, versuchen wir es noch einmal
                    try:
                        update_flag_in_code_json(False)
                        upload_file()
                    except:
                        pass
                    attempts += 1
                    time.sleep(5)

        except Exception as e:
            print(f"Allgemeiner Fehler: {e}")
            attempts += 1
            if attempts >= max_attempts:
                break
            time.sleep(5)

    # Wenn wir keinen Access-Token haben nach den Versuchen oder bei Fehler
    if not access_token:
        error_redirect = handle_token_refresh()
        if error_redirect:
            return error_redirect
        access_token = session.get("access_token")

    username = session.get("username")
    initials = session.get("initials")
    userId = session.get("userId")
    outputType = "date"
    week_dates = []
    selected_date = ""

    holidays = set(
        [
            "Neujahr",
            "Heilige Drei Könige",
            "Karfreitag",
            "Ostermontag",
            "Tag der Arbeit",
            "Christi Himmelfahrt",
            "Pfingstmontag",
            "Fronleichnam",
            "Mariä Himmelfahrt",
            "Tag der Deutschen Einheit",
            "Allerheiligen",
            "Erster Weihnachtstag",
            "Zweiter Weihnachtstag",
        ]
    )

    try:
        request_data = request.get_json()
        inputType = request_data.get("inputType")
        outputType = inputType
        date_param = request_data.get("date")

        if inputType == "date":
            date_requested = datetime.strptime(date_param, "%Y-%m-%d").date()
            startDate = date_requested - timedelta(days=1)
            endDate = date_requested + timedelta(days=1)

            week_dates.clear()
            day = startDate + timedelta(days=1)
            formatted_day = day.strftime("%d.%m.%Y")
            week_dates.append(formatted_day)

        elif inputType == "week":
            selected_date = date_param
            year, week = date_param.split("-W")
            if year == "2025":
                date_requested = datetime.strptime(
                    f"{year}-W{week}-1", "%Y-W%W-%w"
                ).date() - timedelta(days=7)
            else:
                date_requested = datetime.strptime(
                    f"{year}-W{week}-1", "%Y-W%W-%w"
                ).date()
            startDate = date_requested - timedelta(days=date_requested.weekday())
            endDate = startDate + timedelta(days=5)

            week_dates.clear()
            for i in range(5):  # Montag bis Freitag
                day = startDate + timedelta(days=i)
                formatted_day = day.strftime("%d.%m.%Y")
                week_dates.append(formatted_day)

        else:
            raise ValueError("Invalid inputType")

    except Exception as e:
        date_requested = datetime.today().date()
        week_dates.clear()
        week_dates.append(date_requested.strftime("%d.%m.%Y"))
        startDate = date_requested - timedelta(days=1)
        endDate = date_requested + timedelta(days=1)

    # Loading whitelist data from whitelist.json
    with open("app/static/data/whitelist.json", "r", encoding="utf-8") as f:
        whitelist = json.load(f)

    # Searching whitelist for userId and determining team_id
    team_id = None
    team_id2 = None
    team_id3 = None
    # Dictionary für Team-Konfigurationen
    team_configs = {
        # Gesamtes Team Jörg K.
        "635876ac-a7f0-0e02-ad5d-0190f3f32f2e": ["f49c6b93-b930-044d-be5d-2e9a7a22bfad",
                                                 "0ed1261b-cde1-07af-ba56-315561d3082d"],
        # Gesamtes Team Fabian H.                                                 
        "f49c6b93-b930-044d-be5d-2e9a7a22bfad": ["635876ac-a7f0-0e02-ad5d-0190f3f32f2e",
                                                 "0ed1261b-cde1-07af-ba56-315561d3082d"],
        # Gesamtes Team Fabian M.
        "0ed1261b-cde1-07af-ba56-315561d3082d": ["635876ac-a7f0-0e02-ad5d-0190f3f32f2e",
                                                 "f49c6b93-b930-044d-be5d-2e9a7a22bfad"],
        # Gesamtes Team Stephan S.
        "a935254e-b5ce-0a6c-8558-916bd4f2bfba": ["33b56e06-2bd1-0034-a45b-53b91a737d1a"],
        # Gesamtes Team Fabian O.
        "d1701b1c-0423-0f0a-8c5d-ff1c5a72bfaa": ["974fca82-4ff9-0275-8052-1fde5f336fa5",
                                                 "299434b4-47a5-026c-b059-42f32b9357f8"],
        # Gesamtes Team Patrick W.
        "1789bee0-ec3e-03f3-8058-ae1b14c36bf8": ["9c8ea525-e054-0a7c-9f5d-c087ba53750d",
                                                 "e0eda744-94d3-0803-9d5f-de2700b2bfb8"],
    }

    for user_info in whitelist:
        if user_info["id"] == userId:
            team_id = user_info["team_id"]
            break

    if not team_id:
        return "Unauthorized", 401

    if team_id in team_configs:
        additional_team_ids = team_configs[team_id]
        response = get_teamleader_teams(access_token, team_id, *additional_team_ids)
    else:
        response = get_teamleader_teams(access_token, team_id)

    try:
        ids = [member["id"] for team in response for member in team["members"]]
    except Exception as e:
        error_message = (
            f"Dein Token ist abgelaufen, melde dich erneut an um den Token zu erneuern"
        )
        return render_template(
            "absence.html",
            error_message=error_message,
            username=username,
            initials=initials,
            holidays=holidays,
        )

    # Prepare list for absences
    absences_list = []

    # Fetch absences for authorized users based on whitelist
    for user_info in whitelist:
        if user_info["id"] in ids:
            # Finding user's name
            for team in response:
                for member in team["members"]:
                    if member["id"] == user_info["id"]:
                        name = user_info["employee"]
                        break
                else:
                    continue
                break
            else:
                name = "Unknown"

            if outputType == "date":
                absence_info = get_user_absence(
                    access_token, user_info["id"], startDate, endDate
                )
                absences_list.append(
                    {
                        "name": name,
                        "absence": absence_info,  # Assuming get_user_absence returns absence information
                    }
                )
            elif outputType == "week":
                absence_info = get_user_absence(
                    access_token,
                    user_info["id"],
                    startDate - timedelta(days=1),
                    endDate,
                    True,
                    week_dates,
                )
                # Check if the user is already in the absences_list
                user_found = False
                for entry in absences_list:
                    if entry["name"] == name:
                        entry["absence"] = absence_info
                        user_found = True
                        break
                if not user_found:
                    absences_list.append(
                        {
                            "name": name,
                            "absence": absence_info,  # Start a new list with the first absence info
                        }
                    )

    if outputType == "date":
        selected_date = date_requested.strftime("%Y-%m-%d")

    day_of_week = date_requested.strftime("%A")

    # Rendering the 'absence.html' template and passing data
    return render_template(
        "absence.html",
        username=username,
        initials=initials,
        absences=absences_list,
        today=selected_date,
        view=outputType,
        day=day_of_week,
        date=week_dates,
        holidays=holidays,
    )

@app.route("/illness.html")
def illness():

    username = session.get("username")
    initials = session.get("initials")
    user_permissions = session.get("user_permissions", {})

    if not user_permissions.get("illness", False):
        return render_template("error.html", username=username, initials=initials)

    # Hol dir das heutige Datum
    current_date = date.today()

    # Formatiere den Monat im Format "YYYY-MM"
    currentMonth = current_date.strftime("%Y-%m")

    return render_template(
        "illness.html",
        username=username,
        initials=initials,
        today=currentMonth,
    )


@app.route("/illness.html", methods=["POST", "GET"])
def get_illness_days():
    username = session.get("username")
    initials = session.get("initials")
    user_permissions = session.get("user_permissions", {})

    if not user_permissions.get("illness", False):
        return render_template("error.html", username=username, initials=initials)

    # Hol dir das heutige Datum
    request_data = request.get_json()
    current_date_str = request_data.get("date")
    current_date = datetime.strptime(current_date_str, "%Y-%m")
    current_date.strftime("%Y-%m-01")

    # Berechne den ersten Tag des aktuellen Monats
    first_day_of_current_month = current_date.replace(day=1)

    # Berechne den letzten Tag des Vormonats (start_date)
    start_date = (first_day_of_current_month - timedelta(days=1)).strftime("%Y-%m-%d")

    # Berechne den ersten Tag des Folgemonats (end_date)
    if current_date.month == 12:
        end_date = date(current_date.year + 1, 1, 1).strftime("%Y-%m-%d")
    else:
        end_date = date(current_date.year, current_date.month + 1, 1).strftime(
            "%Y-%m-%d"
        )

    # Formatiere den Monat im Format "YYYY-MM"
    currentMonth = current_date.strftime("%Y-%m")

    # Lade die Whitelist
    with open("app/static/data/whitelist.json", "r", encoding="utf-8") as f:
        whitelist = json.load(f)

    illness_table = []

    # Hole das Access-Token (Annahme: Es ist in der Session gespeichert)
    access_token = session.get("access_token")

    for index, employee in enumerate(whitelist, 1):
        days = get_number_of_illness_days(
            access_token, employee["id"], start_date, end_date
        )
        if days > 0:
            illness_table.append(
                {
                    "employee": employee["employee"],
                    "days": str(days),
                    "hours": str(days * 8),
                }
            )

    # Monatsname für die Fehlermeldung
    month_name = current_date.strftime("%B")

    if illness_table:
        save_illness_table_to_csv(illness_table, currentMonth)
        session["currentMonth"] = currentMonth

        return render_template(
            "illness.html",
            username=username,
            initials=initials,
            today=currentMonth,
            illness=illness_table,
        )
    else:
        return render_template(
            "illness.html",
            username=username,
            initials=initials,
            today=currentMonth,
            error_message=f"Im {month_name} gab es keine Krankheitsausfälle",
        )


@app.route("/upload-times.html")
def zeiten_hochladen():
    username = session.get("username")
    initials = session.get("initials")
    user_permissions = session.get("user_permissions", {})
    if not user_permissions.get("upload_times", False):
        return render_template("error.html", username=username, initials=initials)

    return render_template("upload-times.html", username=username, initials=initials)


@app.route("/manage-times.html")
def zeiten_verwalten():
    username = session.get("username")
    userId = session.get("userId")
    initials = session.get("initials")
    user_permissions = session.get("user_permissions", {})
    selectedMonth = datetime.today().strftime("%Y-%m")

    if not user_permissions.get("manage_times", False):
        return render_template("error.html", username=username, initials=initials)
    return render_template(
        "manage-times.html",
        username=username,
        initials=initials,
        team_id="",
        selectedMonth=selectedMonth,
    )


@app.route("/manage-times.html", methods=["POST"])
def get_teams():
    error_redirect = handle_token_refresh()
    if error_redirect:
        return error_redirect

    username = session.get("username")
    initials = session.get("initials")
    access_token = session.get("access_token")
    request_data = request.get_json()
    selectedMonth = request_data.get("selectedMonth")

    # Umwandlung in ein Datum (wir nehmen den ersten Tag des Monats)
    selected_date = datetime.strptime(selectedMonth + "-01", "%Y-%m-%d")

    selected_id = request_data.get("selectedId")

    if selected_id == "-2":
        previous_month = selected_date.replace(day=1) - timedelta(days=1)
        beginofMonth = previous_month.replace(day=15).strftime("%Y-%m-%d")
        endofMonth = selected_date.replace(day=16).strftime("%Y-%m-%d")
    else:
        # Berechnung des ersten und letzten Tags des Monats
        beginofMonth = (selected_date - timedelta(days=1)).strftime("%Y-%m-%d")
        # Finde den letzten Tag des Monats durch den ersten Tag des nächsten Monats
        next_month = selected_date.replace(day=28) + timedelta(days=4)
        # Gehe einen Monat weiter
        endofMonth = (
            (next_month - timedelta(days=next_month.day)) + timedelta(days=1)
        ).strftime("%Y-%m-%d")
    selectedOption = request_data.get("selectedOption")
    team_name = request_data.get("team_name")
    first_tmstmp = request_data.get("first_tmstmp")
    second_tmstmp = request_data.get("second_tmstmp")
    third_tmstmp = request_data.get("third_tmstmp")
    end_tmstmp = request_data.get("end_tmstmp")
    fourth_tmstmp = request_data.get("fourth_tmstmp")

    # Initialisiere die Zählvariable für Arbeitstage
    workdays_count = 0

    # Schleife durch alle Tage des Monats und zähle die Arbeitstage
    if selected_id == "-2":
        current_day = datetime.strptime(beginofMonth, "%Y-%m-%d") - timedelta(days=1)
    else:
        current_day = selected_date
    while current_day <= (
        datetime.strptime(endofMonth, "%Y-%m-%d") - timedelta(days=1)
    ):
        # Prüfe, ob der aktuelle Tag ein Arbeitstag ist (Montag bis Freitag)
        if current_day.weekday() < 5:  # Montag (0) bis Freitag (4)
            workdays_count += 1
        # Gehe zum nächsten Tag
        current_day += timedelta(days=1)

    team_configs = {
        # Gesamtes Team Jörg K.
        "635876ac-a7f0-0e02-ad5d-0190f3f32f2e": [
            "f49c6b93-b930-044d-be5d-2e9a7a22bfad",
            "0ed1261b-cde1-07af-ba56-315561d3082d",
        ],
        # Gesamtes Team Reinhold G.
        "7f88fa5f-e174-061f-9e54-8b4586234146": [
            "299434b4-47a5-026c-b059-42f32b9357f8"
        ],
        # Gesamtes Team Jannis S.
        "6ded28b1-8987-0e20-b655-668170f2bfb5": [
            "283a1bc2-beb1-00c8-be5c-4848566357f7"
        ],
        # Gesamtes Team Fabian O.
        "d1701b1c-0423-0f0a-8c5d-ff1c5a72bfaa": [
            "974fca82-4ff9-0275-8052-1fde5f336fa5"
        ],
        # Gesamtes Team Tilmann R.
        "473c86b8-3929-027c-9853-5a26f84342f5": [
            "b8a1e30f-b21b-0526-b053-31f3de83625d"
        ],
    }

    if selected_id in team_configs:
        team_ids = team_configs[selected_id]
        response = get_teamleader_teams(access_token, selected_id, *team_ids)
    else:
        response = get_teamleader_teams(access_token, selected_id)

    members_info = []

    for team in response:
        members = team.get("members", [])
        for member in members:
            member_id = member.get("id")
            first_name, last_name = get_teamleader_user_info(access_token, member_id)

            try:
                days_of_absence = get_number_of_absence_days(
                    access_token, member_id, beginofMonth, endofMonth
                )

                special_working_hours = get_special_working_hours(
                    member_id, workdays_count
                )

                times_data = get_teamleader_user_times(
                    access_token,
                    member_id,
                    first_tmstmp,
                    second_tmstmp,
                    third_tmstmp,
                    end_tmstmp,
                    fourth_tmstmp,
                )

                denominator = (special_working_hours - days_of_absence) * 8
                members_info.append(
                    {
                        "first_name": first_name,
                        "last_name": last_name,
                        "total_duration": times_data["total_duration"].replace(
                            ".", ","
                        ),
                        "invoiceable_duration": times_data[
                            "invoiceable_duration"
                        ].replace(".", ","),
                        "non_invoiceable_duration": times_data[
                            "non_invoiceable_duration"
                        ].replace(".", ","),
                        "total_days": str(special_working_hours - days_of_absence),
                        "invoiceable_percentage": "{:.2f}".format(
                            float(times_data["invoiceable_duration"].replace(",", "."))
                            / denominator
                            if denominator != 0
                            else 0
                        ).replace(".", ","),
                        "overtime_hours": "{:.2f}".format(
                            float(times_data["total_duration"].replace(",", "."))
                            - (special_working_hours - days_of_absence) * 8
                            if special_working_hours != days_of_absence
                            else 0
                        ).replace(".", ","),
                    }
                )

            except Exception as e:
                error_message = (
                    e,
                    f"Dir fehlen die Berechtigung, um dieses Team anzuschauen",
                )
                return render_template(
                    "manage-times.html",
                    error_message=error_message,
                    username=username,
                    initials=initials,
                    selectedMonth=selectedMonth,
                    team_id=selected_id,
                    selectedOption=selectedOption,
                    team_name=team_name,
                )
        time.sleep(5)

    # Erstelle einen IO-Stream für die CSV-Datei
    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")  # Nutze ; als Trennzeichen

    # Schreibe die Kopfzeile in die CSV-Datei
    writer.writerow(
        [
            "Vorname",
            "Nachname",
            "Erfasste Zeit",
            "Abrechenbar",
            "Nicht Abrechenbar",
            "Arbeitstage",
            "Fakuraquote",
            "Überstunden",
        ]
    )

    # Schreibe die Mitgliederinformationen in die CSV-Datei
    for member in members_info:
        # Formatiere total_days mit Komma statt Punkt
        total_days_formatted = str(member["total_days"]).replace(".", ",")

        writer.writerow(
            [
                member["first_name"],
                member["last_name"],
                member["total_duration"],
                member["invoiceable_duration"],
                member["non_invoiceable_duration"],
                total_days_formatted,
                member["invoiceable_percentage"],
                member["overtime_hours"],
            ]
        )

    # Setze den Cursor des IO-Streams auf den Anfang
    output.seek(0)

    # Speichere die CSV-Datei temporär auf dem Server
    csv_filename = "app/static/downloads/Zeitübersicht.csv"  # Beispiel: Temporärer Pfad

    # Schreibe den Inhalt in die CSV-Datei mit newline=''
    with open(csv_filename, "w", newline="", encoding="utf-8") as f:
        f.write("\ufeff")
        f.write(output.getvalue())

    return render_template(
        "manage-times.html",
        members_info=members_info,
        username=username,
        initials=initials,
        selectedMonth=selectedMonth,
        team_id=selected_id,
        selectedOption=selectedOption,
        team_name=team_name,
    )


@app.route("/download-template")
def download_template():
    return send_from_directory(
        directory="static/data", path="template.csv", as_attachment=True
    )


@app.route("/download-json")
def download_json():
    return send_from_directory(
        directory="static/data", path="projects.json", as_attachment=True
    )


@app.route("/download-tickets")
def download_tickets():
    return send_from_directory(
        directory="static/data", path="tickets.json", as_attachment=True
    )


@app.route("/upload-times.html", methods=["GET", "POST"])
def upload():
    temp_dir = tempfile.gettempdir()
    username = session.get("username")
    initials = session.get("initials")

    if "csvFile" not in request.files:
        return render_template(
            "upload-times.html",
            error_message="Keine Datei ausgewählt!",
            username=username,
            initials=initials,
        )

    file = request.files["csvFile"]
    if file.filename == "":
        return render_template(
            "upload-times.html",
            error_message="Keine Datei ausgewählt!",
            username=username,
            initials=initials,
        )

    if file and file.filename.endswith(".csv"):
        try:
            csv_content = file.stream.read().decode("utf-8")
        except UnicodeDecodeError:
            return render_template(
                "upload-times.html",
                error_message="Fehlerhafte Exceldatei!",
                username=username,
                initials=initials,
            )
        csv_data = parse_csv(csv_content)
        temp_csv_path = os.path.join(temp_dir, "temp_upload.csv")
        if csv_data is None:
            return render_template(
                "upload-times.html",
                error_message="Fehler beim Parsen der CSV-Datei!",
                username=username,
                initials=initials,
            )

        try:
            with open(temp_csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(
                    list(csv_data[0].keys())
                )  # Schreibe die Kopfzeile in die CSV-Datei
                for row in csv_data:
                    writer.writerow(
                        list(row.values())
                    )  # Schreibe die Datenzeilen in die CSV-Datei
        except Exception as e:
            return render_template(
                "upload-times.html",
                error_message="Ungültiger Dateityp!",
                username=username,
                initials=initials,
            )

        sorted_data = group_by_date(csv_data)
        return render_template(
            "upload-times.html",
            sorted_data=sorted_data,
            username=username,
            initials=initials,
        )

    return render_template(
        "upload-times.html",
        error_message="Ungültiger Dateityp!",
        username=username,
        initials=initials,
    )


@app.route("/authorize-teamleader")
def authorize_teamleader():
    session["previous_url"] = request.referrer or "/"
    auth_url = get_teamleader_token(Config.CLIENT_ID, Config.REDIRECT_URI)
    return redirect(auth_url)


@app.route("/logout")
def logout_teamleader():
    session.clear()
    time.sleep(1)
    return redirect("/")


@app.route("/oauth/callback")
def oauth_callback():
    code = request.args.get("code")
    try:
        token_response = get_teamleader_token(
            Config.CLIENT_ID,
            f"{Config.REDIRECT_URI}/oauth/callback",
            Config.CLIENT_SECRET,
            code,
        )
        if "access_token" in token_response:
            session["access_token"] = token_response["access_token"]
            return redirect("/login")
        else:
            error_message = token_response.get(
                "error_description", "Autorisierungsfehler"
            )
            return render_template("error.html", error_message=error_message)
    except requests.exceptions.RequestException as e:
        return render_template("error.html", error_message=str(e))


@app.route("/login")
def login():
    access_token = session.get("access_token")
    if not access_token:
        return redirect(request.url)

    try:
        user_info = get_teamleader_user(access_token)

        session["username"] = f"{user_info['first_name']} {user_info['last_name']}"
        session["initials"] = f"{user_info['first_name'][0]}{user_info['last_name'][0]}"
        session["userId"] = user_info["id"]
        return redirect(session.get("previous_url", "/"))
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)})


@app.route("/upload-to-teamleader")
def fetch_teamleader_data():
    username = session.get("username")
    initials = session.get("initials")
    temp_dir = tempfile.gettempdir()
    temp_csv_path = os.path.join(temp_dir, "temp_upload.csv")
    # Lade Daten aus der temporären CSV-Datei
    with open(temp_csv_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        csv_data = list(reader)

    error_redirect = handle_token_refresh()
    if error_redirect:
        return error_redirect

    access_token = session.get("access_token")
    if not access_token:
        return redirect(session.get("previous_url", "/"))

    headers = {"Authorization": f"Bearer {access_token}"}

    for entry in csv_data:
        datum = entry["Datum"]
        von = entry["Von"]
        bis = entry["Bis"]
        abrechenbar = entry["Abrechenbar"] == "Ja"
        description = entry["Beschreibung"]

        # Datum und Zeit in das gewünschte Format konvertieren
        date_time_str = f"{datum} {von}"
        started_at = (
            datetime.strptime(date_time_str, "%d.%m.%Y %H:%M").isoformat() + "+02:00"
        )

        # Dauer berechnen
        duration_seconds = calculate_total_hours(von, bis) * 3600

        worktype = load_worktype()
        worktype_id = next(
            (wktype for wktype in worktype if wktype["type"] == entry["Typ"]), None
        )

        body = {
            "work_type_id": worktype_id["id"],
            "started_at": started_at,
            "duration": duration_seconds,
            "description": description,
            "subject": worktype_id["subject"],
            "invoiceable": abrechenbar,
            "user_id": session.get("userId"),
        }

        try:
            response = requests.post(
                "https://api.focus.teamleader.eu/timeTracking.add",
                headers=headers,
                data=json.dumps(body),
            )
            response.raise_for_status()
            if response.status_code != 201:
                error_message = "Fehler beim Hochladen der Daten in Teamleader."
                return render_template(
                    "upload-times.html",
                    error_message=error_message,
                    username=username,
                    initials=initials,
                )
        except requests.exceptions.RequestException as e:
            return render_template(
                "upload-times.html",
                error_message=str(e),
                username=username,
                initials=initials,
            )

    success_message = "Die Zeiten wurden erfolgreich hochgeladen!"
    return render_template(
        "upload-times.html",
        success_message=success_message,
        username=username,
        initials=initials,
    )


@app.route("/fetch-subjects")
def fetch_subjects():
    error_redirect = handle_token_refresh()
    if error_redirect:
        return error_redirect

    access_token = session.get("access_token")
    if not access_token:
        return redirect(session.get("previous_url", "/"))

    headers = {"Authorization": f"Bearer {access_token}"}

    time_tracking_body = {
        "filter": {
            "user_id": session.get("userId"),
            "started_after": "2025-01-01T00:00:01+02:00",
            "ended_before": "2025-01-30T23:59:59+02:00",
        },
        "sort": [{"field": "starts_on"}],
        "page": {"size": 100, "number": 1},
    }

    try:
        time_tracking_response = requests.post(
            "https://api.focus.teamleader.eu/timeTracking.list",
            headers=headers,
            json=time_tracking_body,
        )
        time_tracking_response.raise_for_status()

        time_tracking_data = time_tracking_response.json()
        teamleader_data = {"subjects": [], "work_types": []}

        for entry in time_tracking_data.get("data", []):
            if "subject" in entry:
                teamleader_data["subjects"].append(entry["subject"])
            if "work_type" in entry:
                teamleader_data["work_types"].append(entry["work_type"])

        # Entferne Duplikate basierend auf der ID
        teamleader_data["subjects"] = [
            dict(t) for t in {tuple(d.items()) for d in teamleader_data["subjects"]}
        ]
        teamleader_data["work_types"] = [
            dict(t) for t in {tuple(d.items()) for d in teamleader_data["work_types"]}
        ]

        # Speichere die JSON-Datei im static/downloads Verzeichnis
        json_path = os.path.join("app/static/downloads", "teamleader_data.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(teamleader_data, f, indent=4)

        return send_from_directory(
            directory="static/downloads",
            path="teamleader_data.json",
            as_attachment=True,
            mimetype="application/json; charset=utf-8",
        )

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500


@app.route("/clear-data", methods=["POST"])
def clear_data():
    temp_dir = tempfile.gettempdir()
    # Routenfunktion zum Löschen der temporären CSV-Daten
    temp_csv_path = os.path.join(temp_dir, "temp_upload.csv")
    if os.path.exists(temp_csv_path):
        os.remove(temp_csv_path)

    return jsonify({"status": "success", "message": "Daten erfolgreich gelöscht"})


@app.route("/download_times_csv")
def download_times_csv():
    # Rufe die Mitgliederinformationen ab

    # Sende die Datei als Download
    return send_from_directory(
        directory="static/downloads",
        path="Zeitübersicht.csv",
        as_attachment=True,
        mimetype="text/csv; charset=utf-8",
    )


@app.route("/download_illness_csv")
def download_csv():
    """
    Lädt die angegebene CSV-Datei herunter.

    Args:
        filename (str): Der Name der CSV-Datei

    Returns:
        file: Die heruntergeladene CSV-Datei
    """

    currentMonth = session.get("currentMonth")
    filename = f"Krankheitsübersicht_{currentMonth}.csv"

    return send_from_directory(
        directory="static/downloads",
        path=filename,
        as_attachment=True,
        mimetype="text/csv; charset=utf-8",
    )


@app.route("/save_changes", methods=["POST"])
def save_changes():
    changes = request.get_json()
    try:
        with open("app/static/data/whitelist.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        for user in data:
            employee = user["employee"]
            if employee in changes:
                for permission, value in changes[employee].items():
                    if permission in user:
                        user[permission] = value

        with open("app/static/data/whitelist.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        return jsonify({"status": "success"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


def load_tickets():
    with open("app/static/data/tickets.json", "r", encoding="utf-8") as f:
        return json.load(f)


def save_tickets(tickets):
    with open("app/static/data/tickets.json", "w", encoding="utf-8") as f:
        json.dump(tickets, f, indent=2, default=str)


@app.route("/create_ticket", methods=["POST"])
def create_ticket():
    username = session.get("username")
    tickets = load_tickets()

    # Set the locale to German for correct day and month names
    locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")

    new_ticket = {
        "id": len(tickets) + 1,
        "title": request.form.get("title"),
        "description": request.form.get("text"),
        "status": "Offen",
        "created_at": datetime.now().strftime("%a, %d. %B %Y, %H:%M:%S Uhr"),
        "images": [],
        "user": username,
    }

    images = request.files.getlist("images")
    for image in images:
        if image:
            filename = request.form.get("title") + secure_filename(image.filename)
            image.save(os.path.join("app/static/uploads", filename))
            new_ticket["images"].append(filename)

    tickets.append(new_ticket)
    save_tickets(tickets)

    return jsonify({"message": "Ticket erstellt!", "id": new_ticket["id"]}), 201


@app.route("/tickets.html")
def list_tickets():
    user_id = session.get("userId")
    username = session.get("username")
    initials = session.get("initials")
    whitelist = load_whitelist()

    tickets = load_tickets()
    tickets.sort(key=lambda x: (x["status"], x["created_at"]), reverse=True)
    return render_template(
        "tickets.html",
        tickets=tickets,
        initials=initials,
        username=username,
    )

    tickets = load_tickets()
    tickets.sort(key=lambda x: (x["status"], x["created_at"]), reverse=True)
    return render_template(
        "tickets.html",
        tickets=tickets,
        initials=initials,
        username=user_permissions["employee"],
    )


@app.route("/ticket/<int:ticket_id>")
def view_ticket(ticket_id):
    tickets = load_tickets()
    ticket = next((t for t in tickets if t["id"] == ticket_id), None)
    if ticket is None:
        return "Ticket nicht gefunden", 404
    return render_template("ticket_detail.html", ticket=ticket)


@app.route("/archive_closed_tickets", methods=["POST"])
def archive_closed_tickets():
    tickets = load_tickets()

    updated_count = 0

    # Gehe durch alle Tickets und setze den Status von "Geschlossen" auf "Archiviert"
    for ticket in tickets:
        if ticket["status"] == "Geschlossen":
            ticket["status"] = "Archiviert"
            updated_count += 1

    # Speichere nur, wenn mindestens ein Ticket aktualisiert wurde
    if updated_count > 0:
        save_tickets(tickets)
        return jsonify({"message": f"{updated_count} Ticket(s) wurden archiviert"}), 200
    else:
        return jsonify({"message": "Keine Tickets zum Archivieren gefunden"}), 404


@app.route("/update_status/<int:ticket_id>", methods=["POST"])
def update_status(ticket_id):
    tickets = load_tickets()
    ticket = next((t for t in tickets if t["id"] == ticket_id), None)
    if ticket is None:
        return jsonify({"message": "Ticket nicht gefunden"}), 404

    data = request.get_json()
    if "status" in data:
        ticket["status"] = data["status"]
        save_tickets(tickets)
        return jsonify({"message": "Status aktualisiert"}), 200
    else:
        return jsonify({"message": "Ungültige Anfrage"}), 400


@app.route("/delete_ticket/<int:ticket_id>", methods=["DELETE"])
def delete_ticket(ticket_id):
    tickets = load_tickets()
    ticket_index = next(
        (index for (index, t) in enumerate(tickets) if t["id"] == ticket_id), None
    )

    if ticket_index is not None:
        ticket = tickets[ticket_index]

        # Löschen der Bilder
        for image in ticket["images"]:
            image_path = os.path.join("app/static/uploads", image)
            if os.path.exists(image_path):
                os.remove(image_path)

        # Ticket aus der Liste entfernen
        tickets.pop(ticket_index)
        save_tickets(tickets)
        return jsonify({"message": "Ticket gelöscht"}), 200
    else:
        return jsonify({"message": "Ticket nicht gefunden"}), 404


# Dummy setup for session for testing purposes
app.secret_key = "supersecretkey"
app.config["SESSION_TYPE"] = "filesystem"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)
