from network.new.client import TaskTrackerClient
import os

CONFIG_FILE_NAME = "client_host.conf"
class ClientManager:
    _instance = None # Классовая переменная для хранения единственного экземпляра
    _initialized = False # Флаг, чтобы убедиться, что __init__ вызывается только один раз

    def __new__(cls, host: str = None):
        """
        Переопределяем метод __new__ для обеспечения того, что создается только один экземпляр.
        """
        if cls._instance is None:
            if host is None:
                raise ValueError("ClientManager: При первой инициализации 'host' должен быть указан.")
            cls._instance = super(ClientManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, host: str = None):
        """
        Инициализирует TaskTrackerClient, но только если он еще не был инициализирован.
        __init__ вызывается при каждой попытке создания экземпляра,
        поэтому используем _initialized флаг.
        """
        if not  ClientManager._initialized:
            if host is None:
                raise ValueError("ClientManager: 'host' не может быть None при первой инициализации.")
            self.host = host
            self.client = TaskTrackerClient(self.host)
            print(f"ClientManager: Экземпляр создан и инициализирован для хоста: {self.host}")
            ClientManager._initialized = True # Устанавливаем флаг, что инициализация прошла

    @staticmethod
    def get_config_path():
        # Можно указать абсолютный путь или рядом с исполняемым файлом
        print(os.path.join(os.path.expanduser("~"), CONFIG_FILE_NAME))
        return os.path.join(os.path.expanduser("~"), CONFIG_FILE_NAME)

    @classmethod
    def save_host_to_file(cls, host: str):
        path = cls.get_config_path()
        with open(path, "w", encoding="utf-8") as f:
            f.write(host)

    @classmethod
    def load_host_from_file(cls) -> str:
        path = cls.get_config_path()
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
        return ""


# --- Использование ---




#
#
# from network.new.client import TaskTrackerClient
#
# _client = None
#
# def get_client():
#     global _client
#     if _client is None:
#         _client = TaskTrackerClient('http://localhost:8080')
#     return _client