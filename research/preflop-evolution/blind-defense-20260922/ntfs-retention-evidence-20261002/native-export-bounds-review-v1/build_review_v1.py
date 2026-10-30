"""Exclusive new read-only native-export review artifacts; no native execution."""
import hashlib
import json
from pathlib import Path
import time

FOLDER = Path(__file__).resolve().parent
ROOT = Path(r'T:\Dev\GTOpen')
TOOLS = ROOT/'tools/research'
EXAMPLES = ROOT/'crates/solver/examples'
PROFILE = Path(r'S:\GTOpen-research\preflop-expected-native-cycle-profile-v1')


def digest(raw): return hashlib.sha256(raw).hexdigest()


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for b in iter(lambda:stream.read(1024*1024), b''): h.update(b)
    return h.hexdigest()


def write_json(name, value):
    with (FOLDER/name).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, sort_keys=True, separators=(',', ':')); stream.write('\n')


def main():
    started = time.time()
    sources = [ROOT/'AGENTS.md'] + [TOOLS/name for name in (
        'preflop_expected_native_execution_v1.py', 'preflop_expected_river_workers_v1.py',
        'preflop_expected_river_transport_v1.py', 'preflop_expected_training_pipeline_v1.py',
        'preflop_expected_board_workers_v1.py', 'preflop_expected_worker_cancellation_v1.py',
        'preflop_expected_native_cycle_profile_v1.py', 'sampled_physical_root_evaluation_v1.py')]
    sources += [EXAMPLES/name for name in (
        'hu_sampled_allin_history_bridge_v1.rs', 'hu_sampled_action_trace_v2.rs',
        'hu_fixed_board_tree_v1.rs', 'hu_river_two_stage_stream_v1.rs',
        'research_sampled/batch_queries_v1.rs', 'research_sampled/observation_v1.rs',
        'research_sampled/state.rs', 'hu_public_economics_v1.rs')]
    assert len(set(sources)) == len(sources) and all(p.is_file() for p in sources)
    raw_sources = {p:p.read_bytes() for p in sources}
    pins = {str(p):digest(raw) for p,raw in raw_sources.items()}
    line_evidence = {}
    terms = ('def run_native', 'def verify_native', 'while child.poll()', "('stdout','stderr')",
        'child.wait(timeout=.1)', 'child.terminate()', 'child.kill()', 'result = run_native',
        'invocation=run_native', 'native = s[', '_invoke(s[', 'board_futures=',
        'max_output_bytes=64_000_000', 'native.json', 'process.json', 'used=sum',
        'fn main', 'std::fs::write', 'println!', 'MAX_BYTES', 'bytes.push', 'output.write_all')
    for path,raw in raw_sources.items():
        lines = raw.decode('utf-8-sig').splitlines()
        line_evidence[str(path)] = [dict(line=i, source=text) for i,text in enumerate(lines,1)
            if any(term in text for term in terms)]
    registration_path = PROFILE/'registration.json'
    registration = json.loads(registration_path.read_bytes())
    binaries = {}
    for role,value in registration['native'].items():
        path = Path(value); identity = sha(path)
        assert registration['config']['source_identities'][str(path)] == identity
        binaries[role] = dict(path=str(path), sha256=identity,
            matches_original_profile_registered_binary=True, executed=False)
        pins[str(path)] = identity
    for name in ('registration.json','result.json','cycle-0001/metrics.json'):
        path = PROFILE/name; pins[str(path)] = sha(path)
    groups = {name:[] for name in ('queries','updates','trace','river-history','river-selected','board')}
    for path in PROFILE.rglob('*'):
        if not path.is_file(): continue
        if path.name in {'queries.json','updates.json','action-trace.json'}:
            role = {'queries.json':'queries','updates.json':'updates','action-trace.json':'trace'}[path.name]
        elif path.name == 'board-tree-stdout.bin': role = 'board'
        elif 'conditional' in path.parts and path.name.endswith('-stdout.bin'):
            role = 'river-history' if '-history-' in path.name else 'river-selected'
        else: continue
        groups[role].append(path)
    measured = {}
    for role,paths in groups.items():
        assert paths
        largest = max(paths,key=lambda p:p.stat().st_size)
        measured[role] = dict(files=len(paths), total_bytes=sum(p.stat().st_size for p in paths),
            largest_bytes=largest.stat().st_size, largest_path=str(largest), largest_sha256=sha(largest))
        pins[str(largest)] = measured[role]['largest_sha256']
    stderr = list(PROFILE.rglob('*-stderr.bin')); process = list(PROFILE.rglob('*-process.json'))
    measured['stderr'] = dict(files=len(stderr), largest_bytes=max(p.stat().st_size for p in stderr))
    measured['river-process-sidecar'] = dict(files=len(process), largest_bytes=max(p.stat().st_size for p in process))
    missing = [
        dict(role='coordinator-query-export', native='bridge', file='queries.json',
            argv_index_including_executable=5, arguments_index_excluding_executable=4,
            python_source=str(TOOLS/'preflop_expected_training_pipeline_v1.py'), python_line=220,
            rust_source=str(EXAMPLES/'hu_sampled_allin_history_bridge_v1.rs'), rust_line=86),
        dict(role='physical-verify-updates', native='bridge', file='updates.json',
            argv_index_including_executable=5, arguments_index_excluding_executable=4,
            python_source=str(TOOLS/'preflop_expected_river_workers_v1.py'), python_line=239,
            rust_source=str(EXAMPLES/'hu_sampled_allin_history_bridge_v1.rs'), rust_line=86),
        dict(role='physical-action-trace', native='trace', file='action-trace.json',
            argv_index_including_executable=4, arguments_index_excluding_executable=3,
            python_source=str(TOOLS/'preflop_expected_river_workers_v1.py'), python_line=241,
            rust_source=str(EXAMPLES/'hu_sampled_action_trace_v2.rs'), rust_line=96)]
    native_envelope = 2*2_000_000_000 + (3+1)*64_000_000
    stdout_duplicate = 3*64_000_000
    observed_reference = measured['board']['total_bytes'] + 3*measured['river-history']['largest_bytes'] + measured['queries']['largest_bytes']
    arithmetic = dict(label='Prospective policy arithmetic; not current enforced bounds or measured concurrency',
        concurrent_board_workers=2, concurrent_physical_workers=3, concurrent_coordinator_queries=1,
        maximum_concurrent_native_children=6,
        proposed_small_transport_aggregate_output_bytes=64_000_000,
        proposed_board_aggregate_output_bytes=2_000_000_000,
        active_native_output_envelope_bytes=native_envelope,
        river_stdout_duplicate_reserve_bytes=stdout_duplicate,
        nominal_native_plus_stdout_copy_bytes=native_envelope+stdout_duplicate,
        six_bounded_capture_streams_overflow_chunks_bytes=6*2*64*1024,
        pessimistic_unqualified_river_stderr_json_copy_extra_bytes=3*6*64_000_000,
        pessimistic_native_plus_river_python_copies_bytes=native_envelope+3*6*64_000_000,
        measured_largest_role_reference_bytes=observed_reference,
        measured_largest_role_reference_with_three_stdout_copies_bytes=observed_reference+3*measured['river-history']['largest_bytes'],
        filesystem_metadata_and_publication_reserve_bytes=2_000_000_000,
        strict_current_polling_overshoot_bound=None,
        polling_overshoot_reason='Finite source-specific or OS sink bounds are not established for direct bridge/trace and board writes; .1s polling also calls guards first and terminal accepts/rejects after writes have occurred.')
    snapshot_manifest = {}
    for index,path in enumerate(sources):
        destination = FOLDER/(f'source-{index:02d}-'+path.name+'.snapshot')
        with destination.open('xb') as stream: stream.write(raw_sources[path])
        assert sha(destination) == pins[str(path)]
        snapshot_manifest[str(path)] = str(destination)
    # The report never imports any research module; verify all reviewed files at
    # terminal before writing the finalized manifest. Original artifacts are read-only.
    for path,identity in pins.items(): assert sha(Path(path)) == identity, path
    pin_record = dict(format=1, reviewed_unix=started, terminal_unix=time.time(),
        scope='Read-only native-export bounds review; no compile/native/scientific run',
        source_identities=pins, source_snapshots=snapshot_manifest, native_binaries=binaries,
        build_review_source_sha256=sha(Path(__file__).resolve()),
        existing_sources_artifacts_registrations_modified=False)
    write_json('source-pins.json', pin_record)
    write_json('review.json', dict(format=1, omitted_direct_cli_outputs=missing,
        measured_original_20bb_profile_outputs=measured, prospective_reserve_arithmetic=arithmetic,
        source_line_evidence=line_evidence, all_reviewed_sources_unchanged_at_terminal=True))
    print(json.dumps(dict(passed_read_only_review=True, files=str(FOLDER), omitted_cli_outputs=missing,
        measured_maxima={k:v['largest_bytes'] for k,v in measured.items()}, reserve=arithmetic,
        source_pins_sha256=sha(FOLDER/'source-pins.json'), review_sha256=sha(FOLDER/'review.json'))))


if __name__ == '__main__': main()
