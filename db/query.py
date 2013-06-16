
from . import Key
from fndb import backend

__all__ = ('Query',)

class Query(object):

    __ancestor = None

    def __init__(self, kind=None, filters=None, ancestor=None):
        if ancestor is not None:
            self.__ancestor = list(ancestor.flat())
        self.__kind = kind
        self.__filters = filters

    def filter(self, f):
        pass

    def get(self):
        values = []
        for k in backend.keys():
            if self.__ancestor is not None and self.__ancestor != k.parent():
                continue
            if self.__kind != k.kind(): #not in k[0::2]:
                continue
            values.append(k.get())
        return values

