"""Accumulate BB root advantages with actions integrated on sampled cards.

Card and board sampling remain. The ordinary shared reservoirs are untouched.
"""
import re
import numpy as np

METHOD = 'showdown-controlled-bb-root-regrets-v1'


def identity(value):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value):
        raise ValueError('SHA-256 identity required')
    return value


class ShowdownRootRegrets:
    def __init__(self, context_sha256, matrix_sha256, coefficients_sha256):
        self.context_sha256 = identity(context_sha256)
        self.matrix_sha256 = identity(matrix_sha256)
        self.coefficients_sha256 = identity(coefficients_sha256)
        self.steps = 0
        self.counts = np.zeros(169, dtype=np.int64)
        self.regrets = np.zeros((169, 4), dtype=np.float64)

    def step(self, iteration, audits, *, expected_deals, expected_batches):
        if type(iteration) is not int or iteration != self.steps+1:
            raise ValueError('One sequential update per complete generation required')
        if (type(expected_deals) is not int or not 0 < expected_deals < 2**31
                or type(expected_batches) is not int or expected_batches <= 0
                or len(audits) != expected_batches):
            raise ValueError('Complete bounded generation required')
        counts = self.counts.copy(); regrets = self.regrets.copy()
        seen = set(); played_policy = None; added = 0
        for audit in audits:
            target = audit['identity']
            if (audit.get('format') != 1
                    or audit.get('method') != 'showdown-controlled-bb-root-targets-v1'
                    or audit.get('iteration') != iteration
                    or target.get('root_estimator') != 'showdown-controlled-bb-root-targets-v1'
                    or target.get('generation') != iteration-1
                    or target.get('context_sha256') != self.context_sha256
                    or target.get('matrix_sha256') != self.matrix_sha256
                    or target.get('control_coefficients_sha256') != self.coefficients_sha256):
                raise ValueError('Wrong corrected root target identity')
            policy = identity(target['current_initial_policy_sha256'])
            if played_policy is not None and policy != played_policy:
                raise ValueError('All subbatches must use one frozen played policy')
            played_policy = policy
            query = identity(audit['queries_sha256'])
            if query in seen:
                raise ValueError('Duplicate subbatch')
            seen.add(query)
            rows = audit['bb_root_corrections']; deals = set()
            if not rows:
                raise ValueError('Empty root batch')
            for row in rows:
                c, deal = row['hand_class'], row['deal']
                if (type(c) is not int or not 0 <= c < 169
                        or type(deal) is not int or deal < 0 or deal in deals):
                    raise ValueError('Invalid class or repeated root deal')
                deals.add(deal)
                value = np.asarray(row['advantages'], dtype=np.float64)
                if value.shape != (4,) or not np.isfinite(value).all():
                    raise ValueError('Four finite corrected advantages required')
                if counts[c] == np.iinfo(np.int64).max:
                    raise ValueError('Sample count overflow')
                counts[c] += 1; regrets[c] += value; added += 1
            if deals != set(range(len(rows))):
                raise ValueError('One root per sequential batch deal required')
        if added != expected_deals or not np.isfinite(regrets).all():
            raise ValueError('Incomplete generation or regret overflow')
        self.counts, self.regrets, self.steps = counts, regrets, iteration

    def probabilities(self, fallback):
        p = np.asarray(fallback, dtype=np.float64)
        if (p.shape != (169, 4) or not np.isfinite(p).all()
                or np.any(p < 0) or np.max(abs(p.sum(1)-1)) > 1e-12):
            raise ValueError('Normalized four-action fallback required')
        p = p.copy()
        for c in np.flatnonzero(self.counts):
            positive = np.maximum(self.regrets[c], 0.)
            if positive.sum() > 0:
                p[c] = positive/positive.sum()
            else:
                p[c] = np.eye(4)[int(np.argmax(self.regrets[c]))]
        return p

    def document(self):
        return dict(format=2, method=METHOD, context_sha256=self.context_sha256,
            matrix_sha256=self.matrix_sha256, coefficients_sha256=self.coefficients_sha256, completed_updates=self.steps,
            sample_counts=self.counts.tolist(), regret_sums=self.regrets.tolist(),
            meaning='Unweighted sums of showdown-controlled BB root advantages on sampled cards, with exact initial jam targets. No reservoir replacement; not exact call/raise values.')

    @classmethod
    def restore(cls, document, *, context_sha256, matrix_sha256, coefficients_sha256):
        result = cls(context_sha256, matrix_sha256, coefficients_sha256)
        if (document.get('format') != 2 or document.get('method') != METHOD
                or document.get('context_sha256') != context_sha256
                or document.get('matrix_sha256') != matrix_sha256
                or document.get('coefficients_sha256') != coefficients_sha256):
            raise ValueError('Unknown root accumulator or changed identity')
        steps = document['completed_updates']; counts = document['sample_counts']
        regrets = np.asarray(document['regret_sums'], dtype=np.float64)
        if (type(steps) is not int or steps < 0 or len(counts) != 169
                or any(type(n) is not int or not 0 <= n < 2**63 for n in counts)
                or regrets.shape != (169, 4) or not np.isfinite(regrets).all()):
            raise ValueError('Invalid root accumulator state')
        if (steps == 0) != (sum(counts) == 0):
            raise ValueError('Completed generations and sample counts disagree')
        if np.any(regrets[np.asarray(counts) == 0]):
            raise ValueError('No regrets allowed for unseen classes')
        result.steps = steps
        result.counts = np.array(counts, dtype=np.int64)
        result.regrets = regrets.copy()
        return result
