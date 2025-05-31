from network.new.client import TaskTrackerClient

_client = None

def get_client():
    global _client
    if _client is None:
        _client = TaskTrackerClient('http://localhost:8080')
    return _client
