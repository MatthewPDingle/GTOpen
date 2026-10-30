"""Preserve all exact controls and publish the first complete-solve decision."""
import json
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h

h.custody()
h.ar.refuse_active(h.ar.live_status())
assert not (ROOT / 'gpu-run.lock').exists() and not (ROOT / 'epoch-sequence.lock').exists()
Q = ROOT / 'comparisons/E121-three-pair-comparison/report.json'
A = ROOT / 'comparisons/E121-root-crosscheck/report.json'
P = ROOT / 'runs/E121-primary-plan/protocol.json'
q, a, plan = h.read(Q), h.read(A), h.read(P)
perf = q['performance']
passed = perf['primary_timing_pass']
assert a['aggregate_gain_pct'] == perf['observed_gain_pct']
assert a['status'] == ('pass_initial_timing_only' if passed else 'pass_rejected')
assert q['exactness'] == {'fixture_results': 18, 'convergence_records': 138, 'all_exact': True}
assert q['ordinary_units_passed'] == 86 and q['ordinary_units_ignored'] == 4
assert not q['excluded_samples']
assert q['extension_runs'] == q['historical_timing_samples_used'] == q['RAM_baseline_samples_scored'] == 0
assert h.read(ROOT / 'runs/E121-primary-wrapper/complete.json')['all_owned_children_terminal']
F = ROOT / 'comparisons/D298-hand-word-fold/report.json'
G = ROOT / 'comparisons/E121-kernel-control-root-check/report.json'
fold, show = h.read(F), h.read(G)
assert fold['status'] == 'pass_scoped_encoded_input_full_raw_equivalence'
assert fold['cases'] == 380 and fold['kernel_launches'] == 760
assert fold['every_physical_input_checked_against_declared_encoding']
assert show['status'] == 'pass_scoped_encoded_hand_word_full_raw_equivalence'
assert show['inventory']['comparison_pairs'] == 13300 and show['kernel_launches'] == 26600
assert show['all21_input_buffers_fully_checked'] and show['encoded_same_all_words_checked_and_decoded']
assert h.read(ROOT / 'runs/E121-direct-owner/complete.json')['all_owned_children_terminal']
manifest = h.read(ROOT / 'runs/E121-source/manifest.json')
for record in manifest['owned'].values():
    h.pin(record['base'], record['base_sha256'])
    h.pin(record['candidate'], record['candidate_sha256'])
fold_raw = h.read(ROOT / 'runs/D298-hand-word-fold/execution/complete.json')['raw_file_sha256']
show_complete = h.read(ROOT / 'runs/E121-show-control/execution/complete.json')
show_raw = ROOT / 'runs/E121-show-control/execution/raw-results.jsonl'
assert show_raw.stat().st_size == show_complete['raw_bytes']
assert show_complete['raw_sha256'] == show['raw_sha256']
receipts = []
for name in ['E121-resource/execution', 'D297-hand-word-native/execution', 'D298-hand-word-fold/execution',
             'E121-show-control/execution', 'E121-direct-execution', 'E121-direct-owner',
             'E121-final-build', 'E121-primary-execution', 'E121-primary-wrapper']:
    for path in (ROOT / 'runs' / name).rglob('*.exit.json'):
        receipt = h.read(path)
        assert receipt['returncode'] == 0 and receipt.get('error') is None and receipt.get('cleanup') is None
        receipts.append({'path': str(path), 'sha256': h.sha(path), 'returncode': 0})
H = ROOT / 'runs/E121-primary-checkpoint'
H.mkdir(exist_ok=False)
reason = (f"Complete-solve medians total {perf['baseline_full_cycle_ms']:.4f} to {perf['candidate_full_cycle_ms']:.4f} ms: "
          f"{perf['observed_gain_pct']:.6f}% observed gain. " +
          ('Initial screen passed. Separate fresh16 and full raw engine/canonical/broad/material/holdout/current-RAM cumulative/app qualification remain before adoption.' if passed else
           'The fixed form failed the 1% or strict fixture guard and is closed without source variants or extra samples.'))
state = 'INITIAL_SPEED_PASS_FULL_QUALIFICATION_PENDING' if passed else 'REJECTED_CLOSED_TERMINAL_HAND_WORD_FORM'
h.save(H / 'report.json', {
    'id': 'E121-primary-checkpoint', 'at': h.now(), 'status': state, 'measurement_epoch': 'RAM20261028',
    'fixed_source': manifest['owned'],
    'prerequisites_sha256': h.sha(ROOT / 'runs/E121-prerequisite-checkpoint/report.json'),
    'change': 'Private terminalword(card1low6/card2next6/matchindexupper11/2047absent) in existing d_same[0/1]. Sameu32arraylengths/ABIs/publicplan and allotherphysicalmetadata. Hostconstructor2temporaryVecs, fold/show1packedwordload replaces2cardloads+matchingindexload. All original floatingexpressions/order/barriers/launch/quality/cadence retained.',
    'resource_warning': 'Showregister38to39;fold39unchanged,local0/staticshared/dynamic/stack/maxthreads/worst64/128/256occupancyunchanged. Hosttemporarypayload<=10608B+headers/allocator/drop, actualpacking/lifetimes/cleanup/capacity/materialeffects remainunqualified.',
    'compiled_scope': 'Prioractualcompiledhost1759602legaltuples+3978mixedrecords/28217307rawbytes/8817900checks. D296four120/75PTXload/decode/sentinel/byteoffset/originalmath-selectregistertopology/barrierwitnesses and21162960compiled-addresschecks;20negativefixtures. D297fixed-drivernativeword/decode/consumer/oldcardpointerrangesabsent,8negativefixtures. Bounded readers, notuniversalABI/memory/FPinterpreter. No counters or speed from these prerequisites.',
    'fold_control': {'cases': fold['cases'], 'kernel_launches': fold['kernel_launches'], 'checks': fold['checks'],
                     'output_words_both_arms': fold['output_words_both_arms'], 'immutable_words_both_arms': fold['immutable_words_both_arms'],
                     'guard_words_both_arms': fold['guard_words_both_arms'], 'raw_files_sha256': fold_raw,
                     'scope': 'Original360cases/34scenarios retained, add20cases/2scenarios alternating c1/c2/same tupleboundaries(0,1,0)/(50,51,1325)/(0,51,absent), bothplayers/allfive16..256widths/base17shift preserved. Candidateonlysamevalidprefix packed;empty/dummy/padding unchanged. Everyphysicalword checked+decoded,other13buffers/wholeoutputs/guards exact.'},
    'show_control': {'inventory': show['inventory'], 'kernel_launches': show['kernel_launches'], 'checks': show['checks'],
                     'raw_path': str(show_raw), 'raw_bytes': show_complete['raw_bytes'], 'raw_sha256': show['raw_sha256'],
                     'scope': 'EntireoriginalE1202636cases/244physicalgeometries retained;24addedunit/subnormal single-opponent reachcases atphysical/511/1023extrema.2660cases x5widths1/32/64/128/256.21completeactualinputbuffers,allencodedwords expected+decoded,other20literalidentical;wholeCFV/guards/NaNbits exact. Originalacceptedrankoracle/anti-vacuity/2roundingwitnesses retained.'},
    'direct_preparation_repair': 'Originalpreparer stoppedbeforeprotocol/compiler/native because comparison_pairs literal appears in twoexistingmarkers, strict once assertion rejected2matches. R2 requires exactly2for thatliteral/1forothers and updatesboth tosameprospectivecount. Existingstaging reusedbyteexact;candidate/corpora/gatesunchanged;original+repair retained. No native repeat or scientificfailure rescue.',
    'raw_not_rehashed_after_complete_readers': True,
    'direct_accuracy_scope': 'Finite isolatedterminalcontrols only, not fullsolver/rawengine/canonical/broader equivalence. Every declaredphysicalencodedmetadataword accounted, no omittedfield/padding/tolerance.',
    'two_fresh_integrated_ordinary_builds_include_actual_NVRTC_JIT': True,
    'ordinary_units_passed': 86, 'ordinary_units_ignored': 4,
    'performance': perf, 'fixtures': q['fixtures'], 'exactness': q['exactness'],
    'primary_protocol_sha256': h.sha(P), 'comparison_sha256': h.sha(Q), 'root_replay_sha256': h.sha(A),
    'full_raw_engine_canonical_broad_material_completed': False,
    'remaining_qualification_requirements': plan['adoption_requirements'] if passed else [],
    'child_receipts': receipts, 'all_owned_work_terminal': True, 'locks_absent': True,
    'accepted_main_live_protected_PTX_unchanged': True, 'candidate_adopted': False,
    'reason': reason, 'extra_or_rescue_samples': 0, 'last_primary_baseline': 'B374', 'next_unused_primary_baseline': 'B375',
    'best_qualified_config': 'E080/GPU/compressed/16workers/defaultaffinity', 'hardware_epoch_baseline_ms': 10456.4109,
    'historical_or_RAMtimings_scored': 0, 'all_new_bulk_X_S_readonly_noT': True, 'goal_active': True
})
sources = [F, G, ROOT / 'runs/E121-source/manifest.json', ROOT / 'runs/E121-resource/report.json',
           ROOT / 'runs/E121-resource/host-encode-report.json', ROOT / 'runs/D296-hand-word-PTX/report.json',
           ROOT / 'runs/D297-hand-word-native/report.json', ROOT / 'runs/E121-prerequisite-checkpoint/report.json',
           ROOT / 'runs/E121-direct-preparation-repair/report.json', ROOT / 'runs/E121-direct-plan/protocol.json',
           ROOT / 'runs/D298-hand-word-fold/protocol.json', ROOT / 'runs/D298-hand-word-fold/preparation.json',
           ROOT / 'runs/D298-hand-word-fold/execution/reader-complete.json',
           ROOT / 'runs/E121-show-control/protocol.json', ROOT / 'runs/E121-direct-execution/complete.json',
           ROOT / 'runs/E121-direct-owner/complete.json', ROOT / 'runs/E121-build-plan/protocol.json',
           ROOT / 'runs/E121-final-build/complete.json', P, Q, A, H / 'report.json']
published = []
for path in sources:
    key = (path.relative_to(ROOT / 'runs') if path.is_relative_to(ROOT / 'runs') else path.relative_to(ROOT / 'comparisons')).as_posix()
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
    experiment.update(status='running' if passed else 'rejected', accepted=False,
                      stage='Initial pass; separate full qualification pending' if passed else 'Closed: complete-solve screen rejected',
                      correctness='13680directpairs/27360launches and86ordinaryunits pass;fullscience/checkpoints exact,broaderraw/material unverified',
                      performance=perf, reason=reason)
    experiment['evidence'] += [{'label': 'Complete-solve initial comparison', 'url': 'evidence/' + Q.parent.name + '/report.json'},
                              {'label': 'Independent full-log and median replay', 'url': 'evidence/' + A.parent.name + '/report.json'},
                              {'label': 'All direct controls and checkpoint', 'url': 'evidence/' + H.name + '/report.json'}]
    status.update(updated_at=h.now(), state='running', goal_status='active', active_experiment='E121',
                  stage='Terminal hand words: full qualification next' if passed else 'Terminal hand-word form closed; next distinct lead',
                  activity=reason + ' E080 remains the qualified live version; no gain adopted.')
    h.ar.atomic_json(h.ar.STATUS, status)
ledger = h.REPO / 'research/postflop-gpu-20261016/experiments.md'
prefix = ledger.read_bytes()
assert b'\n## E121 complete direct terminal and first speed decision' not in prefix
assert not subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=h.REPO, text=True).strip()
entry = f'''

## E121 complete direct terminal and first speed decision - {'initial pass, full qualification pending' if passed else'rejected and closed'}

PreviousgoalturnE121compiledhost/resources/D296PTX/D297native prerequisitespassed,terminalaudit41dc5db0/custody/idle/locks revalidated. Samefixed2filehandword source, CUDA{manifest['owned']['crates/solver/src/gpu/kernels.cu']['candidate_sha256']},Rust{manifest['owned']['crates/solver/src/gpu/mod.rs']['candidate_sha256']}; no mask/sentinel/placement/helper/source/width/flags/quality changes. Publicplan/globalarrays/ABIs/floatingexpressions/order/barriers unchanged;only private d_same[0/1] physicalcontents encodeoriginal3metadatafields. Register38->39showwarning/39fold unchanged;actualhosttemporary/packing/drop/JIT/materialeffectsremainreal.

FrozenD298foldoriginal360cases/34scenarios unchangedprefix plus20boundarycases/2clones containing(0,1,0),(50,51,1325),(0,51,absent)throughvalidownspan,originalbase17andbothplayers/all5widths16/32/64/128/256. Onecompiler/native/fullreader:380pairs/760launches,{fold['checks']}checks,{fold['output_words_both_arms']}wholeoutputwords,{fold['immutable_words_both_arms']}actualimmutablewords,{fold['guard_words_both_arms']}guards exact. Onlycandidate samevalidprefix encoded;allphysicalwords independentlyexpected/decoded,empty/dummy/padding unchanged,other13buffers exact. Complete5rawfiles retainedX withchecksums,wholeoutputfilesbyteequal;no inputfieldomission/tolerance.

FrozenE121show entireE1202636cases/244physicalgeometries unchangedprefix;24addedunit/subnormal singleopponent reaches atphysicalrange/511/1023extrema,bothplayers/boards. Onecompiler/native/fullreader:2660casesx5widths1/32/64/128/256=13300pairs/26600launches;inventory{json.dumps(show['inventory'])},{show['checks']}readerchecks. All21completeactualinputs checked;oneencoded samebuffer everywordexpected+decoded,other20literalidentical;wholephysicalCFV/guards/nonfinitebits exact. Originalrankoracles/anti-vacuity/2roundingwitnesses retained. Showraw{show_complete['raw_bytes']}bytes/SHA{show['raw_sha256']}retainedX;finitecorpus only, notfullengine/canonical/universalFPclaim.

Preparerfirstsafeassertion exitedbeforeprotocol/compiler/native at twoexisting comparison_pairs markerliterals;R2requires exactly2replacementsthere/1elsewhere, reusesexistingstagingbyteexact. Samecandidate/corpora/numericalgates;originalpreparer/staginghashes/repairretained. No completednative repeat/source or scientificfailure rescue. Allencode/rawcontrol clocks unscored. Twofreshordinaryoffline/lockedfeature/primaryintegratedCargobuilds includeactualNVRTC12.9/JIT andnewhostpacking;acceptedCUDA+Rustrestoredaftereach.86ordinaryunits/4ignoredpass.

FrozenB372/E121R1,E121R2/B373,B374/E121R3 once;18whole scientificrecords/138checkpoints exact. Sumfixturemedians{perf['baseline_full_cycle_ms']:.10f}->{perf['candidate_full_cycle_ms']:.10f}ms,unroundedgain{perf['observed_gain_pct']:.12f}%,initialpass={passed},strictguards={json.dumps(perf['fixture_regression_guard'])}. Separatefull-log/record/sortedmedianreplayagrees. Noexclusions/extensions/historical/RAMbaselinepooling/significanceclaim. {reason} {'Fullrawengine/canonical/broad/material/fresh16/holdout/currentRAMcumulative/actualappstillrequired;everychangedprivatemetadatawordmustbedecoded,no arrays/CFVpaddingomitted.' if passed else'Closeexactencoding/source/sentinel/masks/width/architecture/helper/flags/quality/sampleform,no rescuevariant. Fullrawengine/canonical/broad/material notrun afterspeedclosure andneverclaimed.'}

All{len(receipts)}ownedcompiler/native/reader/build/primaryreceipts terminal0;locksabsent,accepted/main/live/protected2PTXexact. AllnewbulkX/Sreadonly/noT;E080/GPU/compressed/16/defaultaffinity qualified/live,newadoptedgain0,RAMreference10456.4109ms separate,lastprimaryB374/nextB375. {len(published)}artifactsHTTPbyteverified;checkpoint{H}. Priorledgerprefixbyteexact/localledger-onlycommit/nopush,goalactive.
'''
ledger.write_bytes(prefix + entry.encode())
assert ledger.read_bytes()[:len(prefix)] == prefix
h.custody()
subprocess.run(['git', 'add', '--', 'research/postflop-gpu-20261016/experiments.md'], cwd=h.REPO, check=True)
assert subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=h.REPO, text=True).splitlines() == ['research/postflop-gpu-20261016/experiments.md']
subprocess.run(['git', '-c', 'gc.auto=0', 'commit', '-m', 'research: measure packed terminal hand metadata complete solves'], cwd=h.REPO, check=True)
with urllib.request.urlopen(h.ar.LIVE + '/research/postflop-gpu-20261016/status.json', timeout=20) as response:
    assert response.read() == h.ar.STATUS.read_bytes()
h.save(H / 'publication.json', {'at': h.now(), 'local_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=h.REPO, text=True).strip(),
                               'HTTP_byte_verified': published, 'report_sha256': h.sha(H / 'report.json'), 'candidate_adopted': False, 'goal_active': True})
h.custody()
print(json.dumps({'status': state, 'gain_pct': perf['observed_gain_pct'], 'primary_pass': passed, 'candidate_adopted': False}), flush=True)
