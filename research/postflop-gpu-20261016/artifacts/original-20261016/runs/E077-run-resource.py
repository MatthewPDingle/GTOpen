"""Execute and publish the sole sealed selective-prefix resource prerequisite."""
from pathlib import Path
import json,shutil,subprocess,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
H=R/'runs/E077-resource';S=R/'runs/E077-source';D=R/'runs/D124-prefix-liveness';M=R/'runs/E077-resource-manager';P=old.read(H/'protocol.json')
old.custody();assert not (R/'gpu-run.lock').exists()and not M.exists();M.mkdir()
for p,h in P['input_sha256'].items():old.pin(p,h)
old.child([sys.executable,'-B',str(H/'execute.py'),old.sha(H/'protocol.json')],M,'resource',old.env(),600)
q=old.read(H/'report.json');e=old.read(M/'resource.exit.json');assert e['returncode']==0 and e['error']is e['cleanup']is None
assert q['all_owned_children_terminal']and q['application_kernel_launches']==0 and q['solver_executions']==0
old.custody();assert not (R/'gpu-run.lock').exists();passed=q['status']=='pass_compiled_selective_prefix_prerequisites'
def publish(p,key):
 dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert dst.read_bytes()==p.read_bytes(),key
 else:shutil.copyfile(p,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
 return {'url':'evidence/'+key,'sha256':old.sha(p)}
pub=[]
for folder in [H,H/'execution',M,S,R/'runs/E077-preparation-draft-r1',R/'runs/E077-preparation-draft-r1/source']:
 for p in folder.iterdir():
  if not p.is_file()or p.suffix not in ['.json','.py','.rs','.cu','.ptx','.patch','.log']:continue
  if folder==H/'execution':key=H.name+'-execution/'+p.name
  elif folder.name=='source'and folder.parent.name=='E077-preparation-draft-r1':key=folder.parent.name+'/source/'+p.name
  else:key=folder.name+'/'+p.name
  pub.append(publish(p,key))
pub.append(publish(Path(__file__),H.name+'/run-resource.py'))
failed=[k for k,v in q['gates'].items()if not v];b=q['rows'][0];c=q['rows'][10]
reason='Compiled selective-prefix prerequisites pass; exact host tagger and full raw GPU controls remain. No numerical or speed result.'if passed else'Closed at compiled prerequisite: '+', '.join(failed)+'. No flag/map/mask/guard/source/helper/width/placement variants or resampling.'
old.save(M/'closure.json',{'at':old.now(),'status':q['status'],'report_sha256':old.sha(H/'report.json'),'all_owned_children_terminal':True,'application_kernel_launches':0,'source_main_live_PTX_custody_pass':True,'HTTP_byte_verified_artifacts':pub,'reason':reason})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);row=next(x for x in s['experiments']if x['id']=='E077');row.update(status='running'if passed else'rejected',stage='Compiled host-tag and full raw GPU controls next'if passed else'Closed: compiled prerequisite failed',reason=reason,accepted=False,updated_at=old.now());row['evidence'].append({'label':'Resource/ABI/PTX mask outcome','url':'evidence/E077-resource/report.json'});s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E077'if passed else None,stage='Preparing E077 exact host/GPU controls'if passed else'Investigating the next GPU optimization',activity=reason+' E051 accepted/live cumulative gain12.44% unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'### E077 selective prefix materialization compiled prerequisite'not in raw
entry=f'''

### E077 selective prefix materialization compiled prerequisite

D124 retained-demand model admitted one prototype: canonical flops have86.1670007195%/84.0668103988% unused weighted shared-prefix cells, integer/source counts only. One CUDA entry changes: low31bit masks at the two original physical-hand dereferences, and bit31 guards on unread prefix[k]=acc stores and dead prefix[k]+=base offset additions. Original ordered local acc, chunk_sum serial recurrence, every barrier, each consumed prefix, card corrections and payouts remain. Same27-argument ABI, shared arrays, launch/graph schedule and output spans. No E022/E062/E059/E073/E076 source composed. Candidate CUDA SHA {old.sha(S/'candidate.cu')}.

Three-file off-tree source bundle also includes one pure integer host tag helper and constructor call after unchanged budget checks/before context creation. It marks lower/upper-boundary predecessor indices and final total in the existing constructor-owned sorted-index vectors, without new arrays/fields/buffers/bytes/synchronizations or changed upload lifetime/order. Public GpuPlan::build, saved/query model and physical hand IDs remain original. One exact-tag/idempotence unit is prepared but not executed yet. CPU tag loops stay inside whole constructor clocks; no free-cost or material proof.

Preparation R1 stopped before any compiler/protocol/native execution because read_text normalized the copied accepted CUDA CRLF to LF. Original script, failed copied baseline and explicit failure preserved in E077-preparation-draft-r1. Repair copies original baseline bytes and candidate newline convention, checking normalized round-trip equality. No candidate arithmetic, experiment scope or gate changed after a completed compilation/observation. Sole resource protocol {old.sha(H/'protocol.json')} frozen/published before compiler/native work.

One Rust compiler and one no-application-kernel process,4 NVRTC compiles across compute120/75 and10 fixed resource shapes per arm, all terminal0. Status {q['status']}; failed gates {json.dumps(failed)}. Show registers {b['registers']} to {c['registers']}, local {b['local_bytes_per_thread']} to {c['local_bytes_per_thread']}, static shared {b['static_shared_bytes']} to {c['static_shared_bytes']}. Exact ABI27, other8 entries exact modulo only compiler-local function ordinal labels, newly emitted low31bit masks and resource feasibility in report SHA {old.sha(H/'report.json')}. Resource warnings {json.dumps(q['resource_warnings'])}. Static FP opcode counts remain diagnostic only. No dynamic store/traffic, SASS, compiled host correctness, GPU raw numeric/state, actual CPU/host/GPU peak/capacity or speed claim. {reason}

All{len(pub)} published code/protocol/failure/report/log/PTX artifacts HTTP byte verified. Accepted162/main163/live/protected2PTX exact, no production source activated, all owned children terminal. No primary timings or E077 adoption. Accepted/deployed E051 cumulative12.4372274192% and last primary B243 unchanged. Goal active; if resources pass, follow the frozen source through12 compiled host-tag maps and exact full GPU input/output/guard controls before unchanged fixed1%/strict-fixture/fresh16/broad/state/F32/menu/save/resume/continuation/material/holdout/cumulative qualification.
''';nl=b'\r\n'if b'\r\n'in raw else b'\n';ledger.write_bytes(raw+entry.encode().replace(b'\n',nl));old.custody();subprocess.run(['git','commit','--only','-m','research: compile selective showdown prefix materialization','--','research/postflop-gpu-20261016/experiments.md'],cwd=old.REPO,check=True);old.custody();print(json.dumps({'resource_status':q['status'],'failed_gates':failed,'resource_warnings':q['resource_warnings'],'registers':[b['registers'],c['registers']],'next':'exact_host_and_GPU_controls'if passed else'new_independent_mechanism','source_activated':False}),flush=True)
