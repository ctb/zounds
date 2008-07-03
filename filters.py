"""
Miscellaneous filters.
"""

def top_matches_only(record):
    """
    Return a list of the top (match, bitscore) tuples with equal bitscores.

    This is useful for my MEGAN analysis stuff. --CTB
    """
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
