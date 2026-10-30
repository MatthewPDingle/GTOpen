"""Freeze one no-launch resource probe for the fixed prefix-index permutation."""
import json, shutil, sys, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
D=ROOT/'runs/D093-prefix-layout';S=ROOT/'runs/E057-source';H=ROOT/'runs/E057-resource';assert not H.exists();H.mkdir()
model=old.read(D/'report-r2.json');assert model['status']=='admit_no_launch_resource_probe' and all(model['gates'].values())
old.pin(S/'candidate.cu',model['candidate_source_sha256']);old.pin(S/'baseline.cu',old.BASE['crates/solver/src/gpu/kernels.cu'])
for name in ['baseline.cu','candidate.cu']:shutil.copyfile(S/name,H/name)
parent=ROOT/'runs/E053-resource'
for name in ['probe.rs','execute.py']:
    text=(parent/name).read_text(encoding='utf-8').replace('E053','E057')
    assert 'E053' not in text and 'e053' not in text
    (H/name).write_text(text,encoding='utf-8',newline='\n')
P=old.read(parent/'protocol.json');P.update(id='E057-resource',at=old.now(),source_manifest_sha256=old.sha(S/'manifest.json'),fixed_gates='One candidate only. Actual up_show body changes, same27parameter ABI, other8entries byte-exact oncompute120/75. No register/local/static/dynamic shared increase or maxthread/64/128/256occupancy loss at all10fixed geometries. A failed gate closes with no variants. No numerical/performance or adoption conclusion from resources.')
P['rustc_command']=[x.replace(str(parent),str(H)) for x in P['rustc_command']]
inputs=[*S.iterdir(),*D.iterdir(),H/'probe.rs',H/'execute.py',H/'baseline.cu',H/'candidate.cu',Path(__file__),ROOT/'runs/D093-prefix-layout.py',ROOT/'runs/accepted-E051/baseline.json',ROOT/'runs/accepted-E051/common_e051.py',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md']
P['input_sha256']={str(p):old.sha(p) for p in inputs if p.is_file()}
P['input_sha256'].update({p:h for p,h in old.read(parent/'protocol.json')['input_sha256'].items() if Path(p).suffix in ['.rlib','.lib']})
P['cpu_model_report']={'path':str(D/'report-r2.json'),'sha256':old.sha(D/'report-r2.json')}
P['cpu_model_correction']={'path':str(D/'total-read-correction.json'),'sha256':old.sha(D/'total-read-correction.json')}
for p,h in P['input_sha256'].items():old.pin(p,h)
assert not (H/'probe.exe').exists() and not (H/'execution').exists();old.save(H/'protocol.json',P)
published={}
for folder in [D,S,H]:
    for src in folder.iterdir():
        if not src.is_file():continue
        key=folder.name+'/'+src.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(src,dst)
        with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==src.read_bytes()
        published[key]=old.sha(src)
old.save(H/'pre-execution-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published,'source_activated':False,'native_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    st=old.read(old.ar.STATUS);assert st['research_policy']['minimum_aggregate_gain_pct']==1
    assert not any(e['id'] in ['D093','E057'] for e in st['experiments'])
    st['experiments'].append({'id':'D093','at':old.now(),'title':'Prefix-buffer index and bank-request model','kind':'diagnostic','status':'measured','correctness':'pass','stage':'Integer controls passed; request model admits resource inspection','reason':'2,654 bounded permutation cases,1,759,602 indices and339,712 block geometries passed. Fixed XOR map preserves32word tiles, partial tail and storage. An arithmetic correction preserved the original model and unchanged candidate/gates. Address model predicts fewer prefix requests; no SASS/counter/time, GPU numerical or solve-speed claim.','evidence':[{'label':'Fixed source/model protocol','url':'evidence/D093-prefix-layout/protocol.json'},{'label':'Corrected address model and integer checks','url':'evidence/D093-prefix-layout/report-r2.json'},{'label':'Preserved constant-count correction','url':'evidence/D093-prefix-layout/total-read-correction.json'}]})
    st['experiments'].append({'id':'E057','at':old.now(),'title':'Permute showdown prefix shared-memory indices','kind':'candidate','status':'running','correctness':'pending','stage':'Frozen no-launch resource gate','reason':'One fixed physical index permutation. Float operations/order, barriers, buffer sizes, host dispatch/ABI/graphs and quality unchanged. Actual resource gate precedes numerical controls and complete-cycle timing.','evidence':[{'label':'Source review and prior mechanisms','url':'evidence/E057-source/source-review.json'},{'label':'Exact CUDA-only patch','url':'evidence/E057-source/candidate.patch'},{'label':'Frozen no-launch resource protocol','url':'evidence/E057-resource/protocol.json'}]})
    st.update(updated_at=old.now(),state='running',active_experiment='E057',stage='E057 compiled-resource prerequisite',activity='Test one fixed prefix-buffer address permutation. CPU ownership/index model passed; no source activation, kernel launch or speed claim.');old.ar.atomic_json(old.ar.STATUS,st)
old.custody();print(json.dumps({'resource_protocol_sha256':old.sha(H/'protocol.json'),'published':len(published),'candidate_sha256':old.sha(S/'candidate.cu')}),flush=True)
