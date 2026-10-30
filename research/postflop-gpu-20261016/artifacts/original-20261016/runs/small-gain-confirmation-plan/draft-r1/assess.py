"""File-only assessment of all128 fixed processes; never adopt a candidate."""
import math, statistics, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *

def distribution(values):
    return {'count':len(values),'median':statistics.median(values),'min':min(values),'max':max(values),'range':max(values)-min(values),'raw':values}

def policy_result(summary,pairs):
    rows=summary['fixtures'];raw=summary['pairs']
    assert len(raw)==len(pairs)==16
    gains=[x['observed_gain_pct'] for x in raw]
    differences=[x['baseline_full_cycle_ms']-x['candidate_full_cycle_ms'] for x in raw]
    blocks=[{'block':b,'gain_pct':distribution([g for g,p in zip(gains,pairs) if p['block']==b])} for b in range(1,5)]
    orientations=[{'orientation':o,'gain_pct':distribution([g for g,p in zip(gains,pairs) if p['orientation']==o])} for o in ['BC','CB']]
    assert all(x['gain_pct']['count']==4 for x in blocks)
    assert all(x['gain_pct']['count']==8 for x in orientations)
    bs=sum(x['baseline']['full_cycle_ms']['median_ms'] for x in rows)
    cs=sum(x['candidate']['full_cycle_ms']['median_ms'] for x in rows)
    aggregate=compare.gain(bs,cs)
    guard=[]
    for row in rows:
        f=row['fixture_id'];slower=[-x['fixture_gain_pct'][f] for x in raw]
        median_slowdown=-row['observed_gain_pct'];count=sum(v>0 for v in slower)
        guard.append({'fixture_id':f,'median_slowdown_pct':median_slowdown,'paired_slowdown_pct':slower,'strictly_slower_pairs':count,'required_slower_pairs':9,'failed':median_slowdown>0 and count>=9})
    gates={'aggregate_ge_1pct':aggregate>=1.0,'at_least13_positive_pairs':sum(x>0 for x in differences)>=13,'paired_median_positive':statistics.median(gains)>0,'every_block_median_positive':all(x['gain_pct']['median']>0 for x in blocks),'both_orientation_medians_positive':all(x['gain_pct']['median']>0 for x in orientations),'fixture_guard_pass':not any(x['failed'] for x in guard)}
    return {'aggregation':'Unrounded sum of three fixture medians,16 observations per fixture per arm','baseline_full_cycle_ms':bs,'candidate_full_cycle_ms':cs,'observed_gain_pct':aggregate,'required_gain_pct':1.0,'positive_pairs':sum(x>0 for x in differences),'paired_gain_pct':distribution(gains),'paired_difference_ms':distribution(differences),'blocks':blocks,'order_strata':orientations,'fixture_regression_guard':guard,'gates':gates,'timing_gate_pass':all(gates.values()),'statistical_significance_established':False,'calibration':'Operational fixed-repeat confirmation criteria only; serial samples need not be independent. Four selected hypotheses, no nominal p-value or confidence claim.'}

def main():
    assert len(sys.argv)==2,'Provide root authorization SHA256'
    auth=sys.argv[1];verify(auth);custody()
    assert not (ROOT/'gpu-run.lock').exists()
    bins=binaries();complete=read(EXEC/'complete.json')
    assert complete['measurement_order']==S['measurement_order'] and complete['unit_order']==S['unit_order']
    assert complete['authorization_sha256']==auth and complete['schedule_sha256']==sha(HERE/'schedule.json')
    invocation=read(EXEC/'invocation.json')
    assert invocation['all_native_ids_previously_absent'] is True
    assert invocation['build_complete_sha256']==sha(BUILD/'complete.json')
    units=read(EXEC/'units-complete.json');assert units['all_passed'] is True and units['unit_order']==S['unit_order']
    for n,h in units['evidence_sha256'].items():pin(n,h)
    for c in P['build_order']:unit_check(c)
    anchor=exact_raw(P['anchor']);reports={};verified={};previous=None
    # High-resolution wrapper intervals prove serialization without inferring subsecond order from ar.now().
    for identity in S['unit_order']+S['measurement_order']:
        exit_path=EXEC/(identity+'.exit.json');e=read(exit_path)
        assert e['returncode']==0 and e['error'] is None and e['cleanup'] is None
        start=datetime.datetime.fromisoformat(e['started_at']);end=datetime.datetime.fromisoformat(e['finished_at'])
        assert start<=end and (previous is None or previous<=start)
        previous=end;verified[str(exit_path)]=sha(exit_path)
        r=read(ROOT/'runs'/identity/'report.json')
        # Native timestamps have whole-second precision; validate overlap with their wrapper interval.
        ns=datetime.datetime.fromisoformat(r['started_at'].replace('Z','+00:00'))
        ne=datetime.datetime.fromisoformat(r['finished_at'].replace('Z','+00:00'))
        assert start.replace(microsecond=0)<=ns<=ne<=end
        assert r['provenance']['source_sha256']==BASE
        if identity in S['measurement_order']:
            compare.validate_run(r,verified);assert exact_raw(identity)==anchor,identity
            reports[identity]=r
    assert len(reports)==128
    first=reports[S['measurement_order'][0]]
    for r in reports.values():assert r['environment']==first['environment'] and compare.gpu_identity(r)==compare.gpu_identity(first)
    arms={}
    for c in P['family']:
        pairs=sorted([p for p in S['pairs'] if p['candidate']==c],key=lambda p:p['pair'])
        assert [p['pair'] for p in pairs]==list(range(1,17))
        b=[reports[p['baseline']] for p in pairs];candidate=[reports[p['candidate_run']] for p in pairs]
        for arm,rs in [('E020',b),(c,candidate)]:
            pinset=bins[(arm,'postflop_autoresearch')]
            for r in rs:
                assert r['binary_sha256']==pinset['sha256'] and r['binary_build_manifest']['sha256']==pinset['manifest_sha256']
                assert r['binary_build_manifest']['data']['source_sha256']==expected(arm)
        summary=compare.summarize(b,candidate,BASE)
        # Do not expose or reuse the historical helper's2%/3% decision fields.
        summary['performance']=policy_result(summary,pairs)
        for p,record in zip(pairs,summary['pairs']):record.update(block=p['block'],round=p['round'],orientation=p['orientation'],order=p['order'])
        summary.update(candidate=c,exactness={'complete_non_timing_results':96,'convergence_records':736,'accepted_anchor':P['anchor'],'pass':True},decision='qualifying_pending_cost_and_broader_gates' if summary['performance']['timing_gate_pass'] else 'rejected',candidate_accepted=False,cost_validation='pending; timing pass never proves no material memory or compatibility cost',adoption_requirements=P['conditional_adoption_requirements'])
        arms[c]=summary
    report={'id':P['id'],'at':now(),'protocol_sha256':sha(HERE/'protocol.json'),'schedule_sha256':sha(HERE/'schedule.json'),'authorization_sha256':auth,'source_package_sha256':P['source_package']['sha256'],'source_review':P['source_review'],'complete_sha256':sha(EXEC/'complete.json'),'build_complete_sha256':sha(BUILD/'complete.json'),'effective_policy':P['policy'],'family_size':4,'fresh_evaluator_processes':128,'exactness':{'fixture_results':384,'convergence_records':2944,'all_exact_to_accepted_anchor':True},'arms':arms,'chronology':[{'id':i,'started_at':reports[i]['started_at'],'finished_at':reports[i]['finished_at']} for i in S['measurement_order']],'preserved_artifacts':verified,'historical_timing_samples_used':0,'excluded_samples':[],'extension_runs':0,'candidate_accepted':False,'publication':'Root publishes after independent audit; this script only saves immutable comparison artifacts.'}
    out=ROOT/P['comparison_output'];assert not out.exists();out.mkdir()
    for c,value in arms.items():save(out/(c+'.json'),value)
    save(out/'report.json',report)
    print(json.dumps({c:{'decision':x['decision'],'gain_pct':x['performance']['observed_gain_pct'],'gates':x['performance']['gates']} for c,x in arms.items()},indent=2))

if __name__=='__main__':main()
