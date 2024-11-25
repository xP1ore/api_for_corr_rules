import requests
from auth import get_token
from config import API_URL


def fetch_incident_list(time_from, time_to=None, limit=10, offset=0):
    """Получает список инцидентов и сохраняет ответ в файл"""
    headers = {
        "Authorization": f"Bearer {get_token()}"
    }
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

    response = requests.post(f"{API_URL}/api/v2/incidents", headers=headers, json=payload, verify=False)

    if response.status_code == 200:
        incidents_data = response.json()
        incidents_summary = [
            {"id": incident["id"], "name": incident["name"], "category": incident["category"]}
            for incident in incidents_data.get("incidents", [])
        ]
        return incidents_summary, incidents_data  # Возвращаем полный ответ
    else:
        print(f"Ошибка при получении списка инцидентов: {response.status_code}, {response.text}")
        return [], {}
