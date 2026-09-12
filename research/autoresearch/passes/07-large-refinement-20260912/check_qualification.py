"""Evidence checklist for the registered experiments; never deploys anything."""
import json,math,re,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
RAW=HERE/'raw'

def read(name):
    return json.loads((RAW/name).read_text())

def main():
    findings=[]
    def check(name,fn):
        try:
            detail=fn()
            findings.append(dict(check=name,passed=True,detail=detail))
        except Exception as e:
            findings.append(dict(check=name,passed=False,detail=str(e)))
    expected=json.loads((HERE/'broad-paths.json').read_text())
    def case(variant,version='adaptive-v3'):
        name=f'large-eight-{variant}-{version}'
        result=read(name+'-result.json')
        process=read(name+'-exit.json')
        assert process['returncode']==0 and process['reason'] is None,'unsuccessful refinement process'
        assert result['nodes']==1567754,'wrong large fixture'
        if version=='compact-v1':assert result['engine']=='gpu','wrong compact comparison engine'
        assert result['unrelated_and_fixed_arenas_unchanged'] is True,'preservation unproven'
        assert result['roundtrip_exact'] is True,'roundtrip unproven'
        assert result['normal_global_resume_supported'] is False,'local-age limitation must remain explicit'
        assert all(p['refinement']['global_iteration_unchanged']==1050 for p in result['refinements']),'global age changed'
        gaps=result['global_gaps']
        assert len(gaps)==8 and all(math.isfinite(x) and x>=0 for x in gaps),'invalid full-check gaps'
        assert sum(gaps)<=0.005,f'global gap {sum(gaps)} exceeds registered target'
        audit=read(name+'-broad.json')
        rows=[r['candidate'] for r in audit['rows']]
        assert [r['path'] for r in rows]==expected,'audit path coverage mismatch'
        failed=[r['path'] for r in rows if r.get('passes_local_tail_gate') is not True or r.get('conditioned_before_evaluation') is not True]
        assert not failed,f'failed, unevaluable, or unconditioned paths: {failed}'
        return dict(paths=len(rows),global_gap=sum(gaps),process_seconds=process['seconds'])
    # User stopped CPU performance work. Retain historical CPU evidence, but
    # qualify the requested GPU implementation on both original input snapshots.
    for variant in ('sampled','native'):check(variant+' compact GPU qualification',lambda v=variant:case(v,'compact-v1'))
    def tests(name,min_suites=1,required=None):
        record=read(name+'-exit.json')
        assert record['returncode']==0 and record['reason'] is None,'test process failed'
        log=(RAW/(name+'.log')).read_text()
        suites=re.findall(r'test result: ok\. (\d+) passed; 0 failed;',log)
        assert sum(int(x)>0 for x in suites)>=min_suites,'missing nonempty passing suites'
        if required:
            # --nocapture may put GPU diagnostic lines between test name and ok.
            pattern=re.escape(required)+r' \.\.\.(?:(?!\ntest ).)*?\bok\s*(?:\n|$)'
            assert re.search(pattern,log,re.S),'required test did not pass'
        return dict(passed=sum(map(int,suites)),nonempty_suites=sum(int(x)>0 for x in suites))
    check('default solver regression',lambda:tests('default-solver-tests-v1'))
    check('GPU equivalence regression',lambda:tests('gpu-equivalence-tests-v1',2))
    check('mixed frozen and locked branch',lambda:tests('research-constraints-tests-v1',required='mixed_branch_refinement_preserves_frozen_and_point_locked_descendants'))
    check('compact GPU versus CPU',lambda:tests('research-constraints-tests-v1',required='compact_gpu_matches_cpu_conditional_branch_and_preserves_constraints'))
    check('GPU CV numerical screen after compact-root changes',lambda:tests('cv-numerical-v2'))
    def cv():
        cases=[]
        for seed in (42,314159):
            for refresh in (0,32,64):
                r=read(f'cv-six-{seed}-refresh{refresh}-result.json')
                assert r['converged_twice'] and r['roundtrip_exact'],'unfinished CV comparison'
                assert len(r['checks'])>=2 and all(c['gap']<=0.005 and c['full_reference_samples']==1024 for c in r['checks'][-2:]),'not two canonical passing checks'
                cases.append(dict(seed=seed,refresh=refresh,seconds=r['checks'][-1]['elapsed_seconds'],iterations=r['iteration']))
        rejected=read('cv-eight-storage-probe-exit.json')
        assert rejected['returncode']!=0,'expected registered storage rejection changed'
        assert '12196748616 extra bytes' in (RAW/'cv-eight-storage-probe.log').read_text(),'storage rejection not established'
        return dict(comparisons=cases,large_probe='rejected at registered storage cap')
    check('actual GPU CV comparisons and large storage probe',cv)
    passed=all(f['passed'] for f in findings)
    print(json.dumps(dict(scope='Registered large fixture, 27 conditional paths, and GPU CV prototype; not deployment approval',all_registered_checks_pass=passed,findings=findings),indent=2))
    return passed

if __name__=='__main__':sys.exit(0 if main() else 1)
