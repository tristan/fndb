from .. import model

__all__ = ['AND', 'OR', 'ConjunctionNode', 'DisjunctionNode',
           'FilterNode', 'FalseNode', 'Node',
           ]

class Node(object):
    """Tree node representing an in-memory filtering operation.

    This is used to represent filters that cannot be executed by the
    datastore, for example a query for a structured value.
    """
    def __new__(cls):
        if cls is Node:
            raise TypeError('Cannot instantiate Node, only a subclass.')
        return super(Node, cls).__new__(cls)

    def __eq__(self, other):
        raise NotImplementedError

    def __ne__(self, other):
        eq = self.__eq__(other)
        if eq is not NotImplemented:
            eq = not eq
        return eq

    def __unordered(self, unused_other):
        raise TypeError('Nodes cannot be ordered')
    __le__ = __lt__ = __ge__ = __gt__ = __unordered 

class FalseNode(Node):
    """Tree node for an always-failing filter."""

    def __eq__(self, other):
        if not isinstance(other, FalseNode):
            return NotImplemented
        return True

class FilterNode(Node):
    """Tree node for a single filter expression."""

    def __new__(cls, name, opsymbol, value):
        if isinstance(value, model.Key):
            value = value.to_old_key()
        if opsymbol == '!=':
            n1 = FilterNode(name, '<', value)
            n2 = FilterNode(name, '>', value)
            return DisjunctionNode(n1, n2)
        if opsymbol == 'in':
            pass # TODO:
        self = super(FilterNode, cls).__new__(cls)
        self.__name = name
        self.__opsymbol = opsymbol
        self.__value = value
        return self

    def __eq__(self, other):
        if not isinstance(other, FilterNode):
            return NotImplemented
        return (self.__name == other.__name and
                self.__opsymbol == other.__opsymbol and
                self.__value == other.__value)

    def matches(self, obj):
        values = getattr(obj, self.__name)
        # TODO: should maybe add in a check for obj.prop._repeated = True
        if not hasattr(values, '__iter__'):
            values = [values]
        if self.__opsymbol == '=':
            return any(v == self.__value for v in values)
        elif self.__opsymbol == '!=':
            return any(v != self.__value for v in values)
        elif self.__opsymbol == '>':
            return any(v > self.__value for v in values)
        elif self.__opsymbol == '<':
            return any(v < self.__value for v in values)
        elif self.__opsymbol == '>=':
            return any(v >= self.__value for v in values)
        elif self.__opsymbol == '<=':
            return any(v <= self.__value for v in values)
        raise TypeError("unexpected op symbol %s" % self.__opsymbol)

class ConjunctionNode(Node):
    """Tree node representing a Boolean AND operator on two or more nodes."""

    def __new__(cls, *nodes):
        if not nodes:
            raise TypeError('ConjunctionNode() requires at least one node.')
        elif len(nodes) == 1:
            return nodes[0]
        clauses = [[]]
        for node in nodes:
            if not isinstance(node, Node):
                raise TypeError('ConjunctionNode() expects Node instances as arguments;'
                                ' received a non-Node instance %r' % node)
            if isinstance(node, DisjunctionNode):
                # Apply the distributive law: (X or Y) and (A or B) becomes
                # (X and A) or (X and B) or (Y and A) or (Y and B).
                new_clauses = []
                for clause in clauses:
                    for subnode in node:
                        new_clause = clause + [subnode]
                        new_clauses.append(new_clause)
                clauses = new_clauses
            elif isinstance(node, ConjunctionNode):
                # Apply half of the distributive law: (X or Y) and A becomes
                # (X and A) or (Y and A).
                for clause in clauses:
                    clause.extend(node.__nodes)
            else:
                # Ditto.
                for clause in clauses:
                    clause.append(node)
        if not clauses:
            return FalseNode()
        if len(clauses) > 1:
            return DisjunctionNode(*[ConjunctionNode(*clause) for clause in clauses])
        self = super(ConjunctionNode, cls).__new__(cls)
        self.__nodes = clauses[0]
        return self

    def __iter__(self):
        return iter(self.__nodes)

    def __eq__(self, other):
        if not isinstance(other, ConjunctionNode):
            return NotImplemented
        return self.__nodes == other.__nodes

    def matches(self, obj):
        return all(x.matches(obj) for x in self.__nodes)
        
class DisjunctionNode(Node):
    """Tree node representing a Boolean OR operator on two or more nodes."""

    def __new__(cls, *nodes):
        if not nodes:
            raise TypeError('DisjunctionNode() requires at least one node')
        elif len(nodes) == 1:
            return nodes[0]
        self = super(DisjunctionNode, cls).__new__(cls)
        self.__nodes = []
        for node in nodes:
            if not isinstance(node, Node):
                raise TypeError('DisjunctionNode() expects Node instances as arguments;'
                                ' received a non-Node instance %r' % node)
            if isinstance(node, DisjunctionNode):
                self.__nodes.extend(node.__nodes)
            else:
                self.__nodes.append(node)
        return self

    def __iter__(self):
        return iter(self.__nodes)

    def __eq__(self, other):
        if not isinstance(other, DisjunctionNode):
            return NotImplemented
        return self.__nodes == other.__nodes

    def matches(self, obj):
        return any(x.matches(obj) for x in self.__nodes)

# AND and OR are preferred aliases for these.
AND = ConjunctionNode
OR = DisjunctionNode
