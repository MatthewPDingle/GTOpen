"""Candidate snapshot for finite JSON-native poker query documents.

Preserves caller isolation without Python deepcopy visiting every atomic item.
Not a general deepcopy replacement. GPU/evaluation integration is unqualified.
"""
import json


def snapshot(queries):
    if type(queries) is not dict:
        raise ValueError('Native JSON query object required')
    # Encoding rejects non-finite numbers and non-JSON objects; equality rejects
    # tuple-to-list and integer-key conversion rather than silently adapting it.
    value=json.loads(json.dumps(queries,allow_nan=False,ensure_ascii=True,separators=(',',':')))
    if value!=queries:
        raise ValueError('Snapshot would change the native query document')
    return value
