from __future__ import absolute_import
from importlib import import_module
from fndb.config import settings
from fndb.backend import BackendBase
from simplekv import KeyValueStore
from fndb.db import Key
import cPickle as pickle

class BackendWrapper(BackendBase):
    def __init__(self, name=None, store=None, **kwargs):
        """Creates a simplekv store based backend.
        store: either a string containing the full packagename and classname of the 
               store to use (i.e. 'simplekv.fs.FilesystemStore') or an instance of
               a class that implements simplekv.KeyValueStore
        kwargs: the arguments required to instantiate an instance of store (only needed
                if store is gives as a string).
        """
        if store is not None and isinstance(store, basestring):
            i = store.rfind('.')
            mod, cls = (store[:i], store[i+1:])
            mod = import_module(mod)
            cls = getattr(mod, cls)
            store = cls(**kwargs)
        if store is None or not isinstance(store, KeyValueStore):
            raise ValueError("settings.BACKEND['store'] needs to be set to a "
                             "simplekv.KeyValueStore instance, got: %r"
                             % store)
        self.store = store
    def get(self, key):
        key = '.'.join(key.flat())
        try:
            return pickle.loads(self.store.get(key))
        except KeyError:
            return None
    def put(self, key, value):
        key = '.'.join(key.flat())
        self.store.put(key, pickle.dumps(value))
    def keys(self):
        return [Key(*k) for k in 
                [k.split('.') for k in self.store.iter_keys()]
                if len(k) % 2 == 0]
