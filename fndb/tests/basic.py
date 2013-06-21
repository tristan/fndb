#import unittest
from basetest import BaseTest

__all__ = ['BasicTest']

class BasicTest(BaseTest):
    def test_keys(self):
        from fndb.db import Key
        k = Key('ABC','def')
        self.assertEqual(k.kind(), 'ABC')
        self.assertEqual(k.id(), 'def')

    def test_urlsafe(self):
        from fndb import db
        class URLSafeTestModel(db.Model):
            pass
        x1 = URLSafeTestModel()
        k1 = x1.put().key
        u = k1.urlsafe()
        k2 = db.Key(urlsafe=u)
        x2 = k2.get()
        self.assertEqual(k1, k2)
        self.assertEqual(x1, x2)

    def test_basic(self):
        from fndb import db

        class BasicTestModel(db.Model):
            a = db.StringProperty(default="A")
        X = BasicTestModel

        x = X()
        self.assertEqual(x.a, "A")
        x = X(a="b")
        self.assertEqual(x.a, "b")
        x.a = "c"
        self.assertEqual(x.a, "c")
        x.put()
        self.assertIsNotNone(x.key.id())
        id = x.key.id()
        x = None
        x = X.get_by_id(id)
        self.assertEqual(x.key.id(), id)
        self.assertEqual(x.a, "c")

    def test_required(self):
        from fndb import db
        class RequiredTestModel(db.Model):
            a = db.StringProperty(required=True)
        x = RequiredTestModel()
        with self.assertRaises(ValueError):
            x.put()


    def test_specific_key(self):
        from fndb import db
        class TestSKModel(db.Model):
            pass
        id = 'xxxxxxxxx'
        idn = 'nnnnnnnnn'
        key=db.Key(TestSKModel._get_kind(), id)
        x = TestSKModel(key=key).put()
        self.assertEqual(x.key.id(), id)

        xn = TestSKModel(parent=x.key, id=idn).put()
        self.assertEqual(xn.key.id(), idn)

    def test_swapped_arg_names(self):
        from fndb import db
        class TestSwappedArgNamesModel(db.Model):
            a = db.StringProperty(name='b')
            b = db.StringProperty(name='a')
        X = TestSwappedArgNamesModel
        x = X(a="1",b="2")
        self.assertEqual(x.a, "1")
        self.assertEqual(x.b, "2")
        x.put()
        y = X.get_by_id(x.key.id())
        self.assertEqual(y.a, "1")
        self.assertEqual(y.b, "2")

    def test_named_property(self):
        from fndb import db
        class TestModelWithNamedProperty(db.Model):
            something_really_long_for_some_reason = db.StringProperty(name='a', default="A")
        X = TestModelWithNamedProperty
        s = "some longer text for no real reason"
        x = X(something_really_long_for_some_reason=s)
        self.assertEqual(x.something_really_long_for_some_reason, s)
        x = X.get_by_id(x.put().key.id())
        self.assertEqual(x.something_really_long_for_some_reason, s)
  
    def test_property_validation(self):
        from fndb import db
        class TestPropValidation(db.Model):
            a = db.StringProperty()

        with self.assertRaises(ValueError):
            TestPropValidation(a=1)

        with self.assertRaises(TypeError):
            class TestPropValidation2(db.Model):
                a = db.Property()

    def test_expando(self):
        from fndb import db
        class TestExpando(db.Expando):
            pass

        x = TestExpando()
        x.a = 1
        x.b = '2'
        x.put()
        k = x.key
        y = TestExpando.get_by_id(k.id())
        self.assertEqual(y.a, 1)
        self.assertEqual(y.b, '2')

    def test_update(self):
        from fndb import db
        class TestUpdate(db.Model):
            a = db.StringProperty()

        x = TestUpdate(a='a')
        id = x.put().key.id()
        self.assertIsNotNone(x.key)
        self.assertIsNotNone(x.key.id())
        x.a = 'b'
        x.put()
        self.assertEqual(x.a, 'b')
        y = TestUpdate.get_by_id(id)
        self.assertEqual(y.a, 'b')


    def test_repeated(self):
        from fndb import db
        class TestRepeated(db.Model):
            a = db.StringProperty(repeated=True)

        x = TestRepeated()
        with self.assertRaises(ValueError):
            x.a = "abc"
        lv1 = ['1','2','3']
        lv2 = ['4','5','6']
        x.a = lv1
        id1 = x.put().key.id()
        x = TestRepeated.get_by_id(id1)
        self.assertEqual(x.a, lv1)
        x.a = lv2
        id2 = x.put().key.id()
        self.assertEqual(id1, id2)
        x = TestRepeated.get_by_id(id2)
        self.assertEqual(x.a, lv2)
        # test always return list
        x.a = tuple(lv1)
        x.put()
        x = TestRepeated.get_by_id(id1)
        self.assertEqual(x.a, lv1)

        x = TestRepeated()
        self.assertFalse('x' in x.a)
