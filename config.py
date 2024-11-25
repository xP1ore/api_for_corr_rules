API_URL = "https://localhost"  # Записывать в виде https://localhost:3334/connect/token
USERNAME = "Administrator"     # Логин учетной записи пользователя PT MC
PASSWORD = "P@ssw0rd"          # Пароль учетной записи
# Идентификатор приложения, например mpx для MaxPatrol SIEM, ptkb для KnowledgeBase,
# idmgr для Management and Configuration
CLIENT_ID = "mpx"
CLIENT_SECRET = "ela74298-ff88-3268-9734-51de0a2c8d5e"  # Ключ доступа к приложению
SCOPE = "offline_access mpx.api ptkb.api"  # Права доступа по токену.
INCIDENT_FETCH_INTERVAL = 60  # Интервал опроса в секундах

# Пути для сохранения ответов
RAW_RESPONSES_DIR = "raw_responses"
RAW_RESPONSES_TOKENS_DIR = f"{RAW_RESPONSES_DIR}/tokens"
RAW_RESPONSES_INCIDENTS_DIR = f"{RAW_RESPONSES_DIR}/incidents"
RAW_RESPONSES_DETAILS_DIR = f"{RAW_RESPONSES_DIR}/details"
HANDLED_RESPONSES_DIR = "handled_responses"
HANDLED_INCIDENTS_FILE = f"{HANDLED_RESPONSES_DIR}/incidents.txt"
