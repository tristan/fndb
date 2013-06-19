# Fake NDB

I wanted the interface to the Google App Engine's NDB without having to run the GAE. Why? Because I'm weird... I'm unsure at the moment which platform I want to deploy some apps I'm working on, found the ndb model intriguing, and decided I wanted to work with it without depending on a large chunk of the GAE code (but while being able to fall back on it if I end up working on it). My hope is that if I choose something else then I can build a `Backend` to use this with it, and that this hasn't lost too much of whatever robustness and speed the ndb has.

### Things not missing

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