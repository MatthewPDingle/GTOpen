"""Preserve the normal-division contract and close missing native mechanism."""
import json, shutil, subprocess, sys, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
h.custody()
h.ar.refuse_active(h.ar.live_status())
assert not (ROOT / 'gpu-run.lock').exists() and not (ROOT / 'epoch-sequence.lock').exists()
D = ROOT / 'runs/D305-normal-division-scout'
T = ROOT / 'runs/D306-normal-division-PTX'
N = ROOT / 'runs/D307-normal-division-native'
R = ROOT / 'runs/E124-resource'
S = ROOT / 'runs/E124-source'
P, q, native = h.read(R / 'protocol.json'), h.read(R / 'report.json'), h.read(N / 'report.json')
for path, digest in P['input_sha256'].items():
    h.pin(path, digest)
assert all(q['gates'].values()) and q['application_kernel_launches'] == q['solver_executions'] == q['performance_samples'] == 0
assert native['status'] == 'rejected_closed_required_native_work_removal_not_established'
assert native['all_candidate_RNFTZ_sites_accounted'] == 28 and not native['candidate_ordinary_primitive_work_removed']
assert len(native['negative_reader_fixtures_rejected']) == 4
assert h.read(T / 'report.json')['site_counts'] == {'compute_120:down_action': 16, 'compute_120:up_action': 12, 'compute_75:down_action': 23, 'compute_75:up_action': 23}
assert len(h.read(T / 'report.json')['negative_fixtures_rejected']) == 4
required = {'MUFU.RCP': 1, 'FCHK': 1, 'FFMA': 5, 'CALL.REL.NOINC': 1}
for name, count in [('down_action', 16), ('up_action', 12)]:
    entry = native['witnesses'][name]
    assert entry['original_first_common_normalization_reference']['local_opcode_inventory'] == required
    assert len(entry['candidate_all_FTZ_site_witnesses']) == count
    for row in entry['candidate_all_FTZ_site_witnesses']:
        assert row['local_opcode_inventory'] == required
        assert [event['stage'] for event in row['five_original_division_refinement_stages']] == [0, 1, 2, 3, 4]
for protocol_path in [T / 'protocol-v2.json', N / 'protocol.json', N / 'reader-protocol.json']:
    for path, digest in h.read(protocol_path)['input_sha256'].items():
        h.pin(path, digest)
receipts = []
for folder in [R / 'execution', N / 'execution']:
    for path in folder.rglob('*.exit.json'):
        receipt = h.read(path)
        assert receipt['returncode'] == 0 and receipt['error'] is receipt['cleanup'] is None
        receipts.append({'path': str(path), 'sha256': h.sha(path), 'returncode': 0})
assert len(receipts) == 4
H = ROOT / 'runs/E124-native-closure'
H.mkdir(exist_ok=False)
h.save(H / 'report.json', {
    'id': 'E124-native-closure', 'at': h.now(), 'status': 'REJECT_CLOSE_E124_REQUIRED_NATIVE_WORK_REMOVAL_NOT_ESTABLISHED',
    'candidate_CUDA_sha256': h.sha(S / 'candidate.cu'), 'resource_protocol_sha256': h.sha(R / 'protocol.json'),
    'source_contract': 'Fixed n>=2^-63,d<=2^63,n<=d proves normalpositiveinputs and RNoutput underNVIDIAPTXsemantics. Ordinary originaldivision fallback for everyotherinput. Source-only universal range algebra plus1764boundarypairs/2negativecounterexamples, not actualGPUaccuracyproof.',
    'resources': 'downregister40/local32/max1024/occupancy24,12,6 unchanged; upregister62to64 warning,local64/max1024/occupancy16,8,4unchanged. Shared/constant/dynamic0/stack1024unchanged, all9ABIs/7untargetedbodies+resources exact. Two NVRTC12.9targets120/75 only.',
    'PTX': 'Every16down+12up actual120 and23down+23upcompat75 FTZsite has exactnormalguard/sameoriginalRNfallbackandsameoperandexpressions/destination/join.4negativefixturespass. V1actual120passed;75blocklayout/identicalclampaliasesnotrecognized; additivev2localCFG/max/movreaderpreservesall4sections/all74sites/gates. No optimizer/compiler/module/native repeat.',
    'native': 'Oneownedmodulecallbackcapture/one nvdisasm, accepted same-driver baseline reused. Every28actualFTZslowCALLsite retains1RCP/FCHK/5originalrefinementFMAdependency-stages/conditionalexceptionalbranch/CALL, sameworkas original common reference pertarget.4negativefixturespass. No predeclared ordinary division-work-removal evidence established; no positive native gate.',
    'limits': 'Scoped local static dependency/window witnesses; not fullnativeCFG/pointer/registerliveness/IEEEinterpreter, dynamicinstruction/counter/time/accuracy/no-cost/universalno-speedup proof. No applicationkernels/numerical/CFR/solver/speed trial followed admissionfailure.',
    'fixed_form_closed': 'No guard/window/asmconstraint/architecture/kernel-subset/arity/zero-or-one-bypass/helper/flags/width/source/quality/sample rescue. E060sharedrefinement/E101/E116bypass/E108integerquotient remainclosed.',
    'child_receipts': receipts, 'all_owned_children_terminal': True, 'locks_absent': True,
    'new_applicationkernels_numerical_solver_or_speed_samples': 0, 'candidate_adopted': False,
    'accepted_main_live_protected_PTX_unchanged': True, 'last_primary_baseline': 'B377', 'next_unused_primary_baseline': 'B378',
    'all_new_bulk_X_S_readonly_no_T': True, 'goal_active': True})
files = [D / name for name in ['history.json', 'range-contract.json', 'report.json']]
files += [S / name for name in ['manifest.json', 'baseline.cu', 'candidate.cu']]
files += [R / name for name in ['protocol.json', 'report.json']]
files += [T / name for name in ['protocol.json', 'reader-v1-failure.json', 'protocol-v2.json', 'report.json']]
files += [N / name for name in ['protocol.json', 'capture-report.json', 'reader-protocol.json', 'report.json']]
files += [R / 'execution' / name for name in ['rustc.invocation.json', 'rustc.exit.json', 'probe.invocation.json', 'probe.exit.json', 'probe.stdout.log', 'complete.json']]
files += [N / 'execution/candidate' / name for name in ['capture.invocation.json', 'capture.exit.json', 'disassemble.invocation.json', 'disassemble.exit.json']]
files += [H / 'report.json']
published = []
for path in files:
    relative = path.relative_to(ROOT / 'runs')
    destination = h.ar.DASHBOARD / 'evidence' / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        assert destination.read_bytes() == path.read_bytes()
    else:
        shutil.copyfile(path, destination)
    with urllib.request.urlopen(h.ar.LIVE + '/research/postflop-gpu-20261016/evidence/' + relative.as_posix(), timeout=20) as response:
        assert response.read() == path.read_bytes()
    published.append({'url': relative.as_posix(), 'sha256': h.sha(path)})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'), timeout=3):
    status = h.read(h.ar.STATUS)
    e = next(row for row in status['experiments'] if row['id'] == 'E124')
    e.update(status='rejected', accepted=False, at=h.now(), stage='Closed: native division work removal not established',
             correctness='source_PTX_native_only_no_numerical_trials',
             reason='All28guarded native sites retain original1RCP/5refinementFMAs/FCHK/conditional slowCALL. Required ordinary division-work removal not established; fixedform closed before GPU numerical/solver/speed trials. Resourcepass/register62to64 warning preserved; no measured performance verdict.')
    e['evidence'] += [{'label': 'All PTX guard/fallback sites', 'url': 'evidence/D306-normal-division-PTX/report.json'},
                      {'label': 'All native division-core witnesses', 'url': 'evidence/D307-normal-division-native/report.json'},
                      {'label': 'Closure, limits and custody', 'url': 'evidence/E124-native-closure/report.json'}]
    status['experiments'] += [
        {'id': 'D306', 'at': h.now(), 'title': 'Every guarded division PTX site and fallback', 'kind': 'diagnostic', 'status': 'measured', 'accepted': False,
         'correctness': 'scoped_PTX_pass', 'reason': 'All74sites across120/75normalizationsections preserve exactnormalguard/sameRNfallback/operands/join;4negativefixtures. Additivecompatibility-layout reader repair,no native repeats.', 'evidence': [{'label': 'Scoped PTX proof', 'url': 'evidence/D306-normal-division-PTX/report.json'}]},
        {'id': 'D307', 'at': h.now(), 'title': 'Actual guarded native division work', 'kind': 'diagnostic', 'status': 'rejected', 'accepted': False,
         'correctness': 'scoped_native_witness_pass', 'reason': 'All28FTZnative sites retain original division core; positive native-work-removal gate not established. No application kernel orspeed test.', 'evidence': [{'label': 'All native core sites and limits', 'url': 'evidence/D307-normal-division-native/report.json'}]}
    ]
    status.update(updated_at=h.now(), state='running', goal_status='active', active_experiment='E124', stage='E124 closed; distinct performance lead search continues',
                  activity='Guarded RN-FTZ division retains ordinary native division core at all28sites. Fixedform closed before numerical/speed trials. E080/GPU/compressed/16 remains qualified/live; no new gain adopted.')
    h.ar.atomic_json(h.ar.STATUS, status)
ledger = h.REPO / 'research/postflop-gpu-20261016/experiments.md'
prefix = ledger.read_bytes()
assert b'\n## D305-D307 / E124 guarded normal RN-FTZ division' not in prefix
assert not subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=h.REPO, text=True).strip()
entry = f'''

## D305-D307 / E124 guarded normal RN-FTZ division - native mechanism gate not established

Previousgoalturnprogress:E123compilerresourcegateclosed,liveUI/menuverified,D304recovered160dates/20scoresin161originalrows plusoneCSSwraprule;everyexistingdatafield/sourcepreserved. Currentaccepted/main/live/protected2PTX/idle/locks/researchHEAD/D304HTMLSHA revalidated; no create-onlyauditoverwritten or native resumed/repeated. LastprimaryB377/nextB378. CPUencoderD014/E012/E013/D019andclosedcache/scope forms remainclosed,no hardwarecounterretry.

D305bounded143uniqueCUDAhashes/alllocalrefrevisions findsno div.rn.ftz.f32 form. Nativeper-quotientRNdivision retains independent quotientwork, unlikeclosedE060sharedreciprocal+refinement; no E101zero/E116singlepositive/E108integerdivisionhunkcomposed. NVIDIA CUDA12.9/PTX8.8 division semantics primaryURL retained inrange-contract. Fixedguard n>=2^-63,d<=2^63,n<=d implies finitepositive normalinputs andexactq in[2^-126,1],so RNoutput normal; FTZchanges neitheroperand norresult underdocumentedsemantics. Originaln/dotherwise.1764CPUboundarypairs(36eligible/1728fallback)/5exactrationalreferencefixtures/2weakened-bound counterexamples; sourcealgebranotactualGPU/compiler/fallbackNaN/speedproof. OldordinarynativeRCP/FMA/FCHKfastpath alreadyexists, so missingwork/headroomneverassumed.

FrozenoneCUDA-onlycandidate{h.sha(S/'candidate.cu')}:oneinlinehelper+2exactquotientcallreplacements reverseentireCRLFsourceexact. Originalfloatclamp/sum/consumers/uniformbranch/FMA/updates/locks/opponents/genericlogic/7otherentries/9ABIs/host/arrays/launch/shared/graphs/quality/checks/saves retained. Exact decimal2^-63/2^63constants,no globalFTZ/fastmath/approximateprimitive/denominatorreuse/zero-or-one shortcut. Resourceprotocol{h.sha(R/'protocol.json')}beforeoneRustcompiler/onemodule-onlyprocess/2NVRTC12.9targets120/75,sealedbaselinePTXreused. Allresourcegatespass;downregister40/local32/max1024/occupancy24,12,6same;upregister62->64warning/local64/max1024/occupancy16,8,4same;constant/static/dynamic0/stack1024unchanged. Same9ABIs/barriers/7untargetedbodies+actualresources.

D306all16down+12upactual120and23down+23upcompat75sites haveexactnormalguardtypedoperands/sameRNfallbackanddestination/immediatejoin;4negativefixturespass. Originalreader120passed;75explicitfallbackblock/duplicatedidenticalclampsunrecognized. Originalscript/protocol/errorretained,additivev2boundedlocal40instructionguard/12stepwalk/max-movexpression-aliasreader retainsall4sections/all74sites/bounds/gates; no source/compiler/module/native repeat. Scopedlocalproofonly,notcompleteFP/CFG/pointer/IEEEinterpreter.

D307oneownedexistingCUPTIresourcecallbackmodulecapture+one nvdisasm, accepted same-driverbaselineCUBIN/SASSreused, no newcompiler/NVRTC/applicationkernel/counter/injection/solver. All28actualFTZslowCALLsites(16down/12up) fullyaccounted againstPTXsites. Eachlocalordinary path retains1MUFU.RCP/5originaldivisionrefinementFFMAdataflowstages/FCHK/conditionalexceptionalbranch/slowCALL, as originalcommonreferencepertarget;4negativefixturespass. Requiredpredeclaredpositive ordinary-division-work-removal evidence NOTestablished. Counts are scopedstaticlocaldependencywindows,notglobaldynamiccounts/numericalperformance/ABI/CFG/IEEEproof/universalno-speedupclaim. Corepresenceisnotmeasuredregression;noapplicationkernels/numerical/CFR/ordinary/primary/fresh16/rawengine/canonical/broad/material/holdout/cumulative/actualapp progression afterfailure.

REJECT/CLOSEexactE124fixedbounds/guard/asmconstraint/architecture/kernel-subset/arity/helper/flags/width/source/quality/sampleform,no rescue. Source/PTX/CUBIN/SASS/rawmodulemarkers/allobserverversions retainedX. All4ownedcompiler/module/capture/disassemblyreceipts terminal0,locksabsent,accepted/main/live/protected2PTXandD304HTMLunchanged. {len(published)}artifactsHTTPbyteverified,closure{H/'report.json'}. E080/GPU/compressed/16/defaultaffinity qualified/live,RAMreference10456.4109msseparate,newadoptedgain0,lastB377/nextB378. AllnewbulkX/Sreadonly/noT,ledgerprefixbyteexact/localledger-onlycommit/nopush;goalactive.
'''
ledger.write_bytes(prefix + entry.encode())
assert ledger.read_bytes()[:len(prefix)] == prefix
h.custody()
subprocess.run(['git', 'add', '--', 'research/postflop-gpu-20261016/experiments.md'], cwd=h.REPO, check=True)
assert subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=h.REPO, text=True).splitlines() == ['research/postflop-gpu-20261016/experiments.md']
subprocess.run(['git', '-c', 'gc.auto=0', 'commit', '-m', 'research: close guarded RN-FTZ division at native mechanism gate'], cwd=h.REPO, check=True)
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=h.REPO, text=True).strip()
h.save(H / 'publication.json', {'at': h.now(), 'local_commit': head, 'HTTP_artifacts': published, 'report_sha256': h.sha(H / 'report.json'),
    'all_owned_children_terminal': True, 'candidate_adopted': False, 'goal_active': True})
h.custody()
assert not subprocess.check_output(['git', 'diff', '--name-only', 'HEAD'], cwd=h.REPO, text=True).strip()
assert not subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=h.REPO, text=True).strip()
h.pin(h.ar.DASHBOARD / 'index.html', h.read(ROOT / 'runs/D304-tracker-display-metadata/layout-fix.json')['after_sha256'])
for path, url in [(h.ar.STATUS, 'status.json'), (h.ar.DASHBOARD / 'index.html', 'index.html'), (H / 'report.json', 'evidence/E124-native-closure/report.json')]:
    with urllib.request.urlopen(h.ar.LIVE + '/research/postflop-gpu-20261016/' + url, timeout=20) as response:
        assert response.read() == path.read_bytes()
process = json.loads(subprocess.check_output(['powershell', '-NoProfile', '-Command', "Get-CimInstance Win32_Process -Filter 'ProcessId = 26528' | Select-Object ProcessId,ExecutablePath | ConvertTo-Json -Compress"], text=True))
assert process['ExecutablePath'].lower() == r'X:\Dev\GTOpen\target\desktop-runtime\release\gto-server.exe'.lower()
h.ar.refuse_active(h.ar.live_status())
assert not (ROOT / 'gpu-run.lock').exists() and not (ROOT / 'epoch-sequence.lock').exists()
h.save(H / 'terminal-audit.json', {'at': h.now(), 'status': 'E124_CLOSED_ALL_OWNED_WORK_TERMINAL', 'child_receipts_terminal0': len(receipts),
    'local_ledger_commit': head, 'research_tracked_diff_clean': True, 'accepted_main_live_protected_PTX_D304_HTML_exact': True,
    'HTTP_status_index_checkpoint_exact': True, 'live_pid': 26528, 'server_idle': True, 'locks_absent': True,
    'new_numerical_application_kernel_solver_or_speed_trials': 0, 'new_adopted_gain': False,
    'last_primary_baseline': 'B377', 'next_unused_primary_baseline': 'B378', 'X_free_bytes': shutil.disk_usage(ROOT).free,
    'all_new_bulk_X_S_readonly_no_T': True, 'goal_active': True})
print(json.dumps(h.read(H / 'terminal-audit.json')), flush=True)
