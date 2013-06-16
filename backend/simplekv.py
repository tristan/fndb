from __future__ import absolute_import
from fndb.config import settings
from fndb.backend import BackendBase
from simplekv import KeyValueStore
from fndb.db import Key
import cPickle as pickle

class BackendWrapper(BackendBase):
    def __init__(self, store=None, **kwargs):
        if store is None or not isinstance(store, KeyValueStore):
            raise ValueError('settings.STORE needs to be set to a '
                             'simplekv.KeyValueStore instance, got: %r'
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
