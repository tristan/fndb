from importlib import import_module

__all__ = ('settings',)

class Settings(dict):
    def __init__(self):
        pass

    def from_object(self, obj):
        if isinstance(obj, basestring):
            obj = import_module(obj)
        for key in dir(obj):
            if key.isupper():
                self[key] = getattr(obj, key)

    def clear(self):
        super(Settings, self).clear()

    def __getattr__(self, key):
        if key.isupper():
            return self.get(key, None)
        return super(Settings, self).__getattr__(key)

    def __setattr__(self, key, value):
        if key.isupper():
            self[key] = value

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, dict.__repr__(self))

settings = Settings()
