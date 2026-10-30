"""Freeze the current allocation/ABI screen after D102 integer controls pass."""
import ast,json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();old.ar.refuse_active(old.ar.live_status());assert not (ROOT/'gpu-run.lock').exists()
C=ROOT/'runs/D102-card-cutoffs-r3';cpu=old.read(C/'report.json')
assert cpu['status']=='pass_cpu_integer_selector_proof_only' and cpu['all_children_terminal'] and cpu['rows']==4591358 and cpu['checks']==331138998
S=ROOT/'runs/E063-source';H=ROOT/'runs/E063-resource';assert not H.exists();H.mkdir();parent=ROOT/'runs/E062-resource';oldp=old.read(parent/'protocol.json')
assert (ROOT/'runs/D102-card-cutoffs/helper.rs').read_bytes()==(C/'helper.rs').read_bytes()
assert (S/'candidate-mod.rs').read_text(encoding='utf-8').endswith((C/'helper.rs').read_text(encoding='utf-8'))
for n in ['baseline.cu','candidate.cu']:(H/n).write_bytes((S/n).read_bytes())
(H/'probe.rs').write_text((parent/'probe.rs').read_text(encoding='utf-8').replace('E062','E063'),encoding='utf-8',newline='\n')
runner=(parent/'execute.py').read_text(encoding='utf-8').replace('E062','E063')
a=runner.index(" for variant in ['baseline','candidate']:\n  for arch in ['compute_120','compute_75']:\n   gates[")
b=runner.index('\n details={};abi={}',a);runner=runner[:a]+runner[b:]
assert 'legacy_ptx' not in runner;ast.parse(runner);(H/'execute.py').write_text(runner,encoding='utf-8',newline='\n')
P={k:oldp[k] for k in ['changed_entries','shapes','shape_dimensions','up_show_parameter_count','gpu_uuid','expected_entries','allocation_proof']}
P.update(id='E063-resource',at=old.now(),status='FROZEN_PRE_RESOURCE_NATIVE',source_manifest_sha256=old.sha(S/'manifest.json'),cpu_integer_proof={'path':str(C/'report.json'),'sha256':old.sha(C/'report.json')},rustc_command=[s.replace(str(parent),str(H)) for s in oldp['rustc_command']],fixed_gates='One fixed E063form. Current unchanged D094allocated warp/block registers, local/shared/dynamic/maxthread/occupancy/fit on all10registered shapes. Exact27parameter ABI and8other entries actual andcompute75; up_showchanged. No application kernel or timing before pass. If any fails close source form without loop/packing/width/placement/block/cap variants. If passes require compiled mechanism review, complete direct-kernel bytes with actual packed metadata, ordinary suites and fixed3whole-cycle pairs;1%/strict-fixture/fresh16/broad/material/holdout/cumulative still mandatory.')
paths=[*S.iterdir(),*H.iterdir(),Path(__file__),C/'report.json',C/'protocol.json',C/'helper.rs',C/'probe.rs',ROOT/'runs/D102-card-cutoffs/protocol.json',ROOT/'runs/D102-card-cutoffs/execution/rustc.exit.json',ROOT/'runs/D102-card-cutoffs-r2/not-executed.json',ROOT/'runs/D094-resource-materiality/report.json',ROOT/'runs/D094-resource-materiality/test-report.json',old.REPO/'tools/postflop_resource_admission.py',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',old.REPO/'research/postflop-gpu-20261016/resource-admission-policy-20261017.md',ROOT/'runs/accepted-E051/common_e051.py']
P['input_sha256']={str(p):old.sha(p) for p in paths if p.is_file()}|{p:h for p,h in oldp['input_sha256'].items() if Path(p).suffix in ['.rlib','.lib']}
cmd=P['rustc_command'];assert cmd[cmd.index('--crate-name')+1] and 'lto=thin' in cmd and 'codegen-units=1' in cmd;old.save(H/'protocol.json',P)
published={}
def put(p,key):
 dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert dst.read_bytes()==p.read_bytes()
 else:dst.write_bytes(p.read_bytes())
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
 published[key]=old.sha(p)
for folder in [ROOT/'runs/D102-card-cutoffs',ROOT/'runs/D102-card-cutoffs-r2',C,H]:
 for p in folder.rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.exe','.pdb','.dll','.obj','.lib','.exp','.bin']:put(p,folder.name+'/'+p.relative_to(folder).as_posix())
put(ROOT/'runs/D102-prepare.py','D102-preparation/D102-prepare.py')
old.save(H/'pre-execution-publication.json',{'at':old.now(),'published':published,'http_bytes_verified':True,'resource_native_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);e=next(e for e in st['experiments'] if e['id']=='D102');e.update(status='completed',correctness='pass',accepted=False,stage='CPU selector proof passes; no GPU/speed claim',reason='All12retained baseline cases:4,591,358rows,124,948,396card positions,331,138,998integer/rank/list/order checks and1,828,606disjoint field values exact. Extra temporary host capacity max4,998,544bytes; GPU payload length unchanged. Initial linker failure and unexecuted command-validation correction preserved. No floating GPU result or performance measurement.');e['evidence'].append({'label':'Complete CPU proof result','url':'evidence/D102-card-cutoffs-r3/report.json'})
 assert not any(e['id']=='E063' for e in st['experiments']);st['experiments'].append({'id':'E063','at':old.now(),'kind':'candidate','title':'Precomputed per-card showdown split boundaries','status':'running','correctness':'pending','accepted':False,'stage':'Compiler/resource filter before GPU numerical work','reason':'Pack CPU card-local split counts into unused bits of existing two GPU boundary words. Same ordered floating subsequences and public plan meanings. Extra temporary host cost bounded and must be counted; no adoption or speed claim.','evidence':[{'label':'Fixed source and memory/order proof','url':'evidence/E063-source/source-review.json'},{'label':'Current resource/ABI protocol','url':'evidence/E063-resource/protocol.json'},{'label':'CPU selector proof','url':'evidence/D102-card-cutoffs-r3/report.json'}]});st.update(updated_at=old.now(),state='running',active_experiment='E063',stage='E063 compiled-resource gate',activity='CPU per-card boundary packing/order proof passes. Check actual compiled resources before any application kernel; preserve current1%no-material-tradeoff qualification.');old.ar.atomic_json(old.ar.STATUS,st)
old.custody();print(json.dumps({'status':'resource_probe_frozen','protocol_sha256':old.sha(H/'protocol.json'),'CPU_checks':cpu['checks'],'published':len(published),'application_kernel_executions':0}),flush=True)
