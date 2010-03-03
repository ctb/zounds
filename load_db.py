#! /usr/bin/env python
from bsddb import btopen
from shelve import BsdDbShelf

def load(filename):
    db = BsdDbShelf(btopen(filename, 'r'))
    return db

if __name__ == '__main__':
    import sys
    load(sys.argv[1])
