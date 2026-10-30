"""Assess the complete fixed three-pair E067 primary screen using the user's1% rule."""
import datetime,json,statistics,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'accepted-E051'))
import common_e051 as old
ar=old.ar
read,sha,pin,save,now=old.read,old.sha,old.pin,old.save,old.now
assert len(sys.argv)==2;pin(HERE/'protocol.json',sys.argv[1]);P=read(HERE/'protocol.json')
for p,h in P['input_sha256'].items():pin(p,h)
old.custody();assert not (ar.RESEARCH/'gpu-run.lock').exists()
execution=ar.RESEARCH/'runs/E067-native-execution';done=read(execution/'complete.json')
assert done['protocol_sha256']==sys.argv[1] and done['measurement_order']==P['measurement_order']
control=read(Path(P['gpu_control_report']['path']))
assert control['status']=='pass_scoped_down_action_full_raw_equivalence' and control['cases']==1196 and control['all_full_outputs_inputs_guards_exact']
anchor=old.historical.exact_raw('E020C1');reports={};pins={};previous=None
for identity in P['control_ids']+P['measurement_order']:
    receipt=read(execution/(identity+'.exit.json'))
    assert receipt['returncode']==0 and receipt['error'] is None and receipt['cleanup'] is None
    start=datetime.datetime.fromisoformat(receipt['started_at']);end=datetime.datetime.fromisoformat(receipt['finished_at'])
    assert start<=end and (previous is None or previous<=start);previous=end
    assert read(execution/(identity+'.invocation.json'))['command']==receipt['command']
    r=read(ar.RESEARCH/'runs'/identity/'report.json');pins[str(ar.RESEARCH/'runs'/identity/'report.json')]=sha(ar.RESEARCH/'runs'/identity/'report.json')
    ns=datetime.datetime.fromisoformat(r['started_at'].replace('Z','+00:00'));ne=datetime.datetime.fromisoformat(r['finished_at'].replace('Z','+00:00'))
    assert start.replace(microsecond=0)<=ns<=ne<=end
    assert r['provenance']['source_sha256']==read(P['baseline']['path'])['source_sha256']
    if identity in P['measurement_order']:
        old.compare.validate_run(r,pins);assert old.historical.exact_raw(identity)==anchor
        reports[identity]=r
base=read(P['baseline']['path'])['source_sha256']
b=[reports[p['baseline']] for p in P['pairs']];c=[reports[p['candidate']] for p in P['pairs']]
summary=old.compare.summarize(b,c,base)
bs=sum(f['baseline']['full_cycle_ms']['median_ms'] for f in summary['fixtures'])
cs=sum(f['candidate']['full_cycle_ms']['median_ms'] for f in summary['fixtures'])
gain=old.compare.gain(bs,cs);guards=[]
for f in summary['fixtures']:
    slower=[-pair['fixture_gain_pct'][f['fixture_id']] for pair in summary['pairs']]
    median_slowdown=-f['observed_gain_pct'];n=sum(x>0 for x in slower)
    guards.append({'fixture_id':f['fixture_id'],'median_slowdown_pct':median_slowdown,'slower_pairs':n,'paired_slowdown_pct':slower,'failed':median_slowdown>0 and n>=2})
passed=gain>=1.0 and not any(g['failed'] for g in guards)
summary['performance']={'aggregation':'Unrounded sum of per-fixture medians, three observations per arm','baseline_full_cycle_ms':bs,'candidate_full_cycle_ms':cs,'observed_gain_pct':gain,'required_gain_pct':1.0,'fixture_regression_guard':guards,'primary_timing_pass':passed,'statistical_significance_established':False}
summary.update(id='E067-primary',at=now(),protocol_sha256=sys.argv[1],exactness={'fixture_results':18,'convergence_records':138,'all_exact':True},gpu_control_report_sha256=sha(Path(P['gpu_control_report']['path'])),preserved_inputs=pins,excluded_samples=[],historical_timing_samples_used=0,extension_runs=0,decision='advance_to_separately_frozen_confirmation' if passed else 'rejected',candidate_accepted=False,adoption_requirements=P['adoption_requirements'])
out=ar.RESEARCH/'comparisons/E067-three-pair-comparison';assert not out.exists();out.mkdir();save(out/'report.json',summary)
print(json.dumps({'decision':summary['decision'],'performance':summary['performance'],'report_sha256':sha(out/'report.json')},indent=2))
