import os
import json
import requests
from auth import get_token, refresh_token
from config import (
    RAW_RESPONSES_TOKENS_DIR,
    RAW_RESPONSES_INCIDENTS_DIR,
    RAW_RESPONSES_DETAILS_DIR,
    HANDLED_RESPONSES_DIR,
    HANDLED_INCIDENTS_FILE,
    API_URL
)


class IncidentManager:
    def __init__(self, api_url, token, refresh_token):
        self.api_url = api_url
        self.token = token
        self.refresh_token = refresh_token

        os.makedirs(RAW_RESPONSES_TOKENS_DIR, exist_ok=True)
        os.makedirs(RAW_RESPONSES_INCIDENTS_DIR, exist_ok=True)
        os.makedirs(RAW_RESPONSES_DETAILS_DIR, exist_ok=True)
        os.makedirs(HANDLED_RESPONSES_DIR, exist_ok=True)

    @staticmethod
    def load_previous_incidents():
        """Загружает ранее сохраненные обработанные инциденты."""
        if not os.path.exists(HANDLED_INCIDENTS_FILE):
            return []

        with open(HANDLED_INCIDENTS_FILE, "r", encoding="utf-8") as file:
            lines = file.readlines()
            return [json.loads(line.strip()) for line in lines if line.strip()]

    @staticmethod
    def save_raw_response(directory, response_data, filename):
        """Сохраняет ответ от сервера в указанной директории."""
        file_path = os.path.join(directory, filename)
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(response_data, file, ensure_ascii=False, indent=4)

    @staticmethod
    def save_handled_response(response_data):
        """Сохраняет обработанные данные в файл incidents.txt."""
        with open(HANDLED_INCIDENTS_FILE, "a", encoding="utf-8") as file:
            file.write(json.dumps(response_data, ensure_ascii=False) + "\n")

    def fetch_incident_list(self, time_from, time_to=None, limit=10, offset=0):
        """Получает список инцидентов и сохраняет ответ в файл"""
        headers = {"Authorization": f"Bearer {self.token}"}
        payload = {
            "offset": offset,
            "limit": limit,
            "groups": {"filterType": "no_filter"},
            "timeFrom": time_from,
            "timeTo": time_to,
            "filterTimeType": "creation",
            "filter": {
                "select": ["key", "name", "category", "type", "status", "created", "assigned"],
                "where": "status NOT IN ('Resolved', 'Closed')",
                "orderby": [
                    {"field": "created", "sortOrder": "descending"},
                    {"field": "status", "sortOrder": "ascending"},
                    {"field": "severity", "sortOrder": "descending"}
                ]
            },
            "queryIds": ["all_incidents"]
        }

        response = requests.post(f"{self.api_url}/api/v2/incidents", headers=headers, json=payload, verify=False)

        if response.status_code == 200:
            incidents_data = response.json()
            incidents_summary = [
                {"id": incident["id"], "name": incident["name"], "category": incident["category"]}
                for incident in incidents_data.get("incidents", [])
            ]

            self.save_raw_response(RAW_RESPONSES_INCIDENTS_DIR, incidents_data, "incident_list.json")

            return incidents_summary, incidents_data
        else:
            print(f"Ошибка при получении списка инцидентов: {response.status_code}, {response.text}")
            return [], {}

    def fetch_incident_details(self, incident_id):
        """Получает детали инцидента и сохраняет ответ в файл"""
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{self.api_url}/api/incidentsReadModel/incidents/{incident_id}", headers=headers, verify=False)

        if response.status_code == 200:
            incident_data = response.json()
            details = {
                "id": incident_data["id"],
                "name": incident_data["name"],
                "correlationRuleNames": incident_data.get("correlationRuleNames", []),
                "influence": incident_data.get("influence"),
                "isConfirmed": incident_data["isConfirmed"]
            }

            self.save_raw_response(RAW_RESPONSES_DETAILS_DIR, incident_data, f"incident_{incident_id}_details.json")

            self.save_handled_response(details)

            return details, incident_data
        else:
            print(f"Ошибка при получении деталей инцидента {incident_id}: {response.status_code}, {response.text}")
            return {}, {}
