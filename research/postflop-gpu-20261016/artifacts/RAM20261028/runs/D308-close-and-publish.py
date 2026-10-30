"""Close the packed primitive after complete native arithmetic accounting."""
import collections, json, re, shutil, subprocess, sys, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
H = ROOT / 'runs/D308-packed-arithmetic'
h.custody()
h.ar.refuse_active(h.ar.live_status())
assert not (ROOT / 'gpu-run.lock').exists() and not (ROOT / 'epoch-sequence.lock').exists()
for protocol in [H / 'protocol.json', H / 'reader-protocol-v2.json']:
    for path, digest in h.read(protocol)['input_sha256'].items():
        h.pin(path, digest)
resource, capture, native = [h.read(H / name) for name in ['resource-report.json', 'capture-report.json', 'native-report.json']]
assert resource['all_gates_pass'] and all(resource['gates'].values())
assert capture['application_kernel_launches'] == capture['solver_or_speed_runs'] == 0
assert native['status'] == 'decline_fixed_packed_form_scalarized_to_original4_FP_sites'
assert native['applicationkernels_numerical_solver_or_speed_samples'] == 0 and not native['solver_candidate_admitted']
assert len(native['negative_reader_fixtures_rejected']) == 4
rows = [json.loads(line.split('D308_RESOURCE ', 1)[1]) for line in (H / 'execution/probe.stdout.log').read_text(encoding='utf-8').splitlines() if 'D308_RESOURCE ' in line]
assert len(rows) == 21 and rows[:-1] == resource['resource_rows']
assert rows[-1] == {'stage': 'complete', 'candidate_NVRTC_compiles': 1, 'resource_rows': 20, 'application_kernel_launches': 0, 'device_array_allocations': 0, 'solver_or_speed_runs': 0}
prefix = (H / 'accepted.cu').read_bytes()
assert prefix == (h.REPO / 'crates/solver/src/gpu/kernels.cu').read_bytes()
assert (H / 'module.cu').read_bytes()[:len(prefix)] == prefix
independent = {}
for name, record in capture['sections'].items():
    path = Path(record['path'])
    h.pin(path, record['sha256'])
    ops = [match[1] for match in re.finditer(r'/\*[0-9a-f]+\*/\s*(.*?)\s*;\s*/\*', path.read_text(encoding='utf-8'))]
    floating = [op for op in ops if re.sub(r'^@!?P\d+ ', '', op).startswith('F')]
    inventory = collections.Counter(op.split()[0] for op in floating)
    assert inventory == {'FADD': 2, 'FFMA': 2}
    assert not any('CALL' in op for op in ops)
    assert native['witnesses'][name]['FP_arithmetic_sites'] == 4
    independent[name] = {'FP_inventory': dict(inventory), 'all_native_FP_instructions': floating,
                         'same4_scalar_arithmetic_sites': True, 'all_native_function_FP_sites_accounted': True}
receipts = []
for path in (H / 'execution').rglob('*.exit.json'):
    receipt = h.read(path)
    assert receipt['returncode'] == 0 and receipt['error'] is receipt['cleanup'] is None
    receipts.append({'path': str(path), 'sha256': h.sha(path), 'returncode': 0})
assert len(receipts) == 4
h.save(H / 'report.json', {'id': 'D308', 'at': h.now(), 'status': 'DECLINE_CLOSE_FIXED_PACKED_ACTION_ARITHMETIC_NATIVE_SCALARIZATION',
    'history_sha256': h.sha(H / 'history.json'), 'source_contract_sha256': h.sha(H / 'source-contract.json'),
    'module_source_sha256': h.sha(H / 'module.cu'), 'original9kernel_source_prefix_byteexact': True,
    'resource_report_sha256': h.sha(H / 'resource-report.json'), 'native_report_sha256': h.sha(H / 'native-report.json'),
    'independent_native_FP_inventory': independent,
    'resource_summary': 'All9originalnormalizedPTX/bodies/resources unchanged. Scalar/packed diagnostics each24registers/local0/static0/dynamic0/constant0/max1024/occupancy64,128,256=24,12,6/stack1024.',
    'decision': 'VirtualFP32x2sub/FMA accepted byNVRTC12.9 forcompute120, buttestedRTX5090/driver610.88 emits2scalarFADD+2scalarFFMA inbothprimitiveentries. RequiredfewerissuedFParithmetic sites perpair notestablished. Closebefore solverprototype/applicationkernels/numerical/speedtests. Notmeasuredregression/universal scalarization/throughputclaim.',
    'numerical_scope': 'No GPU outputs evaluated; CPU169specialwordpair packing checks only. Native subtraction operand order differs; no IEEE/NaNpayload equivalence claimed. OriginalCFR/live source unchanged.',
    'reader_preflight': 'V1 positive parser strips reusehints but negative literalmutation wouldretainhint in rawtext; detectedbefore V1execution. AdditiveV2 normalizesonlynegativefixturetext,allpositiveoriginalfiles/gatesunchanged. Originalscript/protocol/preflightretained; V2passes4corruptionfixtures; no native/compiler repeat.',
    'full_solver_candidate_admitted': False, 'next_unused_candidate': 'E125',
    'closed_form': 'Fixedtwo-action packedFP32SUB/FMA, no width/handpair/placement/guard/helper/flags/scope/source/precision/sample rescue. No FP16/BF16/TF32 substitution.',
    'child_receipts': receipts, 'all_owned_children_terminal': True, 'new_Rust_compilers': 1, 'new_NVRTC_compiles': 1,
    'application_kernel_launches': 0, 'explicit_device_array_allocations': 0, 'solver_or_speed_samples': 0,
    'accepted_main_live_protected_PTX_D304_HTML_unchanged': True, 'last_primary_baseline': 'B377', 'next_unused_primary_baseline': 'B378',
    'all_new_bulk_X_S_readonly_no_T': True, 'candidate_adopted': False, 'goal_active': True})
files = [H / name for name in ['history.json', 'source-contract.json', 'source-manifest.json', 'protocol.json', 'accepted.cu', 'module.cu', 'resource-report.json', 'capture-report.json', 'reader-protocol.json', 'reader-preflight-v1.json', 'reader-protocol-v2.json', 'native-report.json', 'report.json']]
files += [Path(record['path']) for record in capture['sections'].values()]
files += [H / 'execution' / name for name in ['rustc.invocation.json', 'rustc.exit.json', 'probe.invocation.json', 'probe.exit.json', 'probe.stdout.log']]
files += [H / 'execution/capture' / name for name in ['capture.invocation.json', 'capture.exit.json', 'disassemble.invocation.json', 'disassemble.exit.json']]
published = []
for path in files:
    relative = Path(H.name) / path.relative_to(H)
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
    e = next(row for row in status['experiments'] if row['id'] == 'D308')
    e.update(at=h.now(), status='rejected', accepted=False, stage='Closed: packed arithmetic scalarized on tested GPU',
             correctness='source_and_native_structure_only',
             reason='Bothprimitives emit2scalarFADD+2scalarFFMA. Nativearithmetic-saving gate failed; no solvercandidate, GPU numerical orspeed run. All9originalCUDAentries/resources unchanged; originalsource/liveE080 preserved. Notmeasured performance regression.')
    e['evidence'] += [{'label': 'All primitive native arithmetic/dataflow', 'url': 'evidence/D308-packed-arithmetic/native-report.json'},
                      {'label': 'Root replay and closure', 'url': 'evidence/D308-packed-arithmetic/report.json'}]
    status.update(updated_at=h.now(), state='running', goal_status='active', active_experiment='D308', stage='Packed arithmetic lead closed; distinct performance search continues',
                  activity='FP32x2primitive scalarizes to same4nativearithmetic sites ontestedRTX5090. No solvercandidate orspeedgain. E080/GPU/compressed/16 remains qualified/live; nextcandidateE125/nextprimaryB378 unused.')
    h.ar.atomic_json(h.ar.STATUS, status)
ledger = h.REPO / 'research/postflop-gpu-20261016/experiments.md'
old = ledger.read_bytes()
assert b'\n## D308 packed two-action FP32 arithmetic capability' not in old
assert not subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=h.REPO, text=True).strip()
entry = f'''

## D308 packed two-action FP32 arithmetic capability - scalarized, no solver candidate

Previousgoalturnprogress:E124source/range/resource/PTX/nativeall28coreschecked, closedrequirednativeworkremovalnotestablished;4ownedchildren terminal0. Thisturnaccepted/main/live/protected2PTX/idle/locks/ledgerHEAD/D304HTMLSHA revalidated withoutcreate-onlyauditrerun. LastB377/nextB378,E080qualified/live. No closedE099adjacent-handmemory/E114twohandchance/E005/E014arity/E060/E124divisionforms composed/reopened, no hardwarecounterretry.

D308bounded144uniqueCUDAhashes/alllocalrefrevisions findsnorecognizedsub/fma.f32x2form. NewconceptpairsindependentACTIONupdates r*d+(v-out) inregisters,not twohandmemory. PrimaryCUDA12.9/PTX8.8sub/FMAsemantics reviewed:percomponentRN/noFTZ/subnormal/fullFP32; ISAavailabilitynotnativeissued-speedproof. CPU169specialwordpair bitpack/unpackchecks plusalgebra preservelow/highu32bits,notGPUaccuracyproof. ExistingbaselineCFRPTXshows scalarSUBthenRNFMAregretstores. Exactaccepted9kernelCUDAprefix+2diagnosticentries only; no fullsolverprototype(E125notadmitted),host/arrays/launch/quality/save/sourcechange. Fixedprefix{h.sha(H/'accepted.cu')},module{h.sha(H/'module.cu')}. Prospectiveprotocol{h.sha(H/'protocol.json')} requires actualfewer-than4nativeFPsites/pair,not merelyvirtualpackedopcode;oneorboth packedoperationscouldqualifyifreal.

OneRustcompiler/oneNVRTC12.9compute120modulecompile,acceptedbaselinePTXreused. Baseline9+diagnostic11resourcerows/all21markers pass; alloriginal9normalizedheaders/bodies/resourcesexact. Newscalar/packedkernelseach24regs/local0/shared0/constant0/max1024/64,128,256occupancy24,12,6/stack1024. No explicitGPUarrays/applicationkernels/solver/numerical/speedtrial. OneexistingownedCUPTIresourcecallbackmodulecapture+one nvdisasm,11entrymodulecontainsbothprimitivearms; original9functionqueries retained,1ownedmodule/0callbacks errors/0kernel launches. SameRTX5090UUID/driver610.88matchespinnedbaseline.

Bothcompletevalid-thread nativepathsaccountedeveryFPinstruction:2plainFADD withcommonsubtrahend,2plainFFMA consumingbothdistinctdeltas,2scalaroutputstoresbase+0/+4; nohiddenFP/branch/call beforeterminalEXIT. PackedvirtualSUB/FMA scalarizes,4issuedarithmeticsites versusreference4. Fourcorruptionfixtures(missingFMA/FTZopcode/wrongoutputoffset/crosscomponentdelta)reject;rootindependentfullFP-opinventoryagrees. Subtractionoperandorderdiffersbetweenlowerings;no IEEE/NaNpayload/numericalequivalenceclaimed. Readerpreflightdetectedignored.reusehints wouldbreaknegative literalmutationbeforeV1execution;originalreader/protocolretained,V2normalizesonlynegativefixturetext,allpositivecapturedfiles/gatesunchanged,no compiler/native repeat.

DECLINE/CLOSEfixedtwo-actionpackedFP32SUB/FMAform atnativecapabilitygate. No width/handpair/placement/guard/helper/flags/scope/source/precision/sample rescue orreducedprecision substitution. No E125CFRsource/ordinary/GPUraw/engine/canonical/primary/fresh16/broad/material/holdout/cumulative/app trial; notmeasuredregression/numericalpass/universalGPUscalarization/throughputclaim. Rawsource/PTX/CUBIN/SASS/modulemarkers/readerversions retainedX;{len(published)}artifactsHTTPbyteverified. All4ownedchildren terminal0,locksabsent,accepted/main/live/protected2PTX/D304HTMLexact. No newgainadopted,E080/GPU/compressed/16/defaultaffinitylive,RAMreference10456.4109msseparate,lastB377/nextB378,nextcandidateE125unused. AllnewbulkX/Sreadonly/noT,ledgerprefixbyteexact/localledger-onlycommit/nopush;goalactive.
'''
ledger.write_bytes(old + entry.encode())
assert ledger.read_bytes()[:len(old)] == old
h.custody()
subprocess.run(['git', 'add', '--', 'research/postflop-gpu-20261016/experiments.md'], cwd=h.REPO, check=True)
assert subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=h.REPO, text=True).splitlines() == ['research/postflop-gpu-20261016/experiments.md']
subprocess.run(['git', '-c', 'gc.auto=0', 'commit', '-m', 'research: close packed FP32 primitive at native capability gate'], cwd=h.REPO, check=True)
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=h.REPO, text=True).strip()
h.save(H / 'publication.json', {'at': h.now(), 'local_commit': head, 'HTTP_artifacts': published, 'report_sha256': h.sha(H / 'report.json'), 'goal_active': True})
h.custody()
assert not subprocess.check_output(['git', 'diff', '--name-only', 'HEAD'], cwd=h.REPO, text=True).strip()
assert not subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=h.REPO, text=True).strip()
h.pin(h.ar.DASHBOARD / 'index.html', h.read(ROOT / 'runs/D304-tracker-display-metadata/layout-fix.json')['after_sha256'])
for path, url in [(h.ar.STATUS, 'status.json'), (h.ar.DASHBOARD / 'index.html', 'index.html'), (H / 'report.json', 'evidence/D308-packed-arithmetic/report.json')]:
    with urllib.request.urlopen(h.ar.LIVE + '/research/postflop-gpu-20261016/' + url, timeout=20) as response:
        assert response.read() == path.read_bytes()
process = json.loads(subprocess.check_output(['powershell', '-NoProfile', '-Command', "Get-CimInstance Win32_Process -Filter 'ProcessId = 26528' | Select-Object ProcessId,ExecutablePath | ConvertTo-Json -Compress"], text=True))
assert process['ExecutablePath'].lower() == r'X:\Dev\GTOpen\target\desktop-runtime\release\gto-server.exe'.lower()
h.ar.refuse_active(h.ar.live_status())
assert not (ROOT / 'gpu-run.lock').exists() and not (ROOT / 'epoch-sequence.lock').exists()
h.save(H / 'terminal-audit.json', {'at': h.now(), 'status': 'D308_CLOSED_ALL_OWNED_WORK_TERMINAL_NO_SOLVER_CANDIDATE',
    'child_receipts_terminal0': len(receipts), 'local_ledger_commit': head, 'research_tracked_diff_clean': True,
    'accepted_main_live_protected_PTX_D304_HTML_exact': True, 'HTTP_status_index_report_exact': True,
    'live_pid': 26528, 'server_idle': True, 'locks_absent': True, 'new_application_kernel_numerical_solver_or_speed_trials': 0,
    'new_adopted_gain': False, 'next_unused_candidate': 'E125', 'last_primary_baseline': 'B377', 'next_unused_primary_baseline': 'B378',
    'X_free_bytes': shutil.disk_usage(ROOT).free, 'all_new_bulk_X_S_readonly_no_T': True, 'goal_active': True})
print(json.dumps(h.read(H / 'terminal-audit.json')), flush=True)
