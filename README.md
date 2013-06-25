# Fake NDB

I wanted the interface to the Google App Engine's NDB without having to run the GAE. Why? Because I'm weird... I'm unsure at the moment which platform I want to deploy some apps I'm working on, found the ndb model intriguing, and decided I wanted to work with it without depending on a large chunk of the GAE code (but while being able to fall back on it if I end up working on it).

After managing to enter the right things into google and finding the right parts in the sdk code I was able to figure out how to use the ndb code and the backend services used by the `dev_appserver.py` outside of the `dev_appserver.py` environment. This easily enables all the functionality of the NDB while allowing you to use whatever development server you want (e.g. behind mod_wsgi).

I'm yet to figure out what the performance limitations of this are. A lot of the GAE api stub code has comments like:
> Stubs may be either trivial implementations of APIProxy services (e.g.
>  DatastoreFileStub, UserServiceStub) or "real" implementations.

Which to me `"real"` in quotes makes it seem like they're probably still much more trivial implementations of the APIProxy services than what you would get in production running on google's servers.

### Setup

##### simplekv backend

	pip install simplekv

##### configure

Create a config file (e.g. `settings.py`) in your project and add the following:

```
BACKEND = {
	'name':'simplekv',
	'store':'<path.to.KeyValueStore.subclass>',
	'arg1':'<additional arg needed to instanciate store>'
}
```

an example using `simplekv.fs.FilesystemStore`
```
BACKEND = {
	'name':'simplekv',
	'store':simplekv.fs.FilesystemStore',
	'root':'/tmp'
}
```

then from you project startup call:

	from fndb.config import settings
	settings.from_object('path.to.your.project.config')

### Reconfigure backend on the fly

If you need to change which backend you're using on the fly, you need to do the following (I found I wanted this functionality for clearning the datastore inbetween tests)

	from fndb.backend import backend
	backend.reconfigure()

### Enabling GAE NDB classes without changing namespaces

If you want to switch in the GAE's NDB classes without having to change all your namespaces use:

	from fndb import ndb
	ndb.enable()

Additionally you can set up the dev GAE datastores used by `dev_appserver.py` outside of the GAE dev environment by calling:

	ndb.setup_stubs(app_id, app_path, storage_path)

Note that for the above to work, the GAE SDK and its associated libraries needs to be on your python path. An easy way to do this is to use a `.pth` file in your `site-packages` e.g. create a file `/path/to/python/site-packages/gae.pth` containing the following:

	/path/to/google_appengine_sdk
	import dev_appserver; dev_appserver.fix_sys_paths()

### Things missing

 * A LOT! (pretty much everything)

### Ideas for things

##### REST query interface

Build a flask blueprint that provides wrappers for the ndb queries

Get all of kind `ModelA`
```
GET http://rest-server/blueprint_prefix/query/ModelA
```

Get a specific ModelA
```
GET http://rest-server/blueprint_prefix/query/ModelA/id/
```

Get all with a composite key
```
GET http://rest-server/blueprint_prefix/query/Kind1/ID1/Kind2/ID2/Kind3/
```


### Random thoughts

I've had to change the `Model.put` and `Key.get` methods a bit too much for my liking. What I would like is to just keep the majority of the .ndb code from GAE in tact and simply have a database backend of my choosing, but the code is a bit too tied in with the database code.

### Thing I'm scared of (mostly due to lack of time spent trying to understand how they work)

##### async stuff

tasklets, contexts,  etc

##### database transactional stuff

transactions, caches, etc.

##### eventual consistency

My current code doesn't mimic this in any way, which could be catastrophic in the future.

##### model/query projections

https://developers.google.com/appengine/docs/python/datastore/projectionqueries

Scared is the wrong term here, this should really be easy, I've just gotta do it.

##### `Key` namespaces

##### gql

I really hope I wont have to implement any of this manually. I'm sure the code based query() stuff is going to be painful enough.

##### How I store data

I have a feeling I have a long journey infront of me.

##### That I'm wasting my time!

Wasting is a harsh term, I'm learning at least, but I have a feeling that once I understand how everything is actually working here there will be an obvious point of entry where I could have simply copied all the ndb code and replaced X with Y and have exactly what I wanted in the first place.
