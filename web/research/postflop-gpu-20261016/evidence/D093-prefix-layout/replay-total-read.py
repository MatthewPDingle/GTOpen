"""Correct one common model constant without repeating or changing a candidate."""
import json, sys
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();original=old.read(H/'report.json');r=old.read(H/'report.json')
for f,before in zip(r['fixtures'],original['fixtures']):
    correction=0
    for row in f['rows']:
        nonempty=sum(freq for count,freq in row['opponent_count_distribution'].items() if int(count)>0)
        delta=3*nonempty
        row['baseline_scan']+=delta;row['candidate_scan']+=delta;correction+=delta
    f['baseline_modeled_requests']+=correction;f['candidate_modeled_requests']+=correction
    assert f['candidate_modeled_requests']-f['baseline_modeled_requests']==before['candidate_modeled_requests']-before['baseline_modeled_requests']
r.update(at=old.now(),id='D093-prefix-layout-r2',original_report_sha256=old.sha(H/'report.json'),assessment_correction='Total-prefix read is one same-address broadcast per active warp:4 warps for128threads, not1 per block. Add3 requests per nonempty terminal/player to BOTH arms from retained complete slot frequencies. No metadata, source, flags, gates, observed GPU or timing outcome changed; all per-fixture modeled differences and gate outcomes unchanged. Original report preserved.',candidate_source_sha256=old.sha(ROOT/'runs/E057-source/candidate.cu'),gpu_executions=0)
assert all(r['gates'].values()) and r['status']=='admit_no_launch_resource_probe'
old.save(H/'report-r2.json',r)
old.save(H/'total-read-correction.json',{'at':old.now(),'original_sha256':old.sha(H/'report.json'),'corrected_sha256':old.sha(H/'report-r2.json'),'script_sha256':old.sha(Path(__file__)),'candidate_unchanged':True,'gate_outcomes_unchanged':True,'source_activated':False,'gpu_executions':0,'performance_measured':False})
print(json.dumps({'status':r['status'],'model':[{k:f[k] for k in ['board','baseline_modeled_requests','candidate_modeled_requests']} for f in r['fixtures']],'source_unchanged':True}),flush=True)
