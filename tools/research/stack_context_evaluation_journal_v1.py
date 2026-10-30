"""Append-only evaluation batches for the registered seven-depth comparison.

A durable claim precedes sampling and an intent pins the exact physical hands.
Only complete authenticated evidence can advance the prefix. Recovery never
invokes an evaluator: an incomplete scientific batch must remain a failure.
The caller owns admission, a single process lock and the frozen policy banks.
"""
import json
import os
from pathlib import Path
import re
import uuid
import numpy as np
from owned_columnar_evaluation_archive_v1 import (
    ROOT, ARTIFACTS, MAX_MEMBER, MAX_HEADER, MAX_PACKED, OwnedColumnarEvaluationArchive,
    digest, durable, encoded, read_bounded, restore, unlinked)
from sampled_physical_deals_v1 import PhysicalDeals
from crossed_complete_policy_comparison_v1 import CompletePolicyComparison, PROFILE_NAMES, differences
from stack_context_matched_analysis_v1 import DEPTHS, DEALS, ALPHA

BATCH = 32
QUERY_LIMIT = 1000000
HEX = re.compile(r'[0-9a-f]{64}')
COMMIT = re.compile(r'commit-([0-9]{6})-([0-9a-f]{64})\.json')
MAX_RECORD = 1024 * 1024


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path, limit=MAX_RECORD):
    return json.loads(read_bounded(path, limit))


def publish_new(path, value, guard):
    """Ignore orphan pending files, but never replace an existing commitment."""
    path = unlinked(path)
    require(not path.exists(), 'Preserve existing immutable record')
    raw = encoded(value)
    require(len(raw) <= MAX_RECORD, 'Oversized evaluation record')
    temporary = path.parent / ('.' + path.name + '.' + uuid.uuid4().hex + '.pending')
    durable(temporary, raw)
    guard()
    # On Windows rename refuses an existing destination. The caller also owns
    # the study lock; no check-then-replace of a competing committed record.
    os.rename(temporary, path)
    return digest(raw)


def checked_root(root):
    root = unlinked(root)
    require(root != ROOT and root.is_relative_to(ROOT), 'Explicit research descendant required')
    top = root.relative_to(ROOT).parts[0]
    require(top.startswith(('stack-context-matched-evaluation-', 'stack-context-matched-journal-check-')),
            'Unexpected study evidence root')
    return root


def protocol(context_source, registration_sha256, bank_identities_sha256, cache_sha256):
    for value in (registration_sha256, bank_identities_sha256, cache_sha256):
        require(isinstance(value, str) and HEX.fullmatch(value), 'Explicit pinned identity required')
    context = json.loads(context_source)
    depth = context['config']['stack']
    require(type(depth) in (int, float) and depth in DEPTHS and context['dead_money'] == .5,
            'Unregistered stack or dead money')
    return dict(format=1, purpose='registered-stack-context-complete-policy-evaluation',
        context_sha256=digest(context_source.encode()), depth=int(depth),
        registration_sha256=registration_sha256, bank_identities_sha256=bank_identities_sha256,
        cache_sha256=cache_sha256, seed=9309000+int(depth), total_deals=DEALS, batch_size=BATCH,
        query_limit=QUERY_LIMIT, chance='full_deck', alpha_per_context=ALPHA/len(DEPTHS),
        one_final_look=True, profile_order=list(PROFILE_NAMES))


class EvaluationJournal:
    @classmethod
    def create(cls, root, *, context_source, registration_sha256, bank_identities_sha256, cache_sha256, guard):
        guard()
        root = checked_root(root)
        require(not root.exists() and root.parent.is_dir(), 'New context directory with existing parent required')
        plan = protocol(context_source, registration_sha256, bank_identities_sha256, cache_sha256)
        require(root.name == f"stack-{plan['depth']}", 'Context directory/depth mismatch')
        root.mkdir()
        owner = dict(plan=plan, root=str(root), token=uuid.uuid4().hex)
        durable(root/'journal-owner.json', encoded(owner))
        (root/'intents').mkdir()
        archive = OwnedColumnarEvaluationArchive.create(root/'archive', guard=guard)
        durable(root/'archive-identity.json', encoded(dict(owner_sha256=archive.owner_sha256)))
        return cls(root, context_source=context_source, registration_sha256=registration_sha256,
                   bank_identities_sha256=bank_identities_sha256, cache_sha256=cache_sha256, guard=guard)

    def __init__(self, root, *, context_source, registration_sha256, bank_identities_sha256, cache_sha256, guard):
        self.root = checked_root(root)
        self.guard = guard
        self.source = context_source
        self.plan = protocol(context_source, registration_sha256, bank_identities_sha256, cache_sha256)
        raw = read_bounded(self.root/'journal-owner.json', 4096)
        self.owner = digest(raw)
        owner = json.loads(raw)
        require(owner['root'] == str(self.root) and owner['plan'] == self.plan
                and re.fullmatch(r'[0-9a-f]{32}', owner['token']), 'Changed journal ownership or protocol')
        require(self.root.name == f"stack-{self.plan['depth']}", 'Context directory/depth mismatch')
        identity = read_json(self.root/'archive-identity.json', 4096)
        self.archive = OwnedColumnarEvaluationArchive(self.root/'archive', identity['owner_sha256'], guard=guard)

    def _owned(self):
        self.guard()
        require(digest(read_bounded(self.root/'journal-owner.json', 4096)) == self.owner,
                'Journal ownership changed')

    def _paths(self, start):
        require(type(start) is int and 0 <= start < DEALS and start % BATCH == 0, 'Invalid batch offset')
        name = f'test-{start:06d}'
        return name, self.root/'intents'/(name+'.claim.json'), self.root/'intents'/(name+'.json')

    def _intent(self, start, sampler):
        name, claim, path = self._paths(start)
        require(read_json(claim, 4096) == dict(journal_owner_sha256=self.owner, start=start), 'Intent claim differs')
        raw = read_bounded(path, MAX_RECORD)
        intent = json.loads(raw)
        require(intent['format'] == 1 and intent['journal_owner_sha256'] == self.owner and intent['start'] == start
                and intent['sampler_before'] == sampler.checkpoint(), 'Changed intent lineage or sampler')
        sampled = sampler.sample(BATCH)
        expected = self._batch(start, sampled['deals'])
        require(intent['batch'] == expected and intent['sampler_after'] == sampler.checkpoint(),
                'Test hands or continuation differ from the registered chance stream')
        return intent, digest(raw)

    def _batch(self, start, deals):
        return dict(format=2, batch_id=f"stack-context-matched-evaluation-v1/{self.plan['depth']}/{start:06d}",
                    seed=self.plan['seed'], query_limit=QUERY_LIMIT, deals=deals)

    def _proof(self, name, manifest_sha256, summary_sha256, *, full):
        self.archive._owner()
        store = self.archive.root
        raw = read_bounded(store/(name+'.manifest.json'), MAX_HEADER)
        require(digest(raw) == manifest_sha256, 'Archive manifest identity changed')
        manifest = json.loads(raw)
        receipt = read_json(store/'.batch-work'/(name+'.receipt.json'), 4096)
        require(receipt == dict(name=name, owner_sha256=self.archive.owner_sha256,
                                manifest_sha256=manifest_sha256), 'Archive publication receipt differs')
        require(read_json(store/'.batch-work'/(name+'.claim.json'), 4096) ==
                dict(name=name, owner_sha256=self.archive.owner_sha256), 'Archive claim differs')
        summaries = [row for row in manifest['members'] if row['name'] == 'summary.json']
        require(len(summaries) == 1 and summaries[0]['raw_sha256'] == summary_sha256,
                'Archived summary identity differs')
        packed = unlinked(store/(name+'.xz'))
        require(packed.stat().st_size == manifest['packed_bytes'], 'Archive length changed')
        if full:
            return restore(packed, manifest, guard=self.guard)
        return None

    def _evidence(self, parts, intent):
        require(set(parts) == ARTIFACTS, 'Complete seven-member evaluation evidence required')
        summary = json.loads(parts['summary.json'])
        require(summary['format'] == 1 and summary['purpose'] == 'crossed-complete-policy-effectiveness'
                and summary['deals'] == BATCH and summary['profile_order'] == list(PROFILE_NAMES)
                and summary['allin_cache_sha256'] == self.plan['cache_sha256'], 'Changed evaluator or cache')
        expected_hashes = {name:digest(raw) for name,raw in parts.items() if name != 'summary.json'}
        require(summary['artifacts'] == expected_hashes, 'Evaluation artifact hashes differ')
        query_batch = json.loads(parts['query-batch.json'])
        require(query_batch == intent['batch'], 'Evaluator used different test hands')
        conditional = json.loads(parts['conditional-batch.json'])
        require(conditional.get('format') == 3
                and conditional.get('terminal_estimator') == 'conditional-preflop-allin-v1'
                and conditional.get('allin_cache_sha256') == self.plan['cache_sha256']
                and all(conditional.get(k) == v for k,v in query_batch.items() if k != 'format'),
                'Conditional labels changed the visible batch')
        queries = json.loads(parts['queries.json'])
        profiles = json.loads(parts['profiles.json'])
        require(queries['context_source'] == self.source and profiles['context_source'] == self.source
                and queries['batch_source'] == parts['query-batch.json'].decode()
                and profiles['batch_source'] == parts['conditional-batch.json'].decode(), 'Native input identity differs')
        require([row['name'] for row in profiles['profiles']] == list(PROFILE_NAMES), 'Crossed policy order differs')
        native = json.loads(parts['native.json'])
        require(native['format'] == 2 and native['terminal_estimator'] == 'conditional-preflop-allin-v1'
                and native['postflop_outcomes'] == 'sampled-board'
                and [p['name'] for p in native['profiles']] == list(PROFILE_NAMES), 'Unexpected native result protocol')
        for name in ('maximum_forward_cashflow_error', 'maximum_conservation_error'):
            require(0 <= native[name] < 1e-10 and summary[name] == native[name], 'Native payoff identity failed')
        require(all(len(row['deals']) == BATCH for row in native['profiles']), 'Incomplete native profile')
        values = np.asarray(summary['values'], dtype=np.float64)
        actual = np.asarray([[row['values'] for row in p['deals']] for p in native['profiles']], dtype=np.float64)
        require(values.shape == (BATCH,2,4,2) and actual.shape == (8,BATCH,2)
                and np.array_equal(values, actual.transpose(1,0,2).reshape(BATCH,2,4,2)), 'Native values and summary differ')
        comparison = CompletePolicyComparison(stack=self.plan['depth'], dead_money=.5, deals=DEALS,
                                              alpha=self.plan['alpha_per_context'])
        comparison.add(values)  # Validate finite physical bounds, with no interim look.
        residuals = json.loads(parts['residuals.json'])
        require(residuals['purpose'] == 'eight-paired-complete-policy-gains'
                and residuals['bounds_best_response_above'] is False
                and np.array_equal(np.asarray(residuals['values']), differences(values)), 'Paired gain artifact differs')
        return summary

    def prefix(self, *, verify_archives=False):
        self._owned()
        files = []
        for path in self.root.glob('commit-*.json'):
            match = COMMIT.fullmatch(path.name)
            require(match is not None, 'Unexpected committed record name')
            raw = read_bounded(path, MAX_RECORD)
            require(digest(raw) == match[2], 'Committed record identity changed')
            files.append((int(match[1]), match[2], json.loads(raw)))
        files.sort(key=lambda row:row[0])
        require([row[0] for row in files] == list(range(BATCH, BATCH*(len(files)+1), BATCH))
                and len(files)*BATCH <= DEALS, 'Non-prefix or conflicting completed batches')
        sampler = PhysicalDeals(self.source, mode='full_deck', seed=self.plan['seed'])
        comparison = CompletePolicyComparison(stack=self.plan['depth'], dead_money=.5, deals=DEALS,
                                              alpha=self.plan['alpha_per_context'])
        previous = None
        chunks = []
        for count, identity, record in files:
            self.guard()
            start = count-BATCH
            require(record['format'] == 1 and record['journal_owner_sha256'] == self.owner
                    and record['completed_deals'] == count and record['previous_commit_sha256'] == previous,
                    'Changed completion lineage')
            intent, intent_sha = self._intent(start, sampler)
            require(record['intent_sha256'] == intent_sha and record['sampler_after'] == sampler.checkpoint(),
                    'Committed intent or chance continuation changed')
            parts = self._proof(f'test-{start:06d}', record['manifest_sha256'], record['summary_sha256'], full=verify_archives)
            values = np.asarray(record['values'], dtype=np.float64)
            require(values.shape == (BATCH,2,4,2), 'Wrong committed value shape')
            comparison.add(values)
            if parts is not None:
                summary = self._evidence(parts, intent)
                require(record['values'] == summary['values'], 'Committed values differ from authentic native evidence')
            chunks.append(values)
            previous = identity
        count = len(files)*BATCH
        # A pending batch may only be the next prefix. Extra future intents or
        # claims indicate an attempted skip, not evidence to silently ignore.
        allowed = set()
        for start in range(0, min(count+BATCH, DEALS), BATCH):
            name, _, _ = self._paths(start)
            allowed.update((name+'.json', name+'.claim.json'))
        require(all(p.name in allowed or (p.name.startswith('.') and p.name.endswith('.pending'))
                    for p in (self.root/'intents').iterdir()), 'Unexpected future or unknown test intent')
        return dict(completed_deals=count, sampler=sampler, comparison=comparison,
                    previous_commit_sha256=previous,
                    values=np.concatenate(chunks) if chunks else np.empty((0,2,4,2)))

    def begin(self):
        """Call once per new batch; an existing claim always refuses new sampling."""
        state = self.prefix()
        start = state['completed_deals']
        name, claim, intent_path = self._paths(start)
        require(not claim.exists() and not intent_path.exists(), 'Started batch must be recovered, never sampled/evaluated again')
        durable(claim, encoded(dict(journal_owner_sha256=self.owner, start=start)))
        before = state['sampler'].checkpoint()
        drawn = state['sampler'].sample(BATCH)
        batch = self._batch(start, drawn['deals'])
        intent = dict(format=1, journal_owner_sha256=self.owner, start=start,
                      sampler_before=before, sampler_after=state['sampler'].checkpoint(), batch=batch)
        publish_new(intent_path, intent, self.guard)
        folder = self.archive.begin(name)
        return batch, folder

    def recover_next(self, *, retire=False, on_stage=lambda stage:None):
        """Publish already completed evidence, without invoking any scientific work.

        Receipt-backed archives recover even after raw-copy retirement. An
        interrupted archive with no receipt is preserved for explicit analysis.
        """
        state = self.prefix()
        start = state['completed_deals']
        if start == DEALS:
            return None
        name, claim, intent_path = self._paths(start)
        if not claim.exists() and not intent_path.exists():
            return None
        require(claim.exists() and intent_path.exists(), 'Interrupted sampling; preserve partial attempt, no automatic retry')
        intent, intent_sha = self._intent(start, state['sampler'])
        source, packed, manifest_path, archive_claim, receipt_path = self.archive._paths(name)
        require(archive_claim.exists(), 'Started intent has no completed evaluation; no automatic retry')
        if receipt_path.exists():
            receipt = read_json(receipt_path, 4096)
            manifest_raw = read_bounded(manifest_path, MAX_HEADER)
            manifest = json.loads(manifest_raw)
            summary_sha = next(row['raw_sha256'] for row in manifest['members'] if row['name'] == 'summary.json')
            parts = self._proof(name, receipt['manifest_sha256'], summary_sha, full=True)
            identity = digest(manifest_raw)
        else:
            require(not packed.exists() and not manifest_path.exists(),
                    'Interrupted archive without durable receipt; preserve evidence, no automatic republish')
            require(source.is_dir() and {p.name for p in source.iterdir()} == ARTIFACTS,
                    'Incomplete scientific batch; preserve evidence, no automatic retry')
            parts = {n:read_bounded(source/n, MAX_MEMBER) for n in ARTIFACTS}
            self._evidence(parts, intent)
            identity = self.archive.publish(name)
        summary = self._evidence(parts, intent)
        record = dict(format=1, journal_owner_sha256=self.owner, completed_deals=start+BATCH,
            previous_commit_sha256=state['previous_commit_sha256'], intent_sha256=intent_sha,
            sampler_after=state['sampler'].checkpoint(), manifest_sha256=identity,
            summary_sha256=digest(parts['summary.json']), values=summary['values'])
        on_stage('before-commit')
        raw = encoded(record)
        destination = self.root/f'commit-{start+BATCH:06d}-{digest(raw)}.json'
        publish_new(destination, record, self.guard)
        on_stage('committed')
        if retire:
            self.archive.release(name)
        return dict(file=destination.name, sha256=digest(raw), completed_deals=start+BATCH)
