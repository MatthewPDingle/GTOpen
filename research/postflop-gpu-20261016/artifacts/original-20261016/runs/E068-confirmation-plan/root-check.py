import datetime,json,math,statistics,sys
from pathlib import Path
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent/'accepted-E051'));import common_e051 as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
old.custody();assert not (old.ROOT/'gpu-run.lock').exists()
E=old.ROOT/'runs/E068-confirmation-execution';T=old.read(E/'terminal.json');assert T['returncode']==0 and T['complete_sha256']==old.sha(E/'complete.json')
QPATH=old.ROOT/'comparisons/E068-fresh16-confirmation/report.json';q=old.read(QPATH);records={};checks=0;previous=None
def require(c,m):
 global checks
 assert c,m;checks+=1
for identity in P['measurement_order']:
 r=old.read(old.ROOT/'runs'/identity/'report.json');raw=old.ROOT/'runs'/identity/'stdout.log';old.pin(raw,r['stdout_sha256']);text=raw.read_text(encoding='utf-8')
 records[identity]=[json.loads(x.split('AUTORESEARCH_RESULT ',1)[1]) for x in text.splitlines() if 'AUTORESEARCH_RESULT ' in x]
 require(records[identity]==r['results'],'raw/report result agreement')
 require(old.historical.exact_raw(identity)==old.historical.exact_raw('E020C1'),'full non-timing/checkpoint equality')
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
O=old.ROOT/'comparisons/E068-fresh16-root-check';O.mkdir();r={'id':'E068-fresh16-root-check','at':old.now(),'status':'pass_timing_only' if passed else 'pass_rejected','root_cross_check_only':True,'checks':checks,'aggregate_gain_pct':gain,'positive_pairs':positive,'pair_median_gain_pct':median,'block_median_gains_pct':blocks,'order_strata_median_gains_pct':strata,'assessment_sha256':old.sha(QPATH),'terminal_sha256':old.sha(E/'terminal.json'),'all96results_736checkpoints_exact':True,'candidate_accepted':False,'accepted162_main_live_ptx_unchanged':True,'limits':'Root stdlib arithmetic/raw-log replay, not an external independent audit or broader qualification.'};old.save(O/'report.json',r);print(json.dumps(r),flush=True)
