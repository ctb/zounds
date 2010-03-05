"""
Miscellaneous filters.
"""

import blastparser

def parse_blast(result):
    out, err = result
    records = blastparser.parse_string(out)
    records = list(records)

    # error?
    if not records:
        print '--\n** sequence:\n%s' % out
        print >>sys.stderr, '--\n** sequence: %s\n%s' % (name, err)
        return ()
    else:
        assert len(records) == 1, len(records)
        record = records[0]

    return record

def top_matches_only(result):
    """
    Return a list of the top (match, bitscore) tuples with equal bitscores.

    This is useful for my MEGAN analysis stuff. --CTB
    """
    out, err = result
    record = parse_blast(out, err)
    
    if not record:
        return ()

    hit = record.hits[0]
    score = hit.total_score

    hits = []
    hits.append((hit.subject_name, hit.total_score))
    
    for hit in record._hitlines[1:]:
        if hit.total_score == score:
            hits.append((hit.subject_name, hit.total_score))

    return hits
