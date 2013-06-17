
from importlib import import_module
from utils import cached_property
from config import settings

__all__ = ('backend',)

class BackendProxy(object):

    #@cached_property
    # TODO: this is ok, but if i change the backend property this isn't notified
    @property
    def _backend(self):
        if settings.BACKEND is None:
            raise KeyError, "settings missing BACKEND key"
        mod = import_module('fndb.backend.{0}'.format(settings.BACKEND))
        cls = getattr(mod, 'BackendWrapper')
        return cls(**{k.lower(): v for k,v in settings.iteritems()})

    def __getattr__(self, item):
        return getattr(self._backend, item)

    def __setattr__(self, name, value):
        return setattr(self._backend, name, value)

    def __delattr__(self, name):
        return delattr(self._backend, name)

backend = BackendProxy()
