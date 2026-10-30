"""Independent host-only E032 audit. Reads preserved evidence; runs no solver/toolchain.

Does not import the runner, assessor or comparison helper. Output is exclusive-create.
"""
import datetime
import hashlib
import json
import math
import pathlib
import re
import statistics
import struct

ROOT = pathlib.Path(r'S:\GTOpen-research\postflop-gpu-20261016')
HERE = pathlib.Path(__file__).resolve().parent
REPO = pathlib.Path(r'X:\Dev\GTOpen-gpu-research-20261016')
ORDER = ['V032-unit', 'B101', 'E032R1', 'E032R2', 'B102', 'B103', 'E032R3']
BASE = ['B101', 'B102', 'B103']
CAND = ['E032R1', 'E032R2', 'E032R3']
FIXTURES = ['rainbow', 'two-tone', 'river']
STOPS = [200, 200, 60]
TIMINGS = ['full_cycle_ms', 'build_ms', 'init_ms', 'solve_ms', 'readback_ms']
EXCLUDED = set(TIMINGS + ['fingerprint_ms_excluded'])
PINS = {}
CHECKS = []

def check(value, label):
    if not value:
        raise AssertionError(label)
    CHECKS.append(label)

def pin(path, expected=None):
    path = pathlib.Path(path)
    h = hashlib.sha256(path.read_bytes()).hexdigest()
    if expected is not None:
        check(h == expected, 'sha256 ' + str(path))
    PINS[str(path)] = h
    return h

def read(path, expected=None):
    pin(path, expected)
    return json.loads(pathlib.Path(path).read_text(encoding='utf-8'))

def markers(text, marker):
    return [json.loads(line.split(marker, 1)[1]) for line in text.splitlines() if marker in line]

def finite(value):
    return isinstance(value, (float, int)) and not isinstance(value, bool) and math.isfinite(value)

def summary(text):
    rows = re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;', text)
    check(len(rows) == 1, 'one terminal native summary')
    return list(map(int, rows[0]))

def gain(old, new):
    return 100.0 * (old - new) / old

def exact_result(result):
    return {k: v for k, v in result.items() if k not in EXCLUDED}

def distribution(values):
    return dict(count=len(values), median_ms=statistics.median(values), min_ms=min(values),
                max_ms=max(values), range_ms=max(values)-min(values), raw_ms=values)

def main():
    check(not (HERE/'validation.json').exists(), 'new immutable audit output')
    plan = ROOT/'runs/E032-primary-plan'
    protocol_hash = '6b13cb69e12e48c225a11e5beba5509ca6811c3b8d63a33d90b8bf59ad407402'
    protocol = read(plan/'protocol.json', protocol_hash)
    check(protocol['order'] == ORDER and protocol['expected_fixtures'] == FIXTURES, 'frozen order and fixtures')
    check(protocol['expected_stops'] == dict(zip(FIXTURES, STOPS)), 'frozen stops')
    check(protocol['expected_unit_passed'] == 85 and protocol['expected_unit_ignored'] == 4, 'frozen unit inventory')
    seal = read(plan/'scripts-manifest.json', 'b3690242063acc2f8160a21e0266923ed9d04bcad4e0cf825c551126bab5940a')
    for name, h in seal['script_sha256'].items():
        pin(plan/name, h)
    auth = read(plan/'authorization.json')
    for p, h in auth['evidence_sha256'].items():
        pin(p, h)
    source = read(ROOT/'runs/E032-design/manifest.json', protocol['source_archive_sha256'])
    published = read(ROOT/'comparisons/E032-three-pair-comparison/report.json')
    for item in published['input_reports']:
        pin(item['path'], item['sha256'])
    pin(REPO/'crates/solver/tests/postflop_autoresearch.rs', protocol['evaluator_sha256'])
    check(published['excluded_runs'] == [], 'no excluded samples')

    builds = {}
    for name, expected in [('E020-postflop_autoresearch', protocol['reference_manifest_sha256']),
                           ('E032-postflop_autoresearch', '890f688913d01e72152755c4e6ee46052bff30ad1c9eb444a8e519c20fcc5489'),
                           ('E032-solver', '8fb32b3525232d288c63607f31f53a8b03c3ccb2dcf48e1c9a696270da127e0c')]:
        mpath = ROOT/'binaries'/f'{name}.manifest.json'
        m = read(mpath, expected)
        pin(ROOT/'binaries'/f'{name}.exe', m['binary_sha256'])
        check(len(m['source_sha256']) == 162, name + ' full source map')
        for group in ['candidate_sources', 'source_copies']:
            for item in m[group].values():
                pin(item['path'], item['sha256'])
        if name.startswith('E032'):
            check(m['primary_protocol_sha256'] == protocol_hash, name + ' protocol binding')
            check(m['probe_authorization_sha256'] == PINS[str(plan/'authorization.json')], name + ' authorization binding')
            check(m['source_matches_prebuild'] and m['accepted_cuda_present'], name + ' frozen build assertions')
            check(m['unchanged_cuda_sha256'] == protocol['accepted_kernel_sha256'], name + ' CUDA identity')
            for field in ['cargo_artifact', 'solver_artifact']:
                check(m[field]['fresh'] is False and m[field]['features'] == ['gpu'], name + ' fresh gpu-only ' + field)
            pin(m['build_log'], m['build_log_sha256'])
            pin(m['build_stderr_log'], m['build_stderr_sha256'])
        builds[name] = m
    bs = builds['E020-postflop_autoresearch']['source_sha256']
    cs = builds['E032-postflop_autoresearch']['source_sha256']
    check(bs.keys() == cs.keys(), 'same 162 source names')
    changed = [{'path': p, 'baseline': bs[p], 'candidate': cs[p]} for p in bs if bs[p] != cs[p]]
    check(changed == published['source_changes'], 'published source delta')
    check([v['path'] for v in changed] == ['crates/solver/src/gpu/mod.rs'], 'one host source delta only')
    check(changed[0]['baseline'] == protocol['accepted_owned_sha256'][changed[0]['path']] and
          changed[0]['candidate'] == protocol['candidate_owned_sha256'][changed[0]['path']], 'source delta matches protocol')
    check(builds['E032-solver']['source_sha256'] == cs, 'unit and benchmark same sources')
    check(builds['E020-postflop_autoresearch']['benchmark_sha256'] == builds['E032-postflop_autoresearch']['benchmark_sha256'], 'all frozen benchmark inputs unchanged')

    runs, results, convergence = {}, {}, {}
    native_summaries = {}
    expected_stage_order = ['suite_start']
    for f, stop in zip(FIXTURES, STOPS):
        expected_stage_order += ['fixture_start', 'build_complete', 'gpu_ready'] + ['convergence_check']*(stop//20) + ['timing_complete']
    expected_stage_order += ['suite_complete']
    for rid in ORDER:
        r = read(ROOT/'runs'/rid/'report.json')
        rawpath = ROOT/'runs'/rid/'stdout.log'
        pin(rawpath, r['stdout_sha256'])
        raw = rawpath.read_text(encoding='utf-8')
        ns = summary(raw)
        native_summaries[rid] = ns
        unit = rid == 'V032-unit'
        check(ns == ([85, 0, 4, 0, 0] if unit else [1, 0, 0, 0, 0]), rid + ' native terminal inventory')
        check(r['status'] == 'measured' and r['returncode'] == 0 and r['test_pass_count'] == ns[0], rid + ' runner terminal status')
        binname = 'E032-solver' if unit else ('E020-postflop_autoresearch' if rid in BASE else 'E032-postflop_autoresearch')
        bm = r['binary_build_manifest']
        check(bm['data'] == builds[binname] and bm['binary_hash_verified'], rid + ' recorded build manifest exact')
        pin(bm['path'], bm['sha256'])
        check(r['binary_sha256'] == builds[binname]['binary_sha256'], rid + ' executable binding')
        check(pathlib.Path(r['command'][0]) == ROOT/'binaries'/f'{binname}.exe', rid + ' executable command')
        check(r['command'][1:] == (['--nocapture', '--test-threads=1'] if unit else ['postflop_complete_cycle', '--nocapture', '--test-threads=1', '--ignored']), rid + ' command arguments')
        check(r['environment']['POSTFLOP_AUTORESEARCH_FIXTURE'] is None and r['environment']['POSTFLOP_AUTORESEARCH_PROFILE'] == '0', rid + ' no fixture/profile override')
        if unit:
            for test in protocol['expected_new_unit_tests']:
                check(f'test {test} ... ok' in raw, 'new coverage test executed ' + test)
            check('running 89 tests' in raw, 'complete unit inventory announced')
        else:
            check(r['environment'] == runs['B101']['environment'] if 'B101' in runs else True, rid + ' consistent run environment')
            rr = markers(raw, 'AUTORESEARCH_RESULT ')
            stages = markers(raw, 'AUTORESEARCH_STAGE ')
            check(rr == r['results'], rid + ' raw results equal report')
            check(stages == [s['data'] for s in r['stages']], rid + ' raw stages equal report')
            check([s['stage'] for s in stages] == expected_stage_order, rid + ' exact stage schedule')
            check([v['fixture_id'] for v in rr] == FIXTURES, rid + ' complete fixture order')
            checks = [s for s in stages if s['stage'] == 'convergence_check']
            check(len(checks) == 23, rid + ' complete 23 checks')
            convergence[rid] = [{k: v for k, v in c.items() if k != 'solve_checks_elapsed_ms'} for c in checks]
            for i, (f, stop, v) in enumerate(zip(FIXTURES, STOPS, rr)):
                fc = [c for c in checks if c['fixture_id'] == f]
                check([c['iteration'] for c in fc] == list(range(20, stop+1, 20)), rid + f + ' exact check schedule')
                check(v['iteration'] == stop and v['fixture_index'] == i and v['target_met'], rid + f + ' stop/target')
                check(v['check_every'] == 20 and v['max_iterations'] == 400 and v['target_pct'] == 0.3 and v['storage'] == 'compressed', rid + f + ' fixed workload')
                check(all(finite(v[k]) and v[k] >= 0 for k in EXCLUDED), rid + f + ' finite nonnegative times')
                for c in fc + [v]:
                    bits = struct.unpack('<Q', struct.pack('<d', c['exploit_chips']))[0]
                    check(bits == c['exploit_bits'], rid + f + ' exact float64 exploit encoding')
                    check(c['exploit_pct_pot'] == c['exploit_chips']/v['config']['tree']['starting_pot']*100.0, rid + f + ' exploit percentage arithmetic')
                check(all(c['exploit_pct_pot'] > 0.3 for c in fc[:-1]) and fc[-1]['exploit_pct_pot'] <= 0.3, rid + f + ' first fixed-cadence target crossing')
                for k in ['exploit_chips', 'exploit_pct_pot', 'exploit_bits', 'iteration']:
                    check(v[k] == fc[-1][k], rid + f + ' final result/check ' + k)
                timing = next(s for s in stages if s['stage'] == 'timing_complete' and s['fixture_id'] == f)
                check(all(v[k] == timing[k] for k in TIMINGS), rid + f + ' final raw timing marker agreement')
                fp = v['state_fingerprint']
                check(fp['hash'] == v['fingerprint'] and fp['exploit_bits'] == v['exploit_bits'] and fp['iteration'] == stop, rid + f + ' fingerprint header')
                check(fp['iteration_le_bytes'] == list(struct.pack('<I', stop)), rid + f + ' iteration encoding')
                check([(a['player'],a['arena'],a['kind']) for a in fp['arenas']] == [(0,'regrets','i16'),(0,'strategy_sums','u16'),(1,'regrets','i16'),(1,'strategy_sums','u16')], rid + f + ' all four typed arenas')
                check(all(a['bytes'] == a['entries']*2+a['scale_entries']*4 for a in fp['arenas']), rid + f + ' arena byte geometry')
                check(sum(a['bytes'] for a in fp['arenas']) == v['cpu_arena_bytes'], rid + f + ' full CPU arena byte accounting')
                check(len(fp['root_strategy_bits']) > 0 and all(isinstance(b,int) and 0 <= b < 2**32 for b in fp['root_strategy_bits']), rid + f + ' complete emitted root bit vector')
            results[rid] = rr
        runs[rid] = r
    for rid in BASE+CAND:
        check([exact_result(v) for v in results[rid]] == [exact_result(v) for v in results['B101']], rid + ' ALL non-timing fields exact')
        check(convergence[rid] == convergence['B101'], rid + ' ALL non-timing convergence fields exact')
    check(sum(len(v) for v in results.values()) == 18 and sum(len(v) for v in convergence.values()) == 138, 'all 18 results and 138 checks retained')
    chronology = sorted([dict(id=rid, started_at=runs[rid]['started_at'], finished_at=runs[rid]['finished_at']) for rid in ORDER[1:]], key=lambda x:x['started_at'])
    check([x['id'] for x in chronology] == ORDER[1:] and chronology == published['chronology'], 'chronology and alternation exact')
    check(all(runs[a]['finished_at'] <= runs[b]['started_at'] for a,b in zip(ORDER,ORDER[1:])), 'no overlapping reported child intervals')
    complete = read(ROOT/'runs/E032-primary-execution/complete.json')
    check(complete['order'] == ORDER and complete['accepted_performance_claim'] is False, 'fixed cohort terminal record')

    pair_rows = []
    for b,c in zip(BASE,CAND):
        old=sum(v['full_cycle_ms'] for v in results[b]); new=sum(v['full_cycle_ms'] for v in results[c])
        pair_rows.append(dict(baseline_id=b,candidate_id=c,order=sorted([b,c],key=lambda r:runs[r]['started_at']),baseline_full_cycle_ms=old,candidate_full_cycle_ms=new,observed_gain_pct=gain(old,new),fixture_gain_pct={f:gain(results[b][i]['full_cycle_ms'],results[c][i]['full_cycle_ms']) for i,f in enumerate(FIXTURES)}))
    check(pair_rows == published['pairs'], 'all paired arithmetic exact')
    fixture_rows=[]; guards=[]
    for i,f in enumerate(FIXTURES):
        arms={arm:{k:distribution([results[rid][i][k] for rid in ids]) for k in TIMINGS} for arm,ids in [('baseline',BASE),('candidate',CAND)]}
        old=arms['baseline']['full_cycle_ms']['median_ms'];new=arms['candidate']['full_cycle_ms']['median_ms']
        fg=gain(old,new)
        pub=published['fixtures'][i]
        check(pub['fixture_id'] == f and pub['baseline'] == arms['baseline'] and pub['candidate'] == arms['candidate'] and pub['observed_gain_pct'] == fg, f + ' all timing distributions/medians/gain exact')
        pair_reg=[-p['fixture_gain_pct'][f] for p in pair_rows]
        gr=dict(fixture_id=f,median_regression_pct=-fg,paired_regression_pct=pair_reg,repetitions_above_3pct=sum(x>3 for x in pair_reg),paired_repetitions=3,required_repetitions=2,repeatable_material_regression=(-fg>3 and sum(x>3 for x in pair_reg)>=2))
        pg=published['performance']['fixture_regression_guard']['fixtures'][i]
        check(all(pg[k] == v for k,v in gr.items()), f + ' exact repeated fixture guard')
        guards.append(gr)
        fixture_rows.append(dict(fixture_id=f,**arms,observed_gain_pct=fg))
    old=sum(f['baseline']['full_cycle_ms']['median_ms'] for f in fixture_rows)
    new=sum(f['candidate']['full_cycle_ms']['median_ms'] for f in fixture_rows)
    g=gain(old,new);failed=[x['fixture_id'] for x in guards if x['repeatable_material_regression']]
    score=dict(baseline_full_cycle_ms=old,candidate_full_cycle_ms=new,observed_gain_pct=g,required_gain_pct=2.0,aggregate_gate_met=g>=2.0)
    check(all(published['performance'][k] == v for k,v in score.items()), 'aggregate median score/gate exact')
    check(not failed and published['performance']['fixture_regression_guard']['affected_fixtures'] == [] and published['performance']['fixture_regression_guard']['failed'] is False, 'no fixture guard failures')
    check(g<2 and published['decision']=='rejected' and not published['accepted'] and not published['deployed'], 'rejection is required solely by aggregate threshold')
    check(published['correctness']['exact_compressed_screen']=='pass' and published['correctness']['broader_validation']=='not run' and published['correctness']['f32_storage']=='not run', 'primary exactness scoped; no broader qualification')
    pin(__file__)
    evidence=[]
    for v in results['B101']:
        fp=v['state_fingerprint']
        evidence.append(dict(fixture_id=v['fixture_id'],iteration=v['iteration'],exploit_bits=v['exploit_bits'],fingerprint=v['fingerprint'],cpu_arena_bytes=v['cpu_arena_bytes'],root_vector_words=len(fp['root_strategy_bits']),arena_fingerprints=fp['arenas']))
    out=dict(id='E032',verdict='PASS_AUDIT_REJECTED_PRIMARY',at=datetime.datetime.now(datetime.timezone.utc).isoformat(),independent_numerical_audit_pass=True,
             candidate_accepted=False,deployment_changed=False,reviewer_execution='host-only standard-library evidence parsing; no solver, tests, compiler, GPU or status mutation',
             check_count=len(CHECKS),checks=CHECKS,input_sha256=PINS,protocol_sha256=protocol_hash,
             complete_results=18,convergence_records=138,all_non_timing_result_fields_exact=True,all_non_timing_convergence_fields_exact=True,
             excluded_result_fields=sorted(EXCLUDED),excluded_convergence_fields=['solve_checks_elapsed_ms'],native_summaries=native_summaries,
             final_state_evidence=evidence,chronology=chronology,all_samples_included=True,exclusions=[],pairs=pair_rows,fixtures=fixture_rows,
             performance=score,fixture_regression_guards=guards,fixture_guard_failures=failed,decision='rejected',reason='1.1460346635930425 percent is below the fixed 2 percent complete-cycle gate.',
             limitations=['Equality covers all emitted complete non-timing objects, four full-arena fingerprints and root strategy bits. The primary does not retain full arena byte files for an independent byte-by-byte replay of the hashes.',
                          'The added unit and existing shared-dispatch reference are not an immutable-original implementation oracle; the three frozen E020 binary runs provide the independent original comparison.',
                          'No additional F32, wider state/menu/resume, holdout or cumulative qualification was run for this rejected candidate; no accepted speedup or significance claim.',
                          'Build/custody/restoration checks are separately owned by the independent custody reviewer.'])
    with (HERE/'validation.json').open('x',encoding='utf-8',newline='\n') as f: json.dump(out,f,indent=2);f.write('\n')
    text=(f'E032 independent numerical audit passed; the candidate remains rejected.\n\n'
          f'All 18 complete results and 138 convergence checks match across six frozen runs. Unit summary: 85 passed, 0 failed, 4 ignored. '
          f'Sum of fixture medians: {old:.4f} -> {new:.4f} ms ({g:.10f}% reduction), below the 2% gate. No repeated fixture regression guard failed. '
          'Every sample is retained. No broader, holdout or cumulative run is warranted.\n\n'
          'The audit independently parsed raw logs and recomputed distributions, pairs and gates without importing the assessor. '
          'State equality is the full emitted fingerprint/metadata/root-vector contract, not a new full-arena byte export. No native/GPU/compiler work or source/status changes were performed.\n')
    with (HERE/'summary.md').open('x',encoding='utf-8',newline='\n') as f: f.write(text)
    print(json.dumps(dict(verdict=out['verdict'],checks=len(CHECKS),pins=len(PINS),validation_sha256=hashlib.sha256((HERE/'validation.json').read_bytes()).hexdigest(),summary_sha256=hashlib.sha256((HERE/'summary.md').read_bytes()).hexdigest(),audit_sha256=PINS[str(pathlib.Path(__file__))])))

if __name__ == '__main__':
    main()
