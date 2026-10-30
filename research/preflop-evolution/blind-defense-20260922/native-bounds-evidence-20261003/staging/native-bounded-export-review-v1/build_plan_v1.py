"""Prospective read-only plan; never compile, spawn, sample, fit or mutate evidence."""
import hashlib
import itertools
import json
from pathlib import Path
import re
import time

OUT = Path(__file__).resolve().parent
STAGE = OUT.parent
ROOT = Path(r'T:\Dev\GTOpen')
EXAMPLES = ROOT/'crates/solver/examples'
PROFILE = Path(r'S:\GTOpen-research\preflop-expected-native-cycle-profile-v1')
MANIFEST = STAGE/'preflop-expected-native-cycle-independent-readback-v2/retained-files.json'
READBACK = STAGE/'preflop-expected-native-cycle-independent-readback-v2/result.json'
FINGERPRINTS = ROOT/'target/release/.fingerprint'
NAMES = dict(board='hu_fixed_board_tree_v1',bridge='hu_sampled_allin_history_bridge_v1',
    trace='hu_sampled_action_trace_v2',river='hu_river_two_stage_stream_v1')
PINS = {}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def pin(path, expected=None):
    path = Path(path).resolve()
    identity = sha(path)
    if expected is not None:
        assert identity == expected, str(path)
    if str(path) in PINS:
        assert PINS[str(path)] == identity
    PINS[str(path)] = identity
    return dict(path=str(path),sha256=identity,bytes=path.stat().st_size)


def read(path, expected=None):
    pin(path,expected)
    return json.loads(Path(path).read_bytes())


def save(name,value):
    with (OUT/name).open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(value,stream,sort_keys=True,indent=2,allow_nan=False)
        stream.write('\n')


def main():
    began = time.monotonic()
    assert not (OUT/'plan.json').exists()
    manifest = read(MANIFEST,'d1fb931157542df733cdcb7b67bdb4002073266bcfa505a1e4f2d8ff75817b27')
    previous = read(READBACK,'1221219d70f68be560655e3d53d6d7899796f028283d4a8e9dff528f0a47ef09')
    registration = read(PROFILE/'registration.json','22cb43489f0c9be4c4625639cf778ff7ac1b444765e22e376f025a6e21ac9e4a')
    terminal = read(PROFILE/'result.json','7341ac78404cb69dc8f32e42fd0be74cee77564541479cd85bb44acabcd7ff30')
    assert previous['passed'] and previous['native_receipt_count'] == 117
    assert len(manifest) == 809 and sum(v['bytes'] for v in manifest.values()) == 1_278_992_546
    assert set(manifest) == {str(p.relative_to(PROFILE)) for p in PROFILE.rglob('*') if p.is_file()}
    for name,item in manifest.items():
        assert (PROFILE/name).stat().st_size == item['bytes']
        pin(PROFILE/name,item['sha256'])
    assert terminal['passed'] and terminal['scientific_accuracy_qualified'] is False
    sources = [ROOT/'AGENTS.md',ROOT/'Cargo.toml',ROOT/'Cargo.lock',ROOT/'crates/solver/Cargo.toml']
    sources += [EXAMPLES/(name+'.rs') for name in NAMES.values()]
    modules = set()
    for source in sources[4:]:
        modules.update(re.findall(r'#\[path\s*=\s*"([^"]+)"\]',source.read_text(encoding='utf-8')))
        assert registration['config']['source_identities'][str(source)] == sha(source)
    sources += [EXAMPLES/name for name in sorted(modules)]
    sources += [ROOT/'crates/solver/src'/name for name in ('lib.rs','tree.rs','evaluator.rs','cards.rs')]
    snapshots = {}
    for index,source in enumerate(sources):
        ref = pin(source)
        destination = OUT/(f'source-{index:02d}-'+source.name+'.snapshot')
        with destination.open('xb') as stream:
            stream.write(source.read_bytes())
        assert sha(destination) == ref['sha256']
        snapshots[str(source)] = str(destination)
    old_binaries = {role:pin(path,registration['config']['source_identities'][path])
        for role,path in registration['native'].items()}
    compilation = {}
    for role,name in NAMES.items():
        paths = list(FINGERPRINTS.glob('solver-*/example-'+name+'.json'))
        assert len(paths) == 1,(role,paths)
        path = paths[0];document = read(path)
        features = json.loads(document['features'])
        expected = [] if role != 'river' else ['continuation-transfer-research','gpu','preflop-research']
        assert features == expected and document['rustflags'] == []
        dependency = next(v[3] for v in document['deps'] if v[1] == 'serde_json')
        serde = [p for p in FINGERPRINTS.glob('serde_json-*/lib-serde_json')
            if int.from_bytes(bytes.fromhex(p.read_text().strip()),'little') == dependency]
        assert len(serde) == 1
        marker = serde[0];depdocument = read(marker.with_suffix('.json'));pin(marker)
        serde_features = json.loads(depdocument['features'])
        assert ('float_roundtrip' in serde_features) == (role == 'river')
        compilation[role] = dict(example=pin(path),observed_solver_features=features,
            serde_json_fingerprint=pin(marker.with_suffix('.json')),serde_json_marker=pin(marker),
            serde_json_features=serde_features,rustflags=document['rustflags'],
            release_profile=document['profile'],rustc_fingerprint=document['rustc'],
            caveat='Retained Cargo fingerprints match role dependency markers; no cryptographic binary-to-build attestation or fresh compilation is claimed.')
    context = pin(registration['inputs'][next(iter(registration['inputs']))]['context_path'])
    assert json.loads(Path(context['path']).read_bytes())['config']['stack'] == 20
    inventory = []
    for name in sorted(manifest):
        if not name.endswith('-receipt.json'):
            continue
        path = PROFILE/name;receipt = read(path,manifest[name]['sha256'])
        exe = receipt['executable'];role = next(k for k,v in registration['native'].items() if v == exe)
        if role == 'bridge':
            group = 'bridge-'+receipt['argv'][1]
            assert group in ('bridge-queries','bridge-verify')
            payload = Path(receipt['argv'][-1])
        elif role == 'trace':
            group = 'trace';payload = Path(receipt['argv'][-1])
        elif role == 'board':
            group = 'board';payload = Path(receipt['stdout']['path'])
        else:
            request = json.loads(Path(receipt['stdin']['path']).read_bytes())
            group = 'river-'+request['mode'];payload = Path(receipt['stdout']['path'])
            assert group in ('river-history','river-selected')
        assert receipt['outcome'] == 'success' and receipt['returncode'] == 0
        assert receipt['process']['observed_argv'] == receipt['argv']
        assert receipt['process']['parent_pid'] == receipt['caller']['pid']
        assert receipt['caller']['creation_time'] <= receipt['started_unix'] <= receipt['terminal_unix']
        assert str(path) in previous['native_receipts']
        assert previous['native_receipts'][str(path)]['sha256'] == sha(path)
        for input_path,identity in receipt['expected_identities'].items():
            pin(input_path,identity)
        for stream in ('stdout','stderr'):
            pin(receipt[stream]['path'],receipt[stream]['sha256'])
            assert Path(receipt[stream]['path']).stat().st_size == receipt[stream]['bytes']
        inputs = [context]
        if role == 'board':
            request_path = Path(receipt['argv'][2]);request = read(request_path)
            board = request['board']
            legal = [list(hand) for hand in itertools.combinations([c for c in range(52) if c not in board],2)]
            assert len(board) == len(set(board)) == 5 and len(legal) == 1081
            assert request == dict(board=board,hands=[legal,legal])
            inputs.append(pin(request_path))
            domain = dict(board=request['board'],private_hands_per_actor=1081,draw_index=int(request_path.parent.name.split('-')[-1]))
        elif role in ('bridge','trace'):
            batch_path = Path(receipt['argv'][3] if role == 'bridge' else receipt['argv'][2])
            batch = read(batch_path);inputs.append(pin(batch_path))
            assert batch['format'] == 3 and len(batch['deals']) == 13
            policy = None
            if role == 'trace' or group == 'bridge-verify':
                policy_path = Path(receipt['argv'][4] if role == 'bridge' else receipt['argv'][3])
                policy = read(policy_path);inputs.append(pin(policy_path))
                assert policy['context_source'] == Path(context['path']).read_bytes().decode('utf-8')
                assert policy['batch_source'] == batch_path.read_bytes().decode('utf-8')
            domain = dict(batch_folder=payload.parent.name,physical_deals=13,batch_id=batch['batch_id'],
                seed=batch['seed'],frozen_policy_rows=len(policy['policies']) if policy else None)
        else:
            request_path = Path(receipt['stdin']['path']);request = read(request_path);inputs.append(pin(request_path))
            domain = dict(batch_folder=request_path.parents[1].name,request_mode=request['mode'],
                targets=len(request['targets']),target_keys=[[r['hi'],r['lo']] for r in request['targets']],
                compatible_pairs_per_history_target=990 if request['mode'] == 'history' else None,
                selected_pairs_per_target=[len(r['selected_pairs']) for r in request['targets']] if request['mode'] == 'selected' else None)
        inventory.append(dict(group=group,original_executable=pin(exe),original_receipt=pin(path),
            original_argv=receipt['argv'],stdin=receipt['stdin'],request_inputs=inputs,
            expected_payload=pin(payload),expected_stdout=pin(receipt['stdout']['path']),
            expected_stderr=pin(receipt['stderr']['path']),domain=domain,caller=receipt['caller'],process=receipt['process']))
    counts = {group:sum(r['group'] == group for r in inventory) for group in
        ('board','bridge-queries','bridge-verify','trace','river-history','river-selected')}
    assert counts == dict(board=2,**{'bridge-queries':13,'bridge-verify':13,'trace':13,'river-history':38,'river-selected':38})
    assert len(inventory) == 117
    representatives = [r for r in inventory if r['group'] == 'board']
    for group in ('bridge-queries','bridge-verify','trace','river-history','river-selected'):
        representatives.append(max((r for r in inventory if r['group'] == group),key=lambda r:r['expected_payload']['bytes']))
    assert len(representatives) == 7
    optional_coherent = [r for r in inventory if r['group'] in ('bridge-queries','bridge-verify','trace')
        and r['domain']['batch_folder'] == 'batch-007']
    assert len(optional_coherent) == 3
    for r in representatives:
        r['future_parity'] = dict(status='prospective-not-run',new_executable=None,new_source=None,
            keep_all_original_inputs_and_stdin_exact=True,
            replacement='Replace argv[0] with the pinned new binary; for bridge/trace replace only the output destination with a fresh never-existing owned path.',
            payload_bytes_sha256_and_length_exact=True,stdout_and_stderr_bytes_exact=True,
            no_new_deals_policy_inference_or_fit=True)
    save('all-117-invocations.json',inventory)
    save('representative-controls.json',dict(primary=representatives,optional_same_batch_transport=optional_coherent))
    save('source-and-build-evidence.json',dict(snapshots=snapshots,compilation=compilation,original_binaries=old_binaries))
    plan = dict(format=1,status='prospective-read-only-not-executed',
        scope='Separate bounded native exporter software qualification using retained 20bb requests/policies only; no new scientific deals, poker accuracy claim, fitting, production change or old artifact mutation.',
        profile=str(PROFILE),profile_manifest=pin(MANIFEST),profile_readback=pin(READBACK),
        verified_retained_files=809,verified_retained_logical_bytes=1_278_992_546,
        invocation_inventory_counts=counts,invocations=117,representative_controls=7,
        representative_expected_payload_bytes=sum(r['expected_payload']['bytes'] for r in representatives),
        exact_io_contract=dict(board='stdout compact JSON + one LF',
            bridge='direct output file compact JSON without LF; separate summary stdout JSON + one LF',
            trace='direct output file compact JSON without LF; empty stdout',
            river='stdout compact JSON + one LF; deterministic summary stderr JSON + one LF'),
        compilation_evidence=compilation,
        native_executed=False,compiled=False,git_operations=False,new_source_and_binary_paths_pending=True,
        no_retry_of_original_profile=True,source_pins=PINS,source_snapshots=snapshots,
        plan_builder_sha256=sha(__file__),seconds=time.monotonic()-began)
    # Freeze all evidence after review, including original request/output bytes.
    for path,identity in PINS.items():
        assert sha(path) == identity,path
    save('plan.json',plan)
    print(json.dumps(dict(prospective_plan_complete=True,compiled=False,native_executed=False,
        source_and_evidence_pins=len(PINS),primary_controls=7,invocations=117,
        controls=[dict(group=r['group'],payload=r['expected_payload'],domain=r['domain']) for r in representatives],
        plan_sha256=sha(OUT/'plan.json')),sort_keys=True))


if __name__ == '__main__':
    main()
