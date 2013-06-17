import unittest
import os
import uuid
import shutil
from fndb.config import settings

class BaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.tempdir = str(uuid.uuid1())
        os.mkdir(self.tempdir)

        from simplekv import fs
        settings.BACKEND = "simplekv"
        settings.STORE = fs.FilesystemStore(self.tempdir)

    @classmethod
    def tearDownClass(self):
        shutil.rmtree(self.tempdir)
        settings.clear()

    def setUp(self):
        self.assertEqual(settings.BACKEND, "simplekv")
