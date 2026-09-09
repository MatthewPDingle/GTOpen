"""Stage postflop evidence into a copied library; dry-run unless --out is given.

No APIs, process control, preflop edits or in-place writes. The running primary
library is explicitly forbidden as an output while reports are being generated.
"""
import argparse
import copy
import hashlib
import json
import math
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIVE_LIBRARY = Path('T:/Dev/GTOpen/cache/archetypes.json')
CORPUS_SHA = '6cdd3b7e522253cfdbde55d3e4189b92f7bae63bbf61c0593e02d7feb4f4f197'
BASE_POSTFLOP = dict(cbet=[62.73, 55.23, 50.95], fold_to_bet=[44.69, 45.7, 53.86],
                    raise_bet=9.14, donk=25.25, bet_size='min')
SOURCE = 'Ignition NL10 regular; heads-up postflop contextual evidence v1; retrospective, board/hand composition inferred'


def same_path(a, b):
    a, b = Path(a), Path(b)
    return (os.path.normcase(str(a.resolve())) == os.path.normcase(str(b.resolve()))
            or (a.exists() and b.exists() and a.samefile(b)))


def wrapper(evidence):
    if (evidence.get('schema'), evidence.get('site'), evidence.get('stake')) != (1, 'Ignition', 'NL10 regular'):
        raise ValueError('Evidence is not the expected Ignition NL10 regular context schema')
    if evidence.get('source_content_sha256') != CORPUS_SHA or evidence.get('source_files') != 574 or evidence.get('audit', {}).get('accepted') != 34466:
        raise ValueError('Evidence corpus does not match the validated library source')
    cells = evidence.get('contextual_bets')
    if not isinstance(cells, list) or not cells:
        raise ValueError('Evidence has no contextual cells')
    seen = set()
    for cell in cells:
        if not isinstance(cell, dict) or set(cell) != {'street', 'kind', 'pot_type', 'opportunities', 'bets'}:
            raise ValueError('Invalid contextual cell fields')
        street, kind = cell['street'], cell['kind']
        if type(street) is not int or street not in (0, 1, 2) or kind not in ('donk', 'stab', 'lead', 'probe'):
            raise ValueError('Invalid street or betting context')
        if (kind == 'donk' and street != 0) or (kind in ('lead', 'probe') and street == 0):
            raise ValueError('Betting context is impossible on that street')
        if cell['pot_type'] not in ('limped', 'single_raised', 'three_bet_plus'):
            raise ValueError('Invalid pot type')
        n, b = cell['opportunities'], cell['bets']
        if type(n) is not int or type(b) is not int or not 0 <= b <= n or n <= 0:
            raise ValueError('Invalid opportunity or bet count')
        key = (street, kind, cell['pot_type'])
        if key in seen:
            raise ValueError('Duplicate contextual cell')
        seen.add(key)
    return dict(version=1, source=SOURCE, cells=copy.deepcopy(cells))


def source_matches(model):
    source = model.get('source') or {}
    dataset = (model.get('stats') or {}).get('dataset') or {}
    return (source.get('site') == 'Ignition' and source.get('stakes') == 'NL10 regular'
            and source.get('type') == 'anonymous_pool' and source.get('unique_hands') == 34466
            and source.get('sessions') == 555 and source.get('date_from') == '2025-08-20'
            and source.get('date_to') == '2025-12-02' and dataset.get('site') == 'Ignition NL10 regular')


def equal_rate(value, baseline):
    if isinstance(baseline, list):
        return isinstance(value, list) and len(value) == len(baseline) and all(equal_rate(a, b) for a, b in zip(value, baseline))
    if isinstance(baseline, (int, float)):
        # Permit ordinary f32 serialization roundoff; never accept a 0.01 edit.
        return type(value) in (int, float) and math.isfinite(value) and abs(value-baseline) <= .00001
    return value == baseline


def migrate(library, evidence):
    if not isinstance(library, list) or any(not isinstance(m, dict) for m in library):
        raise ValueError('Library must be an array of model objects')
    contextual = wrapper(evidence)
    output = copy.deepcopy(library)
    summary = dict(updated=[], unchanged=[], skipped=[])
    for index, (old, new) in enumerate(zip(library, output)):
        label = dict(index=index, name=old.get('name', '(unnamed)'))
        if not source_matches(old):
            summary['skipped'].append(dict(**label, reason='Source provenance does not match the validated anonymous NL10 regular pool'))
            continue
        postflop = old.get('postflop') or {}
        if any(not equal_rate(postflop.get(key), value) for key, value in BASE_POSTFLOP.items()):
            summary['skipped'].append(dict(**label, reason='Postflop fields were changed or are missing; preserve custom model'))
            continue
        existing = postflop.get('contextual_betting')
        if existing == contextual:
            summary['unchanged'].append(label)
        elif existing is not None:
            summary['skipped'].append(dict(**label, reason='Different contextual evidence already exists; preserve custom model'))
        else:
            new['postflop']['contextual_betting'] = copy.deepcopy(contextual)
            summary['updated'].append(label)
    # Enforce the precise mutation contract, including unknown fields and IDs.
    restored = copy.deepcopy(output)
    for label in summary['updated']:
        original = library[label['index']]['postflop']
        if 'contextual_betting' in original:
            restored[label['index']]['postflop']['contextual_betting'] = copy.deepcopy(original['contextual_betting'])
        else:
            restored[label['index']]['postflop'].pop('contextual_betting')
    if restored != library:
        raise AssertionError('Migration modified fields outside contextual_betting')
    return output, summary


def run(library_path, evidence_path, out=None, dry_run=False):
    library_path, evidence_path = Path(library_path), Path(evidence_path)
    if out is not None and (same_path(out, library_path) or same_path(out, LIVE_LIBRARY) or same_path(out, evidence_path)):
        raise ValueError('Output must differ from input, evidence, and the running primary library; in-place writes are forbidden')
    raw = library_path.read_bytes()
    evidence_raw = evidence_path.read_bytes()
    upgraded, summary = migrate(json.loads(raw), json.loads(evidence_raw))
    summary.update(input_sha256=hashlib.sha256(raw).hexdigest(), evidence_sha256=hashlib.sha256(evidence_raw).hexdigest(),
                   dry_run=out is None or dry_run, written_to=None)
    if out is not None and not dry_run:
        destination = Path(out)
        destination.parent.mkdir(parents=True, exist_ok=True)
        # write_text uses platform newline translation on Windows. Preserve
        # the source convention and trailing newline bytes explicitly so a
        # small migration does not rewrite every existing line in the library.
        newline = '\r\n' if b'\r\n' in raw else '\n'
        trailing = raw[len(raw.rstrip(b'\r\n')):]
        encoded = json.dumps(upgraded, ensure_ascii=False, indent=2, allow_nan=False).replace('\n', newline).encode('utf-8')
        if raw.startswith(b'\xef\xbb\xbf'):
            encoded = b'\xef\xbb\xbf'+encoded
        destination.write_bytes(encoded+trailing)
        summary['written_to'] = str(destination.resolve())
        summary['output_sha256'] = hashlib.sha256(destination.read_bytes()).hexdigest()
    if library_path.read_bytes() != raw:
        raise RuntimeError('Input library changed during migration; staged output must be reviewed again')
    print(json.dumps(summary, indent=2, ensure_ascii=True))
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--library', default=str(LIVE_LIBRARY))
    parser.add_argument('--evidence', default=str(ROOT/'research/ignition-postflop-contexts/evidence.json'))
    parser.add_argument('--out', help='Explicit destination for a copied library; omitted means dry-run')
    parser.add_argument('--dry-run', action='store_true', help='Preview even when --out was supplied')
    args = parser.parse_args()
    run(args.library, args.evidence, args.out, args.dry_run)
