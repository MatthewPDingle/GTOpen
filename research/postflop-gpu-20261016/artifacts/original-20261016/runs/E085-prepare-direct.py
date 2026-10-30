"""Freeze all original819 raw action cases for the strategy-store candidate."""
import ast
from pathlib import Path
import shutil
import sys
import urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
C=R/'runs/accepted-E080-live-20261018'
sys.path.insert(0,str(C));import common_e080_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
assert shutil.disk_usage(R).free>=66*1024**3
RES=R/'runs/E085-resource-r2';q=old.read(RES/'report.json')
assert q['status']=='pass_compiled_strategy_streaming_prerequisites'and all(q['gates'].values())
x=old.read(R/'runs/E085-resource-manager/resource.exit.json')
assert x['returncode']==0and x['error']is x['cleanup']is None
prior=R/'runs/E075-kernel-control';H=R/'runs/E085-kernel-control'
H.mkdir(exist_ok=False)
for arm in ['baseline','candidate']:
    p=RES/'execution'/(arm+'-compute_120.ptx');old.pin(p,q['ptx_sha256'][arm+'-compute_120'])
    shutil.copyfile(p,H/(arm+'.ptx'))
for n in ['corpus.json','discounts.rs']:shutil.copyfile(prior/n,H/n)
for n in ['probe.rs','execute.py','audit.py']:
    t=(prior/n).read_text().replace('E075','E085').replace('accepted-E051-live-20261018','accepted-E080-live-20261018').replace('import common_e051_live as old','import common_e080_live as old')
    if n=='execute.py':t=t.replace('pass_compiled_uniform_load_prerequisites','pass_compiled_strategy_streaming_prerequisites')
    if n!='probe.rs':ast.parse(t)
    (H/n).write_text(t,encoding='utf-8',newline='\n')
old.save(H/'source-review.json',{'at':old.now(),'corpus_sha256':old.sha(H/'corpus.json'),
    'cases':819,'launches':1638,'source_and_controls':'Exact existing819case full action matrix and discount function. Change only labels/custody epoch and sealed PTX paths. Same full inputs, actual allocation-disjointness witnesses, full mutable images, guards, owned spans, kernels and case order. Both variants receive every identical input; no metadata encoding/tagging.',
    'coverage':'p0/p1; unlocked,locked,opponent; common2/3/4 and generic1/5/8/9/17 actions; zero/count/tails and hand lengths through1326;64/128/256 widths; DCFR/CFR+/PCFR+ discount cases, finite/signedzero/subnormal/quietNaN/infinity/overflow; actual parent-childCFV rows and mutable allocation extents disjoint.',
    'scope':'Finite819case matrix; no universal malformed-address, signaling-NaN or alias contract proof. No whole-solver/performance/material qualification.'})
P0=old.read(RES/'protocol.json')
cmd=[x.replace(str(RES),str(H))for x in P0['rustc_command']]
deps={p:h for p,h in P0['input_sha256'].items()if Path(p).suffix in ['.rlib','.rmeta','.lib','.dll']}
paths=[Path(__file__),*[p for p in H.iterdir()if p.is_file()],RES/'protocol.json',RES/'report.json',R/'runs/E085-source/manifest.json',C/'common_e080_live.py',C/'protected-main.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md']
P={'id':'E085-kernel-control','at':old.now(),'status':'FROZEN_PRE_FIRST_NUMERICAL_LAUNCH',
    'rustc_command':cmd,'input_sha256':deps|{str(p):old.sha(p)for p in paths},
    'resource_report':str(RES/'report.json'),'raw_output':str(H/'evidence'),
    'expected_cases':819,'expected_launches':1638,
    'sealed_PTX_sha256':{a:old.sha(H/(a+'.ptx'))for a in ['baseline','candidate']},
    'scope':'OneRustcompiler,one819pair1638launch process with sealed120PTX(noNVRTC),then separate full raw reader. Preserve all5rawimages; no production activation, numerical retry/extension/source/cache/clobber/width/helper/scope/placement variants or performance sample. Actual failure closes exact form.',
    'candidate_accepted':False}
old.save(H/'protocol.json',P)
pub=[]
for folder in [H,RES,R/'runs/E085-resource-manager']:
    for p in folder.rglob('*'):
        if not p.is_file()or p.suffix not in ['.json','.py','.rs','.cu','.patch','.log']:continue
        key=folder.name+'/'+p.relative_to(folder).as_posix();dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
        if dst.exists():assert dst.read_bytes()==p.read_bytes()
        else:shutil.copyfile(p,dst)
        with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as response:assert response.read()==p.read_bytes()
        pub.append(key)
old.save(H/'pre-execution-publication.json',{'at':old.now(),'HTTP_verified_artifacts':pub,'protocol_sha256':old.sha(H/'protocol.json'),'application_kernel_launches':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E085')
    e.update(stage='Full raw GPU action controls',reason='Compiled resource gates pass:62to56registers, unchanged64local/0shared,128thread theoretical occupancy8to9. Run fixed819 full action pairs. No speed result.')
    e['evidence'].extend([{'label':'Actual compiled resources','url':'evidence/E085-resource-r2/report.json'},{'label':'Frozen full raw action matrix','url':'evidence/E085-kernel-control/protocol.json'}])
    s.update(updated_at=old.now(),stage='E085 full raw GPU accuracy controls',activity='Compiled resource limits pass. Compare full strategy,regret,CFV,input and guard images on819fixed action cases before complete-solve timing. E080 remains live at14.74% registered improvement.')
    old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print(old.sha(H/'protocol.json'),flush=True)
