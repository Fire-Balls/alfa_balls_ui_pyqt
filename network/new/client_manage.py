from network.new.client import TaskTrackerClient

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