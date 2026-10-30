"""Publish full canonical proof, ordinary builds/units and fixed primary rejection."""
import json,shutil,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists()
S=ROOT/'runs/E115-source-v2';M=h.read(S/'manifest.json');Q=ROOT/'comparisons/E115-three-pair-comparison/report.json';A=ROOT/'comparisons/E115-root-crosscheck/report.json';q=h.read(Q);a=h.read(A)
assert q['decision']=='rejected'and not q['performance']['primary_timing_pass']and a['status']=='pass_rejected'
assert q['performance']['observed_gain_pct']==a['aggregate_gain_pct']==0.1923249216779929
assert q['exactness']=={'fixture_results':18,'convergence_records':138,'all_exact':True}and q['ordinary_units_passed']==86 and q['ordinary_units_ignored']==4
assert not q['excluded_samples']and q['extension_runs']==q['historical_timing_samples_used']==q['RAM_baseline_samples_scored']==0
paths={'CPU_production':ROOT/'runs/D270-actual-metadata-CPU/root-report-r2.json','actual_host_types':ROOT/'runs/D269-host-layout/report.json','GPU_engine':ROOT/'comparisons/D271-metadata-engine/report.json','canonical':ROOT/'comparisons/D272-metadata-canonical-v2/report.json'}
full=h.read(paths['canonical']);engine=h.read(paths['GPU_engine'])
assert full['scientific_full_records_exact']==6 and full['canonical_checkpoints_exact']==46 and full['CPU_raw_pairs']==full['GPU_all69field_pairs']==12
assert full['query_pairs']==6 and full['save_pairs']==3 and full['future_EV_pairs']==9 and full['pair_bytes_compared']==54608665195
assert full['all43_unmapped_device_buffers_including_entire_physical_CFV_literal_exact']and full['all66_device_buffers_exact_under_only_declared_metadata_identity']
assert full['metadata_data_bytes_compared_after_identity_inverse']==405758528 and full['literal_GPU_data_bytes_compared']==37624061220 and full['GPU_header_bytes_compared']==23652
assert full['candidate_selected_constructors']==2 and full['candidate_original_fallback_constructors']==4 and engine['extra_lock_controls']['cases']==6
for n,v in M['owned'].items():
    h.pin(v['candidate'],v['candidate_sha256'])
    if v['base']:h.pin(h.REPO/n,v['base_sha256'])
    else:assert not(h.REPO/n).exists()
for p,v in full['whole_compared_raw_file_sha256'].items():assert Path(p).stat().st_size==v['bytes']
receipts=[]
for folder in['D272-metadata-canonical-v2/execution','E115-final-build','E115-primary-execution','E115-primary-wrapper']:
    for p in(ROOT/'runs'/folder).rglob('*.exit.json'):
        r=h.read(p);assert r['returncode']==0 and r.get('error')is None and r.get('cleanup')is None;receipts.append({'path':str(p),'sha256':h.sha(p),'returncode':0})
assert len(receipts)==17 and h.read(ROOT/'runs/E115-primary-wrapper/complete.json')['all_owned_children_terminal']
H=ROOT/'runs/E115-primary-checkpoint';H.mkdir(exist_ok=False)
reason='Complete-solve fixture medians sum10052.1554 to10032.8226ms, observed gain0.1923249216779929%, below frozen1%. Two-tone1.2840724628207043% faster/0of3slower, rainbow0.5234297931362248% median slower/1of3slower, river1.7729649017839622% slower/2of3slower (guard failed). Fixed E115 form rejected and closed; no field/predicate/selection/placement/width/helper/source/scope/flags/quality/sample rescue or fresh16/broader speed extension.'
h.save(H/'report.json',{'id':'E115-primary-checkpoint','at':h.now(),'status':'rejected_closed_metadata_execution_order_form','measurement_epoch':'RAM20261028','previous_goal_turn_classification':'Progress: D271 actual two-host GPU original36case/752phase and6extra lock controls/full raw replay passed; original extra-path reader failure preserved and corrected without GPU repeats. Current source unchanged.',
 'source_manifest_sha256':h.sha(S/'manifest.json'),'source_review_sha256':h.sha(S/'source-review.json'),'evidence_sha256':{k:h.sha(v)for k,v in paths.items()},
 'source_form':M['change'],'fixed_selection':M['selection'],'locks_and_cost_limit':M['locks'],
 'canonical_scope':'Full original compressed three games,target0.3%pot/check20/cap400/stops200/200/60.6science46checks,12wholeCPU+12all69fieldGPU/all66device/fullphysicalCFV,6queries3saves9futureEVs. Same source/state/dtypes/counts/graphs/wrapper metadata. Both actual host types, original full snapshot suffix exact. Only23metadata row/node-ID fields inverse-mapped to original CPU identity; other43GPU buffers andwholephysicalCFV/padding/CPU/qscales/query/save/EV values literal exact.12actualoriginal53field/kind/mapcaptures checked, only2two-tone constructor selections and4rainbow/river originals. RawGPU hashes differ where IDs differ; each independent original hash retained. No field/padding omission/tolerance/shorter workload.',
 'canonical_metrics':{k:full[k]for k in['reader_checks','pair_bytes_compared','raw_output_bytes','literal_GPU_data_bytes_compared','metadata_data_bytes_compared_after_identity_inverse','GPU_header_bytes_compared','candidate_selected_constructors','candidate_original_fallback_constructors']},
 'retained_canonical_raw_extents':full['whole_compared_raw_file_sha256'],'canonical_CPU_plan_kind_map_extents':full['whole_original_CPU_plan_kind_map_extents'],'raw_files_not_rehashed_after_successful_complete_reader':True,
 'preparer_failure_preserved':'First D272 preparer failed text locator for generic Rust function before any source/protocol/compiler/native output. Empty failed directory/failure record preserved. Additive generator locator/string-delimiter correction only, same candidate/source/cases/gates. D272v2 compilers/native/reader each ran original schedule once; no scientific cases repeated.',
 'ordinary_builds':'Two fresh offline/locked feature andprimary Cargo builds of exact5owned source files, actual original9CUDA include_str/runtimeNVRTC12.9/JIT, no sealed code or diagnostics.4tracked originals restored andverified newmodule removed after each compiler; all dependencies/binary provenance pinned.86units/4ignored pass before timing.',
 'primary_protocol_sha256':h.sha(ROOT/'runs/E115-primary-plan/protocol.json'),'comparison_sha256':h.sha(Q),'root_replay_sha256':h.sha(A),'performance':q['performance'],'exactness':q['exactness'],'ordinary_units_passed':86,'ordinary_units_ignored':4,
 'sequence':'V115-unit then B360/E115R1,E115R2/B361,B362/E115R3,each once; samequality/storage/16workers/defaultaffinity/science anchor. Full tree/CPU/GPUinit/metadata setup/copies/fence/solve/readback included,actualNVRTC/JIT. Cargo/fingerprints/destruction/browser/API/saving excluded. No exclusions/extensions/historical/RAM timing pooling or significance claim.',
 'successful_child_receipts':receipts,'all_owned_compilers_native_GPU_processes_and_readers_terminal':True,'accepted_research_sources_main_live_protected_two_PTX_unchanged':True,'reason':reason,'candidate_adopted_or_deployed':False,'remaining_adoption_requirements':[],'no_additional_fresh16_or_broader_speed_trials':True,
 'best_qualified_live_config':'E080/GPU/compressed/16workers/defaultaffinity','hardware_epoch_baseline_ms':10456.4109,'last_primary_baseline':'B362','next_unused_baseline':'B363','new_qualified_gain_pct':0,'all_new_bulk_X_S_read_only_no_T_access':True,'X_free_bytes':shutil.disk_usage(ROOT).free,'next':'D273 bounded history/source scout for a genuinely distinct full-cycle opportunity; no widening or retuning closed metadata-order form.','goal_active':True})
sources=list(paths.values())+[S/'manifest.json',S/'source-review.json',ROOT/'runs/D272-metadata-canonical/generation-failure.json',ROOT/'runs/D272-metadata-canonical-v2/protocol.json',ROOT/'runs/D272-metadata-canonical-v2/source-review.json',ROOT/'runs/D272-metadata-canonical-v2/execution/complete.json',ROOT/'runs/E115-build-plan/protocol.json',ROOT/'runs/E115-final-build/complete.json',ROOT/'runs/E115-primary-plan/protocol.json',Q,A,H/'report.json']
published=[]
for p in sources:
    key=p.parent.name+'/'+p.name
    if p.parent.name=='execution':key=p.parent.parent.name+'/'+p.name
    dest=h.ar.DASHBOARD/'evidence'/key;dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():assert dest.read_bytes()==p.read_bytes()
    else:shutil.copyfile(p,dest)
    with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==p.read_bytes()
    published.append({'url':'evidence/'+key,'sha256':h.sha(p)})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=h.read(h.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E115');e.update(updated_at=h.now(),status='rejected',accepted=False,stage='Closed: complete-solve1%/river guard rejected',correctness='CPU/42GPUcases/fullcanonical and86units pass; performance rejected',performance=q['performance'],reason=reason);e['evidence'] += [{'label':'Complete-solve primary decision','url':'evidence/'+Q.parent.name+'/report.json'},{'label':'Independent full-log and median replay','url':'evidence/'+A.parent.name+'/report.json'},{'label':'All prerequisites, full canonical state and decision','url':'evidence/'+H.name+'/report.json'}]
    s.update(updated_at=h.now(),state='running',goal_status='active',active_experiment='E115',stage='Metadata layout closed; next distinct lead',activity=reason+' E080 remains best qualified/live; no new gain adopted.');h.ar.atomic_json(h.ar.STATUS,s)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/status.json',timeout=20)as z:assert z.read()==h.ar.STATUS.read_bytes()
ledger=h.REPO/'research/postflop-gpu-20261016/experiments.md';prefix=ledger.read_bytes();assert b'\n## E115 complete canonical and primary decision'not in prefix;assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=h.REPO,text=True).strip()
entry=f'''

## E115 complete canonical and primary decision - rejected and closed

Previousgoalturn progress:D271 actualtwo-host original36GPUcases/752phases plus6extra locks/fullraw replay pass,with oldextra-path reader failure preserved and read-only corrected; all42native cases once. Frozen5file E115 source andboth-compact predicate unchanged throughout. D272 full original compressed200/200/60 target.3%pot/check20/cap400,6science46checks/12CPU+12all69fieldGPU/all66buffers/wholephysicalCFV,6queries3saves9futureEVs pass. All original snapshot/prefix statements inverse byte-exact except appended read-only original53field/kind/map capture.2actualtwo-tone selected initial/resumed constructors,4rainbow/river originals; all12CPUplans/kinds/maps/capabilities verified. No source widening.

Canonical raw comparison accounts every54608665195paired bytes:37624061220GPUdata bytes literal,405758528metadata bytes inverse only15per-node rows/8node-ID fields,23652GPUheader bytes literal; other43devicebuffers includingentirephysicalCFV/padding andallCPU/qscale/query/save/EV/geometry/graph/wrapper/dtype/length values literal exact.21617585readerchecks. Each original raw GPU file independently hashed; no false literal-ID equality claim.110210262986rawbytes retainedX,original256GiB+64GiBdisk/64before32duringRAM/32GiBprocess guards retained. Firstpreparer generic-functionlocator failedbefore source/protocol/compiler/native output; oldempty attempt/failure kept,additive generator locator/stringdelimiter repair only. Two fresh standalone compilers andB/Cguardednativeprobes/fullreader terminal0, no scientific repeat. Prebuilt identical accepted9entryPTX andobserver clocks unscored.

Two fresh ordinaryoffline/locked feature/primary Cargo builds useexact5sourcefiles andactualNVRTC12.9/JIT, no sealedPTX/observer/map/enum inperformance source.4tracked originals andnewmodule restoredaftereachcompiler.86ordinaryunits/4ignored pass. Frozen V115-unit thenB360/E115R1,E115R2/B361,B362/E115R3 eachonce,18science138checkpoints exact. Full tree/CPU/GPUinit/newmetadata setup/copies/fence/solve/readback included. Sumfixturemedians10052.1554->10032.8226ms,unroundedgain0.1923249216779929% below1%. Two-tone1.2840724628207043% faster/0of3slower;rainbow0.5234297931362248% median slower/1of3slower;river1.7729649017839622% slower/2of3slower,strictfixtureguard fails. Independent complete-log/median/guard replay agrees;no excluded/extension/historical/RAMreference samples orsignificanceclaim.

Fixed E115 metadata execution-order form rejected/closed: no field/predicate/selection/placement/width/helper/source/scope/flags/quality/sample rescue orfresh16/broader speedextension. Useful CPU/42GPU/fullcanonical evidence retained; no universal material/capacity/no-tradeoff/adoption claim. All17owned childreceipts terminal0,locksabsent,accepted/main/live/protected2PTX unchanged. E080/GPU/compressed/16/defaultaffinity remains bestqualified/live,epochRAM10456.4109ms keptseparate,lastprimaryB362/nextB363. NewbulkX,Sarchive readonly,noT;{len(published)}artifacts/statusHTTPbyteverified,checkpoint `{H}`. Next D273 bounded history/source scout for distinctfullcycle opportunity, neverrescue closedmetadatalayout. Priorledgerprefix byteexact,goalactive.
'''
ledger.write_bytes(prefix+entry.encode());assert ledger.read_bytes()[:len(prefix)]==prefix;h.custody();subprocess.run(['git','add','--','research/postflop-gpu-20261016/experiments.md'],cwd=h.REPO,check=True)
assert subprocess.check_output(['git','diff','--cached','--name-only'],cwd=h.REPO,text=True).splitlines()==['research/postflop-gpu-20261016/experiments.md'];subprocess.run(['git','-c','gc.auto=0','commit','-m','research: close metadata ordering after full-state and speed tests'],cwd=h.REPO,check=True)
h.save(H/'publication.json',{'at':h.now(),'local_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=h.REPO,text=True).strip(),'report_sha256':h.sha(H/'report.json'),'HTTP_byte_verified_artifacts':published,'all_owned_children_terminal':True,'candidate_adopted':False,'goal_active':True})
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists()
print(json.dumps({'status':'rejected_closed','gain_pct':q['performance']['observed_gain_pct'],'fixture_guard_failed':'river','candidate_adopted':False,'HTTP_artifacts':len(published),'next_baseline':'B363','goal_active':True}),flush=True)
