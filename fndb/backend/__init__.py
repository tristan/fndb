class BackendBase(object):
    def __init__(*args, **kwargs):
        raise NotImplementedError

    def get(self, key):
        raise NotImplementedError

    def put(self, key, value):
        """Writes the key:value pair to the backend, generating an ID if key.id is None
        and returns the resulting key"""
        raise NotImplementedError

    def keys(self):
        raise NotImplementedError

from .proxy import BackendProxy
backend = BackendProxy()
