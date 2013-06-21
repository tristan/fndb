from __future__ import absolute_import
from fndb.config import settings
from fndb.backend import BackendBase
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
        key = '.'.join(key.flat())
        return self.store.get(key)
    def put(self, key, value):
        key = '.'.join(key.flat())
        self.store[key] = value
        if self.pickle_file is not None:
            pickle.dump(self.store, self.pickle_file)
    def keys(self):
        return [Key(*k) for k in 
                [k.split('.') for k in self.store.iterkeys()]
                if len(k) % 2 == 0]
