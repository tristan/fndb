"""
Mimics the Google App Engine's NDB Models and Properties
https://developers.google.com/appengine/docs/python/ndb/entities

I wanted to be able to build data models with the google app engine in mind
but not have to actually develop everything under the google app engine.

Things are being added as I need them, so there's no guarantee that functionality
that is available in the ndb will be available here, but anything developed here
is guaranteed to run on the google app engine.
"""
import copy
import datetime
import uuid

from fndb import backend

from . import key as key_module
Key = key_module.Key # For export

__all__ = ['Key', 'ModelKey', 'Model', 'Expando']

def _validate_key(value, entity=None):
    if not isinstance(value, Key):
        raise ValueError('Expected Key, got %r' % value)
    if entity and entity.__class__ not in (Model, Expando):
        if value.kind() != entity._get_kind():
            raise TypeError('Expected Key kind to be %s; received %s' %
                            (entity._get_kind(), value.kind()))
    return value

class Property(object):
    """
    TODO: some way to make sure this doesn't get instantiated itself
    """
    _code_name = None
    _name = None
    _repeated = False
    _required = False
    _default = None
    _choices = None
    _validator = None
    _verbose_name = None

    _attributes = ['_name', '_repeated', '_required', '_default',
                   '_verbose_name']

    def __new__(cls, *args, **kwargs):
        if cls is Property:
            raise TypeError("Property class may not be directly instantiated")
        return object.__new__(cls, *args, **kwargs)

    def __init__(self, name=None, required=None, default=None, validator=None,
                 verbose_name=None, choices=None, repeated=None):
        if name is not None:
            if isinstance(name, unicode):
                name = name.encode('utf-8')
            if not isinstance(name, str):
                raise TypeError('Name %r is not a string' % (name,))
            if '.' in name:
                raise ValueError('Name %r cannot contain period characters' % (name,))
            self._name = name
        if required is not None:
            self._required = required
        if default is not None:
            self._default = default
        if verbose_name is not None:
            self._verbose_name = verbose_name
        if choices is not None:
            if not isinstance(choices, (list, tuple, set, frozenset)):
                raise TypeError('choices must be a list, tuple or set; received %r' %
                                choices)
            self._choices = choices
        if repeated is not None:
            self._repeated = repeated
        if validator is not None:
            if not hasattr(validator, '__call__'):
                raise TypeError('validator must be callable or None; received %r' %
                                validator)
            self._validator = validator

        if (bool(self._repeated) + bool(self._required) + (self._default is not None)) > 1:
            raise ValueError('repeated, required and default are mutally exclusive.')

        # TODO: validator

    def _set_code_name(self, cls, code_name):
        self._code_name = code_name
        if self._name is None:
            self._name = code_name

    # Comparison operators on Property instances don't compare the
    # properties; instead they return FilterNode instances that can be
    # used in queries.  See the module docstrings above and in query.py
    # for details on how these can be used.

    def _comparison(self, op, value):
        # TODO: cannot filter undex properties, I don't deal with indexed properties at all
        from .query import FilterNode
        if value is not None:
            value = self._do_validate(value)
        return FilterNode(self._name, op, value)

    def __eq__(self, value):
        """Return a FilterNode instance representing the '=' comparison."""
        return self._comparison('=', value)

    def __ne__(self, value):
        """Return a FilterNode instance representing the '!=' comparison."""
        return self._comparison('!=', value)

    def __lt__(self, value):
        """Return a FilterNode instance representing the '<' comparison."""
        return self._comparison('<', value)

    def __le__(self, value):
        """Return a FilterNode instance representing the '<=' comparison."""
        return self._comparison('<=', value)

    def __gt__(self, value):
        """Return a FilterNode instance representing the '>' comparison."""
        return self._comparison('>', value)

    def __ge__(self, value):
        """Return a FilterNode instance representing the '>=' comparison."""
        return self._comparison('>=', value)

    #def _serialize(self, entity):
    #    return self._get_value(entity)

    #def _deserialize(self, entity, value):
    #    self._set_value(entity, value)

    def _do_validate(self, value):
        value = self._validate(value)
        if self._validator is not None:
            newvalue = self._validator(self, value)
            if newvalue is not None:
                value = newvalue
        if self._choices is not None:
            if value not in self._choices:
                raise ValueError('Value %r for property %s is not an allowed choice' %
                                 (value, self._name))
        return value
    
    def _validate(self, value):
        return value

    def _pre_put(self, entity):
        pass

    def _has_value(self, entity, unused_rest=None):
        return self._name in entity._values

    def _set_value(self, entity, value):
        if self._repeated:
            if not isinstance(value, (list, tuple, set, frozenset)):
                raise ValueError('Expected list or tuple, got %r' % (value,))
            cls = type(value)
            value = cls([self._do_validate(v) for v in value])
        else:
            if value is not None:
                value = self._do_validate(value)
        entity._values[self._name] = value

    def _get_value(self, entity):
        return entity._values.get(self._name, self._default)

    def _delete_value(self, entity):
        if self._name in entity._values:
            del entity._values[self._name]

    def __get__(self, entity, type=None):
        if entity is None:
            return self # __get__ called on class
        return self._get_value(entity)

    def __set__(self, entity, value):
        self._set_value(entity, value)

    def __delete__(self, entity):
        self._delete_value(entity)

class ModelKey(Property):
    def __init__(self):
        super(ModelKey, self).__init__()
        self._name = '__key__'
    def _set_value(self, entity, value):
        if value is not None:
            value = entity._validate_key(value)
        entity._entity_key = value
    def _get_value(self, entity):
        return entity._entity_key
    def _delete_value(self, entity):
        entity._entity_key = None
    def _validate(self, value):
        return _validate_key(value)

class KeyProperty(Property):
    def __init__(self, *args, **kwargs):
        name = kind = None
        for arg in args:
            if isinstance(arg, basestring):
                if name is not None:
                    raise TypeError('You can only specify one name')
                name = arg
            elif isinstance(arg, type) and issubclass(arg, Model):
                if kind is not None:
                    raise TypeError('You can only specify one kind')
                kind = arg
            elif arg is not None:
                raise TypeError('Unexpected positional argument: %r' % (arg,))

        if name is None:
            name = kwargs.pop('name', None)
        elif 'name' in kwargs:
            raise TypeError('You can only specify one name')

        if kind is None:
            kind = kwargs.pop('kind', None)
        elif 'kind' in kwargs:
            raise TypeError('You can only specify one kind')

        super(KeyProperty, self).__init__(name, **kwargs)
        self._kind = kind

    def _validate(self, value):
        if not isinstance(value, Key):
            raise ValueError('%r expects Key, got %r' % (self, value))
        if not value.id():
            raise ValueError('%r expects complete Key, got %r' % (self, value))
        if self._kind is not None:
            if value.kind() != self._kind:
                raise ValueError('%r expects Key with kind=%r, got %r' % (self, self._kind, value))
        return value

class GenericProperty(Property):
    pass

class DateTimeProperty(Property):
    _auto_now = False
    _auto_now_add = False

    def __init__(self, name=None, auto_now=False, auto_now_add=False, **kwargs):
        super(DateTimeProperty, self).__init__(name=name, **kwargs)
        if self._repeated:
            if auto_now:
                raise ValueError('DateTimeProperty %s could use auto_now and be '
                                 'repeated, but there would be no point.' % self._name)
            elif auto_now_add:
                raise ValueError('DateTimeProperty %s could use auto_now_add and be '
                                 'repeated, but there would be no point.' % self._name)

            self._auto_now = auto_now
            self._auto_now_add = auto_now_add

    def _validate(self, value):
        if not isinstance(value, datetime.datetime):
            raise ValueError('%r expects datetime, got %r' % (value,))
        return value

    def _pre_put(self, entity):
        if (self._auto_now or
            (self._auto_now_add and not self._has_value(entity))):
            value = datetime.datetime.now()
            self._set_value(entity, value)

class TextProperty(Property):
    def _validate(self, value):
        if isinstance(value, str):
            # decode from utf-8
            try:
                value = unicode(value, 'utf-8')
            except UnicodeError:
                raise ValueError("%r expects valid utf-8, got %r" % (self, value,))
        elif not isinstance(value, unicode):
            raise ValueError("%r expects string, got %r" % (self, value,))
        if not isinstance(value, basestring):
            raise ValueError('%r expects string value, got %r' %
                             (self, value))
        return value

_MAX_STRING_LENGTH = 1000
class StringProperty(TextProperty):
    def _validate(self, value):
        value = super(StringProperty, self)._validate(value)
        if len(value) > _MAX_STRING_LENGTH:
            raise ValueError('%r value must be at most %d characters' % 
                             (self, _MAX_STRING_LENGTH))
        return value

class BooleanProperty(Property):
    def _validate(self, value):
        if not isinstance(value, bool):
            raise ValueError('%r expects boolean, got %r' %
                             (self, value,))
        return value

class IntegerProperty(Property):
    def _validate(self, value):
        if not isinstance(value, (int, long)):
            raise ValueError('%r expects integer, got %r' %
                             (self, value,))
        return int(value)

class FloatProperty(Property):
    def _validate(self, value):
        if not isinstance(value, (int, long, float)):
            raise ValueError('%r expects float, got %r' %
                             (self, value,))
        return float(value)

class ModelMeta(type):
    def __init__(cls, name, bases, classdict):
        super(ModelMeta, cls).__init__(name, bases, classdict)
        cls._configure_properties()

class Model(object):
    __metaclass__ = ModelMeta
    # Class variables for properties
    _properties = None
    _has_repeated = False
    _kind_map = {}

    # Defaults for instance variables.
    _entity_key = None
    _values = None
    
    # Hardcoded pseudo-property for the key (makes sure every model has a key).
    _key = ModelKey()
    key = _key

    @classmethod
    def _configure_properties(cls):
        kind = cls._get_kind()
        if not isinstance(kind, basestring):
            raise KindError('Class %s defines a _get_kind() method that returns '
                            'a non-string (%r)' % (cls.__name__, kind))
        if not isinstance(kind, str):
            try:
                kind = kind.encode('ascii')  # ASCII contents is okay.
            except UnicodeEncodeError:
                raise KindError('Class %s defines a _get_kind() method that returns '
                                'a Unicode string (%r); please encode using utf-8' %
                                (cls.__name__, kind))
        cls._properties = {}
        if cls.__module__ == __name__:
            return
        for name in set(dir(cls)):
            attr = getattr(cls, name, None)
            if isinstance(attr, Property) and not isinstance(attr, ModelKey):
                attr._set_code_name(cls, name)
                if attr._name in cls._properties:
                    raise ValueError('Class %s defines multiple properties with the '
                                     'same name: %s' % (cls.__name__, attr._name))
                cls._properties[attr._name] = attr
        cls._kind_map[cls._get_kind()] = cls

    def __init__(*args, **kwargs):
        if len(args) > 1:
            raise TypeError('Model constructor takes no positional arguments.')
        (self,) = args
        get_arg = self.__get_arg
        key = get_arg(kwargs, 'key')
        id = get_arg(kwargs, 'id')
        parent = get_arg(kwargs, 'parent')
        if key is not None:
            if id is not None or parent is not None:
                raise AttributeError(
                    'Model constructor given key= does not accept '
                    'id= or parent=.')
            self._key = _validate_key(key, entity=self)
        elif parent is not None:
            self._key = Key(self._get_kind(), id, parent=parent)
        self._values = {}
        self._set_attributes(kwargs)
        
    def _set_attributes(self, kwargs):
        cls = self.__class__
        for name, value in kwargs.iteritems():
            prop = getattr(cls, name)
            if not isinstance(prop, Property):
                raise TypeError('Cannot set non-property %s' % name)
            # TODO: maybe we shouldn't call __x__ directly?
            prop._set_value(self, value)

    def _validate_key(self, key):
        return key

    @classmethod
    def __get_arg(cls, kwargs, kwd):
        alt_kwd = '_' + kwd
        if alt_kwd in kwargs:
            return kwargs.pop(alt_kwd)
        if kwd in kwargs:
            obj = getattr(cls, kwd, None)
            if not isinstance(obj, Property) or isinstance(obj, ModelKey):
                return kwargs.pop(kwd)
        return None

    @classmethod
    def _get_kind(cls):
        return cls.__name__

    def put(self):
        if self._key is None or self._key.id is None:
            key = (self._get_kind(), None) if self._key is None else self._key.flat()
            while True:
                key = key[:-1] + (str(uuid.uuid1()),)
                self._key = Key(*key)
                # make sure the key doesn't already exist
                if backend.get(self._key) is None:
                    break
        val = {}
        for name, prop in sorted(self._properties.iteritems()):
            prop._pre_put(self)
            val[name] = prop._get_value(self)
            if prop._required and val[name] is None:
                raise ValueError('Entity has uninitialized properties: %s' % name)
        backend.put(self._key, val)
        return self

    @classmethod
    def get_by_id(cls, id, parent=None):
        key = Key(cls._get_kind(), id, parent=parent)
        return key.get()

    @classmethod
    def get_or_insert(cls, name, parent=None, **kwargs):
        key = Key(cls,name,parent=parent)
        return key.get() or cls(key=key)

    @classmethod
    def query(cls, *args, **kwargs):
        from .query import Query
        q = Query(kind=cls._get_kind())
        #q = q.filter(*cls._default_filters())
        q = q.filter(*args)
        return q

    def __repr__(self):
        args = []
        for prop in self._properties.itervalues():
            if prop._has_value(self):
                val = prop._get_value(self)
                if val is None:
                    rep = 'None'
                elif prop._repeated:
                    rep = '[...]'
                else:
                    rep = val.__repr__()#prop._value_to_repr(val)
                args.append('%s=%s' % (prop._code_name, rep))
        args.sort()
        if self._key is not None:
            args.insert(0, 'key=%r' % self._key)
        s = '%s(%s)' % (self.__class__.__name__, ', '.join(args))
        return s

    def __hash__(self):
        """Dummy hash function.
        Raises:
        Always TypeError to emphasize that entities are mutable.
        """
        raise TypeError('Model is not immutable')

    def __eq__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        if self._key != other._key:
            return False
        if len(self._properties) != len(other._properties):
            return False  # Can only happen for Expandos.
        my_prop_names = set(self._properties.iterkeys())
        their_prop_names = set(other._properties.iterkeys())
        if my_prop_names != their_prop_names:
            return False
        for name in my_prop_names:
            if '.' in name:
                name, _ = name.split('.', 1)
            my_value = self._properties[name]._get_value(self)
            their_value = other._properties[name]._get_value(other)
            if my_value != their_value:
                return False
        return True

class Expando(Model):
   
    def _set_attributes(self, kwargs):
        for name, value in kwargs.iteritems():
            setattr(self, name, value)

    def __getattr__(self, name):
        if name.startswith('_'):
            return super(Expando, self).__getattr__(name)
        prop = self._properties.get(name)
        if prop is None:
            return super(Expando, self).__getattribute__(name)
        return prop._get_value(self)

    def __setattr__(self, name, value):
        if (name.startswith('_') or
            isinstance(getattr(self.__class__, name, None), (Property, property))):
            return super(Expando, self).__setattr__(name, value)
        repeated = isinstance(value, list)
        prop = GenericProperty(name, repeated=repeated)
        prop._code_name = name
        self._properties[name] = prop
        prop._set_value(self, value)

    def __delattr__(self, name):
        if (name.startswith('_') or
            isinstance(getattr(self.__class__, name, None), (Property, property))):
            return super(Expando, self).__delattr__(name, value)
        prop = self._properties.get(name)
        if not isinstance(prop, Property):
            raise TypeError('Model properties must be Property instances; not %r' % prop)
        prop._delete_value(self)
        if prop in self.__class__._properties:
            raise RuntimeError('Property %s still in the list of properties for the '
                               'base class.' % name)
        del self._properties[name]


# Update __all__ to contain all Property and Exception subclasses.
for _name, _object in globals().items():
    if ((_name.endswith('Property') and issubclass(_object, Property)) or
        (_name.endswith('Error') and issubclass(_object, Exception))):
        __all__.append(_name)
