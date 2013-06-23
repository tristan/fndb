import os

def setup_stubs(app_id, app_path, storage_path):
    """Sets up the GAE apiproxy stubs. This is needed if you want to use the 
    ndb libraries outside of the GAE.

    Sets up a datastore using sqlite.

    Args:
        app_id: The id of your application.
        app_path: The root path of your application.
        storage_path: The path to write the datastore to.
    
    Notes:
        * To clear the datastore, delete the <storage_path>/datastore file.
    """
    from google.appengine.api import apiproxy_stub_map
    #from google.appengine.api import datastore_file_stub
    from google.appengine.datastore import datastore_stub_util
    from google.appengine.datastore import datastore_sqlite_stub
    from google.appengine.api import memcache
    from google.appengine.api.memcache import memcache_stub
    from google.appengine.api import taskqueue
    from google.appengine.api.taskqueue import taskqueue_stub
    from google.appengine.api import urlfetch_stub

    apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()

    ds_stub = datastore_sqlite_stub.DatastoreSqliteStub(
        app_id,
        os.path.join(storage_path, 'datastore'),
        root_path=app_path,
        auto_id_policy=datastore_stub_util.SCATTERED)
    ds_stub.SetConsistencyPolicy(datastore_stub_util.TimeBasedHRConsistencyPolicy()) # arg defaults to `time`
    #ds_stub = datastore_file_stub.DatastoreFileStub('_', None)
    apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3', ds_stub)
    mc_stub = memcache_stub.MemcacheServiceStub()
    apiproxy_stub_map.apiproxy.RegisterStub('memcache', mc_stub)
    tq_stub = taskqueue_stub.TaskQueueServiceStub()
    apiproxy_stub_map.apiproxy.RegisterStub('taskqueue', tq_stub)
    uf_stub = urlfetch_stub.URLFetchServiceStub()
    apiproxy_stub_map.apiproxy.RegisterStub('urlfetch', uf_stub)
    os.environ['APPLICATION_ID'] = app_id

def enable():
    """Enables using ndb classes in place of fndb

    NOTE: this should be called before any model classes are created
    to ensure no fndb classes are used (e.g. in your app's __init__.py)
    """
    import sys
    from google.appengine.ext import ndb as NDB
    from fndb import backend
    from fndb import config
    import types

    # this creates a new builtin module to replace the current fndb module with
    class fndb_hack(types.ModuleType):
        def __init__(self, *args, **kwargs):
            super(fndb_hack, self).__init__(*args, **kwargs)
            self.db = NDB
            self.ndb = sys.modules['fndb.ndb']
            self.backend = sys.modules['fndb.backend']
            self.config = sys.modules['fndb.backend']

    sys.modules['fndb'] = fndb_hack('fndb')
