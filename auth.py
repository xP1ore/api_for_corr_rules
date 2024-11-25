import requests
import json
import os
from config import API_URL, USERNAME, PASSWORD, CLIENT_ID, CLIENT_SECRET, RAW_RESPONSES_TOKENS_DIR


def get_token():
    """Получает новый токен доступа и сохраняет ответ в файл."""
    data = {
        "username": USERNAME,
        "password": PASSWORD,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "password",
        "response_type": "code id_token",
        "scope": "offline_access mpx.api ptkb.api"
    }
    response = requests.post(f"{API_URL}/connect/token", data=data, verify=False)

    if response.status_code == 200:
        token_data = response.json()

        save_response_to_file("token", token_data)

        return token_data["access_token"], token_data.get("refresh_token")
    else:
        print(f"Ошибка при получении токена: {response.status_code}, {response.text}")


def refresh_token(refresh_token):
    """Обновляет токен с помощью refresh_token и сохраняет ответ в файл."""
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    response = requests.post(f"{API_URL}/connect/token", data=data, verify=False)

    if response.status_code == 200:
        new_token_data = response.json()

        save_response_to_file("refresh_token", new_token_data)

        return new_token_data["access_token"], new_token_data.get("refresh_token")
    else:
        print(f"Ошибка при обновлении токена: {response.status_code}, {response.text}")


def save_response_to_file(file_prefix, response_data):
    """Сохраняет полный ответ в текстовый файл."""
    os.makedirs(RAW_RESPONSES_TOKENS_DIR, exist_ok=True)
    file_path = f"{RAW_RESPONSES_TOKENS_DIR}/{file_prefix}_response.json"
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(response_data, file, ensure_ascii=False, indent=4)
    print(f"Полный ответ сохранен в файл: {file_path}")
