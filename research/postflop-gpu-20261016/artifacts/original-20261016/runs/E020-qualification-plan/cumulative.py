"""Root-only: fixed fresh-original cumulative cohort after every qualification gate."""
import common as c

def main():
    assert len(c.sys.argv)==3,'authorization SHA and qualification-ready SHA required'
    p=c.initialize(c.sys.argv[1]);rp=c.HERE/'qualification-ready.json'
    assert c.ar.sha256(rp)==c.sys.argv[2]
    ready=c.read(rp)
    for flag in ('broader_pass','holdout_pass','independent_broader_review_pass','independent_holdout_review_pass'):
        assert ready[flag] is True,flag
    assert c.Path(ready['all_builds_ready']['path'])==c.HERE/'all-builds-ready.json'
    c.check_record(ready['all_builds_ready']);c.build_ready(ready['all_builds_ready']['sha256'])
    b=c.check_record(ready['broader_report'])
    assert c.Path(ready['broader_report']['path'])==c.ROOT/'comparisons'/p['broader_comparison_id']/'report.json'
    assert b['status']=='pass' and (b['original_snapshots'],b['f32_fixtures'],b['gpu_tests'],b['continuation_tests'])==(160,3,6,3)
    assert c.Path(ready['holdout_report']['path'])==c.ROOT/'runs/E020-wide-turn-holdout-implementation/cohort/report.json'
    h=c.check_record(ready['holdout_report']);assert h['status']=='pass'
    assert h['protocol_sha256']=='33d4a047f67d1b23bd125cbfc8c31b564b6cf6a8417da768023beb8389c71510'
    assert h['repeatable_regression'] is False and h['candidate_accepted'] is False and h['deployment_changed'] is False
    assert set(h['run_report_sha256'])=={'B1','C1','C2','B2','B3','C3'}
    holdout=c.Path(ready['holdout_report']['path']).parent
    for label,sha in h['run_report_sha256'].items():assert c.ar.sha256(holdout/label/'report.json')==sha
    assert ready['evidence_sha256']
    for path,sha in ready['evidence_sha256'].items():assert c.ar.sha256(c.Path(path))==sha,path
    c.require_unused([r['id'] for r in p['cumulative_order']])
    out=c.Path(p['cumulative_execution_directory']);out.mkdir(exist_ok=False)
    pins={name:c.binary_pair(name)[2] for name in ('baseline-complete','E020-postflop_autoresearch')}
    c.save(out/'invocation.json',{'at':c.ar.now(),'authorization_sha256':c.sys.argv[1],'qualification_ready_sha256':c.sys.argv[2],'order':[r['id'] for r in p['cumulative_order']],'pairs':p['pairs'],'binary_pins':pins,'all_builds_terminal':True})
    reference=None;completed=[];error=None
    try:
        for row in p['cumulative_order']:
            report,raw=c.native(row,pins)
            exact=c.results_exact(report,raw,'compressed')
            if reference is None:reference=exact
            assert exact==reference,row['id']
            completed.append(row['id'])
        c.verify_source();c.verify_binary_pins(pins)
        c.save(out/'complete.json',{'at':c.ar.now(),'status':'pass','order':completed,'qualification_ready_sha256':c.sys.argv[2],'binary_pins':pins,'accepted':False,'deployed':False,'note':'All fixed native runs completed; statistical gates not yet assessed.'})
    except BaseException as exc:
        error=repr(exc);raise
    finally:
        c.save(out/'terminal.json',{'at':c.ar.now(),'completed':completed,'error':error,'no_exclusions':True,'no_extension':True})

if __name__=='__main__':main()
