import json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/E103-primary-plan';P=h.read(H/'protocol.json');Q=h.read(ROOT/'comparisons/E103-three-pair-comparison/report.json');anchor=h.read(ROOT/'epoch/exact-anchor.json');h.custody();checks=0
def req(v):
 global checks
 assert v;checks+=1
req(Q['protocol_sha256']==h.sha(H/'protocol.json'))
for p,d in P['input_sha256'].items():req(h.sha(p)==d)
values={};times={}
for row in P['sequence']:
 D=ROOT/'runs'/row['id'];r=h.read(D/'report.json');raw=(D/'stdout.log').read_bytes();req(hashlib.sha256(raw).hexdigest()==r['stdout_sha256']);exit_=h.read(D/'exit.json');req(exit_['returncode']==r['returncode']==0 and exit_['error'] is exit_['cleanup'] is None)
 if row['kind']=='unit':req(b'test result: ok. 86 passed; 0 failed; 4 ignored;' in raw);continue
 lines=raw.decode('utf-8').splitlines();results=[json.loads(x.partition('AUTORESEARCH_RESULT ')[2]) for x in lines if 'AUTORESEARCH_RESULT ' in x];req(results==r['results']);req([x['fixture_id'] for x in results]==['rainbow','two-tone','river'])
 excluded={'build_ms','fingerprint_ms_excluded','full_cycle_ms','init_ms','readback_ms','solve_ms'}
 req([{k:v for k,v in x.items() if k not in excluded} for x in results]==anchor[0])
 stages=[json.loads(x.partition('AUTORESEARCH_STAGE ')[2]) for x in lines if 'AUTORESEARCH_STAGE ' in x];conv=[{k:x[k] for k in ['fixture_id','iteration','exploit_bits','exploit_pct_pot','exploit_chips']} for x in stages if x.get('stage')=='convergence_check'];req(conv==anchor[1] and len(conv)==23)
 if row['kind']=='warmup':continue
 values[row['id']]={x['fixture_id']:x['full_cycle_ms'] for x in results};t=exit_['terminal_process_times'];req(t['CPU_ms']==(t['kernel_100ns']+t['user_100ns'])/10000 and t['lifetime_ms']==(t['exit_FILETIME']-t['creation_FILETIME'])/10000)
 times[row['id']]={**t,'parent_wall_ms':exit_['parent_wall_ms']};req(exit_['parent_wall_ms']>=t['lifetime_ms'])
bs=cs=0.;failed=[]
for name in ['rainbow','two-tone','river']:
 b=[values[x['baseline']][name] for x in P['pairs']];c=[values[x['candidate']][name] for x in P['pairs']];bm=sorted(b)[1];cm=sorted(c)[1];bs+=bm;cs+=cm
 slow=sum(y>x for x,y in zip(b,c));bad=cm>bm and slow>=2;failed.append(bad);f=next(x for x in Q['fixtures'] if x['fixture_id']==name)
 req(f['baseline_ms']==b and f['candidate_ms']==c and f['baseline_median_ms']==bm and f['candidate_median_ms']==cm)
 req(f['slower_pairs']==slow and f['guard_failed']==bad and f['gain_pct']==100*(bm-cm)/bm)
gain=100*(bs-cs)/bs;gates={'aggregate_ge1pct':gain>=1.,'strict_fixture_clear':not any(failed)}
for metric in ['CPU_ms','lifetime_ms','parent_wall_ms']:
 b=[times[x['baseline']][metric] for x in P['pairs']];c=[times[x['candidate']][metric] for x in P['pairs']];delta=100*(sorted(c)[1]/sorted(b)[1]-1);cost=Q['whole_process_costs'][metric]
 req(cost['baseline']==b and cost['candidate']==c and cost['median_regression_pct']==delta);gates[metric+'_median_regression_le1pct']=delta<=1.
passed=all(gates.values());perf=Q['performance'];req(perf['baseline_full_cycle_ms']==bs and perf['candidate_full_cycle_ms']==cs and perf['observed_gain_pct']==gain and perf['gates']==gates and perf['primary_timing_and_cost_pass']==passed)
req(Q['decision']==('advance_to_separately_frozen_confirmation' if passed else 'rejected_closed'));req(not Q['excluded_samples'] and Q['extension_runs']==Q['historical_or_RAM_reference_samples_used']==0)
D=ROOT/'comparisons/E103-root-crosscheck';D.mkdir(exist_ok=False);h.save(D/'report.json',{'id':'E103-root-crosscheck','at':h.now(),'status':'pass_initial_screen_only' if passed else 'pass_rejection_replay','checks':checks,'primary_report_sha256':h.sha(ROOT/'comparisons/E103-three-pair-comparison/report.json'),'protocol_sha256':h.sha(H/'protocol.json'),'baseline_ms':bs,'candidate_ms':cs,'observed_gain_pct':gain,'gates':gates,'all_complete_logs_science_and_checkpoints_exact':True,'ordinary_units_per_arm':86,'full_records_including_warmups':24,'checkpoints_including_warmups':184,'all_samples_retained':True,'candidate_accepted':False,'scope':'Separate parsing of complete retained native logs, exact original payloads/checkpoints and sortedthree-valuemedian/strictfixture/terminalcost arithmetic. No newnative/compiler/GPU calls. Notexternalindependentreview or significance/adoption. Rawprimaryarenabytesnotrecaptured; fullfingerprints partofscientificrecords,D201fullrawseparate.'})
print(json.dumps({'status':'root_replay_pass','checks':checks,'observed_gain_pct':gain,'timing_and_cost_pass':passed}),flush=True)
