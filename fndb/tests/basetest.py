import unittest
import os
import uuid
import shutil
from fndb.backend import backend
from fndb.config import settings

class BaseTest(unittest.TestCase):

    @classmethod
    def setUpFilesystemStoreBackend(self):
        self.tempdir = str(uuid.uuid1())
        os.mkdir(self.tempdir)

        from simplekv import fs
        settings.BACKEND = {
            'name':'simplekv',
            'store': 'simplekv.fs.FilesystemStore',
            'root' : self.tempdir
        }
        backend.reconfigure()

    @classmethod
    def tearDownFilesystemStoreBackend(self):
        shutil.rmtree(self.tempdir)

    @classmethod
    def setUpClass(self):
        settings.BACKEND = {
            'name':'dict'
        }
        backend.reconfigure()
        #self.setUpFilesystemStoreBackend()

    @classmethod
    def tearDownClass(self):
        #self.tearDownFilesystemStoreBackend()
        pass


