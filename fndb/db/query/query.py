
from ..model import Key
from fndb.backend import backend
from .. import model


__all__ = ['Query',]

from .node import *
from .order import *

from . import node
__all__ += node.__all__
from . import order
__all__ += order.__all__

class Query(object):
    """
    """
    def __init__(self, kind=None, filters=None, ancestor=None,
                 orders=None, default_options=None):
        if ancestor is not None:
            if not isinstance(ancestor, model.Key):
                raise TypeError('ancestor must be a Key; received %r' % (ancestor,))
            if not ancestor.id():
                raise ValueError('ancestor cannot be an incomplete key')
        if filters is not None:
            if not isinstance(filters, Node):
                raise TypeError('filters must be a query Node or None; received %r' %
                                (filters,))
        # TODO: orders, default_options
        self.__ancestor = ancestor
        self.__kind = kind
        self.__filters = filters
        self.__orders = orders
        self.__default_options = default_options
        # TODO: projections

    @property
    def filters(self):
        """Accessor for the filters (a Node or None)."""
        return self.__filters

    @property
    def kind(self):
        """Accessor for the kind (a string or None)."""
        return self.__kind

    @property
    def ancestor(self):
        """Accessor for the ancestor (a Key or None)."""
        return self.__ancestor

    @property
    def orders(self):
        """Accessor for the filters (an Order or None)."""
        return self.__orders
    
    @property
    def default_options(self):
        """Accessor for the default_options (a QueryOptions instance or None)."""
        return self.__default_options

    def filter(self, *args):
        """Return a new Query with additional filter(s) applied."""
        if not args:
            return self
        preds = []
        f = self.filters
        if f:
            preds.append(f)
        for arg in args:
            if not isinstance(arg, Node):
                raise TypeError('Cannot filter a non-Node argument; received %r' % arg)
            preds.append(arg)
        if not preds:
            pred = None
        elif len(preds) == 1:
            pred = preds[0]
        else:
            pred = ConjunctionNode(*preds)
        return self.__class__(kind=self.kind, ancestor=self.ancestor,
                              filters=pred, orders=self.orders,
                              default_options=self.default_options)

    def order(self, *args):
        """Return a new Query with additional sort order(s) applied."""
        if not args:
            return self
        orders = []
        o = self.orders
        if o:
            orders.append(o)
        for arg in args:
            if isinstance(arg, model.Property):
                orders.append(PropertyOrder(arg._name, _ASC))
            elif isinstance(arg, Order):
                orders.append(arg)
            else:
                raise TypeError('order() expects a Property or query Order; '
                                'received %r' % arg)
        if not orders:
            orders = None
        elif len(orders) == 1:
            orders = orders[0]
        else:
            orders = CompositeOrder(orders)
        return self.__class__(kind=self.kind, ancestor=self.ancestor,
                              filters=self.filters, orders=orders,
                              default_options=self.default_options)

    def _fetch(self, limit=None):
        """A really dirty fetch
        NOTE: this really sucks as it doesn't take advantage of anything the
        backend might provide to help out with making searches quicker.

        TODO: make the backend code responsible for processing queries.
        _fetch could call a backend.query(self) function, which would use
        all the information available in the query (kind, ancestor, filters, etc)
        to make the query as quick as possible
        """
        matches = 0
        for k in backend.keys():
            if self.__ancestor is not None and self.__ancestor != k.parent():
                continue
            if self.__kind != k.kind(): #not in k[0::2]:
                continue
            if self.__filters is not None:
                flts = self.filters
                if isinstance(flts, Node):
                    flts = [flts]
                if flts:
                    obj = k.get()
                    if not all(f.matches(obj) for f in flts):
                        continue
            matches += 1
            yield k.get()
            if limit is not None and matches >= limit:
                break
        yield None

    def fetch(self, limit=None):
        return [k for k in self._fetch(limit) if k is not None]

    def get(self):
        g = self._fetch()
        r = g.next()
        g.close()
        return r

    def __iter__(self):
        return (x for x in self._fetch() if x is not None)
