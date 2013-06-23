"""
Mimics the Google App Engine's NDB Key class
https://developers.google.com/appengine/docs/python/ndb/entities
"""
import base64
import cPickle as pickle
from fndb.backend import backend

__all__ = ['Key']

class Key(object):
    def __new__(cls, *args, **kwargs):
        self = super(Key, cls).__new__(cls)
        self.__pairs = []
        if args:
            if len(args) % 2:
                raise ValueError('Key() must have an even number of positional '
                                 'arguments.')
            pairs = [(args[i], args[i + 1]) for i in xrange(0, len(args), 2)]
            for i, (kind, id) in enumerate(pairs):
                if isinstance(id, unicode):
                    id = id.encode('utf8')
                elif id is None:
                    if i + 1 < len(pairs):
                        raise ValueError('Incomplete Key entry must be last')
                else:
                    if not isinstance(id, (int, long, str)):
                        raise TypeError('Key id must be a string or a number; received %r' % id)
                if isinstance(kind, type):
                    kind = kind._get_kind()
                if isinstance(kind, unicode):
                    kind = kind.encode('utf8')
                if not isinstance(kind, str):
                    raise TypeError('Key kind must be a string or Model class; '
                                    'received %r' % kind)
                if not id:
                    id = None
                self.__pairs.append((kind, id))
        urlsafe = kwargs.get("urlsafe")
        if urlsafe is not None:
            if not isinstance(urlsafe, basestring):
                raise TypeError('urlsafe must be a string; received %r' % urlsafe)
            if isinstance(urlsafe, unicode):
                urlsafe = urlsafe.encode('utf8')
            mod = len(urlsafe) % 4
            if mod:
                urlsafe += "=" * (4 - mod)
            self.__pairs = pickle.loads(base64.b64decode(urlsafe.replace('-', '+').replace('_', '/')))
        parent = kwargs.get("parent")
        if parent is not None:
            self.__pairs[:0] = parent.pairs()
        return self

    def parent(self):
        pairs = self.pairs()
        if len(pairs) <= 1:
            return None
        return Key(*pairs[:-1])

    def pairs(self):
        return self.__pairs

    def id(self):
        return self.__pairs[-1][1]

    def kind(self):
        return self.__pairs[-1][0]

    def flat(self):
        flat = []
        for kind, id in self.pairs():
            flat.append(kind)
            flat.append(id)
        return tuple(flat)

    def urlsafe(self):
        urlsafe = base64.b64encode(pickle.dumps(self.pairs()))
        return urlsafe.rstrip('=').replace('+', '-').replace('/', '_')

    def get(self):
        from . import model
        obj = backend.get(self)
        if obj is None:
            raise KeyError
        cls = model.Model._kind_map.get(self.kind())
        expando = issubclass(cls, model.Expando)
        kwargs = {}
        for k,v in obj.iteritems():
            if v is not None:
                code_name = cls._properties.get(k)
                if code_name is None:
                    if not expando:
                        raise KeyError
                    code_name = k
                else:
                    code_name = cls._properties[k]._code_name
                kwargs[code_name] = v            
        mdl = cls(key=self, **kwargs)
        return mdl

    def __repr__(self):
        return 'Key(%s)' % ', '.join(str(i) for i in self.flat())

    def __eq__(self, other):
        if not isinstance(other, Key):
            return NotImplemented
        return (tuple(self.pairs()) == tuple(other.pairs()))

    def __ne__(self, other):
        """The opposite of __eq__."""
        if not isinstance(other, Key):
            return NotImplemented
        return not self.__eq__(other)

    def __lt__(self, other):
        """Less than ordering."""
        if not isinstance(other, Key):
            return NotImplemented
        return self.pairs() < other.pairs()

    def __gt__(self, other):
        """Less than ordering."""
        if not isinstance(other, Key):
            return NotImplemented
        return self.pairs() > other.pairs()

    def __le__(self, other):
        """Less than ordering."""
        if not isinstance(other, Key):
            return NotImplemented
        return self.pairs() <= other.pairs()

    def __ge__(self, other):
        """Less than ordering."""
        if not isinstance(other, Key):
            return NotImplemented
        return self.pairs() >= other.pairs()
