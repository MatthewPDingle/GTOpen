"""Replay every CPU slot word and report isolated headroom without qualification."""
import array,json,math,statistics,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;old.custody();assert not (ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/D080-river-slot-headroom';R=H/'r2';E=R/'execution';P=old.read(R/'protocol.json');S=old.read(R/'execution-seal.json');done=old.read(E/'complete.json')
for p,h in S['input_sha256'].items():old.pin(p,h)
for p,h in done['artifact_sha256'].items():old.pin(p,h)
assert old.read(E/'rustc.exit.json')['returncode']==old.read(E/'native.exit.json')['returncode']==0
assert old.read(E/'terminal.json')['returncode']==0 and old.read(E/'terminal.json')['complete_sha256']==old.sha(E/'complete.json')
raw=(E/'native.stdout.log').read_text(encoding='utf-8');rows=[json.loads(x.split('D080_RESULT ',1)[1]) for x in raw.splitlines() if 'D080_RESULT ' in x];assert len(rows)==6
assert [x['id'] for x in rows]==[n+'-'+s for n in ['rainbow','two-tone','river'] for s in ['iso','full']]
checks=0;case_reports=[]
def words(path,kind):
 a=array.array(kind);a.frombytes(Path(path).read_bytes())
 if sys.byteorder!='little':a.byteswap()
 return a
for r in rows:
 id=r['id'];k=words(E/'raw'/(id+'.keys.u64'),'Q');a=words(E/'raw'/(id+'.original.i32'),'i');b=words(E/'raw'/(id+'.indexed.i32'),'i');ordered=words(E/'raw'/(id+'.ordered-keys.u64'),'Q')
 assert len(k)==len(a)==len(b)==r['nodes'];assert a==b
 slot_by_key={};keys=[];show=0
 for i,key in enumerate(k):
  if key==0xffffffffffffffff:assert a[i]==-1
  else:
   assert key<r['domain'];show+=1
   if key not in slot_by_key:slot_by_key[key]=len(keys);keys.append(key)
   assert a[i]==slot_by_key[key]
  checks+=1
 assert list(ordered)==keys and show==r['show_keys'] and r['full_original_plan_agreement']
 assert len(r['samples'])==9
 for i,s in enumerate(r['samples']):
  assert s['pair']==i+1 and s['order']==(['original','indexed'] if i%2==0 else ['indexed','original'])
  assert all(math.isfinite(x) and x>0 for x in s['ms'].values())
 base=[s['ms']['original'] for s in r['samples']];cand=[s['ms']['indexed'] for s in r['samples']];bm=statistics.median(base);cm=statistics.median(cand)
 case_reports.append({'id':id,'fixture':r['fixture'],'isomorphism':r['isomorphism'],'primary_case':r['isomorphism']==r['primary_iso'],'nodes':len(k),'show_keys':show,'unique_keys':len(keys),'domain':r['domain'],'temporary_index_bytes':r['indexed_temporary_bytes'],'all_slot_words_exact':True,'accepted_original_plan_agreement':True,'original_median_ms':bm,'indexed_median_ms':cm,'observed_isolated_saved_ms':bm-cm,'raw_original_ms':base,'raw_indexed_ms':cand})
primary=[x for x in case_reports if x['primary_case']];assert len(primary)==3
total=math.fsum(x['original_median_ms'] for x in primary);saved=math.fsum(x['observed_isolated_saved_ms'] for x in primary);anchor=P['existing_complete_anchor_ms']
potential=100*total/anchor;saved_scale=100*saved/anchor
q={'id':'D080-river-slot-headroom','at':old.now(),'status':'decline_full_candidate_insufficient_measured_component_headroom' if potential<1 else 'component_warrants_integrated_review_only','protocol_sha256':old.sha(R/'protocol.json'),'binary_sha256':done['binary_sha256'],'root_cross_check_only':True,'checks':checks,'cases':case_reports,'primary_isolated_original_sum_median_ms':total,'primary_isolated_saved_sum_median_ms':saved,'historical_complete_anchor_ms':anchor,'full_removal_percent_of_historical_anchor':potential,'isolated_saved_percent_of_historical_anchor':saved_scale,'production_source_changed':False,'gpu_kernel_solver_executions':0,'full_candidate_prepared':False,'candidate_accepted':False,'excluded_samples':[],'extension_runs':0,'limits':'Standalone accepted-library CPU loop timing, outside complete construction/solve. Full component removal ratios use historical complete times only for scale; these are not native complete-cycle bounds or speedups, and unrelated compiler effects cannot justify a performance claim. Exact controls cover these derived supported fixture keys; no malformed/custom key guarantee. No external independent audit.'}
O=ROOT/'comparisons/D080-river-slot-headroom';O.mkdir();old.save(O/'report.json',q)
published={}
for directory in [H,O]:
 for src in directory.rglob('*'):
  if not src.is_file() or src.suffix=='.exe' or '__pycache__' in src.parts:continue
  key=directory.name+'/'+src.relative_to(directory).as_posix();dst=ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);data=src.read_bytes()
  if dst.exists():assert dst.read_bytes()==data
  else:dst.write_bytes(data)
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=30) as response:assert response.read()==data
  published[key]=old.sha(src)
old.save(O/'publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published})
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(ar.STATUS);st.update(state='running',stage='D080 slot lookup investigation closed' if potential<1 else 'D080 integrated source review pending',activity=f'D080 original slot loop totals {total:.3f}ms across primary cases, {potential:.4f}% of historical full-cycle anchor; no accepted gain. E020 retained.',updated_at=ar.now());st['evidence'].append({'label':'D080 full raw CPU slot replay and headroom','url':'evidence/D080-river-slot-headroom/report.json'});ar.atomic_json(ar.STATUS,st)
# H and O have the same basename, so the report uses that common evidence key;
# its content has no colliding source name in H.
ledger=ar.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'## D080 river-slot lookup headroom' not in raw
text=f'''

## D080 river-slot lookup headroom

After E049, source inspection found HashMap slot lookup once per reached showdown node, despite a supported river-key domain of2704/52/1 for flop/turn/river roots. A direct index could preserve first-seen ascending node IDs, ordered slot keys and every downstream plan field. No matching prior slot_of_key change was found in scoped retained patches/reviews or local all-ref plan history. D041 remains counterevidence against cache/context tricks: primary-context retention is already used by the server's VRAM query, historical module calls were only1-2ms and PTX acquire about60ms. Keeping a fresh-test context alive alone would not establish application speed and may move teardown outside the score. Pair-graph fusion also lacks current headroom evidence; D055's perturbed0.000576ms gap is not a native bound.

D080 protocol {old.sha(R/'protocol.json')} and execution seal {old.sha(R/'execution-seal.json')} froze an off-tree CPU-only native probe linked to the exact accepted E020 solver rlib. It constructs actual fixed Spot/GpuPlan inputs with isomorphism on/off, derives original DFS/key expressions, and requires complete original slot-map/unique-count agreement with the accepted planner before any timing. Full keys, ordered slot keys, and both original/indexed maps are retained. Before any compile or outcome, R2 changed only raw file writes to buffered IO; sealed R1 remains preserved. One compiler and one native process completed, with9fixed alternating pairs per6cases and1warmup/arm; no GPU context, kernel, Solver or solve ran. Root directly replayed {checks} node slots and all ordered keys from raw bytes. Standalone original/indexed medians are in report {old.sha(O/'report.json')}.

Across the three primary-isomorphism cases, original loop medians sum {total:.10f}ms; indexed savings sum {saved:.10f}ms. For scale against B146-148's historical {anchor:.10f}ms complete anchor, removing the entire observed loop corresponds to {potential:.10f}% and observed isolated savings to {saved_scale:.10f}%. These cross-boundary ratios are not measured complete-cycle bounds, speedups or compiler-causality proof. Status: {q['status']}. No full production candidate or source activation follows this diagnostic at this checkpoint. All samples/evidence remain included, published and HTTP byte-verified; E020 stays accepted. Goal remains active.
'''
nl=b'\r\n' if b'\r\n' in raw else b'\n';ledger.write_bytes(raw+text.encode('utf-8').replace(b'\n',nl))
old.custody();print(json.dumps({'status':q['status'],'checks':checks,'original_ms':total,'saved_ms':saved,'full_removal_scale_pct':potential,'isolated_saving_scale_pct':saved_scale,'report_sha256':old.sha(O/'report.json'),'published':len(published)}),flush=True)
