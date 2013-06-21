class BackendBase(object):
    def __init__(*args, **kwargs):
        raise NotImplementedError

    def get(self, key):
        raise NotImplementedError

    def put(self, key, value):
        raise NotImplementedError

    def keys(self):
        raise NotImplementedError

from .proxy import BackendProxy
backend = BackendProxy()
