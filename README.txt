======
zounds
======

'zounds' is a client-server setup for running many parallel commands
(typically BLAST) on clusters of computers.  It uses XML-RPC to
coordinate between the server & clients.

The 'zounds-central' process runs on the server and serves both
configuration information and sequences to clients upon request.

The 'zounds-worker' processes must have access to the command (e.g.
'blastall' for BLAST, the search database(s) in question, and any code
you want to use for post-processing (e.g. the 'blastparser' Python
module).  All of the sequences and configuration information is
supplied by the server to the zounds-worker; all of the actual source
code needs to be on the client machine where zounds-worker runs.

How does it work?
=================

When you start 'zounds-worker', it contacts the 'zounds-central'
server and requests config info and a set of sequences.  It then runs
whatever command you've specified (e.g. BLAST) on the sequences
individually, with the configured parameters.  The results are then
optionally passed through some filter (e.g. parsed by blastparser) and
then pickled and returned to the server via XML-RPC.  The
'zounds-central' server saves the returned value as a record in a
'BsdDbShelf', with the sequence name as the key.

Because XML-RPC works via HTTP, and the clients contact the server,
the individual cluster machines need to be able to talk to the server
directly over the network.  However, the server never contacts the
clients so the cluster can be hidden behind a firewall, proxy, and/or
NAT.

Installing
==========

You'll need to install `Python <http://www.python.org>`__.

For the moment, you need to get zounds via 'git', at ::

    git@github.com:ctb/zounds.git

This can be done with 'git clone git@github.com:ctb/zounds.git'.

Running 'zounds-central'
========================

Briefly, ::

   python zounds-central <config file> <config section>

See 'config.rc' for examples.

For BLAST, the only trickiness is that the 'blastdb' must be a path
accessible to the 'zounds-worker' processes, while the 'sequences' and
'store_db' must be paths on the server.  This is because the sequences
are sent from the server to the client, and but the actual comparison
is done on the client.

An Example
==========

In one shell, run: ::

   python zounds-central config-dev.rc test

In another shell, run: ::

   python zounds-worker http://localhost:5678/

Once zounds-worker finishes, use CTRL-C to kill the server.

Now run: ::

   python dump-raw-output test-output.db

You should get individual BLAST records for each of your query sequences,
almost as if you'd simply run 'blastall' locally.

Retrieving results
==================

Use

Use ::

   python -i load_db.py <output filename>

You'll now have a dictionary 'db' containing the keys (query sequences)
and values.

If you haven't specified a filter, then the values will be tuples::

   (stdout, stderr)

from the BLAST output.

--


**Stupid note:** that iterating over very large BsdDbShelf databases
is slow to start, because BsdDbShelf retrieves all of the keys at
once.  You can speed things up by using the raw bsddb database to
retrieve the keys into the shelf: ::

   _db = btopen(store_db, 'r')
   db = BsdDbShelf(_db)

   for key in _db:
      value = db[key]

Using filters
=============

Filters can be used both for parsing output and actual filtering of
results.

A 'filter' is specified in a config file as 'filter='; for example, in
config-dev.rc, section [test_filter], ::

  filter=filters.parse_blast

wmakes each zounds-worker program import the module 'filters' and run
the function 'parse_blast' on the stdout and stderr of the subprocess
command; the result is then pickled and passed back to the server.

If the filter returns an empty record (None, or (), "", or whatever)
then that too is pickled and returned.

Parsing the BLAST results with filters.parse_blast
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For this filter, the blastparser and parse_blast modules must be installed.

  filter=filters.parse_blast

After parsing, each record is a blastparser.BlastRecord, and you can
do something like this to get some basic results: ::

   record = db[seq_name]
   for hit in record:
      print hit.subject_name, hit.total_expect

Retrieving only a subset of BLAST results with filters.top_matches_only
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Filters are useful for situations where you only need a small subset
of the information: e.g. rather than pickling and encoding a full
BLAST record, filters can reduce the full blastparser.BlastRecord to
something much smaller.

There's an example filter function in 'filters.py', function
'top_matches_only'.

How well does it scale?
=======================

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

 2. The worker submits the BLAST data to the server directly, without
    starting a thread.  This means that if the server or network
    is really busy, the worker may be network-bound.  (This should be
    particularly easy to fix.)

None of these problems prevent zounds from working and so I just
ignore 'em.  You can fix them if you like.  Personally I'd prefer to
keep the worker code as simple as possible, but it should be fairly
easy to hack performance improvements in if you need or want them.

Author Info
===========

zounds was hacked together by C. Titus Brown, <titus@idyll.org>.  It is
freely available under the BSD license.

Acknowledgements
================

Tracy Teal and Qingpeng Zhang alpha- and beta-tested zounds.

Questions?
==========

Please contact the `biology-in-python
<http://lists.idyll.org/listinfo/biology-in-python>`__ mailing list with
any questions or comments about zounds.

--

TODO:
 
 - expand to HMMER
 - use sqlite shelve instead, for storage results
 - fix/work with screed v2
 - automatically set number of comparisons/seqs in db for BLAST and HMMER

--

CTB: Woods Hole MBL, 7/2008; MSU 3/2010.
