"""Independently replay resource markers and preserve the closed E123 form."""
import json, shutil, subprocess, sys, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
H, S, D = [ROOT / ('runs/' + name) for name in ['E123-resource', 'E123-source', 'D303-child-cache-scout']]
UI = ROOT / 'runs/D302-live-UI-check'
O = H / 'execution'
R, P = h.read(H / 'report.json'), h.read(H / 'protocol.json')
h.custody()
h.ar.refuse_active(h.ar.live_status())
assert not (ROOT / 'gpu-run.lock').exists() and not (ROOT / 'epoch-sequence.lock').exists()
for path, digest in P['input_sha256'].items():
    h.pin(path, digest)
assert R['status'] == 'rejected_closed_resource_or_ABI_gate'
assert R['application_kernel_launches'] == R['solver_executions'] == R['performance_samples'] == 0
assert not R['source_activated'] and not R['candidate_accepted']
receipts = []
for label in ['rustc', 'probe']:
    path = O / (label + '.exit.json')
    receipt = h.read(path)
    assert receipt['returncode'] == 0 and receipt['error'] is receipt['cleanup'] is None
    receipts.append({'path': str(path), 'sha256': h.sha(path), 'returncode': 0})
markers = [json.loads(line.split('E123_RESOURCE ', 1)[1]) for line in (O / 'probe.stdout.log').read_text().splitlines() if 'E123_RESOURCE ' in line]
assert len(markers) == 19 and markers[-1]['stage'] == 'complete'
assert markers[-1]['application_kernels'] == markers[-1]['solver_or_speed_runs'] == 0
assert markers[-1]['candidate_NVRTC_compiles'] == 2 and markers[-1]['baseline_PTX_reused']
assert markers[:-1] == R['resource_rows']
rows = {(r['variant'], r['kernel']): r for r in markers[:-1]}
assert len(rows) == 18
b, c = rows['baseline', 'up_action'], rows['candidate', 'up_action']
assert (b['registers'], c['registers']) == (62, 68)
assert (b['max_threads'], c['max_threads']) == (1024, 896)
assert (b['local_bytes_per_thread'], c['local_bytes_per_thread']) == (64, 32)
assert b['occupancy_by_threads'] == [[64, 16], [128, 8], [256, 4]]
assert c['occupancy_by_threads'] == [[64, 14], [128, 7], [256, 3]]
keys = ['registers', 'constant_bytes', 'local_bytes_per_thread', 'static_shared_bytes', 'dynamic_shared_bytes', 'max_threads', 'occupancy_by_threads', 'context_stack_after']
for name in P['original_entries']:
    if name != 'up_action':
        assert all(rows['baseline', name][key] == rows['candidate', name][key] for key in keys)
for key in ['constant_bytes', 'static_shared_bytes', 'dynamic_shared_bytes', 'context_stack_after']:
    assert c[key] == b[key]
expected = {'up_action:no_maxthread_loss': c['max_threads'] >= b['max_threads'],
            'up_action:strict_actual_register_reduction': c['registers'] < b['registers']}
assert all(R['gates'][key] == value for key, value in expected.items())
failed = [key for key, value in R['gates'].items() if not value]
assert set(failed) == set(expected) and not any(expected.values())
h.save(H / 'closure.json', {
    'at': h.now(), 'decision': 'REJECT_CLOSE_E123_AT_COMPILED_RESOURCE_AND_MECHANISM_GATE',
    'report_sha256': h.sha(H / 'report.json'), 'protocol_sha256': h.sha(H / 'protocol.json'),
    'candidate_source_sha256': h.sha(S / 'candidate.cu'),
    'raw_marker_root_crosscheck': {'baseline': b, 'candidate': c, 'failed_gates_independently_recomputed': failed},
    'reason': 'Actual up_action registers62to68, maximumthreads1024to896 and occupancy16/8/4to14/7/3. Local64to32 is a reduction, but original no-maxthread-loss gate and prospective strictregister-reduction mechanism gate fail. No application kernel, numerical or timed regression was measured.',
    'actual_child_reload_FP_mechanism_or_accuracy_qualified': False,
    'new_applicationkernels_numerical_CFR_solver_or_speed_samples': 0,
    'fixed_plain_source_form_closed_no_volatile_asm_restrict_arity_placement_helper_width_flags_source_quality_sample_rescue': True,
    'child_receipts': receipts, 'all_owned_compiler_module_children_terminal': True,
    'accepted_main_live_protected_PTX_unchanged': True, 'goal_active': True})

# Preserve complete UI evidence separately from CLI's ignored working folder.
ui_report = h.read(UI / 'report.json')
copies = UI / 'raw-browser-evidence'
copies.mkdir(exist_ok=False)
for path, digest in ui_report['inspected_files_sha256'].items():
    source = Path(path)
    h.pin(source, digest)
    destination = copies / source.name
    assert not destination.exists()
    shutil.copyfile(source, destination)
    h.pin(destination, digest)
files = [UI / 'report.json', *copies.iterdir(), D / 'report.json', S / 'manifest.json', S / 'candidate.cu', S / 'baseline.cu']
files += [H / name for name in ['protocol.json', 'report.json', 'closure.json']]
files += [O / name for name in ['rustc.invocation.json', 'rustc.exit.json', 'probe.invocation.json', 'probe.exit.json', 'probe.stdout.log', 'binary.json', 'complete.json']]
published = []
for path in files:
    base = next(root for root in [UI, D, S, H] if path.is_relative_to(root))
    relative = Path(base.name) / path.relative_to(base)
    destination = h.ar.DASHBOARD / 'evidence' / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        assert destination.read_bytes() == path.read_bytes()
    else:
        shutil.copyfile(path, destination)
    with urllib.request.urlopen(h.ar.LIVE + '/research/postflop-gpu-20261016/evidence/' + relative.as_posix(), timeout=20) as response:
        assert response.read() == path.read_bytes()
    published.append({'relative': relative.as_posix(), 'sha256': h.sha(path), 'bytes': path.stat().st_size})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'), timeout=3):
    status = h.read(h.ar.STATUS)
    e = next(row for row in status['experiments'] if row['id'] == 'E123')
    e.update(status='rejected', accepted=False, stage='Closed at compiler resource and mechanism gates',
             reason='Original child cache removal increases registers62to68 and reduces maxthreads1024to896; local64to32 does not satisfy frozen gates. All9ABIs/8untargetedbodies/resources exact. No numerical/solver/speed test or source activation; fixed form closed without variants.')
    e['evidence'].append({'label': 'Raw resource replay and closure', 'url': 'evidence/E123-resource/closure.json'})
    ui = next(row for row in status['experiments'] if row['id'] == 'D302')
    ui['evidence'] += [{'label': 'Rendered tracker', 'url': 'evidence/D302-live-UI-check/raw-browser-evidence/D302-tracker-before.png'},
                       {'label': 'Rendered simplified menu', 'url': 'evidence/D302-live-UI-check/raw-browser-evidence/D302-preflop-menu.png'}]
    status.update(updated_at=h.now(), state='running', goal_status='active', active_experiment='E123',
                  stage='E123 closed; distinct lead search continues',
                  activity='Child-value reload form rejected at compiler prerequisites: registers62to68/maxthreads1024to896. No speed claim. Live menu and tracker browser-verified; E080/GPU/compressed/16 remains qualified/live.')
    h.ar.atomic_json(h.ar.STATUS, status)
ledger = h.REPO / 'research/postflop-gpu-20261016/experiments.md'
prefix = ledger.read_bytes()
assert b'\n## D302 live UI and D303/E123 child-value cache removal' not in prefix
assert not subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=h.REPO, text=True).strip()
entry = f'''

## D302 live UI and D303/E123 child-value cache removal - rejected at compiler gates

Prior goal turn E122 completed13300rawpairs/26600launches/86ordinaryunits/freshbuilds/fixed3pairs, closed-0.447667383267%/two-toneguard. Currentaccepted/main/live/protected2PTX/idle/locks/ledgerHEAD rechecked. Re-running oldcreate-onlyterminalauditor passed all checks then refused overwritingexistingterminal-audit.json; no native/compiler/solver restarted. Explicitreadonlyrecheckpassed; originalreceiptunchanged. D100/D187 cache/carveout/scope, E005/E014 aritysplit, E063ranksegments, E024genericcache, E117earlierchildloads remainclosed. No hardwarecounterretry.

D302actualisolatedPlaywrightbrowser opens live tracker and PreflopLab, snapshots/screenshots/console retained,ownedbrowserclosed. NewRAM10.46s/5fresh/E080GPUcompressed16 explicitly separate fromearlierRAM14.74%chart; E122closure displayed; trackerconsole0errors0warnings. Beforemilestoneupdates honeststaleindicatorafter6minutes shown,thresholdunchanged. Liveinitialpreflopview has nolegacypostflop selector/options; source DEFAULT_REALIZATION=balanced. One400/api/preflop/session isexpectedwhen no currentgameexists,notclaimedUIexception. No build/load/save/solve orlive-sessionreplacement. Scopedinitialrenderproof only,notnewold-save/numerical/model-qualityproof. Alloriginalbrowserartifacts copied/fullSHAcheckedfromignoredCLIworkingfolder intoX/UIrawarchive.

D303bounded142uniqueCUDAhashes andalllocalrefkernels revisions findno recognized helperretainingrc while removingvc and rereadinglateCFV. Boundedliteral/helperquery notexhaustive semantic/remotenovelty. E024removesbothcachesONLYgenericNA0 andfailedspeed; E117moveschildreadsEARLIER intovc andfailedresources. Thisdifferentoneplain-sourceform removesonlyvc acrossoriginaltemplatehelper,retainsrc/small/sum/sigma/out/strat/discount/regretoperations/order. Sameinitialchildread,latephase rereads identicalimmutableCFVword; noCFVwritesbetweenloads,regret/strategyallocationsdisjoint,finalparentwriteafterupdates. SourceargumentneedsactualGPUalias/FP/NaN/callerproofifadvancing,notassumed. No volatile/asm/flags/aritysubset/newhelper/shared/global/host/ABI/launch/quality/cadence/savechange. Fourliteral/commentedits wholeCRLFinverseexact;candidate{h.sha(S/'candidate.cu')}.

FrozenE123resourceprotocol{h.sha(H/'protocol.json')} beforeoneRustcompiler/oneownedmoduleprobe,2candidateNVRTC12.9targets120/75, sealedacceptedbaselinePTXreused. All9ABIs/barriers/8untargetedbodies+actualresourcesexact; targetbodychangesbotharches. Prospectiveactualcompute120registercountstrictlybelow62required toshow intendedregisterresourcebenefit,plusoriginalD108nomaxthreadlossandallothergates. Actualup_actionregister62->68,local64->32,maxthreads1024->896,64/128/256residency16/8/4->14/7/3;constant/static/dynamic0/stack1024unchanged. Failedgates{json.dumps(failed)}. Independentcomplete19rawmodulemarker/receipt/sourcepinreplayagrees; all2ownedchildren terminal0. Localstorageimprovement isnotacceptedgain; noactualFP/reloadmechanism,numericalaccuracyorspeedclaim.

REJECT/CLOSEfixedE123form. No volatile/asm/restrict/arity/cacheplacement/helper/flags/width/source/quality/sample rescue. No applicationkernels/CFR/solver/numerical/ordinary/primary/fresh16/broad/rawengine/canonical/material/holdout/cumulative/app extension aftercompilerfailure,no productionactivation. Original2PTX/source/raw/moduleevidencepreserved;{len(published)}artifactsHTTPbyteverified,closure{H/'closure.json'}. QualifiedliveE080/GPU/compressed/16/defaultaffinity,RAMreference10456.4109ms unchanged,lastprimaryB377/nextB378,newadoptedgain0. AllnewbulkX/Sreadonly/noT,ledgerprefixbyteexact/localledgeronlycommit/nopush;goalactive.
'''
ledger.write_bytes(prefix + entry.encode())
assert ledger.read_bytes()[:len(prefix)] == prefix
h.custody()
subprocess.run(['git', 'add', '--', 'research/postflop-gpu-20261016/experiments.md'], cwd=h.REPO, check=True)
assert subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=h.REPO, text=True).splitlines() == ['research/postflop-gpu-20261016/experiments.md']
subprocess.run(['git', '-c', 'gc.auto=0', 'commit', '-m', 'research: reject child-value cache removal at compiler gates'], cwd=h.REPO, check=True)
h.save(H / 'publication.json', {'at': h.now(), 'local_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=h.REPO, text=True).strip(),
    'report_sha256': h.sha(H / 'report.json'), 'closure_sha256': h.sha(H / 'closure.json'), 'HTTP_byte_verified': published,
    'all_owned_children_terminal': True, 'new_applicationkernels_solver_or_speed_samples': 0,
    'accepted_main_live_protected_PTX_unchanged': True, 'goal_active': True})
h.custody()
print(json.dumps({'status': 'E123_CLOSED', 'HTTP_artifacts': len(published), 'last_primary': 'B377', 'next_primary': 'B378'}), flush=True)
