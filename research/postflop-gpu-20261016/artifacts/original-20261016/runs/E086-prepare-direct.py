"""Reuse the fixed canonical chance corpus with identical original mask ABI."""
import ast
import difflib
from pathlib import Path
import re
import shutil
import sys
import urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
C=R/'runs/accepted-E080-live-20261018'
sys.path.insert(0,str(C));import common_e080_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
assert shutil.disk_usage(R).free>=66*1024**3
RES=R/'runs/E086-resource';q=old.read(RES/'report.json')
assert q['status']=='pass_compiled_bitfield_prerequisites' and all(q['gates'].values())
x=old.read(R/'runs/E086-resource-manager/resource.exit.json')
assert x['returncode']==0 and x['error'] is x['cleanup'] is None
prior=R/'runs/E048-kernel-control';H=R/'runs/E086-kernel-control';H.mkdir(exist_ok=False)
for arm in ['baseline','candidate']:
    p=RES/'execution'/(arm+'-compute_120.ptx');old.pin(p,q['ptx_sha256'][arm+'-compute_120'])
    shutil.copyfile(p,H/(arm+'.ptx'))
original_corpus=old.read(prior/'corpus.json');corpus=dict(original_corpus)
corpus.update(id='E086-canonical-chance-corpus',raw_schema=corpus['raw_schema'].replace('E048','E086'))
assert corpus['cases']==original_corpus['cases'] and corpus['case_count']==425
old.save(H/'corpus.json',corpus)
probe=(prior/'probe.rs').read_text().replace('E048','E086')
probe,n=re.subn(r'  unsafe\{if new\{[^\n]+\n   else\{([^\n]+)\}\}\n',lambda m:'  unsafe{'+m.group(1)+'}\n',probe)
assert n==2 and 'if new{' not in probe
probe=probe.replace('new:bool','_new:bool')
probe=probe.replace('original-mask/new-card direct GPU comparator','original-mask/bit-field direct GPU comparator')
(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
for name in ['execute.py','audit.py']:
    t=(prior/name).read_text().replace('E048','E086')
    t=t.replace("HERE.parent/'small-gain-confirmation-plan'","HERE.parent/'accepted-E080-live-20261018'").replace('import common as old','import common_e080_live as old')
    if name=='execute.py':t=t.replace('pass_resource_feasibility_only','pass_compiled_bitfield_prerequisites').replace('54*1024**3','66*1024**3')
    t=t.replace('mask/card chance comparison','mask/bit-field chance comparison')
    ast.parse(t);(H/name).write_text(t,encoding='utf-8',newline='\n')
for name in ['probe.rs','execute.py','audit.py']:
    (H/(name+'.adaptation.patch')).write_text(''.join(difflib.unified_diff((prior/name).read_text().splitlines(True),(H/name).read_text().splitlines(True),fromfile='retained/'+name,tofile='E086/'+name)),encoding='utf-8',newline='\n')
old.save(H/'source-review.json',{'at':old.now(),'cases':425,'kernel_launches':850,
    'family_cases':{'down_chance_unchanged_control':157,'up_chance_changed_predicate':268},
    'corpus_descriptors_identical':True,'original_corpus_sha256':old.sha(prior/'corpus.json'),
    'adaptation':'Keep original425descriptors/order/geometry/float profiles/guards. Both arms now use original mask argument builder for both kernels; delete only historical candidate card-ID ABI branches and rename unused variant parameter. All original canonical mask/card-ID arrays still allocated and read back in both arms. Down_chance source/PTX unchanged; up_chance differs only in bit-field predicate. Corpus metadata changes only ID/raw-schema magic labels.',
    'coverage':'Every canonical1326hand/dealt52card relationship individually; both down player orientations/asymmetry; zero counts/empty lists/tails; five widths1/32/64/128/256; identity/nonidentity permutations; signedzero/subnormal/quietNaN/infinity/finite overflow. Full outputs,actual immutable inputs and unowned guards retained in3raw files. Positive finite down zero/copy relation separately checked.',
    'limits':'Finite canonical geometries/small offsets only. No malformed mask/large-address, universal NaN or whole-solver/speed proof.'})
P0=old.read(RES/'protocol.json');deps={p:h for p,h in P0['input_sha256'].items()if Path(p).suffix in ['.rlib','.rmeta','.lib','.dll']}
paths=[Path(__file__),*[p for p in H.iterdir()if p.is_file()],RES/'protocol.json',RES/'report.json',
    R/'runs/D137-bitfield-membership/integer-control.json',R/'runs/E086-source/manifest.json',
    C/'common_e080_live.py',C/'protected-main.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md']
P={'id':'E086-kernel-control','at':old.now(),'status':'FROZEN_PRE_FIRST_NUMERICAL_LAUNCH',
    'rustc_command':[p.replace(str(RES),str(H))for p in P0['rustc_command']],
    'input_sha256':deps|{str(p):old.sha(p)for p in paths},'resource_report':str(RES/'report.json'),
    'raw_output':str(H/'evidence'),'expected_cases':425,'expected_launches':850,
    'sealed_PTX_sha256':{a:old.sha(H/(a+'.ptx'))for a in ['baseline','candidate']},
    'scope':'OneRustcompiler/one425pair850launch native process using sealed120PTX(noNVRTC),then separate raw reader. No source activation,solver or speed score. All original cases retained,no tolerance,variant,extra sample or rescue on a real failure.',
    'candidate_accepted':False}
old.save(H/'protocol.json',P)
pub=[]
for folder in [H,RES,R/'runs/E086-resource-manager']:
    for p in folder.rglob('*'):
        if not p.is_file()or p.suffix not in ['.json','.py','.rs','.cu','.patch','.log']:continue
        key=folder.name+'/'+p.relative_to(folder).as_posix();dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
        if dst.exists():assert dst.read_bytes()==p.read_bytes()
        else:shutil.copyfile(p,dst)
        with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as response:assert response.read()==p.read_bytes()
        pub.append(key)
old.save(H/'pre-execution-publication.json',{'at':old.now(),'HTTP_verified_artifacts':pub,'protocol_sha256':old.sha(H/'protocol.json'),'application_kernel_launches':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E086')
    e.update(stage='Full raw chance-kernel controls',reason='Resource gates pass:30registers/local0/shared0/maxthreads1024/128thread residency12 unchanged. Run425fixed pairs with both arms using the original mask ABI. No speed result.')
    e['evidence'].extend([{'label':'Compiled resource observations','url':'evidence/E086-resource/report.json'},{'label':'Frozen raw chance matrix','url':'evidence/E086-kernel-control/protocol.json'}])
    s.update(updated_at=old.now(),stage='E086 full raw GPU accuracy controls',activity='Compiled resource limits match. Compare full chance-kernel outputs,actual immutable inputs and guard regions across425fixed pairs before complete-solve timing. E080 remains live.')
    old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print(old.sha(H/'protocol.json'),flush=True)
