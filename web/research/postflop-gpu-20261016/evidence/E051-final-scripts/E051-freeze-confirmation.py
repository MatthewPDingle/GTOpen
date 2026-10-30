"""Freeze a separate fresh16pair cohort; initial timing observations cannot enter its score."""
import ast,json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;old.custody();assert not (ROOT/'gpu-run.lock').exists()
PRIOR=ROOT/'runs/E051-primary-plan';initial=ROOT/'comparisons/E051-three-pair-comparison/report.json';cross=ROOT/'comparisons/E051-root-crosscheck/report.json'
assert old.read(initial)['decision']=='advance_to_separately_frozen_confirmation'
assert old.read(cross)['status']=='pass_initial_timing_only'
H=ROOT/'runs/E051-confirmation-plan';H.mkdir()
native=(PRIOR/'native.py').read_text(encoding='utf-8').replace("OUT=ROOT/'runs/E051-native-execution'","OUT=ROOT/'runs/E051-confirmation-execution'")
start=native.index("assert len(P['control_ids'])==1");end=native.index("baseline=P['baseline_binary']",start)
native=native[:start]+'''assert P['control_ids']==[]
unit=read(ROOT/'runs/V051-unit/report.json');unitraw=ROOT/'runs/V051-unit/stdout.log';pin(unitraw,unit['stdout_sha256'])
assert unit['returncode']==0 and unit['status']=='measured'
assert re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',unitraw.read_text(encoding='utf-8'))==[('84','0','4','0','0')]
save(OUT/'controls-complete.json',{'at':now(),'previously_terminal_unit':'V051-unit','unit_report_sha256':sha(ROOT/'runs/V051-unit/report.json'),'gpu_control_report_sha256':sha(Path(P['gpu_control_report']['path'])),'no_control_reexecution':True,'all_passed':True})
'''+native[end:]
native=native.replace("'fixture_results':18,'convergence_records':138","'fixture_results':3*len(P['measurement_order']),'convergence_records':23*len(P['measurement_order'])")
native=native.replace('ordinary units then one fixed3-pair complete-cycle screen','fresh16pair complete-cycle confirmation').replace('fixed primary complete; assess before any confirmation.','fresh16pair confirmation complete; assess before any adoption.')
(H/'native.py').write_text(native,encoding='utf-8')
assessment=r'''import datetime,json,math,statistics,sys
from pathlib import Path
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent/'small-gain-confirmation-plan'));import common as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
old.custody();assert not (old.ROOT/'gpu-run.lock').exists()
E=old.ROOT/'runs/E051-confirmation-execution';done=old.read(E/'complete.json');terminal=old.read(E/'terminal.json')
assert terminal['returncode']==0 and terminal['complete_sha256']==old.sha(E/'complete.json')
assert done['protocol_sha256']==sys.argv[1] and done['measurement_order']==P['measurement_order']
assert done['fixture_results']==96 and done['convergence_records']==736
anchor=old.exact_raw('E020C1');runs={};pins={};last=None;environment=None;gpu=None
for identity in P['measurement_order']:
 receipt=old.read(E/(identity+'.exit.json'));assert receipt['returncode']==0 and receipt['error'] is receipt['cleanup'] is None
 start=datetime.datetime.fromisoformat(receipt['started_at']);end=datetime.datetime.fromisoformat(receipt['finished_at']);assert start<=end and (last is None or last<=start);last=end
 r=old.read(old.ROOT/'runs'/identity/'report.json');assert r['returncode']==0 and r['status']=='measured'
 assert r['provenance']['source_sha256']==old.BASE
 ns=datetime.datetime.fromisoformat(r['started_at'].replace('Z','+00:00'));ne=datetime.datetime.fromisoformat(r['finished_at'].replace('Z','+00:00'));assert start.replace(microsecond=0)<=ns<=ne<=end
 old.compare.validate_run(r,pins);assert old.exact_raw(identity)==anchor
 if environment is None:environment=r['environment'];gpu=old.compare.gpu_identity(r)
 assert r['environment']==environment and old.compare.gpu_identity(r)==gpu
 runs[identity]=r
 for path in [old.ROOT/'runs'/identity/'report.json',old.ROOT/'runs'/identity/'stdout.log',E/(identity+'.exit.json')]:pins[str(path)]=old.sha(path)
fixtures=[]
for i,name in enumerate(['rainbow','two-tone','river']):
 b=[runs[p['baseline']]['results'][i]['full_cycle_ms'] for p in P['pairs']];c=[runs[p['candidate']]['results'][i]['full_cycle_ms'] for p in P['pairs']]
 assert len(b)==len(c)==16
 bm,cm=statistics.median(b),statistics.median(c);slower=sum(y>x for x,y in zip(b,c));fail=cm>bm and slower>=9
 fixtures.append({'fixture_id':name,'baseline_ms':b,'candidate_ms':c,'baseline_median_ms':bm,'candidate_median_ms':cm,'gain_pct':100*(bm-cm)/bm,'paired_slowdown_pct':[100*(y-x)/x for x,y in zip(b,c)],'slower_pairs':slower,'fixture_guard_failed':fail})
bs=math.fsum(f['baseline_median_ms'] for f in fixtures);cs=math.fsum(f['candidate_median_ms'] for f in fixtures);gain=100*(bs-cs)/bs
pairs=[]
for i,p in enumerate(P['pairs']):
 b=math.fsum(x['full_cycle_ms'] for x in runs[p['baseline']]['results']);c=math.fsum(x['full_cycle_ms'] for x in runs[p['candidate']]['results'])
 pairs.append({'pair':i+1,'baseline':p['baseline'],'candidate':p['candidate'],'order':p['order'],'baseline_sum_ms':b,'candidate_sum_ms':c,'gain_pct':100*(b-c)/b})
positive=sum(x['gain_pct']>0 for x in pairs);median=statistics.median(x['gain_pct'] for x in pairs)
blocks=[statistics.median(x['gain_pct'] for x in pairs[i:i+4]) for i in range(0,16,4)]
strata={order:statistics.median(x['gain_pct'] for x in pairs if x['order']==order) for order in ['BC','CB']}
gates={'aggregate_at_least1pct':gain>=1,'at_least13_positive_pairs':positive>=13,'positive_pair_median':median>0,'all4block_medians_positive':all(x>0 for x in blocks),'both_order_strata_positive':all(x>0 for x in strata.values()),'no_fixture_regression':not any(x['fixture_guard_failed'] for x in fixtures),'all96results_736checkpoints_exact':True}
passed=all(gates.values());O=old.ROOT/'comparisons/E051-fresh16-confirmation';O.mkdir()
report={'id':'E051-fresh16-confirmation','at':old.now(),'protocol_sha256':sys.argv[1],'status':'pass_fresh16_timing_only' if passed else 'rejected','decision':'advance_to_broader_qualification_only' if passed else 'rejected','candidate_accepted':False,'performance':{'baseline_full_cycle_ms':bs,'candidate_full_cycle_ms':cs,'observed_gain_pct':gain,'required_gain_pct':1,'positive_pairs':positive,'required_positive_pairs':13,'pair_median_gain_pct':median,'block_median_gains_pct':blocks,'order_strata_median_gains_pct':strata,'fresh_confirmation_pass':passed},'gates':gates,'fixtures':fixtures,'pairs':pairs,'exactness':{'full_results':96,'convergence_checkpoints':736,'all_exact':True},'excluded_samples':[],'extension_runs':0,'historical_timing_samples_used':0,'native_terminal_sha256':old.sha(E/'terminal.json'),'preserved_sha256':pins,'adoption_requirements':P['adoption_requirements'],'limits':'Fresh warm-cache complete-cycle timing confirmation on three registered fixtures/RTX5090 only. No statistical-significance/universal/no-cost claim. Broader,F32,state/menu/resume/continuation,holdout,fresh-original cumulative and actual material-cost evidence remain required.'}
old.save(O/'report.json',report);print(json.dumps({'status':report['status'],'performance':report['performance'],'gates':gates,'report_sha256':old.sha(O/'report.json')},indent=2),flush=True)
'''
(H/'assess.py').write_text(assessment,encoding='utf-8')
root=r'''import datetime,json,math,statistics,sys
from pathlib import Path
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent/'small-gain-confirmation-plan'));import common as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
old.custody();assert not (old.ROOT/'gpu-run.lock').exists()
E=old.ROOT/'runs/E051-confirmation-execution';T=old.read(E/'terminal.json');assert T['returncode']==0 and T['complete_sha256']==old.sha(E/'complete.json')
QPATH=old.ROOT/'comparisons/E051-fresh16-confirmation/report.json';q=old.read(QPATH);records={};checks=0;previous=None
def require(c,m):
 global checks
 assert c,m;checks+=1
for identity in P['measurement_order']:
 r=old.read(old.ROOT/'runs'/identity/'report.json');raw=old.ROOT/'runs'/identity/'stdout.log';old.pin(raw,r['stdout_sha256']);text=raw.read_text(encoding='utf-8')
 records[identity]=[json.loads(x.split('AUTORESEARCH_RESULT ',1)[1]) for x in text.splitlines() if 'AUTORESEARCH_RESULT ' in x]
 require(records[identity]==r['results'],'raw/report result agreement')
 require(old.exact_raw(identity)==old.exact_raw('E020C1'),'full non-timing/checkpoint equality')
 require(r['status']=='measured' and r['returncode']==0 and r['provenance']['source_sha256']==old.BASE,'valid restored-source native process')
 e=old.read(E/(identity+'.exit.json'));require(e['returncode']==0 and e['error'] is e['cleanup'] is None,'terminal child')
 start=datetime.datetime.fromisoformat(e['started_at']);end=datetime.datetime.fromisoformat(e['finished_at']);require(start<=end and (previous is None or previous<=start),'serialized command order');previous=end
f=[]
for i,name in enumerate(['rainbow','two-tone','river']):
 b=[records[p['baseline']][i]['full_cycle_ms'] for p in P['pairs']];c=[records[p['candidate']][i]['full_cycle_ms'] for p in P['pairs']]
 bm,cm=statistics.median(b),statistics.median(c);slower=sum(cv>bv for bv,cv in zip(b,c));fail=(cm>bm and slower>=9)
 declared=q['fixtures'][i];require(declared['baseline_ms']==b and declared['candidate_ms']==c,'exact16 timing observations per arm')
 require(declared['baseline_median_ms']==bm and declared['candidate_median_ms']==cm and declared['gain_pct']==100*(bm-cm)/bm,'fixture medians/arithmetic')
 require(declared['slower_pairs']==slower and declared['fixture_guard_failed']==fail,'strict9of16 fixture guard')
 f.append((bm,cm,fail))
bs=math.fsum(x[0] for x in f);cs=math.fsum(x[1] for x in f);gain=100*(bs-cs)/bs
g=[];orders=[]
for i,p in enumerate(P['pairs']):
 b=math.fsum(x['full_cycle_ms'] for x in records[p['baseline']]);c=math.fsum(x['full_cycle_ms'] for x in records[p['candidate']]);v=100*(b-c)/b;g.append(v);orders.append(p['order'])
 require(q['pairs'][i]['gain_pct']==v and q['pairs'][i]['baseline_sum_ms']==b and q['pairs'][i]['candidate_sum_ms']==c,'paired complete-cycle arithmetic')
positive=sum(x>0 for x in g);median=statistics.median(g);blocks=[statistics.median(g[j:j+4]) for j in range(0,16,4)];strata={o:statistics.median([v for v,k in zip(g,orders) if k==o]) for o in ['BC','CB']}
passed=gain>=1 and positive>=13 and median>0 and all(v>0 for v in blocks) and all(v>0 for v in strata.values()) and not any(x[2] for x in f)
v=q['performance'];require((v['baseline_full_cycle_ms'],v['candidate_full_cycle_ms'],v['observed_gain_pct'])==(bs,cs,gain),'aggregate arithmetic')
require(v['positive_pairs']==positive and v['pair_median_gain_pct']==median and v['block_median_gains_pct']==blocks and v['order_strata_median_gains_pct']==strata,'quorum/block/order arithmetic')
require(v['fresh_confirmation_pass']==passed and q['status']==('pass_fresh16_timing_only' if passed else 'rejected'),'frozen decision')
require(q['excluded_samples']==[] and q['extension_runs']==0 and q['historical_timing_samples_used']==0,'no sample exclusions/pooling/extensions')
require(q['exactness']=={'full_results':96,'convergence_checkpoints':736,'all_exact':True} and q['candidate_accepted'] is False,'scope and exactness')
O=old.ROOT/'comparisons/E051-fresh16-root-check';O.mkdir();r={'id':'E051-fresh16-root-check','at':old.now(),'status':'pass_timing_only' if passed else 'pass_rejected','root_cross_check_only':True,'checks':checks,'aggregate_gain_pct':gain,'positive_pairs':positive,'pair_median_gain_pct':median,'block_median_gains_pct':blocks,'order_strata_median_gains_pct':strata,'assessment_sha256':old.sha(QPATH),'terminal_sha256':old.sha(E/'terminal.json'),'all96results_736checkpoints_exact':True,'candidate_accepted':False,'accepted162_main_live_ptx_unchanged':True,'limits':'Root stdlib arithmetic/raw-log replay, not an external independent audit or broader qualification.'};old.save(O/'report.json',r);print(json.dumps(r),flush=True)
'''
(H/'root-check.py').write_text(root,encoding='utf-8')
for name in ['native.py','assess.py','root-check.py']:ast.parse((H/name).read_text(encoding='utf-8'))
p=old.read(PRIOR/'protocol.json');p.update(id='E051-fresh16-confirmation',at=old.now(),control_ids=[],previously_terminal_unit_id='V051-unit')
pairs=[];order=[]
for i in range(16):
 b='B'+str(152+i);c='E051C'+str(i+1).zfill(2);which=['BC','CB','CB','BC'][i%4]
 pairs.append({'baseline':b,'candidate':c,'order':which});order.extend([b,c] if which=='BC' else [c,b])
p.update(pairs=pairs,measurement_order=order,policy={'minimum_complete_cycle_gain_pct':1.0,'fixture_guard':'Positive per-fixture median slowdown and at least9of16 slower pairs rejects, noepsilon.','quorum':'At least13of16 positive paired summed-cycle gains, positive median paired gain, all4nonoverlapping4pair block medians positive and both8pair BC/CBorder medians positive.','exactness':'All96full non-timing results and736checkpoints exact against frozen E020C1.','sampling':'Exactly16freshpairs; no initial/historical timing pooling, exclusions, extensions or rescue samples.','scope':'Timing confirmation only; broader/holdout/cumulative/no-material-cost requirements still apply.'})
p['scope']='Separately frozen fresh16pair warm-cache confirmation only. Source/binaries/quality/stops remain exact. Initial3pair timing observations are prerequisites only and never scored.'
paths=[H/n for n in ['native.py','assess.py','root-check.py']]+[PRIOR/'protocol.json',PRIOR/'primary-publication.json',initial,cross,ROOT/'runs/E051-native-execution/complete.json',ROOT/'runs/E051-native-execution/terminal.json',ROOT/'runs/V051-unit/report.json',ROOT/'runs/V051-unit/stdout.log']
p['input_sha256']={k:v for k,v in p['input_sha256'].items() if Path(k).name not in ['native.py','assess.py','root-check.py']}|{str(x):old.sha(x) for x in paths}
st=old.read(ar.STATUS)
for identity in order:assert not (ROOT/'runs'/identity).exists() and not any(x['id']==identity for x in st['experiments'])
assert len(order)==32 and len(set(order))==32 and sum(x['order']=='BC' for x in pairs)==8
old.save(H/'protocol.json',p)
published={}
for src in H.rglob('*'):
 if not src.is_file():continue
 key=H.name+'/'+src.relative_to(H).as_posix();dst=ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(src.read_bytes())
 with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==src.read_bytes()
 published[key]=old.sha(src)
old.save(H/'pre-native-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published,'new_confirmation_samples':0})
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(ar.STATUS);e=next(x for x in st['experiments'] if x['id']=='E051');e.update(status='preparing',stage='Frozen fresh16pair confirmation; native next',reason='Initial1.8437102311% passes. Separate32fresh processes; at least13positive pairs,aggregate1%,positive all4blocks/bothorders,no fixture slowdown. No initial timing pooling or adoption.');e['evidence'].append({'label':'E051 fresh16pair prospective protocol','url':'evidence/E051-confirmation-plan/protocol.json'});st.update(state='running',stage='E051 fresh16pair confirmation',activity='Fixed B152-B167 and E051C01-C16 in balanced BC/CBorder; no new accepted gain.',updated_at=ar.now());ar.atomic_json(ar.STATUS,st)
old.custody();print(json.dumps({'protocol_sha256':old.sha(H/'protocol.json'),'measurements':len(order),'pairs':len(pairs),'published':len(published)}),flush=True)
