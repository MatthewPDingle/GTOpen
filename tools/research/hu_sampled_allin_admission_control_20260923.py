"""Offline admission rejection tests and exact launcher change isolation."""
import copy
import json
from pathlib import Path
import tempfile
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from sampled_allin_admission_v2 import completed_hybrid_paths

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
SOURCES = ROOT/'tools/research'


def main():
    oldpath = SOURCES/'hu_sampled_physical_allin_study_20260923.py'
    newpath = SOURCES/'hu_sampled_physical_allin_study_v2_20260923.py'
    old = oldpath.read_text()
    start = old.index('    dense_review_path = OUT/')
    end = old.index('    assert not (OUT/', start)
    expected = old[:start] + '    from sampled_allin_admission_v2 import completed_hybrid_paths\n    prerequisites = completed_hybrid_paths(OUT)\n' + old[end:]
    expected = expected.replace("PREFIX = 'sampled-physical-allin-study-v1'", "PREFIX = 'sampled-physical-allin-study-v2'")
    expected = expected.replace('paths = [Path(__file__),dense_review_path,dense_result_path,cache_review_path,pipeline_path,', "paths = [Path(__file__),*prerequisites,cache_review_path,pipeline_path,\n             ROOT/'tools/research/sampled_allin_admission_v2.py',OUT/'ALLIN-ADMISSION-V2.md',")
    assert newpath.read_text() == expected, 'Unexpected change beyond admission and frozen prerequisites'
    pipeline_path = OUT/'sampled-physical-allin-pipeline-control-v1-result.json'
    pipeline = json.loads(pipeline_path.read_text()); assert pipeline['passed']
    for p,h in pipeline['inputs'].items(): assert sha(p)==h,p
    rejected = []
    with tempfile.TemporaryDirectory(prefix='gtopen-admission-control-') as folder:
        out = Path(folder)
        r = 'sampled-physical-hybrid-repair-v1'
        e = 'sampled-physical-hybrid-evaluation-v2'
        b = 'sampled-physical-hybrid-btn-jam-diagnosis-v1'
        log = out/'fixture.log'; log.write_text('synthetic admission test only')
        fixture = {
            r+'-registration.json':dict(stages=[(str(i),'unused',[]) for i in range(6)],inputs={}),
            e+'-registration.json':dict(inputs={}),
            e+'-status.json':dict(state='complete',error=None),
            e+'-result.json':dict(synthetic_fixture=True),
            b+'-independent-review.json':dict(passed=True,paired_differences_reconstructed=16384,inputs={},
                reviewer_sha256=sha(SOURCES/'hu_sampled_physical_hybrid_btn_jam_review_20260923.py')),
            'sampled-physical-hybrid-comparison-v1-result.json':dict(synthetic_fixture=True),
        }
        for name,value in fixture.items(): save(out/name,value)
        fixture[r+'-status.json'] = dict(state='complete',error=None,
            registration_sha256=sha(out/(r+'-registration.json')),
            completed_stages=[dict(stage=str(i),exit_code=0,log=str(log),log_sha256=sha(log)) for i in range(6)])
        fixture[e+'-independent-review.json'] = dict(passed=True,
            registration_sha256=sha(out/(e+'-registration.json')),result_sha256=sha(out/(e+'-result.json')),
            terminal_status_sha256=sha(out/(e+'-status.json')),training_deals_replayed=8192,evaluation_deals_replayed=16384,
            reviewer_sha256=sha(SOURCES/'hu_sampled_physical_hybrid_evaluation_review_20260923.py'))

        def reset():
            for name,value in fixture.items():
                (out/name).write_text(json.dumps(value,separators=(',',':'))+'\n',newline='\n')

        reset(); assert len(completed_hybrid_paths(out)) == 8
        cases = [
            ('running-repair',r+'-status.json',lambda d:d.update(state='evaluation')),
            ('missing-stage',r+'-status.json',lambda d:d['completed_stages'].pop()),
            ('failed-stage',r+'-status.json',lambda d:d['completed_stages'][2].update(exit_code=1)),
            ('changed-log',r+'-status.json',lambda d:d['completed_stages'][2].update(log_sha256='bad')),
            ('failed-evaluation-review',e+'-independent-review.json',lambda d:d.update(passed=False)),
            ('short-evaluation',e+'-independent-review.json',lambda d:d.update(evaluation_deals_replayed=16383)),
            ('stale-result',e+'-result.json',lambda d:d.update(changed=True)),
            ('stale-terminal-status',e+'-status.json',lambda d:d.update(changed=True)),
            ('failed-btn-review',b+'-independent-review.json',lambda d:d.update(passed=False)),
            ('stale-btn-input',b+'-independent-review.json',lambda d:d.update(inputs={str(log):'bad'})),
        ]
        for label,name,mutate in cases:
            reset(); value=copy.deepcopy(fixture[name]); mutate(value); (out/name).write_text(json.dumps(value))
            try: completed_hybrid_paths(out)
            except AssertionError: rejected.append(label)
            else: raise AssertionError('Admitted invalid prerequisite: '+label)
    paths=[Path(__file__),oldpath,newpath,SOURCES/'sampled_allin_admission_v2.py',pipeline_path,OUT/'ALLIN-ADMISSION-V2.md']
    result=dict(passed=True,inputs={str(p):sha(p) for p in paths},exact_admission_only_change=True,
        frozen_pipeline_inputs_verified=len(pipeline['inputs']),synthetic_rejection_cases=rejected,
        training_launched=False,production_modified=False,
        scope='Offline gate tests and exact source comparison. Synthetic fixtures are not research results or proof of live prerequisites completing.')
    save(OUT/'sampled-physical-allin-admission-v2-control.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='inputs'}))


if __name__ == '__main__': main()
