import unittest
from unittest.mock import patch, MagicMock
from main import main


class TestMainWithMocks(unittest.TestCase):
    def test_main_logic(self):
        """Тестирует основную функцию main."""
        # Входные данные
        input_sequence = ["", "да", "q"]

        # Данные для IncidentManager
        mock_incident_list = (
            [{"id": "2", "name": "Incident 2", "category": "Category 1"}],  # Новые инциденты
            {}  # Сырые данные
        )
        mock_previous_incidents = [
            {"id": "1", "name": "Incident 1", "category": "Category 2"}
        ]
        mock_incident_details = (
            {"id": "2", "name": "Incident 2", "details": "Some details"},  # Обработанные данные
            {}
        )

        with patch("config.API_URL", "https://mock-api.com"), \
             patch("sys.exit", MagicMock()) as mock_exit, \
             patch("time.sleep", return_value=None), \
             patch("builtins.input", side_effect=input_sequence), \
             patch("main.IncidentManager") as mock_manager_class, \
             patch("main.get_token", return_value=("mock_access_token", "mock_refresh_token")) as mock_get_token:

            # поведение IncidentManager
            mock_manager = MagicMock()
            mock_manager.fetch_incident_list.return_value = mock_incident_list
            mock_manager.load_previous_incidents.return_value = mock_previous_incidents
            mock_manager.fetch_incident_details.return_value = mock_incident_details
            mock_manager_class.return_value = mock_manager

            main()

            mock_get_token.assert_called_once()

            mock_manager_class.assert_called_once_with(
                api_url="https://mock-api.com",
                token="mock_access_token",
                refresh_token="mock_refresh_token"
            )

            mock_manager.fetch_incident_list.assert_called_once()
            mock_manager.load_previous_incidents.assert_called_once()
            mock_manager.fetch_incident_details.assert_called_once_with("2")

            mock_exit.assert_called_once_with(0)


if __name__ == "__main__":
    unittest.main()
