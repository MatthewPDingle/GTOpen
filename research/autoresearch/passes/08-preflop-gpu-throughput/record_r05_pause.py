"""Record the verified deployment and the user's requested research pause."""
import json,datetime
from pathlib import Path
p=Path(__file__).resolve().parent;lab=p.parents[3]
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def put(path,x):path.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
deploy=json.loads((lab/'target/deployments/r05-20260914-live/deployment.json').read_text(encoding='utf-8'))
assert deploy['deployed'] and deploy['verified']
put(p/'raw/r05-deployment-verified.json',dict(verified=True,deployed=True,port=56708,pid=deploy['new']['ProcessId'],executable=deploy['candidate'],sha256=deploy['candidate_sha256'],preflop_iteration=53,postflop_iteration=210,session_results_restored_exactly=True,backup=deploy['backup'],verified_at=now))
x=json.loads((p/'raw/r05-release-verified.json').read_text(encoding='utf-8'))
x.update(deployed=True,paused=True,status='Paused - C23 + C24 deployed on 56708');put(p/'raw/r05-verified.json',x)
put(p/'control.json',dict(state='paused',updated_at=now,reason='User requested deployment followed by pause',resume_requires_user_request=True,live_release='r05',app_port=56708,dashboard_port=56709,active_experiment=None))
s=(p/'program.md').read_text(encoding='utf-8')
s=s.replace('# GPU preflop throughput autoresearch','# GPU preflop throughput autoresearch\n\n> PAUSED by user request after R05 deployment (C23 + C24), 2026-09-14.\n> Do not start experiments on automatic continuations. Read RESUME.md and wait\n> for explicit authorization of the next overnight window.')
(p/'program.md').write_text(s,encoding='utf-8')
x=json.loads((p/'experiments.json').read_text(encoding='utf-8'))
for e in x:
 if e['id']=='c23':e['detail']=e['detail'].replace('R04 normal app qualification is complete; R03 stays live on 56708.','Combined R05 release is deployed on 56708; research paused.')
 if e['id']=='c24':e['detail']=e['detail'].replace('Normal-app integration and deployment remain.','Normal-app integration and deployment passed in R05; research paused.')
assert not any(e['id']=='r05' for e in x)
x.append(dict(id='r05',kind='diagnostic',baseline='c24',label='C23 + C24 deployed - research paused',idea='One normal app build selects the appropriate retained optimization for each game.',detail='Both GPU paths passed numerical, allocation recovery, saved-game and normal server checks. Port 56708 is updated and both sessions restored. Experiments, benchmarks and restart instructions are preserved for the next authorized overnight run.'))
put(p/'experiments.json',x)
s=(p/'dashboard.html').read_text(encoding='utf-8')
s=s.replace("latest.decision.ready_for_deployment?'Release checks passed; integration adds no separate speed point.'","latest.decision.deployed?'Deployed on 56708; research paused. Integration adds no separate speed point.':latest.decision.ready_for_deployment?'Release checks passed; integration adds no separate speed point.'")
s=s.replace("active.decision.ready_for_deployment?'<em>✓</em>Ready for deployment'","active.decision.paused?'<em>✓</em>Deployed - research paused':active.decision.ready_for_deployment?'<em>✓</em>Ready for deployment'")
s=s.replace('<main>','<main>\n<div class="banner"><div><b>Research paused - C23 + C24 deployed on <a href="http://127.0.0.1:56708/">56708</a></b><p>The graphs compare different games: C23 uses the historical benchmark; C24 uses the larger memory-limited game. Their gains are not additive. Results and restart instructions are saved for the next overnight run.</p></div></div>',1)
(p/'dashboard.html').write_text(s,encoding='utf-8')
print('Deployment receipt, pause state and restart guide recorded.')
