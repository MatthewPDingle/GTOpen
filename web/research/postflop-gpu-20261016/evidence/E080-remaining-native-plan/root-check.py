"""Independently replay all native records, full raw bytes and strict decisions."""
from pathlib import Path
import datetime,importlib.util,json,math,re,statistics,sys
H=Path(__file__).resolve().parent;R=H.parent.parent;sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json');E=R/'runs/E080-remaining-native-execution';O=R/'comparisons/E080-remaining-native';D=R/'comparisons/E080-remaining-root-check';old.custody();assert not(R/'gpu-run.lock').exists()and not D.exists();D.mkdir()
for p,h in P['input_sha256'].items():old.pin(p,h)
checks=[]
def ck(label,ok):checks.append({'label':label,'passed':bool(ok)});assert ok,label
def markers(path,tag):return[json.loads(x.split(tag+' ',1)[1])for x in path.read_text(encoding='utf-8').splitlines()if tag+' 'in x]
def near(a,b):return math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-9)
def receipt(path):
    e=old.read(path);ck(str(path)+' terminal',e['returncode']==0 and e['error']is e['cleanup']is None);return e
def full_equal(a,b):
    if a.stat().st_size!=b.stat().st_size:return False
    with a.open('rb')as x,b.open('rb')as y:
        while True:
            left,right=x.read(1048576),y.read(1048576)
            if left!=right:return False
            if not left:return True
done=old.read(E/'complete.json');ck('all owned children terminal',done['all_children_terminal']);capacity=old.read(O/'capacity.json');caps={}
for arm in['baseline','candidate']:
    path=E/('capacity-'+arm)/'native.stdout.log';caps[arm]=markers(path,'E051_CAPACITY');ck(arm+' full capacity log agreement',caps[arm]==capacity['rows'][arm]);ck(arm+' exactly six capacity ids',[x['id']for x in caps[arm][:-1]]==list(range(6)));receipt(path.with_name('native.exit.json'))
    for i,row in enumerate(caps[arm][:-1]):ck(arm+' case '+str(i)+' actual assertions',row['actual_metadata_assertions_passed']and row['solver_iterations']==0)
for i,(b,c)in enumerate(zip(caps['baseline'],caps['candidate'])):ck('full owned accounting equal '+str(i),{k:v for k,v in b.items()if k!='device_wide_observation'}=={k:v for k,v in c.items()if k!='device_wide_observation'})
spec=importlib.util.spec_from_file_location('holdout_codec',P['codec']);codec=importlib.util.module_from_spec(spec);spec.loader.exec_module(codec);hold=old.read(O/'holdout.json');anchor=Path(P['historical_holdout'])/'stdout.log';gold=markers(anchor,'AUTORESEARCH_RESULT')[0];times={};previous=None
canon=lambda row:{k:v for k,v in row.items()if k not in codec.TIMINGS}
def points(log):return[{k:x[k]for k in['fixture_id','iteration','exploit_bits','exploit_pct_pot','exploit_chips']}for x in markers(log,'AUTORESEARCH_STAGE')if x.get('stage')=='convergence_check']
ck('fixed holdout order',P['holdout_order']==['H080B1','H080C1','H080C2','H080B2','H080B3','H080C3'])
for identity in P['holdout_order']:
    folder=E/identity;log=folder/'native.stdout.log';rows=markers(log,'AUTORESEARCH_RESULT');ck(identity+' one result',len(rows)==1);row=rows[0];ck(identity+' full record exact',canon(row)==canon(gold));ck(identity+' six quality checkpoints exact',points(log)==points(anchor)and len(points(log))==6)
    ck(identity+' real full clock',row['full_cycle_ms']>=sum(row[k]for k in['build_ms','init_ms','solve_ms','readback_ms']));raw=E/(identity+'.raw');ck(identity+' raw layout',codec.raw_layout(raw,row)==hold['rows'][identity]['raw']);ck(identity+' all raw bytes',full_equal(raw,Path(P['historical_raw'])))
    e=receipt(folder/'native.exit.json');inv=old.read(folder/'native.invocation.json');b=P['binaries']['holdout-'+P['holdout_arms'][identity]];ck(identity+' command',inv['command']==e['command']==[b['path'],'postflop_wide_turn_holdout','--ignored','--nocapture','--test-threads=1'])
    start=datetime.datetime.fromisoformat(e['started_at']);end=datetime.datetime.fromisoformat(e['finished_at']);ck(identity+' serialized',start<=end and(previous is None or previous<=start));previous=end;times[identity]=row['full_cycle_ms'];ck(identity+' report and raw times',hold['rows'][identity]['full_cycle_ms']==row['full_cycle_ms'])
b=[times[x['baseline']]for x in P['holdout_pairs']];c=[times[x['candidate']]for x in P['holdout_pairs']];bm,cm=statistics.median(b),statistics.median(c);slow=(cm/bm-1)*100;paired=[(cv/bv-1)*100 for bv,cv in zip(b,c)];guard=slow>0 and sum(x>0 for x in paired)>=2
ck('holdout strict guard arithmetic',hold['strict_guard_failed']==guard and hold['paired_slowdown_pct']==paired and near(hold['median_slowdown_pct'],slow));ck('holdout fixed decision',hold['status']==('rejected_repeatable_holdout_slowdown'if guard else'pass_fixed_holdout_nonregression'))
cumgain=None;cumguards=[]
if guard:
    ck('cumulative not executed after rejection',done['status']=='rejected_holdout'and done['cumulative_not_executed']and not(O/'cumulative.json').exists()and all(not(R/'runs'/x).exists()for x in P['cumulative_order']));status='pass_rejected_holdout'
else:
    cum=old.read(O/'cumulative.json');values={};gold_primary=old.historical.exact_raw('E020C1')
    ck('fixed cumulative order',P['cumulative_order']==['B272','E080O1','E080O2','B273','B274','E080O3'])
    for identity in P['cumulative_order']:
        folder=R/'runs'/identity;r=old.read(folder/'report.json');log=folder/'stdout.log';old.pin(log,r['stdout_sha256']);values[identity]=markers(log,'AUTORESEARCH_RESULT');ck(identity+' raw/report equality',values[identity]==r['results']);ck(identity+' complete records/checkpoints exact',old.historical.exact_raw(identity)==gold_primary)
        e=receipt(E/(identity+'.exit.json'));start=datetime.datetime.fromisoformat(e['started_at']);end=datetime.datetime.fromisoformat(e['finished_at']);ck(identity+' serialized',previous<=start<=end);previous=end;b=P['binaries']['original'if P['cumulative_arms'][identity]=='baseline'else'primary-candidate'];ck(identity+' binary/provenance',r['binary_sha256']==b['sha256']and r['binary_build_manifest']['sha256']==b['manifest_sha256']and r['binary_build_manifest']['data']==old.read(b['manifest']))
    totalb=totalc=0.0
    for i,name in enumerate(['rainbow','two-tone','river']):
        bs=[values[p['baseline']][i]['full_cycle_ms']for p in P['cumulative_pairs']];cs=[values[p['candidate']][i]['full_cycle_ms']for p in P['cumulative_pairs']];bm,cm=statistics.median(bs),statistics.median(cs);totalb+=bm;totalc+=cm;bad=cm>bm and sum(cv>bv for bv,cv in zip(bs,cs))>=2;cumguards.append({'fixture_id':name,'failed':bad});row=cum['fixtures'][i];ck(name+' exact median timings',row['baseline']['full_cycle_ms']['median_ms']==bm and row['candidate']['full_cycle_ms']['median_ms']==cm);ck(name+' strict guard',cum['strict_fixture_guards'][i]['failed']==bad)
    cumgain=100*(totalb-totalc)/totalb;passed=cumgain>=1 and not any(x['failed']for x in cumguards);ck('cumulative arithmetic',near(cum['observed_gain_pct'],cumgain)and cum['baseline_full_cycle_ms']==totalb and cum['candidate_full_cycle_ms']==totalc);ck('no timing pooling',cum['historical_timing_samples_used']==0);ck('cumulative fixed outcome',cum['performance']['passed']==passed and cum['status']==('pass_fresh_original_cumulative'if passed else'rejected_cumulative'));status='pass_remaining_timing_and_capacity_only'if passed else'pass_rejected_cumulative'
old.custody();report={'id':'E080-remaining-root-check','at':old.now(),'status':status,'checks':checks,'checks_passed':len(checks),'holdout_gain_pct':hold['observed_gain_pct'],'holdout_guard_failed':guard,'cumulative_gain_pct':cumgain,'cumulative_guards':cumguards,'actual_owned_capacity_equal_six_cases_each':True,'exact_holdout_records':6,'exact_holdout_checkpoints':36,'exact_holdout_full_raw_files':6,'exact_cumulative_records':0 if guard else 18,'exact_cumulative_checkpoints':0 if guard else 138,'protocol_sha256':sys.argv[1],'reports_sha256':{str(p):old.sha(p)for p in O.glob('*.json')},'candidate_accepted':False,'research_equivalence_cleared':False,'source_main_live_PTX_custody_pass':True,'limits':'Root arithmetic/raw-record/full-byte replay, not an external independent review or whole-resource proof. All samples retained. Actual CPU/host/GPU peak/capacity/responsiveness and final source/scope audit remain. The known failed experimental equivalence test stays failed.'};old.save(D/'report.json',report);print(json.dumps({'status':status,'holdout_gain_pct':hold['observed_gain_pct'],'cumulative_gain_pct':cumgain,'checks':len(checks)}),flush=True)
