import unittest
from unittest.mock import patch, MagicMock
import os
import json
from datetime import datetime, timedelta
from incident_manager import IncidentManager
from config import (
    RAW_RESPONSES_TOKENS_DIR,
    RAW_RESPONSES_INCIDENTS_DIR,
    RAW_RESPONSES_DETAILS_DIR,
    HANDLED_RESPONSES_DIR,
    HANDLED_INCIDENTS_FILE,
    API_URL
)


class TestIncidentManager(unittest.TestCase):

    def setUp(self):
        """Подготовка тестовой среды: создаем директории, если их нет."""
        self.api_url = API_URL
        self.token = "dummy_token"
        self.refresh_token = "dummy_refresh_token"
        self.manager = IncidentManager(self.api_url, self.token, self.refresh_token)

        os.makedirs(RAW_RESPONSES_TOKENS_DIR, exist_ok=True)
        os.makedirs(RAW_RESPONSES_INCIDENTS_DIR, exist_ok=True)
        os.makedirs(RAW_RESPONSES_DETAILS_DIR, exist_ok=True)
        os.makedirs(HANDLED_RESPONSES_DIR, exist_ok=True)

        # if os.path.exists(HANDLED_INCIDENTS_FILE):
        #   os.remove(HANDLED_INCIDENTS_FILE)

    """
    def tearDown(self):

        # Удаляем файлы из директорий
        for directory in [RAW_RESPONSES_TOKENS_DIR, RAW_RESPONSES_INCIDENTS_DIR, RAW_RESPONSES_DETAILS_DIR]:
            for file in os.listdir(directory):
                os.remove(os.path.join(directory, file))
        if os.path.exists(HANDLED_INCIDENTS_FILE):
            os.remove(HANDLED_INCIDENTS_FILE)

        # Удаляем директории, если они пустые
        for directory in [RAW_RESPONSES_TOKENS_DIR, RAW_RESPONSES_INCIDENTS_DIR, RAW_RESPONSES_DETAILS_DIR, HANDLED_RESPONSES_DIR]:
            if os.path.exists(directory) and not os.listdir(directory):
                os.rmdir(directory)
    """

    @patch("requests.post")
    def test_fetch_incident_list(self, mock_post):
        """Тестирует получение списка инцидентов."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "incidents": [
                {"id": "1", "name": "Incident 1", "category": "Category A"},
                {"id": "2", "name": "Incident 2", "category": "Category B"}
            ]
        }
        mock_post.return_value = mock_response

        time_from = (datetime.now() - timedelta(days=1)).isoformat() + "Z"
        incidents_summary, incidents_data = self.manager.fetch_incident_list(time_from)

        # Проверка корректности данных
        self.assertEqual(len(incidents_summary), 2)
        self.assertEqual(incidents_summary[0]["id"], "1")

        # Проверка сохранения сырых данных
        raw_file = os.path.join(RAW_RESPONSES_INCIDENTS_DIR, "incident_list.json")
        self.assertTrue(os.path.exists(raw_file))
        with open(raw_file, "r", encoding="utf-8") as file:
            raw_data = json.load(file)
            self.assertEqual(raw_data, mock_response.json.return_value)

    @patch("requests.get")
    def test_fetch_incident_details(self, mock_get):
        """Тестирует получение деталей инцидента."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "1",
            "name": "Incident 1",
            "correlationRuleNames": ["Rule 1"],
            "influence": "High",
            "isConfirmed": True
        }
        mock_get.return_value = mock_response

        details, raw_data = self.manager.fetch_incident_details("1")

        # Проверка корректности данных
        self.assertEqual(details["id"], "1")
        self.assertEqual(details["name"], "Incident 1")

        # Проверка сохранения сырых данных
        raw_file = os.path.join(RAW_RESPONSES_DETAILS_DIR, "incident_1_details.json")
        self.assertTrue(os.path.exists(raw_file))
        with open(raw_file, "r", encoding="utf-8") as file:
            raw_data_from_file = json.load(file)
            self.assertEqual(raw_data_from_file, mock_response.json.return_value)

        # Проверка сохранения обработанных данных
        self.assertTrue(os.path.exists(HANDLED_INCIDENTS_FILE))
        with open(HANDLED_INCIDENTS_FILE, "r", encoding="utf-8") as file:
            handled_data = json.loads(file.readline().strip())
            self.assertEqual(handled_data, details)

    def test_load_previous_incidents(self):
        """Тестирует загрузку ранее обработанных инцидентов."""
        # Тестовые данные
        test_data = [{"id": "1", "name": "Incident 1"}, {"id": "2", "name": "Incident 2"}]
        with open(HANDLED_INCIDENTS_FILE, "w", encoding="utf-8") as file:
            for entry in test_data:
                file.write(json.dumps(entry, ensure_ascii=False) + "\n")

        loaded_data = self.manager.load_previous_incidents()
        self.assertEqual(len(loaded_data), 2)
        self.assertEqual(loaded_data[0]["id"], "1")

    def test_save_raw_response(self):
        """Тестирует сохранение сырых данных."""
        test_data = {"key": "value"}
        self.manager.save_raw_response(RAW_RESPONSES_INCIDENTS_DIR, test_data, "test.json")
        file_path = os.path.join(RAW_RESPONSES_INCIDENTS_DIR, "test.json")

        self.assertTrue(os.path.exists(file_path))
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            self.assertEqual(data, test_data)

    def test_save_handled_response(self):
        """Тестирует сохранение обработанных данных."""
        test_data = {"id": "1", "name": "Incident 1"}
        self.manager.save_handled_response(test_data)

        self.assertTrue(os.path.exists(HANDLED_INCIDENTS_FILE))
        with open(HANDLED_INCIDENTS_FILE, "r", encoding="utf-8") as file:
            data = json.loads(file.readline().strip())
            self.assertEqual(data, test_data)


if __name__ == "__main__":
    unittest.main()
