"""Exact source and live-prerequisite checks for the diagnosed launch repair."""
import ast
import json
from pathlib import Path
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from sampled_allin_admission_v2 import completed_hybrid_paths

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
SOURCES=ROOT/'tools/research'


def main():
    pilot=SOURCES/'hu_sampled_physical_allin_pilot_20260923.py'
    newpilot=SOURCES/'hu_sampled_physical_allin_pilot_v2_20260923.py'
    expected=pilot.read_text().replace('sampled-physical-hybrid-evaluation-v1','sampled-physical-hybrid-evaluation-v2').replace('hu_sampled_physical_allin_review_20260923.py','hu_sampled_physical_allin_review_v2_20260923.py')
    expected=expected.replace("Path(__file__),ROOT/'tools/research/sampled_allin_protocol_v3.py',","Path(__file__),OUT/'ALLIN-ADMISSION-V3.md',ROOT/'tools/research/sampled_allin_protocol_v3.py',")
    assert newpilot.read_text()==expected
    def worker(path):
        return ast.dump(next(n for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='worker'),include_attributes=False)
    assert worker(pilot)==worker(newpilot)
    reviewer=SOURCES/'hu_sampled_physical_allin_review_20260923.py'
    newreviewer=SOURCES/'hu_sampled_physical_allin_review_v2_20260923.py'
    assert newreviewer.read_text()==reviewer.read_text().replace('hu_sampled_physical_allin_pilot_20260923.py','hu_sampled_physical_allin_pilot_v2_20260923.py')
    wrapper=SOURCES/'hu_sampled_physical_allin_study_v2_20260923.py'
    newwrapper=SOURCES/'hu_sampled_physical_allin_study_v3_20260923.py'
    expected=wrapper.read_text().replace("PREFIX = 'sampled-physical-allin-study-v2'","PREFIX = 'sampled-physical-allin-study-v3'").replace('hu_sampled_physical_allin_pilot_20260923.py','hu_sampled_physical_allin_pilot_v2_20260923.py').replace('hu_sampled_physical_allin_review_20260923.py','hu_sampled_physical_allin_review_v2_20260923.py').replace("OUT/'ALLIN-ADMISSION-V2.md',","OUT/'ALLIN-ADMISSION-V3.md',\n             OUT/'sampled-physical-allin-study-v2-registration.json',\n             OUT/'sampled-physical-allin-study-v2-status.json',\n             OUT/'sampled-physical-allin-study-v2-training.log',")
    assert newwrapper.read_text()==expected
    for path in [newpilot,newreviewer,newwrapper]: compile(path.read_text(),str(path),'exec')
    pipeline_path=OUT/'sampled-physical-allin-pipeline-control-v1-result.json'
    pipeline=json.loads(pipeline_path.read_text());assert pipeline['passed']
    for p,h in pipeline['inputs'].items():assert sha(p)==h,p
    failure_paths=[OUT/f'sampled-physical-allin-study-v2-{s}.json' for s in ['registration','status']]
    registration,status=[json.loads(p.read_text()) for p in failure_paths]
    assert status['state']=='stopped' and status['registration_sha256']==sha(failure_paths[0])
    assert len(status['completed_stages'])==1 and status['completed_stages'][0]['stage']=='training' and status['completed_stages'][0]['exit_code']==1
    for p,h in registration['inputs'].items():assert sha(p)==h,p
    log=Path(status['completed_stages'][0]['log']);assert sha(log)==status['completed_stages'][0]['log_sha256']
    assert 'FileNotFoundError' in log.read_text() and 'sampled-physical-hybrid-evaluation-v1-independent-review.json' in log.read_text()
    assert not (OUT/'sampled-physical-allin-pilot-v1-registration.json').exists()
    assert not Path('S:/GTOpen-research/sampled-physical-allin-pilot-v1').exists()
    prerequisites=completed_hybrid_paths(OUT)
    paths=[Path(__file__),pilot,newpilot,reviewer,newreviewer,wrapper,newwrapper,pipeline_path,
        OUT/'ALLIN-ADMISSION-V3.md',*failure_paths,log,*prerequisites]
    result=dict(passed=True,inputs={str(p):sha(p) for p in paths},training_worker_unchanged=True,
        reviewer_change_only_process_name=True,source_changes_only_admission_and_frozen_metadata=True,
        no_child_training_artifacts=True,completed_hybrid_prerequisites=len(prerequisites),
        original_pipeline_inputs_verified=len(pipeline['inputs']),training_launched=False,production_modified=False)
    save(OUT/'sampled-physical-allin-admission-v3-control.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='inputs'}))


if __name__=='__main__':main()
