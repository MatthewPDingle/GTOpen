"""Replay every encoded plan word; close the prospective component admission."""
import array,datetime,json,math,statistics,struct,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/D099-plan-posting-scratch';E=H/'execution';P=old.read(H/'protocol-r2.json');N=old.read(H/'native-report.json');A=ROOT/'runs/D092-action-arity-order';AR=old.read(A/'report.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
assert N['protocol_sha256']==old.sha(H/'protocol-r2.json') and N['all_owned_children_terminal'] and len(N['cases'])==12
assert old.read(H/'build/rustc.exit.json')['returncode']==0
checks=0;word_total=0;raw_bytes=0;results=[];previous=None
def require(v,label):
 global checks
 assert v,label;checks+=1
def vector(f,skip=False):
 n=struct.unpack('<Q',f.read(8))[0];require(n<=100000000,'bounded words')
 if skip:f.seek(8*n,1);return None
 a=array.array('Q');a.fromfile(f,n);require(len(a)==n,'whole vector');return a
for identity,observed in enumerate(N['cases']):
 label=f'case-{identity:02d}';receipt=old.read(E/(label+'.exit.json'));require(receipt['returncode']==0 and receipt['error'] is receipt['cleanup'] is None,'terminal native')
 start=datetime.datetime.fromisoformat(receipt['started_at']);end=datetime.datetime.fromisoformat(receipt['finished_at']);require(start<=end and (previous is None or previous<=start),'serial native order');previous=end
 path=E/(label+'.bin');old.pin(path,N['raw_sha256'][path.name]);oldpin=AR['cases'][identity];old.pin(A/'execution'/(label+'.bin'),oldpin['raw_sha256'])
 native=[json.loads(x.split('D099 ',1)[1]) for x in (E/(label+'.stdout.log')).read_text(encoding='utf-8').splitlines() if x.startswith('D099 ')];require(native==[observed],'native report agreement')
 words=0
 with path.open('rb') as f,(A/'execution'/(label+'.bin')).open('rb') as g:
  require(f.read(16)==b'D099-PLAN-RAW1\0\0' and g.read(16)==b'D092-PLAN-RAW1\0\0','raw magic')
  require(struct.unpack('<II',f.read(8))==struct.unpack('<II',g.read(8))==(identity,53),'case and schema')
  sa,sb=struct.unpack('<QQ',f.read(16));ga,gb=struct.unpack('<QQ',g.read(16));require(sa==sb==ga==gb and sa>0,'same struct sizes')
  for field in range(53):
   require(struct.unpack('<I',f.read(4))[0]==struct.unpack('<I',g.read(4))[0]==field,'field ids')
   ca,cb,wa,wb=[vector(f) for _ in range(4)];oc=vector(g);vector(g,True);ow=vector(g);vector(g,True)
   require(ca==cb==oc,'all capacities equal retained accepted planner');require(wa==wb==ow,'all full field words exact accepted and prototype');words+=len(wa)
  for _ in range(2):require(vector(f)==vector(g),'actual tree/kind source exact')
  require(f.read(1)==g.read(1)==b'','complete raw endpoints')
 require(words==observed['baseline_words'],'full word inventory');word_total+=words;raw_bytes+=path.stat().st_size
 b,c=observed['baseline_samples_ms'],observed['candidate_samples_ms'];require(len(b)==len(c)==9,'fixed measured pairs')
 require(observed['pair_orders']==['BC','CB','BC','CB','BC','CB','BC','CB','BC'],'fixed order')
 require(all(math.isfinite(v) and v>=0 for v in b+c),'finite nonnegative timings')
 bm,cm=statistics.median(b),statistics.median(c);require(bm==observed['baseline_plan_ms'] and cm==observed['candidate_plan_ms'],'median replay')
 slower=sum(y>x for x,y in zip(b,c));guard=cm>bm and slower>=5
 require(observed['first']=='baseline' and observed['warmup_pairs']==2 and observed['measured_pairs']==9,'correct lifetime/order metadata')
 for m in observed['posting_mechanism']:
  require(m['all_card_posting_values_and_order_exact'] and m['reused_allocation_growth_events']<=m['baseline_allocation_growth_events'],'posting mechanism evidence')
 results.append({'case':identity,'baseline_median_plan_ms':bm,'prototype_median_plan_ms':cm,'median_savings_ms':bm-cm,'slower_pairs':slower,'component_guard_failed':guard,'baseline_samples_ms':b,'prototype_samples_ms':c,'posting_mechanism':observed['posting_mechanism'],'raw_file_sha256':old.sha(path),'raw_bytes':path.stat().st_size,'all53_fields_and_capacities_exact':True,'baseline_matches_retained_D092_accepted_fields':True})
canonical=[results[i] for i in [2,6,10]];savings=sum(v['median_savings_ms'] for v in canonical);passed=savings>=P['screen_minimum_savings_ms'] and not any(v['component_guard_failed'] for v in canonical)
R=ROOT/'comparisons/D099-plan-scratch-root-check';R.mkdir()
report={'id':'D099','at':old.now(),'status':'advance_component_only' if passed else 'declined_component_admission','checks':checks,'protocol_sha256':old.sha(H/'protocol-r2.json'),'native_report_sha256':old.sha(H/'native-report.json'),'cases':results,'all12cases_53fields_and_capacities_exact':True,'all_encoded_baseline_words_compared':word_total,'raw_bytes':raw_bytes,'source_mechanism':'Stable reuse of temporary per-card vectors only; same accepted solver/mimalloc and local exact game source. No returned fields, capacities, metadata order, CUDA or quality changed.','canonical_cases':[2,6,10],'canonical_component_savings_ms':savings,'frozen_prior_full_cycle_reference_ms':P['screen_reference_ms'],'frozen_component_minimum_savings_ms':P['screen_minimum_savings_ms'],'reference_proxy_pct':100*savings/P['screen_reference_ms'],'screen_pass':passed,'limits':'Only CPU full-plan component clocks with explicit warmup and separate unscored output proof plans. Reference ratio is a prospective research-selection proxy, not measured/bounded complete-cycle gain. Requested temporary capacities and Vec growth events are not OS allocator calls/RSS or GPU capacity observations. Root replay is not external independent review.','all_owned_children_terminal':True,'excluded_samples':[],'extension_runs':0,'source_activated':False,'gpu_executions':0,'whole_solver_executions':0,'full_cycle_performance_measured':False,'optimization_accepted':False,'no_scratch_guard_scope_or_allocation_variant_rescue':not passed,'accepted_source':'E051'}
old.save(R/'report.json',report)
old.save(H/'checkpoint.json',{'at':old.now(),'previous_goal_turn_classification':'progress: source-matched driver capture, E060direct controls and initial complete-cycle rejection changed next action','current_goal_turn':'D099complete source/12native CPU plan/53field and capacity/raw accepted-anchor/component evidence','goal_active':True,'accepted_source':'E051','accepted_cumulative_gain_pct':12.4372274192464,'all_owned_sessions_terminal':[98886],'all_owned_children_terminal':True,'last_primary_baseline':'B188','source_main_live_ptx_unchanged':True,'decision':report['status'],'component_savings_ms':savings,'next':'Close allocation-reuse hypothesis if fixed proxy fails; do not integrate or rescue scratch placement/capacity/batching variants. Return to GPUexecution. Scoped ledger search found no prior per-function CUDAcache/carveout configuration candidate. Inspect official driver documentation and actual device cache/shared configuration plus occupancy before admitting any such hypothesis. No cache-hint source or native probe exists yet. Preserve accuracy and unchanged complete-cycle1%/fixture/fresh16/broad/material/holdout/cumulative requirements.','live_deployment':'Prior automatic approval block remains; do not retry or ask duplicate permission.'})
published={}
def put(p,key):
 dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert dst.read_bytes()==p.read_bytes()
 else:dst.write_bytes(p.read_bytes())
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
 published[key]=old.sha(p)
for p in H.rglob('*'):
 if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.exe','.pdb','.bin','.obj']:put(p,H.name+'/'+p.relative_to(H).as_posix())
put(R/'report.json',R.name+'/report.json')
for p in [Path(__file__),ROOT/'runs/D099-prepare.py',ROOT/'runs/D099-freeze-revision.py']:put(p,'D099-preparation-sources/'+p.name)
old.save(H/'publication.json',{'at':old.now(),'http_byte_verified_files':len(published),'artifact_sha256':published,'all3650458064raw_bytes_preserved_on_S':True})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);e=next(e for e in st['experiments'] if e['id']=='D099')
 e.update(status='measured',correctness='pass',accepted=False,stage='Closed: CPU savings too small for registered admission' if not passed else 'Component-only admission passed',reason=f'All12x53fields/capacities exact, accepted raw anchor matches. Canonical CPU-plan savings{savings:.6f}ms vs frozen{P["screen_minimum_savings_ms"]:.6f}ms admission threshold. Reference ratio{report["reference_proxy_pct"]:.6f}%is not measured complete-cycle speed; no solver integration/adoption.')
 e['evidence'].extend([{'label':'Frozen component rules','url':'evidence/'+H.name+'/protocol-r2.json'},{'label':'Full raw and timing root replay','url':'evidence/'+R.name+'/report.json'},{'label':'Current checkpoint','url':'evidence/'+H.name+'/checkpoint.json'}])
 st.update(updated_at=old.now(),state='running',active_experiment=None,stage='Next GPU execution mechanism investigation',activity='D099scratch reuse declined:5.18ms CPU-plan saving is insufficient under its prospective reference screen. Exact plan fields and all evidence retained; E051accepted source/gain unchanged.');old.ar.atomic_json(old.ar.STATUS,st)
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'### D099 river-posting' not in raw
note=f'''

### D099 river-posting temporary allocation reuse -- component screen declined

Previous goal turn made progress: D098captured source-matched driver code; E060exact controls/84units/initial3pairs measured1.2170441078%aggregate but failed river guard and closed. D099tests a distinct CPU metadata-preparation lead only. Accepted plan already constructs2card memberships/hand in one pass; it is not52hand scans. One off-tree plan prototype moves52temporary by_cardVecs to per-player scope and clears them each river slot. Append/flatten order and every returned array stay identical; no tracked source/CUDA/graph/quality change. Source c064e119b5977fe50e044e8fce639a6705d3383d221a0bd51dc97acb857582e1.

Before any compile/native outcome, static preflight corrected inherited first-arm metadata and asymmetric final measured-pair retention. Original protocol328464f7e6cc98502e4dce4f66d56f0b1c0795bed910333efbd16da93078bd6d/source preserved; R2drops every measured plan after stopping its timer and uses2separate untimed final plans for full raw controls. Transform and sampling/gates unchanged. R2protocol2197252ddf686f650beaea3c415dfef96b19dfbe3d34ca70bb0449f2acab2fc3. One compile and12fresh native processes in handle98886all terminal0, accepted solver rlib/mimalloc, exact localgame source. Three canonical fixtures x isooff/on x compact/full; each2unscored warmup pairs and9fixed alternating measured pairs, all retained. Component clocks exclude Spotconstruction, result destruction and raw evidence work; no fresh GPU/context/solve/full-cycle inference.

All12x53full encoded plan fields, capacities, struct sizes and actual tree maps match prototype and retained D092accepted baseline, including exact worklist and card/position order. Root{checks}checks, {word_total}encoded baseline words compared;3,650,458,064raw bytes retained with hashes. Native untimed posting reconstruction compares both actual Vec algorithms against actual plan tables. Canonical rainbow growth events294111to264,two-tone199982to264,river247to247. These count Vecallocation/growth requests, not OS heap calls. Requested peaktemporary capacity grows32bytes/player in the sampled flop cases; returned persistent capacities identical. No GPU capacity or material broad claim.

Canonical iso-on compact cases2/6/10 median planner savings: {canonical[0]['median_savings_ms']:.10f},{canonical[1]['median_savings_ms']:.10f},{canonical[2]['median_savings_ms']:.10f}ms; sum **{savings:.10f}ms**. Frozen pre-native admission required at least{P['screen_minimum_savings_ms']:.10f}ms,1%of the prior accepted complete-cycle reference9802.7425ms, plus no majority component regression. The {report['reference_proxy_pct']:.10f}%reference ratio is a research-selection proxy, not a measured or universal complete-cycle gain/bound. Threshold fails; no integrated candidate, CUDA launch, full solver/primary/fresh16/broad/material/holdout/cumulative qualification or allocation-reuse placement/capacity/batching variant rescue. All9pairs percase remain, no exclusions/extensions/pooled timing. Root SHA{old.sha(R/'report.json')}; root replay is not external independent review. All{len(published)}reports/sources/receipts HTTP-byte verified. Accepted162/main157/live/protectedPTX and E051cumulative12.4372274192%unchanged. Last actual primary baselineB188. Goal active; return to GPU execution costs.
'''
nl=b'\r\n' if b'\r\n' in raw else b'\n';ledger.write_bytes(raw+note.encode('utf-8').replace(b'\n',nl));old.custody()
print(json.dumps({'status':report['status'],'checks':checks,'encoded_baseline_words':word_total,'canonical_component_savings_ms':savings,'frozen_required_ms':P['screen_minimum_savings_ms'],'reference_proxy_pct':report['reference_proxy_pct'],'published':len(published),'production_source_activated':False}),flush=True)
