import requests
from auth import get_token
from config import API_URL


def fetch_incident_details(incident_id):
    """Получает детали инцидента и сохраняет ответ в файл"""
    headers = {
        "Authorization": f"Bearer {get_token()}"
    }
    response = requests.get(f"{API_URL}/api/incidentsReadModel/incidents/{incident_id}", headers=headers, verify=False)

    if response.status_code == 200:
        incident_data = response.json()
        details = {
            "id": incident_data["id"],
            "name": incident_data["name"],
            "correlationRuleNames": incident_data.get("correlationRuleNames", []),
            "influence": incident_data.get("influence"),
            "isConfirmed": incident_data["isConfirmed"]
        }
        return details, incident_data  # Возвращаем полный ответ
    else:
        print(f"Ошибка при получении деталей инцидента {incident_id}: {response.status_code}, {response.text}")
        return {}, {}
