"""Separate full-log/scientific-record and timing-arithmetic replay."""
import sys,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/E108-primary-plan';P=h.read(H/'protocol.json');Q=h.read(ROOT/'comparisons/E108-three-pair-comparison/report.json');anchor=h.read(h.EPOCH/'exact-anchor.json')
assert Q['protocol_sha256']==h.sha(H/'protocol.json');h.custody()
checks=0
def req(v):
 global checks
 assert v;checks+=1
for p,digest in P['input_sha256'].items():req(h.sha(p)==digest)
reports={};raws={};results={}
for rec in P['sequence']:
 ident=rec['id'];D=ROOT/'runs'/ident;r=h.read(D/'report.json');raw=(D/'stdout.log').read_bytes();req(hashlib.sha256(raw).hexdigest()==r['stdout_sha256']);req(r['status']=='measured'and r['returncode']==0)
 if rec['unit']:req(b'test result: ok. 86 passed; 0 failed; 4 ignored;'in raw);continue
 text=raw.decode('utf-8');out=[json.loads(l.partition('AUTORESEARCH_RESULT ')[2])for l in text.splitlines()if'AUTORESEARCH_RESULT 'in l]
 req(out==r['results']);req([v['fixture_id']for v in out]==['rainbow','two-tone','river'])
 stripped=[{k:v for k,v in x.items()if k not in{'build_ms','fingerprint_ms_excluded','full_cycle_ms','init_ms','readback_ms','solve_ms'}}for x in out]
 req(stripped==anchor[0]);stages=[json.loads(l.partition('AUTORESEARCH_STAGE ')[2])for l in text.splitlines()if'AUTORESEARCH_STAGE 'in l]
 checkpoints=[{k:x[k]for k in['fixture_id','iteration','exploit_bits','exploit_pct_pot','exploit_chips']}for x in stages if x.get('stage')=='convergence_check'];req(checkpoints==anchor[1]);req(len(checkpoints)==23)
 reports[ident]=r;results[ident]={x['fixture_id']:x['full_cycle_ms']for x in out}
base=0.;cand=0.;guard=[]
for fid in['rainbow','two-tone','river']:
 b=[results[p['baseline']][fid]for p in P['pairs']];c=[results[p['candidate']][fid]for p in P['pairs']];bm=sorted(b)[1];cm=sorted(c)[1]
 base+=bm;cand+=cm;slower=sum(y>x for x,y in zip(b,c));failed=cm>bm and slower>=2;guard.append(failed)
 f=next(x for x in Q['fixtures']if x['fixture_id']==fid);req(f['baseline_ms']==b and f['candidate_ms']==c);req(f['baseline_median_ms']==bm and f['candidate_median_ms']==cm);req(f['guard_failed']==failed)
 for i,(x,y)in enumerate(zip(b,c)):req(abs(f['paired_gain_pct'][i]-100*(x-y)/x)<1e-10)
gain=100*(base-cand)/base;passed=gain>=1 and not any(guard);perf=Q['performance']
req(perf['baseline_full_cycle_ms']==base and perf['candidate_full_cycle_ms']==cand);req(perf['observed_gain_pct']==gain and perf['primary_timing_pass']==passed)
req(Q['decision']==('advance_to_separately_frozen_confirmation'if passed else'rejected'));req(not Q['excluded_samples']and Q['extension_runs']==Q['historical_timing_samples_used']==Q['RAM_baseline_samples_scored']==0)
req(Q['exactness']=={'fixture_results':18,'convergence_records':138,'all_exact':True})
D=ROOT/'comparisons/E108-root-crosscheck';D.mkdir(exist_ok=False)
h.save(D/'report.json',{'id':'E108-root-crosscheck','at':h.now(),'status':'pass_initial_timing_only'if passed else'pass_rejected','checks':checks,'protocol_sha256':h.sha(H/'protocol.json'),'assessment_sha256':h.sha(ROOT/'comparisons/E108-three-pair-comparison/report.json'),'baseline_ms':base,'candidate_ms':cand,'aggregate_gain_pct':gain,'full_scientific_records_exact':18,'full_checkpoints_exact':138,'ordinary_units_passed':86,'all_observations_retained':True,'candidate_accepted':False,'scope':'Independent parsing of complete retained logs and all non-timing records, sorted three-value medians and strict fixture guards. Raw primary arena bytes were not independently compared; exact full arena fingerprints are included in scientific records. No significance or adoption from this screen.'})
print(json.dumps({'status':'pass','checks':checks,'gain_pct':gain,'timing_pass':passed}),flush=True)
