"""Root arithmetic/raw-record cross-check of the fixed E047 initial screen."""
import datetime,json,math,statistics,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'small-gain-confirmation-plan'));import common as old
assert len(sys.argv)==2;old.pin(HERE/'protocol.json',sys.argv[1]);P=old.read(HERE/'protocol.json')
ROOT=old.ROOT;EX=ROOT/'runs/E047-native-execution';COMP=ROOT/'comparisons/E047-three-pair-comparison/report.json';q=old.read(COMP)
T=old.read(EX/'terminal.json');assert T['returncode']==0 and T['complete_sha256']==old.sha(EX/'complete.json')
old.custody();assert not (ROOT/'gpu-run.lock').exists()
O=ROOT/'comparisons/E047-root-crosscheck';assert not O.exists();O.mkdir();checks=0
def req(c,m):
 global checks
 assert c,m;checks+=1
anchor=old.exact_raw('E020C1');rs={};pins={};last=None
for identity in P['control_ids']+P['measurement_order']:
 r=old.read(ROOT/'runs'/identity/'report.json');rawp=ROOT/'runs'/identity/'stdout.log';old.pin(rawp,r['stdout_sha256']);raw=rawp.read_text(encoding='utf-8')
 req(r['status']=='measured' and r['returncode']==0,'successful native')
 receipt=old.read(EX/(identity+'.exit.json'));req(receipt['returncode']==0 and receipt['error'] is None and receipt['cleanup'] is None,'terminal child')
 start=datetime.datetime.fromisoformat(receipt['started_at']);end=datetime.datetime.fromisoformat(receipt['finished_at']);req(start<=end and (last is None or last<=start),'serialized wrapper order');last=end
 for f in [ROOT/'runs'/identity/'report.json',rawp,EX/(identity+'.exit.json')]:pins[str(f)]=old.sha(f)
 if identity in P['measurement_order']:
  req(old.exact_raw(identity)==anchor,'full non-timing payload/checkpoint exactness')
  values=[json.loads(x.split('AUTORESEARCH_RESULT ',1)[1]) for x in raw.splitlines() if 'AUTORESEARCH_RESULT ' in x]
  req(values==r['results'],'raw/report result agreement');rs[identity]=values
 req(r['provenance']['source_sha256']==old.BASE,'accepted sources during native')
fixture=[];bs=0.0;cs=0.0
for i,name in enumerate(['rainbow','two-tone','river']):
 b=[rs[p['baseline']][i]['full_cycle_ms'] for p in P['pairs']];c=[rs[p['candidate']][i]['full_cycle_ms'] for p in P['pairs']]
 bm,cm=statistics.median(b),statistics.median(c);g=100*(bm-cm)/bm;slower=sum(x>y for x,y in zip(c,b));fail=cm>bm and slower>=2
 f=q['fixtures'][i];req(f['baseline']['full_cycle_ms']['raw_ms']==b and f['candidate']['full_cycle_ms']['raw_ms']==c,'raw timing vectors');req(f['observed_gain_pct']==g,'fixture arithmetic')
 guard=q['performance']['fixture_regression_guard'][i];req(guard['failed']==fail and guard['slower_pairs']==slower,'strict fixture guard');bs+=bm;cs+=cm
 fixture.append({'fixture_id':name,'baseline_median_ms':bm,'candidate_median_ms':cm,'observed_gain_pct':g,'slower_pairs':slower,'fixture_guard_failed':fail,'components':{arm:{k:statistics.median([rs[p[arm]][i][k] for p in P['pairs']]) for k in ['build_ms','init_ms','solve_ms','readback_ms']} for arm in ['baseline','candidate']}})
bs=math.fsum(f['baseline_median_ms'] for f in fixture);cs=math.fsum(f['candidate_median_ms'] for f in fixture)
gain=100*(bs-cs)/bs;passed=gain>=1 and not any(f['fixture_guard_failed'] for f in fixture)
req(q['performance']['baseline_full_cycle_ms']==bs and q['performance']['candidate_full_cycle_ms']==cs and q['performance']['observed_gain_pct']==gain,'aggregate arithmetic')
req(q['performance']['primary_timing_pass']==passed and q['decision']==('advance_to_separately_frozen_confirmation' if passed else 'rejected'),'current policy outcome')
req(set(x['path'] for x in q['source_changes'])==set(P['candidate_owned_sha256']),'exact one-source scope')
req(q['excluded_samples']==[] and q['extension_runs']==0 and q['historical_timing_samples_used']==0,'no rescues/pooling')
old.custody()
report={'id':'E047-root-crosscheck','at':old.now(),'status':'pass_initial_timing_only' if passed else 'pass_rejected','checks':checks,'root_cross_check_only':True,'assessment_sha256':old.sha(COMP),'native_terminal_sha256':old.sha(EX/'terminal.json'),'aggregate_gain_pct':gain,'exact_fixture_results':18,'exact_checkpoints':138,'fixtures':fixture,'preserved_sha256':pins,'accepted162_restored':True,'main_live_ptx_unchanged':True,'candidate_accepted':False,'limits':'Separate stdlib arithmetic from retained raw records by root, not an external independent audit. Initial screen only; component medians are not an additive partition or cause attribution.'}
old.save(O/'report.json',report);print(json.dumps({'status':report['status'],'gain_pct':gain,'checks':checks,'report_sha256':old.sha(O/'report.json')}))
