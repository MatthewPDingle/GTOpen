"""Separately typed importance-weighted retained-mean preflop lookup."""
import json
import numpy as np
from weighted_visible_objective_v1 import grouped_rows
from weighted_physical_reservoir_v1 import checked_weight
from sampled_physical_reservoir_v1 import checked_row
from sampled_physical_preflop_table_v1 import context_hash, validate_preflop, Table as OriginalTable

METHOD = 'source-deal-weighted-preflop-table-v1'


def build(reservoir, context_source):
    if reservoir.context_sha256 != context_hash(context_source): raise ValueError('Changed context')
    grouped = grouped_rows(reservoir)
    keys = np.unique(reservoir.keys[:reservoir.size], axis=0)
    context = json.loads(context_source); rows = []
    for i in np.flatnonzero(keys[:, 0] < 2**63):
        row = dict(hi=str(int(keys[i, 0])), lo=str(int(keys[i, 1])), actor=reservoir.player,
            n=int(grouped['arity'][i]), active_features=grouped['active'][i].astype(int).tolist(),
            count=int(grouped['counts'][i]), importance_mass=float(grouped['masses'][i]),
            mean_regret=(grouped['targets'][i] * grouped['scale']).tolist())
        validate_preflop(row, context, reservoir.player); checked_row(row, row['mean_regret'])
        rows.append(row)
    return dict(format=2, method=METHOD, context_sha256=context_hash(context_source), player=reservoir.player,
        source_reservoir=reservoir.summary(), rows=rows,
        meaning='Importance-weighted mean retained advantages; count is actual visits. Not action EVs.',
        missing_policy='Preserve neural probabilities for unobserved preflop rows; postflop unchanged')


class Table(OriginalTable):
    def __init__(self, document, context_source):
        if document.get('format') != 2 or document.get('method') != METHOD:
            raise ValueError('Explicit weighted preflop table required')
        for row in document['rows']:
            if type(row['count']) is not int or row['count'] <= 0: raise ValueError('Invalid visit count')
            if type(row['importance_mass']) not in (int, float): raise ValueError('Explicit numeric importance mass required')
            checked_weight(row['importance_mass'] / row['count'])
        # Only the schema-independent probability rule is shared. The public
        # document cannot be loaded by the old unweighted reader.
        super().__init__(dict(document, format=1), context_source)
