zounds
======

'zounds' is a client-server setup for running BLASTs on clusters by
using XML-RPC to coordinate between the server & clients.

The 'zounds-central' process runs on the server and serves both
configuration information and sequences to clients upon request.

The 'zounds-worker' processes must have access to BLAST, the BLAST
database(s) in question, and the 'blastparser' Python module.  All of
the sequences and configuration information is supplied by the server
to the zounds-worker.


How does it work?
-----------------

When you start 'zounds-worker', it contacts the 'zounds-central'
server and requests config info and a set of sequences.  It then
BLASTs these sequences individually against the specified BLAST
database with the configured parameters and parses the results into a
blastparser.BlastRecord object.  This object is then pickled and
returned to the server via XML-RPC.  It can also optionally be passed
through a filter function, following which the filtered value is
returned.  The 'zounds-central' server saves the returned value as a
record in a 'BsdDbShelf', with the sequence name as the key.

Because XML-RPC works via HTTP, and the clients contact the server,
the individual cluster machines need to be able to talk to the server
over the network.  However, the server never contacts the clients so
the cluster can be hidden behind a firewall and/or NAT.

Running 'zounds-central'
------------------------

Briefly, ::

   python zounds-central <config file> <config section>

See 'config.rc' for examples.  The only trickiness is that the
'blastdb' must be a path accessible to the 'zounds-worker' processes,
while the 'sequences' and 'store_db' must be paths on the server.

Retrieving results
------------------

Use ::

   from bsddb import btopen
   from shelve import BsdDbShelf

   db = BsdDbShelf(btopen(store_db, 'r'))

('db' is a dictionary.)

Note that iterating over very large BsdDbShelf databases is slow to start,
because BsdDbShelf retrieves all of the keys at once.  You can speed things
up by using the raw bsddb database to retrieve the keys into the shelf: ::

   _db = btopen(store_db, 'r')
   db = BsdDbShelf(_db)

   for key in _db:
      value = db[key]

CTB: Woods Hole MBL, 7/2008
