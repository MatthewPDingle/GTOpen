"""Two-phase retention at existing joined-context and diagnostic boundaries.

This changes storage only. Original collection/worker/native documents are
unchanged. The complete cycle receipt explicitly resolves archived .bin captures
and resident JSON/NPZ without rerunning native work or changing learning state.
The full scientific study still requires separate resource admission.
"""
import hashlib
import json
from pathlib import Path

from sealed_cycle_references_v2 import SealedReferenceSet, original_key
from sealed_cycle_archive_v3 import FRAME, ROW, MAGIC

METHOD = 'post-joined-context-and-post-diagnostic-cycle-retention-v1'
MAX_PACK_BYTES = 2_000_000_000


def digest(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def read_checked(reference, folder, driver, purpose):
    path = Path(reference['path']).resolve()
    if not path.is_relative_to(folder):
        raise ValueError('Reference escapes this completed cycle')
    driver.charge_integrity(path.stat().st_size, purpose)
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != reference['sha256']:
        raise ValueError('Original resident document changed')
    return json.loads(raw)


class CycleRetention:
    def __init__(self, folder, context_order, *, io, io_config, guard, save):
        self.folder = Path(folder).resolve()
        self.keys = tuple(context_order)
        if not self.keys or len(set(self.keys)) != len(self.keys):
            raise ValueError('Exact unique context order required')
        self.io, self.cfg, self.guard, self.save = io, io_config, guard, save
        self.driver = io._driver(io_config)
        self.root = Path(io_config['store_root']).resolve()
        if not self.folder.is_relative_to(self.root) or self.folder == self.root:
            raise ValueError('Cycle belongs to its current owning store')
        self.base = self.root / 'archives' / self.folder.relative_to(self.root)
        self.physical, self.board, self.collections = {}, {}, {}
        self.finished = False

    def _archive(self, key, phase, include_board):
        context = self.folder / key
        with self.driver._transaction() as c:
            rows = list(c.execute('SELECT closed.path,closed.info,closed.kind FROM closed '
                'LEFT JOIN retirements ON closed.path=retirements.path WHERE retirements.path IS NULL'))
        sizes = []
        for name, info, kind in rows:
            path = self.root / name
            if (kind == 'native-aggregate' and path.is_relative_to(context)
                    and path.suffix == '.bin'
                    and (include_board or not path.is_relative_to(context / 'board-targets'))):
                sizes.append(json.loads(info)['logical'])
        if not sizes:
            raise ValueError('Completed context has no eligible closed captures')
        # Each frame is stored verbatim if compression is larger. This bound
        # uses immutable logical lengths, not an estimated compression ratio.
        upper = len(MAGIC) + sum(n + ((n + FRAME - 1) // FRAME) * ROW.size for n in sizes)
        return self.io.archive_context(context, self.base / key / phase,
            max_pack_bytes=min(MAX_PACK_BYTES, upper), activity_guard=self.guard,
            io_config=self.cfg, include_board_captures=include_board)

    def context_complete(self, key):
        if self.finished or key not in self.keys or key in self.physical:
            raise ValueError('Unknown, repeated or late context completion')
        if key != self.keys[len(self.physical)]:
            raise ValueError('Original context order changed')
        path = self.folder / key / 'collection.json'
        self.driver.charge_integrity(path.stat().st_size, 'context-complete-collection-read')
        raw = path.read_bytes()
        collection = json.loads(raw)
        if collection['context_sha256'] != key:
            raise ValueError('Completed collection context changed')
        reference = dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest())
        receipt = self._archive(key, 'physical', False)
        self.save(self.folder / 'native-retention-contexts' / (key + '.json'),
                  dict(collection=reference, retention=receipt))
        self.collections[key], self.physical[key] = reference, receipt
        return receipt

    def finish(self, metrics, *, diagnostic_contexts, boundary):
        if self.finished or tuple(self.physical) != self.keys:
            raise ValueError('All original contexts must complete exactly once')
        if type(boundary) is not bool or tuple(diagnostic_contexts) != (self.keys if boundary else ()):
            raise ValueError('Board retirement must follow all required boundary diagnostics')
        collections = metrics['collections']
        if tuple(c['context_sha256'] for c in collections) != self.keys:
            raise ValueError('Full cycle collection order or scope changed')
        for key, collection in zip(self.keys, collections):
            if read_checked(self.collections[key], self.folder, self.driver,
                            'retention-collection-read') != collection:
                raise ValueError('Full metrics differs from completed collection')
            self.board[key] = self._archive(key, 'board', True)
        bindings = [dict(root=v['archive']['root'], manifest_sha256=v['archive']['manifest_sha256'])
                    for phase in (self.physical, self.board) for v in phase.values()]
        readers = SealedReferenceSet(bindings, guard=self.guard, charge=self.driver.charge_integrity)
        invocations, rows, seen, outputs_seen = [], [], set(), set()
        for collection in collections:
            invocations.extend(v['result']['native_invocation'] for v in collection['board_results'])
            invocations.extend(v['invocation'] for v in collection['query_invocations'])
            for batch in collection['subbatches']:
                worker = read_checked(batch['result'], self.folder, self.driver, 'retention-worker-read')
                invocations.extend(v['result'] for v in worker['native_invocations'])
        for invocation in invocations:
            self.guard()
            reference = dict(path=invocation['receipt_path'], sha256=invocation['receipt_sha256'])
            key = original_key(reference['path'])
            if key in seen:
                raise ValueError('Duplicate native invocation in completed cycle')
            seen.add(key)
            receipt = read_checked(reference, self.folder, self.driver, 'retention-native-receipt-read')
            if receipt != invocation['receipt'] or receipt['outcome'] != 'success':
                raise ValueError('Original successful invocation receipt changed')
            dispositions = []
            for output in (receipt['stdout'], receipt['stderr'], *receipt['direct_output_artifacts']):
                path = Path(output['path']).resolve()
                key = original_key(path)
                if not path.is_relative_to(self.folder) or key in outputs_seen:
                    raise ValueError('Duplicate or escaped original output')
                outputs_seen.add(key)
                if readers.contains(output):
                    if path.exists() or path.suffix != '.bin':
                        raise ValueError('Archived captures must be archive-only .bin files')
                    readers.verify(output)
                    disposition = dict(storage='sealed-streaming-archive', **readers.location(output))
                else:
                    if path.suffix == '.bin':
                        raise ValueError('Native capture missing explicit archive location')
                    if path.stat().st_size != output['bytes']:
                        raise ValueError('Original resident output size changed')
                    self.driver.charge_integrity(output['bytes'], 'retention-resident-output-read')
                    if digest(path) != output['sha256']:
                        raise ValueError('Original resident output hash changed')
                    disposition = dict(storage='resident-original', original_reference=dict(output))
                dispositions.append(disposition)
            rows.append(dict(native_receipt=reference, outputs=dispositions,
                             original_pipeline_verification_preserved=True))
        if set(readers.by_original) != {original_key(v['original_reference']['path'])
                for row in rows for v in row['outputs'] if v['storage']=='sealed-streaming-archive'}:
            raise ValueError('Every archived capture needs exactly one original invocation')
        after = self.io.quiescent(self.cfg)
        result = dict(format=1, method=METHOD, invocation_count=len(rows), invocations=rows,
            context_order=list(self.keys), physical_phase=self.physical, board_phase=self.board,
            boundary=boundary, completed_diagnostic_contexts=list(diagnostic_contexts), after=after,
            original_raw_references_unchanged=True, source_draws_or_fits_added=False,
            original_native_verification_preserved=True,
            future_capacity_or_ratio_qualified=False, full_study_admitted=False)
        self.finished = True
        return result
