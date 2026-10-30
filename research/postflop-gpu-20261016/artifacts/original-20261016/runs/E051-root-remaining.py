"""Root replay from immutable raw logs and full bytes; no tests or edits."""
import datetime,importlib.util,json,math,re,statistics,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
H=ROOT/'runs/E051-remaining-native-plan-r3';E=ROOT/'runs/E051-remaining-native-execution-r3';O=ROOT/'comparisons/E051-remaining-native-r3';R=ROOT/'comparisons/E051-remaining-root-check'
old.custody();assert not (ROOT/'gpu-run.lock').exists();assert not R.exists();R.mkdir();checks=[]
def ck(label,value):
 checks.append({'label':label,'passed':bool(value)});assert value,label
def markers(p,tag):return [json.loads(x.split(tag+' ',1)[1]) for x in p.read_text(encoding='utf-8').splitlines() if tag+' ' in x]
def near(a,b):return math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-9)
def equalfile(a,b):
 if a.stat().st_size!=b.stat().st_size:return False
 with a.open('rb') as x,b.open('rb') as y:
  while True:
   l,r=x.read(1048576),y.read(1048576)
   if l!=r:return False
   if not l:return True
P=old.read(H/'protocol.json');done=old.read(E/'complete.json');ck('all children terminal',done['all_children_terminal']);ck('same frozen execution protocol',done['protocol_sha256']==old.sha(H/'protocol.json'))
for p,h in P['input_sha256'].items():old.pin(p,h)
capacity=old.read(O/'capacity.json');rawcapacity={}
for arm in ['baseline','candidate']:
 path=ROOT/'runs/E051-remaining-native-execution'/('capacity-'+arm)/'native.stdout.log';rows=markers(path,'E051_CAPACITY');rawcapacity[arm]=rows
 ck(arm+' capacity report equals raw',rows==capacity['rows'][arm]);ck(arm+' capacity exactly six ids',[r['id'] for r in rows[:-1]]==list(range(6)))
 exitpath=path.with_name('native.exit.json');receipt=old.read(exitpath);ck(arm+' capacity terminal0',receipt['returncode']==0 and receipt['error'] is None and receipt['cleanup'] is None)
 for i,r in enumerate(rows[:-1]):
  ck(arm+' case'+str(i)+' same fixed board/pot/stack',(r['board'],r['pot'],r['stack'])==[(b,p,s) for b in ['KsQs2d','KsQs2s','KsQh2d'] for p,s in [(39.5,80.0),(93.5,155.0)]][i])
  ck(arm+' case'+str(i)+' assertions and no iterations',r['actual_metadata_assertions_passed'] is True and r['solver_iterations']==0)
for i,(b,c) in enumerate(zip(rawcapacity['baseline'],rawcapacity['candidate'])):
 ck('capacity full owned accounting equal '+str(i),{k:v for k,v in b.items() if k!='device_wide_observation'}=={k:v for k,v in c.items() if k!='device_wide_observation'})
hold=old.read(O/'holdout.json');anchorlog=Path(P['historical_holdout'])/'stdout.log';anchorresult=markers(anchorlog,'AUTORESEARCH_RESULT')[0]
TIMING={'build_ms','init_ms','solve_ms','readback_ms','full_cycle_ms','fingerprint_ms_excluded'}
canon=lambda r:{k:v for k,v in r.items() if k not in TIMING}
def checkpoints(log):return [{k:r[k] for k in ['fixture_id','iteration','exploit_bits','exploit_pct_pot','exploit_chips']} for r in markers(log,'AUTORESEARCH_STAGE') if r.get('stage')=='convergence_check']
spec=importlib.util.spec_from_file_location('holdout_codec',P['codec']);codec=importlib.util.module_from_spec(spec);spec.loader.exec_module(codec)
holddurations={};previous=None
for identity in P['holdout_order']:
 d=E/identity;log=d/'native.stdout.log';rows=markers(log,'AUTORESEARCH_RESULT');ck(identity+' exactly one result',len(rows)==1);r=rows[0]
 ck(identity+' full non-timing exact historical',canon(r)==canon(anchorresult));ck(identity+' six checkpoints exact',checkpoints(log)==checkpoints(anchorlog) and len(checkpoints(log))==6)
 ck(identity+' successful exact one native test',re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',log.read_text())==[('1','0','0','0','0')])
 ck(identity+' real outer wall includes components',r['full_cycle_ms']>=sum(r[k] for k in ['build_ms','init_ms','solve_ms','readback_ms']))
 raw=E/(identity+'.raw');layout=codec.raw_layout(raw,r);ck(identity+' raw codec/hash same report',layout==hold['rows'][identity]['raw']);ck(identity+' entire raw file same historical',equalfile(raw,Path(P['historical_raw'])))
 receipt=old.read(d/'native.exit.json');inv=old.read(d/'native.invocation.json');ck(identity+' native receipt',receipt['returncode']==0 and receipt['error'] is None and receipt['cleanup'] is None and inv['command']==receipt['command'])
 binary=P['binaries']['holdout-'+P['holdout_arms'][identity]];ck(identity+' selected correct arm',receipt['command']==[binary['path'],'postflop_wide_turn_holdout','--ignored','--nocapture','--test-threads=1'])
 start=datetime.datetime.fromisoformat(receipt['started_at']);end=datetime.datetime.fromisoformat(receipt['finished_at']);ck(identity+' serial timestamps',start<=end and (previous is None or previous<=start));previous=end
 ck(identity+' parsed report equals raw',hold['rows'][identity]['non_timing']==canon(r) and hold['rows'][identity]['full_cycle_ms']==r['full_cycle_ms'] and hold['rows'][identity]['checks']==checkpoints(log));holddurations[identity]=r['full_cycle_ms']
b=[holddurations[x['baseline']] for x in P['holdout_pairs']];c=[holddurations[x['candidate']] for x in P['holdout_pairs']];bm,cm=statistics.median(b),statistics.median(c);slow=(cm/bm-1)*100;paired=[(y/x-1)*100 for x,y in zip(b,c)];guard=slow>0 and sum(x>0 for x in paired)>=2
ck('holdout fixed BC/CB/BC order',P['holdout_order']==['H051B1','H051C1','H051C2','H051B2','H051B3','H051C3']);ck('holdout medians/guard replay',near(hold['median_slowdown_pct'],slow) and hold['paired_slowdown_pct']==paired and hold['strict_guard_failed']==guard);ck('holdout no repeatable slowdown',not guard)
cum=old.read(O/'cumulative.json');results={};anchor=old.exact_raw('E020C1');allpins={}
for identity in P['cumulative_order']:
 d=ROOT/'runs'/identity;r=old.read(d/'report.json');log=d/'stdout.log';old.pin(log,r['stdout_sha256']);raw=markers(log,'AUTORESEARCH_RESULT');ck(identity+' report same all raw results',raw==r['results'])
 ck(identity+' all complete payloads exact',([canon(x) for x in raw],checkpoints(log))==anchor)
 ck(identity+' same quality and stops',[x['iteration'] for x in raw]==[200,200,60] and all(x['target_met'] for x in raw));receipt=old.read(E/(identity+'.exit.json'));ck(identity+' terminal receipt',receipt['returncode']==0 and receipt['error'] is None and receipt['cleanup'] is None)
 start=datetime.datetime.fromisoformat(receipt['started_at']);end=datetime.datetime.fromisoformat(receipt['finished_at']);ck(identity+' serial timestamps',previous<=start<=end);previous=end
 bpin=P['binaries']['original' if P['cumulative_arms'][identity]=='baseline' else 'primary-candidate'];ck(identity+' build provenance binary pinned',r['binary_sha256']==bpin['sha256'] and r['binary_build_manifest']['sha256']==bpin['manifest_sha256'] and r['binary_build_manifest']['data']==old.read(bpin['manifest']))
 results[identity]=raw;allpins[str(d/'report.json')]=old.sha(d/'report.json');allpins[str(log)]=old.sha(log)
bs=cs=0.0;guards=[]
for i,f in enumerate(['rainbow','two-tone','river']):
 b=[results[p['baseline']][i]['full_cycle_ms'] for p in P['cumulative_pairs']];c=[results[p['candidate']][i]['full_cycle_ms'] for p in P['cumulative_pairs']];bm,cm=statistics.median(b),statistics.median(c);bs+=bm;cs+=cm
 slow=(cm/bm-1)*100;paired=[(y/x-1)*100 for x,y in zip(b,c)];guard=slow>0 and sum(x>0 for x in paired)>=2;guards.append({'fixture_id':f,'median_slowdown_pct':slow,'paired_slowdown_pct':paired,'failed':guard})
 row=cum['fixtures'][i];ck(f+' raw medians',near(row['baseline']['full_cycle_ms']['median_ms'],bm) and near(row['candidate']['full_cycle_ms']['median_ms'],cm));ck(f+' no strict repeatable slowdown',not guard)
gain=(bs-cs)/bs*100;ck('cumulative unrounded totals/gain',near(cum['baseline_full_cycle_ms'],bs) and near(cum['candidate_full_cycle_ms'],cs) and near(cum['observed_gain_pct'],gain));ck('cumulative current1%gate',gain>=1 and cum['performance']['required_gain_pct']==1.0);ck('cumulative six fixed processes no old timing',P['cumulative_order']==['B168','E051O1','E051O2','B169','B170','E051O3'] and cum['historical_timing_samples_used']==0)
old.custody();old.save(R/'report.json',{'at':old.now(),'status':'pass_remaining_root_replay','checks':checks,'checks_passed':len(checks),'holdout_gain_pct':hold['observed_gain_pct'],'cumulative_baseline_ms':bs,'cumulative_candidate_ms':cs,'cumulative_gain_pct':gain,'cumulative_guards':guards,'actual_capacity_equal6cases':True,'exact_holdout_full_payloads':6,'exact_holdout_checkpoints':36,'exact_holdout_full_raw_files':6,'exact_cumulative_full_payloads':18,'exact_cumulative_checkpoints':138,'protocol_sha256':old.sha(H/'protocol.json'),'reports_sha256':{str(p):old.sha(p) for p in O.glob('*.json')},'raw_report_pins':allpins,'accepted162_main_live_ptx_unchanged':True,'independent_external_review':False,'candidate_accepted':False})
print(json.dumps({'status':'pass_remaining_root_replay','checks':len(checks),'cumulative_gain_pct':gain,'report_sha256':old.sha(R/'report.json')}),flush=True)
