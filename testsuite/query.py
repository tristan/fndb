import unittest
import os
import uuid
import shutil
from basetest import BaseTest
from fndb.config import settings

__all__ = ['QueryTest']

from fndb import db
class QueryTestModel(db.Model):
    a = db.StringProperty()

class QueryTestModel2(db.Model):
    a = db.StringProperty(repeated=True)

class QueryTest(BaseTest):

    @classmethod
    def setUpClass(cls):
        super(QueryTest, cls).setUpClass()
        QueryTestModel(a='1').put()
        QueryTestModel(a='2').put()
        QueryTestModel(a='3').put()
        QueryTestModel(a='4').put()
        QueryTestModel(a='5').put()
        QueryTestModel(a='5').put()
        QueryTestModel(a='5').put()
        QueryTestModel(a='5').put()

        QueryTestModel2(a=['1','2','3','4']).put()
        QueryTestModel2(a=['5','6','7','8']).put()
        QueryTestModel2(a=['9','0','1','2']).put()
        QueryTestModel2(a=['3','4','5','6']).put()
        QueryTestModel2(a=['7','8','9','0']).put()
        QueryTestModel2(a=['1','2','3','4']).put()

    def test_all(self):
        q = QueryTestModel.query()
        r = q.fetch()
        self.assertEqual(len(r), 8)

    def test_filter_get(self):
        q = QueryTestModel.query(QueryTestModel.a == '5')
        r = q.get()
        self.assertEqual(r.a, '5')
        q = QueryTestModel.query(QueryTestModel.a == '6')
        r = q.get()
        self.assertIsNone(r)

    def test_filter_fetch(self):
        q = QueryTestModel.query(QueryTestModel.a == '5')
        r = q.fetch()
        self.assertEqual(len(r), 4)
        self.assertEqual(r[0].a, '5')
        r = q.fetch(2)
        self.assertEqual(len(r), 2)
        q = QueryTestModel.query(QueryTestModel.a == '6')
        r = q.fetch()
        self.assertEqual(len(r), 0)

    def test_iter(self):
        q = QueryTestModel.query()
        i = 1
        for r in iter(q):
            self.assertEqual(r.a, str(i))
            i += (1 if i < 5 else 0)

    def test_repeated_prop(self):
        q = QueryTestModel2.query(QueryTestModel2.a == '1')
        r = q.fetch()
        self.assertEqual(len(r), 3)
        q = QueryTestModel2.query(QueryTestModel2.a != '1')
        r = q.fetch()
        self.assertEqual(len(r), 6)
