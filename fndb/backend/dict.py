from __future__ import absolute_import
from fndb.config import settings
from fndb.backend import BackendBase, utils
from fndb.db import Key
import cPickle as pickle
from collections import OrderedDict

class BackendWrapper(BackendBase):
    def __init__(self, name=None, pickle_file=None):
        """Creates a dict based backend.
        pickle_file: file to pickle the dict to (optional)
        """
        self.pickle_file = pickle_file
        if pickle_file is not None:
            self.store = pickle.load(pickle_file)
            if not isinstance(self.store, dict):
                raise ValueError, "pickle file '%s' does not contain a dict" % pickle_file
        else:
            self.store = OrderedDict()
    def get(self, key):
        return self.store.get(dump_key(key))
    def put(self, key, value):
        key = utils.validate_key(key)
        self.store[dump_key(key)] = value
        if self.pickle_file is not None:
            pickle.dump(self.store, self.pickle_file)
        return key
    def keys(self):
        return filter(None, [load_key(k) for k in self.store.iterkeys()])

def dump_key(key):
    return '.'.join("{0}.{1}{2}".format(
        k, 'I' if isinstance(i, (int, long)) else 'S', i
    ) for k,i in key.pairs())

def load_key(key):
    a = key.split('.')
    if len(a) % 2 > 0:
        return None
    flat = []
    for k, i in zip(a[:-1:2], a[1::2]):
        cls = int if i[0] == 'I' else str
        i = cls(i[1:])
        flat.extend([k, i])
    return Key(*flat)
