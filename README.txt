zounds
======

'zounds' is a client-server setup for running many parallel BLASTs on
clusters of computers.  It uses XML-RPC to coordinate between the
server & clients.

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

Installing
----------

You'll need to install `Python <http://www.python.org>`__, `pyparsing
<http://pyparsing.wikispaces.com/>`__, and `blastparser
<http://darcs.idyll.org/~t/projects/blastparser-latest.tar.gz>`__, as
well as BLAST and whatever BLAST databases you need.

For the moment, you need to get zounds via 'git', at ::

    git://iorich.caltech.edu/git/public/zounds

or trust that my latest tarball (posted `here
<http://iorich.caltech.edu/~t/transfer/zounds-latest.tar.gz>`__) is in
fact a tarball of the latest version.

Running 'zounds-central'
------------------------

Briefly, ::

   python zounds-central <config file> <config section>

See 'config.rc' for examples.  The only trickiness is that the
'blastdb' must be a path accessible to the 'zounds-worker' processes,
while the 'sequences' and 'store_db' must be paths on the server.

An Example
----------

In one shell, run: ::

   python zounds-central config-dev.rc test

In another shell, run: ::

   python zounds-worker http://localhost:5678/

Once zounds-worker finishes, use CTRL-C to kill the server.

Assuming that all goes well, the file 'test-output.db' will contain 5
BLAST records corresponding to the results of BLASTing
'test-data/seq-db.fa' against itself.  These records are
blastparser.BlastRecord objects; to 'Retrieving results', below.

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

Each record is a blastparser.BlastRecord, and you can do something like this
to get some basic results: ::

   record = db[seq_name]
   for hit in record:
      print hit.subject_name, hit.total_expect

Using filters
-------------

Filters are useful for situations where you only need a small subset
of the information from BLAST: rather than pickling and encoding a
full BLAST record, filters can reduce the full blastparser.BlastRecord
to something much smaller.

The filter function can do anything you want, as long as it takes in a
BlastRecord and returns something picklable.  For now, it must be
specified in the config file as `module.function`; `module` will be
imported and then `function` will be retrieved from that namespace.
The filter is then run on each record, like so:

            if filter:
                record = filter(record)

Note that this all occurs *on the worker* so you will need to make sure
that your filter module(s) are available to 'zounds-worker'.

There's an example filter function in 'filters.py', function
'top_matches_only'.

How well does it scale?
-----------------------

I've BLASTed 200,000 sequences against the 'nr' database using 128
simultaneous workers, without any problems. In theory the disk and
network I/O should be the most time-consuming aspect of the server,
and since everything on the server side is threaded, I don't expect
there to be server-side performance issues.

On the client side there are likely to be a few performance problems:

 1. BLAST is run on each sequence individually, for simplicity's sake.
    This means the BLAST database is reloaded for every BLAST.  This
    could be optimized at the expense of a bit more code complexity
    in 'zounds-worker'.

 2. The blastparser library is sloooooow.

 3. The worker submits the BLAST data to the server directly, without
    starting a thread.  This means that if the server or network
    is really busy, the worker may be network-bound.  (This should be
    particularly easy to fix.)

None of these problems prevent zounds from working and so I just
ignore 'em.  You can fix them if you like.  Personally I'd prefer to
keep the worker code as simple as possible, but it should be fairly
easy to hack performance improvements in if you need or want them.

--

CTB: Woods Hole MBL, 7/2008
