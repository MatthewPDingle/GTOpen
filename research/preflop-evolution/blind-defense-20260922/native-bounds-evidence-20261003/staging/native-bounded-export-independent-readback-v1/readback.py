"""Independent read-only audit of completed evidence. Never imports runners.

No compiler, control, native poker executable, model or calculation is invoked.
Only this directory receives a newly-created result. Inputs are read and hashed.
"""
import ctypes
import hashlib
import json
import math
import os
from pathlib import Path
import stat
import time
import traceback

HERE = Path(__file__).resolve().parent
STAGE = HERE.parent
STORE = Path(r'S:\GTOpen-research\native-bounded-export-controls-v1')
BUILD = Path(r'S:\GTOpen-research\native-bounded-export-build-v1')
REPO = Path(r'T:\Dev\GTOpen')
FAILURES = []
VERIFIED = {}
CHECKS = 0
CHILDREN = []
FINGERPRINTS = []


def require(condition, message, **detail):
    global CHECKS
    CHECKS += 1
    if not condition:
        FAILURES.append(dict(message=message, **detail))


def digest(path):
    p = Path(path)
    before = p.stat()
    h = hashlib.sha256()
    with p.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    after = p.stat()
    require((before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns),
            'File changed during hash', path=str(p))
    return h.hexdigest()


def pin(path, expected=None, size=None):
    p = Path(path)
    key = str(p.resolve())
    if key not in VERIFIED:
        value = dict(path=key, bytes=p.stat().st_size, sha256=digest(p))
        VERIFIED[key] = value
    value = VERIFIED[key]
    if expected is not None:
        require(value['sha256'] == expected, 'SHA256 mismatch', path=key,
                expected=expected, actual=value['sha256'])
    if size is not None:
        require(value['bytes'] == size, 'File size mismatch', path=key,
                expected=size, actual=value['bytes'])
    return value


def load(path):
    pin(path)
    return json.loads(Path(path).read_bytes())


def identity_map(values):
    for path, expected in values.items():
        pin(path, expected)


def artifact(record):
    p = Path(record['path'])
    exists = p.exists()
    require(exists == record.get('exists', True), 'Artifact existence mismatch', path=str(p))
    if exists:
        require(p.is_file() and not p.is_symlink(), 'Artifact not an ordinary file', path=str(p))
        pin(p, record['sha256'], record['bytes'])
    else:
        require(record.get('bytes') is None and record.get('sha256') is None,
                'Missing artifact has nonnull contents', path=str(p))


def process(record, label):
    p, c = record['process'], record['caller']
    require(p is not None and p['pid'] > 0 and c['pid'] > 0, 'Missing process identity', label=label)
    require(p['parent_pid'] == c['pid'] and p['observed_argv'] == record['argv'],
            'Process parent/argv mismatch', label=label)
    require(c['creation_time'] <= record['started_unix'] <= p['creation_time'] <= record['terminal_unix'],
            'Invalid process chronology', label=label)
    require(record['terminal_unix'] - record['started_unix'] <= record.get('timeout_seconds', 86400),
            'Recorded deadline exceeded', label=label)
    return p


def invocation(item, label):
    wrapper = item.get('result', item)
    path = Path(wrapper['receipt_path'])
    pin(path, wrapper['receipt_sha256'])
    receipt = load(path)
    require(receipt == wrapper['receipt'], 'Embedded receipt differs from file', label=label)
    require(item['passed'] is True, 'Case did not pass', label=label)
    require(receipt['format'] == 2 and receipt['method'] == 'native-process-bound-export-v2',
            'Unexpected receipt schema', label=label)
    require(path == Path(receipt['folder']) / (receipt['label'] + '-receipt.json'),
            'Receipt path does not match declared folder', label=label)
    require(path.is_relative_to(STORE), 'Receipt outside qualification store', label=label)
    p = process(receipt, label)
    require(receipt['timeout_seconds'] == 120, 'Unexpected child timeout', label=label)
    identity_map(receipt['expected_identities'])
    require(receipt['executable'] == receipt['argv'][0] and
            receipt['executable'] in receipt['expected_identities'], 'Unpinned executable', label=label)
    require(len(receipt['direct_outputs']) == len(receipt['direct_output_artifacts']),
            'Direct-output witness count mismatch', label=label)
    for channel in ('stdout', 'stderr'):
        record = receipt[channel]
        require(Path(record['path']) == Path(receipt['folder']) / (receipt['label'] + '-' + channel + '.bin'),
                'Channel escaped invocation directory', label=label, channel=channel)
        artifact(record)
        if 'result' in item:
            require(wrapper[channel + '_path'] == record['path'] and wrapper[channel + '_sha256'] == record['sha256'],
                    'Wrapper channel differs from receipt', label=label, channel=channel)
    for spec, value in zip(receipt['direct_outputs'], receipt['direct_output_artifacts']):
        index = spec['argument_index']
        require(spec['path'] == value['path'] == receipt['argv'][index] and value['argument_index'] == index,
                'Direct output is not actual argv target', label=label)
        require(Path(spec['path']).is_relative_to(Path(receipt['folder'])) and
                spec['path'] not in receipt['expected_identities'], 'Unsafe direct output', label=label)
        artifact(value)
    if receipt['stdin']:
        artifact(receipt['stdin'])
        require(receipt['stdin']['path'] in receipt['expected_identities'], 'Unpinned stdin', label=label)
    successful = not item.get('expected_refusal', False)
    if successful:
        require(receipt['outcome'] == 'success' and receipt['returncode'] == 0,
                'Successful case lacks successful process', label=label)
    else:
        require(receipt['outcome'] == 'failed' and receipt['returncode'] in (1, 101),
                'Refusal has unexpected process result', label=label)
        message = b'Research exporter panicked\n' if receipt['returncode'] == 101 else b'Research exporter failed\n'
        require(Path(receipt['stdout']['path']).read_bytes() == b'' and
                Path(receipt['stderr']['path']).read_bytes() == message,
                'Refusal wrote payload or nonfixed diagnostic', label=label)
        require(not any(v['exists'] for v in receipt['direct_output_artifacts']),
                'Refusal created direct payload', label=label)
    total = sum(v['bytes'] or 0 for v in [receipt['stdout'], receipt['stderr'], *receipt['direct_output_artifacts']])
    require(total <= receipt['max_output_bytes'], 'Terminal byte bound exceeded', label=label)
    CHILDREN.append(dict(label=label, process=p, caller=receipt['caller'],
                         receipt_path=str(path), receipt_sha256=wrapper['receipt_sha256'],
                         outcome=receipt['outcome'], returncode=receipt['returncode'],
                         terminal_bytes=total, limit=receipt['max_output_bytes'],
                         started_unix=receipt['started_unix'], terminal_unix=receipt['terminal_unix']))
    return receipt


def original_reference(reference):
    for key in ('original_executable', 'original_receipt', 'expected_payload', 'expected_stdout', 'expected_stderr'):
        artifact(reference[key])
    for value in reference['request_inputs']:
        artifact(value)
    if reference['stdin']:
        artifact(reference['stdin'])
    r = load(reference['original_receipt']['path'])
    require(r['argv'] == reference['original_argv'] and r['process'] == reference['process'] and
            r['caller'] == reference['caller'], 'Original process provenance differs from review', group=reference['group'])
    require(r['returncode'] == 0 and r['outcome'] == 'success', 'Original process did not succeed')
    require(r['stdout'] == reference['expected_stdout'] and r['stderr'] == reference['expected_stderr'] and
            r['stdin'] == reference['stdin'], 'Original channels differ from review', group=reference['group'])
    process(r, 'original-' + reference['group'])
    identity_map(r['expected_identities'])


def build_audit(build, registration):
    require(build['passed'] is True and build['originals_preserved'] is True, 'Build did not pass')
    require(build['source_identities'] == registration['source_identities'], 'Build source pins changed')
    identity_map(build['source_identities'])
    pin(BUILD / 'inventory.json', registration['inventory_sha256'])
    require(len(build['builds']) == 2, 'Unexpected build count')
    names = {'hu_fixed_board_tree_bounded_v2': 'hu_fixed_board_tree_v1',
             'hu_sampled_allin_history_bridge_bounded_v2': 'hu_sampled_allin_history_bridge_v1',
             'hu_sampled_action_trace_bounded_v3': 'hu_sampled_action_trace_v2',
             'hu_river_two_stage_stream_bounded_v2': 'hu_river_two_stage_stream_v1'}
    for item, registered in zip(build['builds'], registration['builds']):
        require(item['passed'] is True and item['returncode'] == 0, 'Failed Cargo build')
        process(item, 'cargo-' + registered['name'])
        argv = item['argv']
        require('--offline' in argv and '--locked' in argv and '--release' in argv and
                '--message-format=json' in argv and argv[argv.index('--jobs') + 1] == '8',
                'Missing registered Cargo constraints')
        target = BUILD / registered['name'] / 'target'
        require(argv[argv.index('--target-dir') + 1] == str(target), 'Cargo target isolation mismatch')
        require(item['features'] == registered['features'], 'Cargo requested features changed')
        expected_features = [] if not registered['features'] else ['continuation-transfer-research', 'gpu', 'preflop-research']
        identity_map(item['log_identities'])
        messages = [json.loads(line) for line in (BUILD / registered['name'] / 'cargo-stdout.jsonl').read_text().splitlines()]
        require(messages[-1] == dict(reason='build-finished', success=True), 'Cargo log lacks successful terminal')
        examples = [m for m in messages if m.get('reason') == 'compiler-artifact' and m['target']['kind'] == ['example']]
        require({m['target']['name'] for m in examples} == set(registered['examples']) == set(item['artifacts']),
                'Cargo example set mismatch')
        for message in examples:
            name = message['target']['name']
            artifact(item['artifacts'][name])
            require(message['features'] == expected_features and not message['fresh'], 'Cargo role features/freshness mismatch', name=name)
            require(message['executable'] == item['artifacts'][name]['path'] and
                    message['target']['src_path'] == str(REPO / 'crates/solver/examples' / (name + '.rs')),
                    'Cargo executable/source identity mismatch', name=name)
            candidates = list(target.glob('release/.fingerprint/solver-*/example-' + name + '.json'))
            original = list((REPO / 'target/release/.fingerprint').glob('solver-*/example-' + names[name] + '.json'))
            require(len(candidates) == 1 and len(original) == 1, 'Ambiguous role fingerprint', name=name)
            current, prior = load(candidates[0]), load(original[0])
            require(json.loads(current['features']) == json.loads(prior['features']) == expected_features,
                    'Old/new Cargo feature graph differs', name=name)
            require(current['rustflags'] == prior['rustflags'] == [], 'Unexpected Rust flags', name=name)
            require(current['profile'] == prior['profile'], 'Old/new Cargo profile differs', name=name)
            serde = [m for m in messages if m.get('reason') == 'compiler-artifact' and m['target']['name'] == 'serde_json']
            require(len(serde) == 1, 'Ambiguous serde_json artifact')
            require(('float_roundtrip' in serde[0]['features']) == bool(expected_features),
                    'Role serializer feature mismatch', name=name)
            FINGERPRINTS.append(dict(name=name, feature_graph=expected_features,
                                     new=pin(candidates[0]), original=pin(original[0]),
                                     serde_json_features=serde[0]['features'], profile=current['profile']))


def run():
    result = load(STORE / 'result.json')
    registration = load(STORE / 'registration.json')
    build = load(BUILD / 'result.json')
    build_registration = load(BUILD / 'registration.json')
    review = load(STAGE / 'native-bounded-export-review-v1/representative-controls.json')
    require(result['passed'] is True and result['accuracy_proven'] is False and result['originals_preserved'] is True,
            'Unexpected terminal qualification claims')
    require(result['native_control_invocations'] == 39 and len(result['primary']) == 7 and
            len(result['helper']) == 13 and len(result['river_input']) == 5, 'Unexpected control count')
    pin(STORE / 'registration.json', result['registered_budget_sha256'])
    require(result['source_identities'] == registration['source_identities'], 'Control source pins changed')
    identity_map(result['source_identities'])
    require(registration['references'] == review['primary'], 'Registration differs from representative path map')
    build_audit(build, build_registration)
    original_preserved = []
    for reference in review['primary'] + review['optional_same_batch_transport']:
        original_reference(reference)
        original_preserved.append(dict(group=reference['group'], receipt=reference['original_receipt']))
    primary = []
    for index, (case, reference) in enumerate(zip(result['primary'], review['primary'])):
        require(case['reference'] == reference and case['passed'] is True, 'Primary fixture differs from reference', index=index)
        role = 'bridge' if reference['group'].startswith('bridge') else 'river' if reference['group'].startswith('river') else reference['group']
        direct_index = 5 if role == 'bridge' else 4 if role == 'trace' else None
        threshold = reference['expected_stdout']['bytes'] + reference['expected_stderr']['bytes'] + 256
        if direct_index:
            threshold += reference['expected_payload']['bytes']
        require(case['threshold'] == threshold and case['role'] == role, 'Primary threshold or role mismatch', index=index)
        require([x['label'] for x in case['invocations']] == ['inclusive', 'one-extra', 'one-short'],
                'Primary boundary case list mismatch', index=index)
        for value, increment in zip(case['invocations'], [0, 1, -1]):
            label = f'{index:02d}-{case["group"]}/{value["label"]}'
            r = invocation(value, label)
            expected = reference['original_argv'].copy()
            expected[0] = registration['binaries'][role]['path']
            if direct_index:
                expected[direct_index] = str(STORE / f'{index:02d}-{case["group"]}' / value['label'] / 'payload.json')
            expected.append('--output-byte-limit=' + str(threshold + increment))
            require(r['argv'] == expected and r['max_output_bytes'] == value['limit'] == threshold + increment,
                    'Actual primary command/limit changed', label=label)
            require(r['stdin'] == reference['stdin'], 'Primary stdin bytes/identity changed', label=label)
            require(len(r['direct_outputs']) == int(direct_index is not None), 'Wrong direct-output declaration', label=label)
            for value_input in reference['request_inputs']:
                require(r['expected_identities'].get(value_input['path']) == value_input['sha256'],
                        'Primary input not pinned', label=label)
            if increment >= 0:
                payload = r['direct_output_artifacts'][0] if direct_index else r['stdout']
                for got, old in [(r['stdout'], reference['expected_stdout']), (r['stderr'], reference['expected_stderr']),
                                 (payload, reference['expected_payload'])]:
                    require((got['bytes'], got['sha256']) == (old['bytes'], old['sha256']),
                            'Primary bytes differ from original', label=label, channel_path=got['path'])
            else:
                require(value.get('expected_refusal') is True, 'T-1 did not record refusal', label=label)
        root = STORE / f'{index:02d}-{case["group"]}' / 'result.json'
        require(load(root) == case, 'Primary local result differs from aggregate', index=index)
        primary.append(dict(index=index, group=case['group'], threshold=threshold,
                            successful_exact_repeats=2, prewrite_zero_payload_refusals=1))
    helper_root = STORE / 'serialization-helper'
    require(load(helper_root / 'result.json')['cases'] == result['helper'], 'Helper local/aggregate mismatch')
    helper_build = load(helper_root / 'build.json')
    require(helper_build['returncode'] == 0 and 'panic=unwind' in helper_build['argv'], 'Helper build is not unwind-qualified')
    pin(helper_root / 'bounded-output-control.exe', helper_build['binary_sha256'])
    pin(STAGE / 'research_bounded_output_control_v1.rs', helper_build['source_sha256'])
    pin(STAGE / 'research_bounded_output_v1.rs', helper_build['helper_sha256'])
    fixture = (helper_root / 'fixture.json').read_bytes()
    expected_helper = ['inclusive', 'one-extra', 'one-short', 'empty', 'large-error', 'large-panic',
                       'invalid-zero', 'above-ceiling', 'invalid-text', 'default-cap', 'stdio-only', 'existing-file', 'existing-directory']
    require([x['label'] for x in result['helper']] == expected_helper, 'Helper case list mismatch')
    for item in result['helper']:
        label = item['label']
        r = invocation(item, 'helper/' + label)
        if not item.get('expected_refusal'):
            if label in ('inclusive', 'one-extra', 'default-cap'):
                require(Path(r['direct_output_artifacts'][0]['path']).read_bytes() == fixture and
                        Path(r['stdout']['path']).read_bytes() == b'out\n' and Path(r['stderr']['path']).read_bytes() == b'note\n',
                        'Raw helper successful bytes changed', label=label)
            if label == 'stdio-only':
                require(Path(r['stdout']['path']).read_bytes() == fixture and Path(r['stderr']['path']).read_bytes() == b'note\n',
                        'Raw helper stdio bytes changed')
            if label == 'empty':
                require(r['direct_output_artifacts'][0]['bytes'] == r['stdout']['bytes'] == r['stderr']['bytes'] == 0,
                        'Empty helper output not empty')
        if label.startswith('existing-'):
            sentinel = helper_root / label / 'sentinel'
            require(item['sentinel_preserved'] is True, 'Collision sentinel was not preserved', label=label)
            require(r['argv'][3] == str(sentinel), 'Collision did not target sentinel', label=label)
            if label == 'existing-file':
                require(sentinel.read_bytes() == b'owned-new-sentinel\n', 'Existing sentinel file changed')
                require(str(sentinel) in r['expected_identities'], 'Existing file sentinel unpinned')
            else:
                require(sentinel.is_dir() and not list(sentinel.iterdir()), 'Existing directory sentinel changed')
    river_root = STORE / 'river-input-limits'
    require(load(river_root / 'result.json')['cases'] == result['river_input'], 'River local/aggregate mismatch')
    expected_river = [('context-at-limit', 16*1024*1024), ('context-over-limit', 16*1024*1024+1),
                      ('request-at-limit', 64*1024), ('request-over-limit', 64*1024+1), ('malformed-request', 1)]
    require([x['label'] for x in result['river_input']] == [x[0] for x in expected_river], 'River input case list mismatch')
    reference = review['primary'][5]
    saved = load(reference['expected_payload']['path'])
    for item, (label, length) in zip(result['river_input'], expected_river):
        r = invocation(item, 'river-input/' + label)
        source = river_root / (label + '.json')
        artifact(dict(path=str(source), bytes=length, sha256=r['expected_identities'][str(source)]))
        if label == 'malformed-request':
            require(source.read_bytes() == b'{', 'Malformed request differs from fixture')
        else:
            old = Path(reference['original_argv'][1] if label.startswith('context') else reference['stdin']['path']).read_bytes()
            require(source.read_bytes() == old + b' ' * (length - len(old)), 'Boundary input changes non-whitespace bytes', label=label)
        if label.endswith('at-limit'):
            payload = load(r['stdout']['path'])
            require(payload['targets'] == saved['targets'] and payload['total_nodes'] == saved['total_nodes'],
                    'Admitted boundary changes target data', label=label)
            require(payload['context_source'] == Path(r['argv'][1]).read_text() and
                    payload['request_source'] == Path(r['stdin']['path']).read_text(),
                    'Boundary input source echo changed', label=label)
            # Stronger readback than the control: normalize only echoed source
            # strings, then compare the entire retained JSON tree (queries too).
            def normalized(value):
                if isinstance(value, dict):
                    return {k: (v.rstrip(' ') if k in ('context_source', 'request_source', 'batch_source') and isinstance(v, str)
                                else normalized(v)) for k, v in value.items()}
                if isinstance(value, list):
                    return [normalized(v) for v in value]
                return value
            require(normalized(payload) == normalized(saved), 'Boundary output differs beyond source whitespace', label=label)
    require(len(CHILDREN) == 39 and len({(x['process']['pid'], x['process']['creation_time']) for x in CHILDREN}) == 39,
            'Not 39 distinct actual child identities')
    receipts = set(STORE.rglob('*-receipt.json'))
    require(receipts == {Path(x['receipt_path']) for x in CHILDREN}, 'Missing or unexpected process receipts')
    events = sorted([(x['process']['creation_time'], 1) for x in CHILDREN] + [(x['terminal_unix'], -1) for x in CHILDREN])
    active = peak = 0
    for _, amount in events:
        active += amount
        peak = max(peak, active)
    require(peak <= registration['maximum_parallel_native_children'] == 6, 'Recorded native concurrency exceeded limit', peak=peak)
    files = [p for p in STORE.rglob('*') if p.is_file() and p != STORE / 'result.json']
    logical = sum(p.stat().st_size for p in files)
    require(logical == result['measurement']['logical_bytes'] and len(files) == result['measurement']['files'],
            'Terminal store logical measurement mismatch', actual_bytes=logical, files=len(files))
    require(logical <= registration['maximum_logical_control_files'] == 1_000_000_000, 'Control storage envelope exceeded')
    # All evidence, including compilation logs and local result files, is pinned
    # in this independent snapshot without overwriting the original manifests.
    for p in STORE.rglob('*'):
        if p.is_file():
            pin(p)
        require(not p.is_symlink() and not (getattr(p.lstat(), 'st_file_attributes', 0) & 0x400),
                'Reparse/symlink in evidence store', path=str(p))
    for value in list(VERIFIED.values()):
        require(digest(value['path']) == value['sha256'], 'Input changed during audit', path=value['path'])
    return dict(primary=primary, original_references_preserved=original_preserved, build_fingerprints=FINGERPRINTS,
                child_receipts=CHILDREN, observed_maximum_overlapping_child_intervals=peak,
                actual_control_files_before_terminal_result=len(files), actual_control_logical_bytes_before_terminal_result=logical)


if __name__ == '__main__':
    destination = HERE / 'result.json'
    if destination.exists():
        raise FileExistsError('Independent audit output is exclusive; never overwrite it')
    began = time.time()
    details = {}
    try:
        details = run()
    except BaseException as error:
        FAILURES.append(dict(message='Unexpected audit exception', error=repr(error), traceback=traceback.format_exc()))
    report = dict(format=1, audit='native-bounded-export-independent-readback-v1', passed=not FAILURES,
                  began_unix=began, terminal_unix=time.time(), checks=CHECKS, failures=FAILURES,
                  scope='Read-only verification of existing byte/resource qualification evidence; no control/native/calculation rerun.',
                  scientific_accuracy_qualified=False, poker_accuracy_proven=False, production_changed=False,
                  no_controls_rerun=True, no_build_rerun=True, no_training=True,
                  evidence_sources=VERIFIED, audit_source_sha256=digest(__file__),
                  limitations=[
                      'Seven retained fixtures establish finite byte parity, not whole-game poker accuracy or untested-mode correctness. Bridge walk and optional same-batch transport were not new control children.',
                      'Output gate acts after complete calculation/serialization buffers are built. These checks do not establish a general RAM or CPU ceiling, and nonriver input reads are not newly bounded.',
                      'After admission an I/O failure may leave bounded partial output. The suite does not inject disk-full, short-write, or abrupt termination failures; only prewrite budget refusals are zero-payload.',
                      'Helper collision controls asserted before/after filesystem identity in the pinned source, but did not retain those identities. This audit independently checks final file bytes and final empty directory, not the unrecorded earlier directory identity.',
                      '39 actual control children excludes two Cargo build parents and the standalone rustc helper compilation. The latter has argv/exit/hash evidence, but no child PID/creation receipt.',
                      'Process observed_argv is a recorded Popen argument vector, not an independent OS command-line query. Windows process creation time is obtained from the owned native process handle.',
                      'Logical store measurement is independently reconstructed. Historical NTFS named allocation and transient free-space/RAM/production guards are recorded assertions; this audit does not replay runtime observations.',
                  ], **details)
    with destination.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(report, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')
    print(json.dumps(dict(passed=report['passed'], checks=CHECKS, verified_files=len(VERIFIED),
                          failures=FAILURES, audit=str(destination)), allow_nan=False))
