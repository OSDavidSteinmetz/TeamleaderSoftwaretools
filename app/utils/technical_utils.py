import json
import os
from datetime import datetime

import paramiko
import requests
from scp import SCPClient

# Konfigurationsvariablen
CLIENT_ID = "a91d4e3804f21bd3dd54bd2fd9f19d91"
CLIENT_SECRET = "a1196dfa3602b3b6c085faae29a8272a"
TOKEN_FILE = os.path.join("app", "static", "data", "code.json")
API_TOKEN_URL = "https://focus.teamleader.eu/oauth2/access_token"

# SSH Konfiguration
SERVER = "p239030.mittwaldserver.info"
PORT = 22
USERNAME = "p239030"
PASSWORD = "35zghdNiMEqE!"
REMOTE_FILE = "/files/teamleader_mail_service/code.json"
LOCAL_FILE = os.path.join("app", "static", "data", "code.json")
REMOTE_FILE_NEW = "/files/teamleader_mail_service/code.json"


def create_ssh_client(server, port, user, password):
    """Create and return an SSH client."""
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port=port, username=user, password=password)
    return client


def download_file():
    # Stelle sicher, dass das Verzeichnis existiert
    static_data_dir = os.path.join("app", "static", "data")
    os.makedirs(static_data_dir, exist_ok=True)

    # Definiere die lokalen Pfade
    code_file = os.path.join(static_data_dir, "code.json")

    print("Connecting to the server...")
    ssh_client = create_ssh_client(SERVER, PORT, USERNAME, PASSWORD)
    try:
        print("Downloading file...")
        with SCPClient(ssh_client.get_transport()) as scp:
            scp.get(REMOTE_FILE, code_file)
        print(f"File successfully downloaded to {code_file}")

    except Exception as e:
        print(f"Error during file download: {e}")
    finally:
        ssh_client.close()


def log_error(message):
    log_dir = os.path.dirname(STATIC_DATA_DIR)
    log_file_path = os.path.join(log_dir, "errors.log")
    os.makedirs(log_dir, exist_ok=True)

    with open(log_file_path, "a") as log_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"{timestamp} - {message}\n")


def load_tokens():
    if os.path.exists("app/static/data/code.json"):
        try:
            with open("app/static/data/code.json", "r", encoding="utf-8") as file:
                data = json.load(file)
                return data.get("access_token"), data.get("refresh_token")
        except Exception as e:
            log_error(f"Fehler beim Laden der Tokens: {str(e)}")
    return None, None


def save_tokens(access_token, refresh_token):
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname("app/static/data/code.json"), exist_ok=True)

        with open("app/static/data/code.json", "w") as file:
            json.dump({
                "access_token": access_token,
                "refresh_token": refresh_token
            }, file, indent=4)
        print("Tokens erfolgreich in app/static/data/code.json gespeichert.")
    except Exception as e:
        log_error(f"Fehler beim Speichern der Tokens: {str(e)}")


def refresh_access_token(client_id, client_secret, refresh_token):
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }
    try:
        response = requests.post(API_TOKEN_URL, data=payload)
        print(response.text)
        response.raise_for_status()
        token_data = response.json()
        return token_data.get("access_token"), token_data.get("refresh_token")
    except requests.RequestException as e:
        log_error(f"Fehler beim Aktualisieren des Access-Tokens: {str(e)}")
        return None, None


def refresh_token_code():
    access_token, refresh_token = load_tokens()

    if not refresh_token:
        print("Kein Refresh-Token vorhanden. Bitte Datei überprüfen.")
        return

    new_access_token, new_refresh_token = refresh_access_token(CLIENT_ID, CLIENT_SECRET, refresh_token)

    if new_access_token and new_refresh_token:
        save_tokens(new_access_token, new_refresh_token)
        print("Token erfolgreich aktualisiert.")
    else:
        print("Token-Aktualisierung fehlgeschlagen.")


def upload_file():
    """Upload a file to the remote server and overwrite it."""
    if not os.path.exists("app/static/data/code.json"):
        print("Error: Local file app/static/data/code.json does not exist.")
        return

    print("Connecting to the server for upload...")
    ssh_client = create_ssh_client(SERVER, PORT, USERNAME, PASSWORD)
    try:
        print("Uploading file...")
        with SCPClient(ssh_client.get_transport()) as scp:
            scp.put("app/static/data/code.json", REMOTE_FILE_NEW)
        print(f"File successfully uploaded to {REMOTE_FILE_NEW}")
    except Exception as e:
        print(f"Error during file upload: {e}")
    finally:
        ssh_client.close()


def update_flag_in_code_json(flag_value):
    """Liest die code.json-Datei ein, setzt das Flag und speichert sie."""
    if os.path.exists("app/static/data/code.json"):
        with open("app/static/data/code.json", "r", encoding="utf-8") as file:
            data = json.load(file)
    else:
        data = {}  # Falls die Datei nicht existiert, ein leeres Dict verwenden

    # Flag setzen
    data["flag"] = flag_value

    # Datei überschreiben
    with open("app/static/data/code.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print(f"Flag in code.json wurde auf {flag_value} gesetzt.")
