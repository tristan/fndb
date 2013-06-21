from importlib import import_module
from fndb.config import settings as global_settings

class BackendProxy(object):
    _b = None # singleton element for the backend

    @property
    def _backend(self):
        if BackendProxy._b is None:
            self.reconfigure()
        return BackendProxy._b

    def reconfigure(self, settings=None):
        if settings is None:
            settings = global_settings
        if not isinstance(settings.BACKEND, dict):
            raise KeyError, "settings BACKEND key must be a dict, got %r" % settings.BACKEND
        name = settings.BACKEND.get('name')
        if name is None:
            raise KeyError, "settings missing 'name' key from BACKEND"
        mod = 'fndb.backend.{0}'.format(name)
        try:
            mod = import_module(mod)
        except ImportError:
            raise ImportError, "No module named {0}".format(mod)
        cls = getattr(mod, 'BackendWrapper')
        BackendProxy._b = cls(**settings.BACKEND)

    def __getattr__(self, item):
        return getattr(self._backend, item)

    def __setattr__(self, name, value):
        return setattr(self._backend, name, value)

    def __delattr__(self, name):
        return delattr(self._backend, name)
