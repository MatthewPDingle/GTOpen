import sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
complete=ROOT/'runs/E051-remaining-build-r3/complete.json';C=old.read(complete);assert C['all_compilers_terminal'] is True and C['native_executions']==0
for p,h in C['artifact_sha256'].items():old.pin(p,h)
H=ROOT/'runs/E051-remaining-native-plan';H.mkdir();script=ROOT/'runs/E051-remaining-native.py'
binaries={}
for key,stem in [('capacity-baseline','E051-capacity-baseline'),('capacity-candidate','E051-capacity-candidate'),('holdout-baseline','E051-holdout-baseline'),('holdout-candidate','E051-holdout-candidate'),('original','baseline-complete'),('primary-candidate','E051-postflop_autoresearch')]:
 p=ROOT/'binaries'/(stem+'.exe');m=p.with_suffix('.manifest.json');d=old.read(m);old.pin(p,d['binary_sha256']);binaries[key]={'path':str(p),'sha256':old.sha(p),'manifest':str(m),'manifest_sha256':old.sha(m)}
 if key.endswith('baseline'):assert d['source_sha256']==old.BASE
 if key.endswith('candidate'):assert d['source_sha256']==old.BASE|{'crates/solver/src/gpu/kernels.cu':'a926bf0bc818a2ba808c862b59a552dfb7ade453ca18f347b4307784e47d9647'}
holdpairs=[{'baseline':'H051B'+str(i),'candidate':'H051C'+str(i)} for i in range(1,4)];cumpairs=[{'baseline':'B'+str(167+i),'candidate':'E051O'+str(i)} for i in range(1,4)]
order=lambda pairs:[pairs[0]['baseline'],pairs[0]['candidate'],pairs[1]['candidate'],pairs[1]['baseline'],pairs[2]['baseline'],pairs[2]['candidate']]
oldhold=ROOT/'runs/E020-wide-turn-holdout-implementation-r2';historical=oldhold/'cohort/C1'
inputs=[script,complete,oldhold/'run.py',oldhold/'evaluator.rs',oldhold/'fixture.json',historical/'stdout.log',historical/'exit.json',historical/'invocation.json',historical/'state.bin',ROOT/'runs/E051-confirmation-plan/protocol.json',ROOT/'comparisons/E051-fresh16-confirmation/report.json',ROOT/'comparisons/E051-broader-root-check/report.json',old.REPO/'tools/postflop_compare.py']
for b in binaries.values():inputs +=[Path(b['path']),Path(b['manifest'])]
P={'id':'E051-remaining-native','at':old.now(),'status':'FROZEN_BEFORE_NATIVE_OUTCOMES','binaries':binaries,'codec':str(oldhold/'run.py'),'holdout_fixture':str(oldhold/'fixture.json'),'historical_holdout':str(historical),'historical_raw':str(historical/'state.bin'),'holdout_pairs':holdpairs,'holdout_order':order(holdpairs),'holdout_arms':{v:k for pair in holdpairs for k,v in pair.items()},'cumulative_pairs':cumpairs,'cumulative_order':order(cumpairs),'cumulative_arms':{v:k for pair in cumpairs for k,v in pair.items()},'input_sha256':{str(p):old.sha(p) for p in inputs},'capacity_rule':'Exact six actual retained owned metadata/canonical state/workspace and public wrapper sizes. Device-wide queries unscored. Same existing stored-case geometry, no solves or forced spill.','holdout_rule':'Exactly three paired observations BC/CB/BC, fixed full169 turn. Same target/stopping. Every full non-timing payload, checkpoint and entire raw q/scale file exact to historical accepted E020. Reject positive candidate median slowdown plus >=2/3 slower pairs; no epsilon, no minimum holdout gain, no extension.','cumulative_rule':'Fresh original-to-E051 three primary pairs BC/CB/BC. Same exactness controls and strict fixture non-regression. Unrounded sum of per-fixture medians >=1%. No historical timing pooling or added historical percentages.','candidate_accepted':False,'next':'Root replay and material/source qualification required before adoption.'}
for name in P['cumulative_order']:assert not (ROOT/'runs'/name).exists()
old.save(H/'protocol.json',P)
pub={}
for src in [script,H/'protocol.json',complete]:
 key=H.name+'/'+src.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(src.read_bytes())
 with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==src.read_bytes()
 pub[key]=old.sha(src)
old.save(H/'pre-native-publication.json',{'at':old.now(),'files_http_byte_verified':pub,'candidate_accepted':False})
print(old.sha(H/'protocol.json'),flush=True)
