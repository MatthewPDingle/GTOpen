import json, shutil, subprocess, sys, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D190-inline-tree-control';R=ROOT/'comparisons/D190-inline-tree-root-check'
h.custody();h.ar.refuse_active(h.ar.live_status())
assert not any((ROOT/x).exists() for x in ['gpu-run.lock','epoch-sequence.lock'])
P=h.read(H/'protocol.json');q=h.read(H/'report.json');r=h.read(R/'report.json')
assert q['status']=='rejected_component_admission' and r['status']=='pass_component_admission_replay' and not r['component_passed']
assert q['sum_component_median_saving_ms']==r['component_saving_ms']<P['minimum_component_saving_ms']
assert r['total_raw_bytes']==2470234362 and r['raw_typed_words_compared']==159838548 and r['native_error_equalities']==10
assert len(r['files'])==23 and len(q['controls'])==30 and len(q['canonical'])==3
assert h.read(H/'execution/complete.json')['all_owned_compilers_native_readers_terminal']
for p,digest in P['input_sha256'].items():h.pin(p,digest)
receipts=[]
for label in ['smallvec-rustc','rustc','canonical-0','canonical-1','canonical-2','controls','audit']:
    p=H/'execution'/(label+'.exit.json');e=h.read(p)
    assert e['returncode']==0 and e['error'] is e['cleanup'] is None
    receipts.append({'label':label,'receipt_sha256':h.sha(p),'returncode':0})
for row in q['raw_files']:
    assert Path(row['path']).stat().st_size==row['bytes']
    # Entire hash and raw paired fields were read by the successful original reader.
baseline=r['baseline_component_median_sum_ms'];candidate=r['candidate_component_median_sum_ms']
N=ROOT/'runs/D190-terminal-checkpoint';N.mkdir(exist_ok=False)
h.save(N/'report.json',{
    'id':'D190/E100-close','at':h.now(),'status':'rejected_component_admission_closed',
    'native_report_sha256':h.sha(H/'report.json'),'root_replay_sha256':h.sha(R/'report.json'),
    'source_review_sha256':h.sha(H/'source-review.json'),'protocol_sha256':h.sha(H/'protocol.json'),
    'baseline_CPU_wrapper_median_sum_ms':baseline,'candidate_CPU_wrapper_median_sum_ms':candidate,
    'CPU_component_saving_ms':r['component_saving_ms'],'required_component_saving_ms':P['minimum_component_saving_ms'],
    'component_fixture_guards':r['component_guards'],'full_cycle_performance_measured':False,
    'raw_typed_words_compared':r['raw_typed_words_compared'],'whole_retained_raw_bytes':r['total_raw_bytes'],
    'full_typed_raw_files':len(r['files']),'native_exact_error_equalities':r['native_error_equalities'],
    'all_retained_raw_extents_verified_after_reader':True,'raw_not_rehashed_after_successful_original_reader':True,
    'successful_child_receipts':receipts,'all_owned_compiler_native_reader_processes_terminal':True,
    'new_GPU_processes':0,'production_source_activation':False,'new_gain_accepted_or_deployed':False,
    'precision_quality_CUDA_or_save_format_changes':False,
    'resource_risks_remaining_unqualified':q['temporary_container_sizes'],
    'closure':'No inline capacity, container, scope, helper, flags, threshold, source or sample rescue. No whole-solve timing or broader/material/adoption progression after the failed component gate.',
    'limitations':'Finite returned-tree/config/fields/capacities and original budget/menu/error corpus only. No GPU/solver numerical qualification or universal exactness claim. CPU wrapper excludes final Tree destruction and cannot prove full-cycle speed or overall resource neutrality.',
    'best_qualified':'E080 / GPU / compressed / 16 workers','last_primary_baseline':'B313',
    'new_output_physical_drive':'X:','archive_read_only':True,'T_drive_accesses':0,
})
published=[]
for folder,names in [(H,['report.json','candidate-tree.rs','baseline-tree.rs','probe.rs','audit.py']),(R,['report.json']),(N,['report.json'])]:
    for name in names:
        p=folder/name;dst=h.ar.DASHBOARD/'evidence'/folder.name/name
        dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
        relative=dst.relative_to(h.ar.DASHBOARD).as_posix()
        with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/'+relative,timeout=20) as response:assert response.read()==p.read_bytes()
        if name=='report.json':published.append({'label':folder.name+' result','url':relative})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=h.read(h.ar.STATUS);item=next(x for x in s['experiments'] if x['id']=='E100')
    item.update(at=P['at'],status='rejected',accepted=False,correctness='pass_scoped_CPU_tree_raw_controls',stage='Closed at CPU setup-cost screen',
        reason=f'Tree setup wrapper: {baseline:.4f} to {candidate:.4f} ms, saving {r["component_saving_ms"]:.4f} ms; below the fixed {P["minimum_component_saving_ms"]:.6f} ms admission proxy. All 23 full typed tree pairs/capacities and 10 native error comparisons exact. No GPU or complete-solve speed result; no adoption or variant rescue.')
    item['component']={'CPU_wrapper_baseline_ms':baseline,'CPU_wrapper_candidate_ms':candidate,'saving_ms':r['component_saving_ms'],'required_saving_ms':P['minimum_component_saving_ms'],'full_cycle':False}
    item['evidence'].extend(published)
    s.update(updated_at=h.now(),active_experiment='E100',stage='Tree setup experiment closed; source research continues',
        activity='E100 preserved all tested tree outputs and saved 17.6 ms of CPU setup, below the fixed admission threshold. It was closed before GPU timing. E080 with 16 workers remains live; no new whole-solve gain adopted.')
    h.ar.atomic_json(h.ar.STATUS,s)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/status.json',timeout=20) as response:assert response.read()==h.ar.STATUS.read_bytes()
ledger=h.REPO/'research/postflop-gpu-20261016/experiments.md'
assert '### D190/E100 CPU tree controls exact; component gate rejected' not in ledger.read_text(encoding='utf-8')
with ledger.open('a',encoding='utf-8',newline='\n') as f:
    f.write('''

### D190/E100 CPU tree controls exact; component gate rejected

Frozen f13ca9b505078cdb527f5c47adef02863d0567235ef55e413800f71956477160 completed the verified SmallVec-default rlib compiler, standalone original/candidate tree compiler, three canonical CPU processes and original diverse-control process, then complete raw reader. All seven children terminal 0, no repair or rerun. Same accepted Mimalloc allocator comes from the unchanged solver library; no source activation, GPU context/kernel, CUDA compilation or solve. Exactly 2 warmup pairs plus 9 alternating measured pairs per original canonical, 27 scored CPU pairs, no exclusions/extensions/historical pooling.

All measured fingerprints/capacities agree. Reader independently compares all 23 full typed final/control paired trees: 10,822,609 nodes, 10,901,576 child slots, 9,532,832 actions, 159,838,548 typed word pairs and 2,470,234,362 retained bytes on X. All f64 fields/config/root/data sizes/3 persistent Vec capacities, parent-first graph offsets/edges and original phantom-runout sentinels exact; 201,948,045 reader checks. Ten same-error comparisons remain native assertions; both independent raw error strings were not separately retained. Finite returned-tree proof only, no GPU/full solver/universal exactness claim.

CPU wrapper median sums 94.08370000000001 -> 76.51950000000001 ms, saving 17.564200000000003 ms. Per-fixture 48.4144 -> 38.3883, 45.6661 -> 38.1281, 0.0032 -> 0.0031 ms; all guards clear, each 2/9 slower pairs. Saving is below prospectively fixed 95.086109 ms effort proxy, so reject component admission. This is not a 0.18% measured complete-solve gain, nor a rigorous removable-time bound. No whole-solve speed sample is scored. Original wrapper timing scope and final Tree-drop exclusion remain.

Observed container type sizes disclose stack risk: Action Vec 24 -> SmallVec 80 bytes, amount Vec 24 -> SmallVec 48 bytes (not actual compiler frame or peak measurements). Broad CPU/RAM/stack/quality/GPU/capacity/application qualification remains unperformed after rejection. Exact inline capacity 4/container/source scope form is CLOSED: no width/container/helper/threshold/flags/source or sample rescue. All source/protocol/native/root/terminal artifacts retained, 7 new small result/source artifacts published and HTTP-byte verified. Original raw reader consumed all files; terminal custody verifies retained extents without a second full rehash. All owned compilers/native/readers terminal, locks absent, accepted source/main/live/protected PTX unchanged. E080/GPU/compressed/16 remains live, last primary B313, no new gain accepted; current-RAM baseline and historical gains stay separate. Goal active.
''')
h.custody()
subprocess.run(['git','add','--','research/postflop-gpu-20261016/experiments.md'],cwd=h.REPO,check=True)
subprocess.run(['git','commit','-m','research: close inline tree allocation component screen'],cwd=h.REPO,check=True)
print(json.dumps({'E100':'rejected CPU component admission','saving_ms':r['component_saving_ms'],'required_ms':P['minimum_component_saving_ms'],'full_cycle_samples':0,'GPU_processes':0,'raw_files_exact':len(r['files']),'owned_children':'all terminal','live':'E080 / 16 workers'}),flush=True)
