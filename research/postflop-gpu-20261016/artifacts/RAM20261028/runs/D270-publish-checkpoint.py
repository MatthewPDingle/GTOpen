"""Publish complete actual CPU replay and preserved reader/forecast failures."""
import json, shutil, subprocess, sys, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status())
assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists()
H=ROOT/'runs/D270-actual-metadata-CPU';Q=H/'root-report-r2.json';q=h.read(Q);P=h.read(H/'protocol.json');R=h.read(H/'reader-repair-protocol.json')
assert q['status']=='pass_full_actual_production_CPU_metadata_replay_corrected_reader_only'
assert len(q['cases'])==18 and q['ordered_cases']==13 and q['fallback_cases']==5 and len(q['negative_reader_fixtures'])==44
assert q['source_case_or_predicate_changes']==0 and q['original_16ordered_2fallback_forecast_not_met']and not q['original_protocol_literal_forecast_pass_claimed']
assert q['all18whole_before_plan_hashes_match_original']and q['all18after53fields_23arrays_maps_arena_records_and_capacities_exact']
assert q['projected_words_compared']==310443039 and q['whole_plan_after_serialized_payload_bytes_compared']==1368719790
assert q['whole_arena_record_snapshot_bytes_both_arms_compared']==116919000 and q['scratch_guard_bytes_checked']==7905247512
assert q['raw_output_bytes']==4225482348 and len(q['all_output_extents'])==144
for v in q['all_output_extents']:assert Path(v['path']).stat().st_size==v['bytes']
assert sum(x['independently_derived_selected']for x in q['independent_original_input_eligibility'])==1
assert next(x['id']for x in q['independent_original_input_eligibility']if x['independently_derived_selected'])=='two-tone-iso-on'
for path,digest in P['input_sha256'].items():h.pin(path,digest)
for path,digest in R['input_sha256'].items():h.pin(path,digest)
S=ROOT/'runs/E115-source-v2';M=h.read(S/'manifest.json')
for name,v in M['owned'].items():
    h.pin(v['candidate'],v['candidate_sha256'])
    if v['base']:h.pin(h.REPO/name,v['base_sha256'])
    else:assert not(h.REPO/name).exists()
receipts=[]
for folder in ['execution','execution-reader-repair']:
    for path in(H/folder).glob('*.exit.json'):
        r=h.read(path);expected=1 if folder=='execution'and path.name=='reader.exit.json'else 0
        assert r['returncode']==expected and r.get('error')is None and r.get('cleanup')is None
        receipts.append({'path':str(path),'sha256':h.sha(path),'returncode':expected})
assert len(receipts)==4 and h.read(H/'execution-reader-repair/complete.json')['all18completed_native_cases_not_repeated']
C=ROOT/'runs/E115-production-CPU-checkpoint';C.mkdir(exist_ok=False)
next_step='D271: freeze original36case/752phase full GPU engine/lifecycle matrix with actual accepted/candidate host types and unchanged sealed CUDA. Preserve every original raw field/frame; independently inverse only23 metadata arrays and directly compare other43 device buffers, entire physical CFV under original poison/regeneration contract, CPU/qscale/query/save/resume/EV/graph controls. Require actual selected/fallback constructors and independent expected map/field CPU oracles. Then full canonical physical-state, manual/nonaction locks and symmetric/paged/stored caller, ordinary build/unit and original complete1%/strictfixture/fresh16/material/holdout/cumulative/application gates. No widening E115 predicate.'
h.save(C/'report.json',{'id':'E115-production-CPU-checkpoint','at':h.now(),'status':'actual_production_CPU_metadata_pass_corrected_reader_GPU_pending','measurement_epoch':'RAM20261028',
 'previous_goal_turn_classification':'Progress: D266 bounded history/no-repeat triage, D267 reversible6-plan model, D268 private record padding and D269 actual full crate type sizes plus byte-inverted E115 isolated source completed. No candidate GPU or speed samples then; source now unchanged.',
 'source_manifest_sha256':h.sha(S/'manifest.json'),'source_review_sha256':h.sha(S/'source-review.json'),'D270_protocol_sha256':h.sha(H/'protocol.json'),'reader_repair_protocol_sha256':h.sha(H/'reader-repair-protocol.json'),'root_report_sha256':h.sha(Q),
 'actual_scope':'One fresh offline/locked actual continuation-transfer-research library build, then one exact CPU test process. Real6 original Spots and compressed CPU Solver/ArenaLayout constructors, original GpuPlan build and actual E115 eligible/prepare/children_image.3fixedarms each=18 cases. Real source prefixes/metadata functions unmodified; only appended observers. No GpuSolver constructor, CUDA API/context/kernel, CFR iteration, GPU solve or timing sample.',
 'whole_replay':{k:q[k]for k in['checks','whole_plan_after_serialized_payload_bytes_compared','projected_words_compared','whole_arena_record_snapshot_bytes_both_arms_compared','scratch_guard_bytes_checked','raw_output_bytes','ordered_cases','fallback_cases']},
 'all18cases_all53fields_all23arrays_every_word_full_record_capacities_and_canaries_exact':True,'all18whole_original_before_plan_hashes_exact':True,'exceptional_bits':'Per-node payout/chance scalar rows cover signed zeros/subnormals/finite/infinite/qNaN/sNaN/signed NaN payloads as frozen; synthetic whole-lock offsets also copied exactly. No floating arithmetic/precision change; unit bit-copy data is not a performance/quality fixture.',
 'boundary_checks':48,'negative_reader_fixtures':44,'real_record_lookup_checks':sum(x['record_lookup_checks']for x in q['cases']),
 'preserved_original_reader_and_forecast_failures':{'original_reader_exit':1,'error':'Reader treated positive node_na as action-only; tree.rs patches chance to52. Source-independent action oracle also excludes positive original node_cdiv. Original16ordered/2river-fallback forecast false; retained full-arena5% policy yields13direct-or-selected ordered tests and5selected identities. This is not claimed to pass original literal forecast.','classification':'Observer/oracle and count forecast corrections only: all18 native cases completed once, no candidate/source/predicate/fixture/output/scored sample changes. Corrected read-only reader independently reconstructs original physical action offsets/compaction/capability from all6immutable original plans and verifies every actual flag, field and word. Every original numerical/full-quality/performance gate remains.',
 'original_protocol_literal_forecast_pass_claimed':False,'completed_native_cases_repeated':0},
 'independent_input_eligibility':q['independent_original_input_eligibility'],'scientific_consequence':'Frozen E115 ordinary predicate applies only when both original arena layouts are compact. In canonical performance suite, only two-tone qualifies; rainbow and river remain original layout. No tree/size/fixture timing threshold added, no fallback changed, no sample excluded. All3 full-cycle fixtures and sum-of-medians gate remain. No width/source/field/selection/helper/scope rescue after genuine failure.',
 'actual_host_sizes_unchanged_from_D269':[4448,8,32,8,40,8,160,8],
 'remaining_limits':P['remaining'],'successful_and_failed_child_receipts':receipts,'all_owned_compilers_native_helpers_and_readers_terminal':True,
 'accepted_research_sources_main_live_protected_two_PTX_unchanged':True,'best_qualified_live_config':'E080/GPU/compressed/16workers/defaultaffinity','hardware_epoch_baseline_ms':10456.4109,'last_primary_baseline':'B359','next_unused_baseline':'B360','candidate_adopted_or_deployed':False,'new_qualified_gain_pct':0,'no_speed_material_or_no_tradeoff_claim':True,
 'raw_output_extents_sha256_preserved_in_root_report':True,'raw_outputs_not_rehashed_after_successful_whole_reader':True,'next':next_step,'all_new_bulk_X_S_read_only_no_T_access':True,'X_free_bytes':shutil.disk_usage(ROOT).free,'goal_active':True})
sources=[H/'protocol.json',H/'reader-repair-protocol.json',Q,H/'fixtures.json',H/'execution/build-manifest.json',H/'execution/restoration.json',H/'execution/compile.exit.json',H/'execution/native.exit.json',H/'execution/native.stdout.log',H/'execution/reader.exit.json',H/'execution/reader.stderr.log',H/'execution/reader.stdout.log',H/'execution-reader-repair/reader-r2.exit.json',H/'execution-reader-repair/complete.json',C/'report.json']
published=[]
for path in sources:
    key=H.name+'/'+path.name if path.parent.name in['execution','execution-reader-repair']else path.parent.name+'/'+path.name
    dest=h.ar.DASHBOARD/'evidence'/key;dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():assert dest.read_bytes()==path.read_bytes()
    else:shutil.copyfile(path,dest)
    with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==path.read_bytes()
    published.append({'url':'evidence/'+key,'sha256':h.sha(path)})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=h.read(h.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E115')
    e.update(updated_at=h.now(),status='running',accepted=False,stage='Actual production CPU metadata passes; full GPU engine next',correctness='18 actual CPU cases, full53-field/23-array/record/capacity replay exact; GPU proof pending',reason='Real actual-crate helper replay passes310443039 projected words/1.368GB full plan payload/116.9MB arena snapshots/7.905GB scratch guards. Original reader/action-kind and16/2 forecast failures preserved; source-independent correction keeps all18 completed native cases. Fixed predicate selects canonical two-tone only, with5 original-layout cases. No source/predicate change, native rerun or speed sample. All3 performance fixtures and every original qualification gate remain.')
    e['evidence'] += [{'label':'Full retained-output CPU replay','url':'evidence/'+H.name+'/root-report-r2.json'},{'label':'Actual native CPU cases','url':'evidence/'+H.name+'/native.stdout.log'},{'label':'Complete scope, forecast correction and next gate','url':'evidence/'+C.name+'/report.json'}]
    s.update(updated_at=h.now(),state='running',goal_status='active',active_experiment='E115',stage='Metadata layout: full GPU engine qualification next',activity='D270 actual production CPU projection/complete raw replay passes. Frozen compact-layout predicate selects two-tone; all original performance fixtures remain. No candidate GPU/speed samples yet. E080 live, new-RAM baseline10456.4109ms; all owned jobs terminal; full engine/canonical/material/performance gates remain.')
    h.ar.atomic_json(h.ar.STATUS,s)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/status.json',timeout=20)as z:assert z.read()==h.ar.STATUS.read_bytes()
ledger=h.REPO/'research/postflop-gpu-20261016/experiments.md';prefix=ledger.read_bytes();assert b'\n## D270 actual production metadata CPU replay'not in prefix
assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=h.REPO,text=True).strip()
entry=f'''

## D270 actual production metadata CPU replay - full data pass with preserved observer corrections

Previous goal turn made progress: D266 history/no-repeat triage, D267 full reversible CPU model, D268 padding and D269 actual full crate host type sizes/byte-inverted isolated source. E115 fixed5-file form remains unchanged. One new fresh offline/locked release continuation-transfer-research library compile and one exact CPU native test; original6config/isoflag/full53-field plans and actual CPU Solver/ArenaLayout records. Three frozen arms each: captured lock/data projection, declared signed-zero/subnormal/infinite/qNaN/sNaN bit-copy plus synthetic-lock data, and actual fixed capability-selected/original layout. No GpuSolver constructor/CUDA API/context/kernel/CFR iteration/GPU solve/timing sample.

All18 native cases complete once. Real eligible/prepare/children_image and every node/player record lookup, full53-field before/after plans,23 projected arrays/maps, all active/inactive/copy/initial/zero records and capacities, original arena-size aligned guarded CPU scratch,48 boundary checks. Every before plan whole hash matches originalD183 input; no phase timings used. Full corrected root replay303900555checks,310443039 projected32-bit words,1368719790 serialized full plan payload bytes,116919000 whole arena snapshot bytes,7905247512 scratch guard bytes,44 meaningful negative fixtures pass. All144 raw files/4225482348bytes retained X with complete extents/hashes. Ordinary CPU scratch is not an actual pinned/CUDA constructor or material/capacity proof.

Original reader failed at compact arena action membership after first3 full case comparisons: node_na>0 wrongly included chance nodes patched to52. Original16ordered/2river fallback forecast also false: original plan retains full arenas below5% saving. Original protocol/failed reader/output/receipt retained; literal forecast is not claimed pass. Additive read-only reader repair excludes positive original chance cdiv and independently reconstructs physical CPU action offsets/arena compaction from original node order/data_off/arena_elements for all6 frozen inputs. It requires every actual capability/compact flag match. Actual13ordered (12 direct CPU function tests+1selected) and5identity selections, each ordered gets original3 negative fixtures, each fallback rejects nonidentity map. No source/predicate/fixture/output/scored sample change or completed native repeat. All18/all53/all23/allrecords/fullword/48boundary gates retained; original quality/complete1%/strictfixture/fresh16/material/holdout/cumulative/app gates unchanged. These are observer/oracle/forecast corrections, not a rescue of a genuine projection/numerical/performance failure.

Scientific consequence: E115 pre-outcome both-compact/padding predicate selects only canonical two-tone iso-on. Rainbow, explicit-chance flops and river retain original metadata; no widening or new threshold/source variant. All3 original full-cycle fixtures remain scored; candidate must earn >=1% whole-suite gain without fixture tradeoff. Actual full crate sizes remain prior4448 wrapper/32,40 records/160 ArenaLayout, allalign8; no retained N-map or memory-neutrality claim from type sizes.

Next: {next_step} E114/E112/E113 remain closed. All4 new child receipts terminal (compiler0/native0/original reader1/repaired reader0), accepted/main/live/protected2PTX unchanged, locks absent. No newgain adopted; E080/GPU/compressed/16/defaultaffinity live, RAM10456.4109ms, lastprimaryB359/nextB360. AllnewbulkX,Sarchive readonly,noT. {len(published)} evidence artifacts/statusHTTPbyteverified; checkpoint `{C}`. Ledgerprefix byteexact, goal active.
'''
ledger.write_bytes(prefix+entry.encode());assert ledger.read_bytes()[:len(prefix)]==prefix;h.custody()
subprocess.run(['git','add','--','research/postflop-gpu-20261016/experiments.md'],cwd=h.REPO,check=True)
assert subprocess.check_output(['git','diff','--cached','--name-only'],cwd=h.REPO,text=True).splitlines()==['research/postflop-gpu-20261016/experiments.md']
subprocess.run(['git','-c','gc.auto=0','commit','-m','research: replay actual metadata projection across full CPU inputs'],cwd=h.REPO,check=True)
h.save(C/'publication.json',{'at':h.now(),'local_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=h.REPO,text=True).strip(),'HTTP_byte_verified_artifacts':published,'report_sha256':h.sha(C/'report.json'),'all_owned_children_terminal':True,'candidate_adopted':False,'goal_active':True})
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists()
print(json.dumps({'status':'actual_full_CPU_replay_pass_corrected_reader_GPU_pending','projected_words':310443039,'fixed_candidate_sources_unchanged':True,'HTTP_verified_artifacts':len(published),'next':'D271 original full GPU engine matrix','candidate_adopted':False,'goal_active':True}),flush=True)
