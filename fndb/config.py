from importlib import import_module

__all__ = ('settings',)

class Settings(dict):
    def __init__(self, **kwargs):
        self.from_object(kwargs)

    def from_object(self, obj):
        if isinstance(obj, basestring):
            obj = import_module(obj)
        if isinstance(obj, dict):
            keys = obj.keys()
            _get = dict.get
        else:
            keys = dir(obj)
            _get = getattr
        for key in keys:
            self[key] = _get(obj, key)

    def clear(self):
        super(Settings, self).clear()

    def __getattr__(self, key):
        if key.isupper():
            return self.get(key, None)
        return super(Settings, self).__getattr__(key)

    def __setattr__(self, key, value):
        if key.isupper():
            self[key] = value
        else:
            super(Settings, self).__setattr__(key)

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, dict.__repr__(self))

settings = Settings()
