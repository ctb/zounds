import sys
sys.path.insert(0, '/u/t/dev/hmmer3parser')
import parse_hmmer3
from cStringIO import StringIO

def parse_hmmscan(result):
    out, err = result
    records = parse_hmmer3.parse_hmmscan_scoreForCompleteSeq(StringIO(out))

    return records
