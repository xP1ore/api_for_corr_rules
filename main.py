import time
from datetime import datetime, timedelta
from config import INCIDENT_FETCH_INTERVAL, API_URL
from incident_manager import IncidentManager
from auth import get_token


def check_for_new_incidents(manager):
    """Проверяет наличие новых инцидентов и возвращает их."""
    time_from = (datetime.now() - timedelta(days=1)).isoformat() + "Z"

    incidents_summary, _ = manager.fetch_incident_list(time_from)

    previous_incidents = manager.load_previous_incidents()
    previous_ids = {incident["id"] for incident in previous_incidents}

    new_incidents = [inc for inc in incidents_summary if inc["id"] not in previous_ids]

    print(f"Новых инцидентов: {len(new_incidents)}")
    return new_incidents if new_incidents else []


def main():
    """Основная логика программы."""
    access_token, refresh_token = get_token()
    manager = IncidentManager(api_url=API_URL, token=access_token, refresh_token=refresh_token)
    while True:
        user_input = input("Нажмите Enter для проверки новых инцидентов или 'q' для выхода: ")

        if user_input.lower() == 'q':
            print("Завершение программы...")
            break

        new_incidents = check_for_new_incidents(manager)

        if new_incidents:
            if input("Хотите запросить детали новых инцидентов? (да/нет) ").lower() == 'да':
                for incident in new_incidents:
                    details, _ = manager.fetch_incident_details(incident["id"])
                    print(f"Детали инцидента {incident['id']} сохранены.")

        print(f"Ожидание {INCIDENT_FETCH_INTERVAL} секунд до следующего запроса.")
        time.sleep(INCIDENT_FETCH_INTERVAL)


if __name__ == "__main__":
    main()
