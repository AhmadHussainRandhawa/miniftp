from pathlib import Path


HOST = "127.0.0.1"
PORT = 2121
BUFFER_SIZE = 4096
ENCODING = "utf-8"
USERS_FILE = "users.json"
SERVER_NAME = "MiniFTP Server"
SERVER_VERSION = "0.5"

PROJECT_ROOT = Path(__file__).parent.resolve()
STORAGE_ROOT = PROJECT_ROOT / "storage"

CLIENT_DOWNLOADS = PROJECT_ROOT / Path("client_downloads")

CLIENT_DOWNLOADS.mkdir(exist_ok=True)