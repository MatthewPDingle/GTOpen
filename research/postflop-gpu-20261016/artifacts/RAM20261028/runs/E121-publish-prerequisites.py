"""Publish completed prerequisites without claiming GPU accuracy or speed."""
import json
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h

accepted = h.custody()
h.ar.refuse_active(h.ar.live_status())
assert not (ROOT / 'gpu-run.lock').exists()
assert not (ROOT / 'epoch-sequence.lock').exists()
S = ROOT / 'runs/E121-source'
R = ROOT / 'runs/E121-resource'
T = ROOT / 'runs/D296-hand-word-PTX'
N = ROOT / 'runs/D297-hand-word-native'
D = ROOT / 'runs/D295-hand-word-scout'
manifest = h.read(S / 'manifest.json')
for name, record in manifest['owned'].items():
    h.pin(record['base'], record['base_sha256'])
    h.pin(record['candidate'], record['candidate_sha256'])
    assert record['base_sha256'] == accepted[name]
resource = h.read(R / 'report.json')
host = h.read(R / 'host-encode-report.json')
ptx = h.read(T / 'report.json')
native = h.read(N / 'report.json')
assert all(resource['gates'].values())
assert host['records'] == 1763580 and host['checks'] == 8817900
assert host['legal_tuples'] == 1759602 and host['mixed_records'] == 3978
h.pin(host['raw_path'], host['raw_sha256'])
assert Path(host['raw_path']).stat().st_size == host['raw_bytes'] == 28217307
assert ptx['compiled_host_records_address_replayed'] == 1763580
assert ptx['compiled_expression_checks'] == 21162960
assert len(ptx['negative_reader_fixtures']) == 20
assert len(native['negative_reader_fixtures']) == 8
assert native['all_owned_capture_disassembly_children_terminal']
for protocol in [R / 'protocol.json', T / 'protocol.json', N / 'protocol.json', N / 'reader-protocol-r3.json']:
    for path, digest in h.read(protocol)['input_sha256'].items():
        h.pin(path, digest)

receipts = []
for folder in [R / 'execution', N / 'execution']:
    for path in folder.rglob('*.exit.json'):
        receipt = h.read(path)
        assert receipt['returncode'] == 0
        assert receipt.get('error') is None and receipt.get('cleanup') is None
        receipts.append({'path': str(path), 'sha256': h.sha(path), 'returncode': 0})
assert len(receipts) == 5
mechanical = {
    'at': h.now(),
    'source_preparer': 'Exit1 before candidate bytes at ambiguous whole-file inverse snippet shared by intended fold/show edits. R2 scopes inverse to entry and reuses immutable scout inputs. Same intended single source form; original and repair retained.',
    'resource_preparer': 'Exit1 before any compiler at generated Python reader bytes-literal newline syntax. R2 removes unnecessary generator replacements; first control probe/source and repair retained. Same candidate and intended magic bytes.',
    'PTX_reader_preparation': 'Python syntax prevented all execution before protocol; one missing token separator corrected, original script and repair retained.',
    'native_reader_original': {'tool_exit_code': 1, 'error': "unsupported constant-read spelling: @!P0 LDC.64 R2, c[0x0][0x3b8]", 'scope': 'Stopped before first completed entry witness/report.'},
    'native_reader_r2': {'tool_exit_code': 1, 'error': 'negative fixture accepted: wrong_word_load', 'cause': 'Unscoped first matching LDG string changed an earlier unrelated reach-copy load; actual required terminal word load unchanged.'},
    'native_reader_r3': {'tool_exit_code': 0, 'correction': 'Conservatively counts predicated constant ranges; negative word-load mutations anchored to required PC1530/1b50. All positive witnesses and8negative fixtures pass. Includes predicated floating ops in both-arm inventory.'},
    'candidate_source_changes_after_freeze': 0,
    'resource_or_capture_or_disassembly_repeated': False,
    'application_kernel_or_speed_results_rescued': False,
    'actual_application_kernel_solver_or_speed_samples': 0,
    'limits': 'Journal transcribes directly observed tool outcomes; it is not a fabricated subprocess receipt. Original scripts/protocols/repair records remain.'
}
h.save(N / 'reader-mechanical-outcomes.json', mechanical)

H = ROOT / 'runs/E121-prerequisite-checkpoint'
H.mkdir(exist_ok=False)
evidence = [D / 'report.json', D / 'history-and-callers.json', D / 'encoding-contract.json',
            D / 'preparation-repair-r2.json', D / 'PTX-reader-pre-exec-syntax-repair.json',
            S / 'manifest.json', R / 'protocol.json', R / 'report.json', R / 'host-encode-report.json',
            R / 'pre-compiler-packaging-repair-r2.json', R / 'execution/complete.json',
            T / 'protocol.json', T / 'report.json', N / 'protocol.json', N / 'capture-report.json',
            N / 'reader-protocol.json', N / 'reader-protocol-r2.json', N / 'reader-protocol-r3.json',
            N / 'reader-mechanical-outcomes.json', N / 'report.json']
reason = 'Compiled host encoder, resources, PTX and native load/decode prerequisites passed. No candidate GPU numerical trial or speed sample exists; full direct fold/show comparisons with independently decoded private metadata are next.'
h.save(H / 'report.json', {
    'id': 'E121-prerequisite-checkpoint', 'at': h.now(),
    'status': 'PREREQUISITES_PASS_FULL_DIRECT_GPU_CONTROLS_PENDING',
    'previous_goal_turn': 'Progress: E120 full direct/ordinary/initial-screen evidence and closure changed authoritative state. Revalidated terminal audit, local commit, idle live runtime, source/main/protected PTX and absent locks before this distinct candidate.',
    'fixed_source': manifest['owned'],
    'change': 'Private u32 hand word: card1 bits0..5/card2 bits6..11/same-opponent index bits12..22 with2047 absent. Only d_same[0/1] values change; all GPU arrays/types/lengths/launch ABIs and public plan unchanged. Host constructor packs two local Vecs; fold/show decode one metadata load. All original floating expressions/order/barriers preserved.',
    'scope_limits': 'Source/caller and compiled metadata prerequisites only. Full integrated host constructor, physical GPU numerical state, full solve, F32/locks/save/resume/continuation/material/capacity/responsiveness and speed remain unverified.',
    'host_integer_control': {key: host[key] for key in ['records', 'checks', 'legal_tuples', 'mixed_records', 'raw_path', 'raw_bytes', 'raw_sha256', 'host_function_sha256']},
    'host_cost': 'Two temporary u32 Vec payloads <=10608B at legal maximum plus headers/allocator costs; no persistent field added by source. Actual material/lifetime/error/latency qualification required.',
    'compiled_resources': {'up_fold': {'registers_before': 39, 'registers_after': 39, 'static_shared_bytes': 1232, 'worst_dynamic_bytes': 5304, 'worst_occupancy_64_128_256': [13, 12, 6]}, 'up_show': {'registers_before': 38, 'registers_after': 39, 'static_shared_bytes': 1040, 'worst_dynamic_bytes': 26520, 'worst_occupancy_64_128_256': [3, 3, 3]}, 'both': 'local0/stack1024/maxthreads1024 unchanged. Both120/75 two targeted entries change; other7 entry bodies/resources andall9ABIs exact. Register rise warning retained, not material-neutrality proof.'},
    'PTX_control': 'Four entry/target witnesses: one packed load, old card pointer dependencies absent, actual card byte offsets(left2&252/right4&252), index>>12/2047 sentinel branch, original ordered FP math/select-register topology (43fold/219show instructions) and barriers exact. All1763580compiledhostwords replay actual address expressions (21162960checks);20negative fixtures. Bounded topology omits full memory/predicate interpretation.',
    'native_control': 'One same-driver owned CUBIN module capture and one nvdisasm, exact baseline reused. Both fixed-driver word-pointer/load/card/index/sentinel/consumer chains bound; every constant-load range including predicated/128bit ranges avoids legacy card pointers. Native FP opcode/barrier inventory unchanged;8negative fixtures. Not universal ABI/pointer/FP proof, dynamic load-count or speed attribution.',
    'source_preparer_and_reader_repairs': mechanical,
    'evidence_sha256': {str(p): h.sha(p) for p in evidence},
    'owned_child_receipts': receipts, 'all_owned_work_terminal': True,
    'locks_absent': True, 'accepted_main_live_protected_PTX_unchanged': True,
    'new_application_kernel_launches': 0, 'new_solver_or_speed_samples': 0,
    'candidate_adopted': False, 'reason': reason,
    'next_required': ['Freeze complete original fold/show GPU corpora and added descriptor boundaries. Only declared per-arm same_p contents differ; compare every actual packed word and decode original cards/index, every other input and whole CFV/guards exact. No numerical tolerance or array omission.', 'Fresh integrated feature/primary builds,86ordinaryunits and initialfixed3pairfullcycle1%/strictfixture screen.', 'Full raw engine/canonical lifecycle/broader F32/locks/save/resume/symmetric/paged/stored/fallback; separately frozenfresh16; actualmaterial/capacity/holdout/freshoriginalcurrentRAMcumulative/actualapp beforeadoption.'],
    'last_primary_baseline': 'B371', 'next_unused_primary_baseline': 'B372',
    'best_qualified_config': 'E080/GPU/compressed/16workers/defaultaffinity',
    'hardware_epoch_baseline_ms': 10456.4109,
    'all_new_bulk_X_S_readonly_no_T': True, 'goal_active': True
})
evidence.append(H / 'report.json')
published = []
for path in evidence:
    key = path.relative_to(ROOT / 'runs').as_posix()
    destination = h.ar.DASHBOARD / 'evidence' / key
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        assert destination.read_bytes() == path.read_bytes()
    else:
        shutil.copyfile(path, destination)
    with urllib.request.urlopen(h.ar.LIVE + '/research/postflop-gpu-20261016/evidence/' + key, timeout=20) as response:
        assert response.read() == path.read_bytes()
    published.append({'url': 'evidence/' + key, 'sha256': h.sha(path)})

with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'), timeout=3):
    status = h.read(h.ar.STATUS)
    experiment = next(row for row in status['experiments'] if row['id'] == 'E121')
    experiment.update(status='running', accepted=False, stage='Prerequisites passed; full direct GPU controls next',
                      correctness='Compiled integer encoder and emitted-code prerequisites pass; GPU numerical accuracy unverified', reason=reason)
    experiment['evidence'] += [{'label': label, 'url': 'evidence/' + path.relative_to(ROOT / 'runs').as_posix()}
                               for label, path in [('Full host encoding domain', R / 'host-encode-report.json'),
                                                   ('PTX topology and address domain', T / 'report.json'),
                                                   ('Native instruction witnesses', N / 'report.json'),
                                                   ('Prerequisite checkpoint and limits', H / 'report.json')]]
    status.update(updated_at=h.now(), state='running', goal_status='active', active_experiment='E121',
                  stage=experiment['stage'], activity=reason + ' E080 remains live, no gain adopted.')
    h.ar.atomic_json(h.ar.STATUS, status)

ledger = h.REPO / 'research/postflop-gpu-20261016/experiments.md'
prefix = ledger.read_bytes()
assert b'\n## E121 packed terminal hand words' not in prefix
assert not subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=h.REPO, text=True).strip()
entry = f'''

## E121 packed terminal hand words - prerequisites pass, GPU correctness and speed pending

Previous goal turn E120 advanced full direct/ordinary/fixed initial screen and closed2.965667264292% aggregate gain for river3.302339510006%/2of3 guard. Its terminal audit/localcommit d7cc07ae/custody/idle/locks revalidated. D295 bounded140uniqueCUDAhashes andalllocalrefCUDA/mod history found no recognized private per-hand descriptor form; notexhaustive semantic/remotenovelty proof. E070nodeplayer/arity,E046chanceAoS,E073boundarywidth,E094nodeoffset,E048dealtcardmask/E115roworder/E120sparsecard allremainclosed;no hunkcomposed.

One fixedoff-tree2file form: CUDA {manifest['owned']['crates/solver/src/gpu/kernels.cu']['candidate_sha256']}, Rust {manifest['owned']['crates/solver/src/gpu/mod.rs']['candidate_sha256']}; wholeCRLF/LFinverses exact. Private d_same words carry card1low6/card2next6/sameindexupper11 with2047absent(u32MAXpublicsentinel); legalindices0..1325. Publicplan/Spot/save andallphysicalarraytypes/lengths/ABIs unchanged; oldcardarrays stillallocated/uploaded/passed, terminalpointees unused. Four current launch sites/common continuation wrappers forward samearrays. Two constructorlocal Vecpayloads<=10608B plusrealallocator/header/drop costs, no structfield/deviceallocation/graphnode added. Early integerreadshow replaces2cardreads and late sameindexread; samefloatingroread/payoutposition retained. No float/arithmetic/order/barrier/width/quality/cadence change. Sourcecallee/constructor/packing costs andfullphysicalmetadata safety remain integrationgates.

One Rustcompiler and one CPUintegerdomain/moduleprocess/twoNVRTC12.9targets; one independentwholeCPUrawreader. Actualcandidatehelper covers1759602legal tuples(52choose2cards x1326indices+sentinel) and3978mixedrecords/3heterogeneousvectors. All1763580quadruples/{host['raw_bytes']}bytes/SHA{host['raw_sha256']} retainedX,8817900checks; encodedVecmaxcapacity1326. Wholeactualwords decodedwithout omissions, butno GPU-floating/hostconstructor integration/speedproof. Resources pass: fold39regs/static1232/dynamic5304/occupancy64/128/256=13/12/6 unchanged; show38->39regs warning/static1040/dynamic26520/worstoccupancy3/3/3same;bothlocal0/stack1024/maxthreads1024same. Actual120/75fold/showPTXchange,7untargetedbodies/resources/all9ABIsexact. D108warningnotmaterialneutrality.

D296fouractualPTXentry/arch witnesses bind one packedload/sameparam15or19, nolegacycardparam11/12or20/21 bodydependencies, actualbyteexpressions(left2&252,right4&252),index>>12/2047 skiporiginalsharedroread. Originalorderedmath/select-registercanonicaltopology43fold/219show andbarriers exact; topologydoesnotinterpretfullmemory/predicateprovenance. All1763580retainedcompiledhostwords replayactualbyteexpressions/21162960checks;20negativefixtures pass. D297oneownedmoduleCUBINcapture/one nvdisasm, pinnedcurrent-driver acceptedbaseline reused; bothnativewordload/decode/card/index/sentinel/consumerchains match. Allconstantreadspans inclpredicated/128bit overlaps excludeoldcardpointers; nativeFPopcode/barrierinventory exact,8negativefixtures pass. Fixed-driverlocalABI/pointerwitness, notuniversalnativeinterpreter/dynamiccounters/fullIEEE/speedproof. No counters/applicationkernel/solver/performanceobservations.

Mechanical failures preserved: sourcepreparer inversecheck ambiguousshortsnippet stoppedbeforecandidatefiles; R2scopesinverseperentry withsame intendedbytes. Resourcegenerator reader-newline syntax stoppedbeforecompiler; R2removedunneededreplacement, originalgeneratedcontrolprobe preserved. PTXreader syntax stoppedbeforeanyprotocol andmissingtoken separatorcorrected. Native readeroriginal exited1 onunknownpredicatedLDC; R2conservativelycountsallpredicatedreadranges/FPops butnegativewrongwordload hit anunrelatedearliermatchingLDG. R3anchorsnegative torequiredPC1530/1b50 andallpositive+8negativechecks pass. No candidate source variant, completedresource/capture/disassembly/native/solver/speed rerun or scientificfailure rescue. Originalscripts/protocols/repairjournals retained.

{reason} Nextfreezeentireoriginalfold/showrawcorpora plusdescriptorboundaries, compareeachactualencodedwordandindependentlydecodeoriginal3fields;allotherinputs/wholephysicalCFV/guards exact, no omittedfield/padding/tolerance. Freshordinary integratedbuilds/86units/initial1%strictfixture andfullrawengine/canonical/broad/material/fresh16/holdout/currentRAMcumulative/actualappbeforeadoption remain. All5ownedcompiler/module/rawreader/capture/disassemblychildren terminal0;directobserverfailuresjournaled/terminal,locksabsent,accepted/main/live/protected2PTXexact. AllnewbulkX/Sreadonly/noT;lastprimaryB371/nextB372;E080/GPU/compressed/16/defaultaffinity qualified/live,adoptednewgain0,RAMreference10456.4109ms separate. {len(published)}artifactsHTTPbyteverified;checkpoint{H}. Priorledgerprefixbyteexact/localledger-onlycommit/nopush,goalactive.
'''
ledger.write_bytes(prefix + entry.encode())
assert ledger.read_bytes()[:len(prefix)] == prefix
h.custody()
subprocess.run(['git', 'add', '--', 'research/postflop-gpu-20261016/experiments.md'], cwd=h.REPO, check=True)
assert subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=h.REPO, text=True).splitlines() == ['research/postflop-gpu-20261016/experiments.md']
subprocess.run(['git', '-c', 'gc.auto=0', 'commit', '-m', 'research: inspect packed terminal hand metadata prerequisites'], cwd=h.REPO, check=True)
with urllib.request.urlopen(h.ar.LIVE + '/research/postflop-gpu-20261016/status.json', timeout=20) as response:
    assert response.read() == h.ar.STATUS.read_bytes()
h.save(H / 'publication.json', {
    'at': h.now(), 'HTTP_byte_verified': published,
    'local_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=h.REPO, text=True).strip(),
    'report_sha256': h.sha(H / 'report.json'), 'all_owned_work_terminal': True,
    'candidate_adopted': False, 'goal_active': True
})
h.custody()
print(json.dumps({'prerequisites': 'pass', 'GPU_numerical_trials': 0, 'speed_samples': 0, 'adopted': False}), flush=True)
