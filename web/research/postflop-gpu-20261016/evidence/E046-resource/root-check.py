"""Root no-launch resource cross-check and pointer-qualified PTX ABI observer repair."""
import hashlib,json,re,sys,urllib.request
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'small-gain-confirmation-plan'));import common as old
P=old.read(HERE/'protocol.json');R=old.read(HERE/'report.json');checks=0
def req(v,m):
 global checks
 assert v,m;checks+=1
for p,h in P['input_sha256'].items():old.pin(p,h);checks+=1
old.custody();req(not (old.ROOT/'gpu-run.lock').exists(),'no active probe/compiler')
for label in ['rustc','probe']:
 receipt=old.read(HERE/'execution'/(label+'.exit.json'));req(receipt['returncode']==0 and receipt['error'] is None and receipt['cleanup'] is None,'terminal child')
 req(receipt['command']==old.read(HERE/'execution'/(label+'.invocation.json'))['command'],'recorded invocation')
rawpath=HERE/'execution/probe.stdout.log';old.pin(rawpath,R['stdout_sha256']);raw=rawpath.read_text(encoding='utf-8')
markers=[json.loads(x.split('E046_RESOURCE ',1)[1]) for x in raw.splitlines() if 'E046_RESOURCE ' in x]
req(markers==R['raw_markers'] and len(markers)==4,'all raw markers')
b,c=markers[1:3];req([b['variant'],c['variant']]==['baseline','candidate'],'arm order')
req(b['registers']==30 and c['registers']==40,'measured register increase')
req(b['occupancy_by_threads']==c['occupancy_by_threads']==[[64,24],[128,12],[256,6]],'same theoretical occupancy')
req(all(x['kernel_launches']==0 for x in markers),'no launches')
def entries(path):
 text=path.read_text(encoding='utf-8');result={};at=0
 while True:
  at=text.find('.visible .entry ',at)
  if at<0:return result
  paren=text.index('(',at);name=text[at+len('.visible .entry '):paren].strip();opening=text.index('{',paren);end=opening+1;depth=1
  while depth:
   depth+=(text[end]=='{')-(text[end]=='}');end+=1
  req(name not in result,'unique PTX entry');result[name]=text[at:end];at=end
e={v:entries(HERE/'execution'/(v+'.ptx')) for v in ['baseline','candidate']}
req(set(e['baseline'])==set(e['candidate'])==set(P['expected_entries']),'entry inventory')
for name in P['expected_entries']:req((e['baseline'][name]==e['candidate'][name])==(name!='up_chance'),'only changed chance entry')
abi={}
for variant in ['baseline','candidate']:
 head=e[variant]['up_chance'].split('{',1)[0]
 params=re.findall(r'\.param\s+\.(u[0-9]+)((?:\s+\.ptr\s+\.align\s+[0-9]+)?)\s+up_chance_param_([0-9]+)',head)
 req([int(x[2]) for x in params]==list(range(15 if variant=='baseline' else 13)),'all contiguous parameter indices')
 abi[variant]=[{'type':x[0],'pointer':bool(x[1]),'index':int(x[2])} for x in params]
 expected_types=['u64','u32','u32']+['u64']*(10 if variant=='baseline' else 8)+['u32','u32']
 req([x['type'] for x in abi[variant]]==expected_types,'ABI type order')
 req(all(x['pointer']==(x['type']=='u64') for x in abi[variant]),'all expected pointer qualifiers')
req(R['abi']=={'baseline':['u32']*4,'candidate':['u32']*4},'preserved observer omitted qualified pointers')
req(R['gates']['registers_not_increased'] is False,'original decisive gate failure')
OUT=old.ROOT/'comparisons/E046-resource-root-check';OUT.mkdir()
report={'id':'E046-resource-root-check','at':old.now(),'status':'pass_rejected_resource','checks':checks,'root_cross_check_only':True,'resource_report_sha256':old.sha(HERE/'report.json'),'abi_observer_correction':{'cause':'Original regex did not allow .ptr .align1 between .u64 and parameter name; it captured only four scalar32bit parameters. Original report/source remain unchanged. Corrected decoder accepts the literal recorded pointer qualifier, checks every index/type/qualifier, and finds15 original/13 new expected parameters.','corrected_abi':abi,'original_abi_false_gates_are_observer_errors':True,'new_native_runs':0},'decisive_failure':'Registers30 to40 violates predeclared no-increase gate. Theoretical occupancy is unchanged; this does not establish lower throughput.','kernel_launches':0,'solver_executions':0,'performance_measured':False,'candidate_accepted':False,'accepted162_main_live_ptx_unchanged':True,'limits':'Source/resource/PTX and receipt verification by root, not external independent review. No numerical, capacity or speed qualification.'}
old.save(OUT/'report.json',report)
published={}
for directory in [HERE,OUT]:
 for src in directory.rglob('*'):
  if not src.is_file() or '__pycache__' in src.parts:continue
  key=directory.name+'/'+src.relative_to(directory).as_posix();dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);data=src.read_bytes()
  if dst.exists():req(dst.read_bytes()==data,'immutable publication')
  else:dst.write_bytes(data)
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:req(response.read()==data,'HTTP bytes')
  published[key]=old.sha(src)
old.save(HERE/'closure-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published,'decision':'rejected_resource_gate','kernel_launches':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 status=old.read(old.ar.STATUS);row=next(x for x in status['experiments'] if x['id']=='E046');row.update(status='rejected',stage='Closed at compiled resource gate',reason='Registers30 to40 violates fixed no-increase gate; occupancy unchanged24/12/6 blocks per SM. Other8 entries exact; corrected raw PTX decoder verifies15-to13 expected arguments. Original ABI regex error preserved. No numerical/kernel/solver/timing work or rescue. E020 retained.')
 row['evidence'].extend([{'label':'E046 resource rejection','url':'evidence/E046-resource/report.json'},{'label':'E046 root check and ABI observer correction','url':'evidence/E046-resource-root-check/report.json'}]);status.update(state='running',stage='Next source investigation',activity='E046 closed before numerical/timing work. Accepted E020 retained.',updated_at=old.ar.now());old.ar.atomic_json(old.ar.STATUS,status)
ledger=old.ar.REPO/'research/postflop-gpu-20261016/experiments.md';prior=ledger.read_bytes();assert b'## D076 bounded packing; E046 resource rejection' not in prior
text=f'''

## D076 bounded packing; E046 resource rejection

D076 refined its interleaved chance-record proposal to keep every public CPU GpuPlan array and avoid a new host packing allocation. The proposed constructor would pack checked3*N u32 words into the existing pinned staging capacity, copy/drain before reuse or error propagation, and use a stack triplet only for staging below3words. Three private device arrays would become one with the same12*N payload; both training/evaluation callers and observed_metadata accounting would change. This host design was not implemented after the resource rejection. A novelty check hashed278 prior preserved CUDA files and searched local all-ref GPU history; no earlier candidate match was found, without claiming exhaustive remote history.

Off-tree CUDA source manifest977b4cdb8cb36a4172f669c15feebbe9eed4750c29bec6ab82f19c7a0c5d617e binds candidate0396eea5736f799ff2592dcfa9abe40846a3770b5a25b80a0ae40ef8f86cc5a1. Only up_chance changes: one interleaved u32 pointer replaces three, record addressing uses64-bit3*t, and the exact mask/permutation/child accesses, ascending reduction and float expressions stay ordered. Resource protocolabc64b2a57581ed2e3fe49696dbf8bf0fe1d4f732af800ce4286515d01e0cde5 ran once off-tree with no production activation, kernel or solver launch. Actual registers increase30 to40, local/static/dynamic shared remainzero, maximum threads stay1024, theoretical64/128/256-thread residency stays24/12/6. The other eight PTX entries are exact. The preset no-register-increase gate fails, so E046 is rejected; unchanged occupancy is not a claim of measured regression.

Original resource report2086fbb064b8956c300b28f562ef79751bdf8a3e1d59d7b1489c1272ef0504b6 also marked both ABI gates false because its regex ignored pointer-qualified PTX parameters. That report and observer are preserved unchanged. Root correction {old.sha(OUT/'report.json')} directly decodes every index/type and .ptr/.align qualifier, verifying the expected15 original and13 new parameters. This assessment-only repair leaves the decisive register rejection unchanged and executes no new native process. Root source/raw-marker/receipt checks are not an external independent audit.

Evidence is published and HTTP byte-verified. No host implementation, numerical test, solver timing, layout-width sweep, confirmation or adoption follows. Accepted162, main/HEAD/live and protected PTX stay exact; no owned process remains active. E020 remains accepted at its previously qualified10.3798454492% cumulative gain, last actual primary baselineB139. The goal remains active for further source investigation.
'''
nl=b'\r\n' if b'\r\n' in prior else b'\n';ledger.write_bytes(prior+text.encode('utf-8').replace(b'\n',nl))
print(json.dumps({'status':report['status'],'root_checks':report['checks'],'root_report_sha256':old.sha(OUT/'report.json'),'published_files':len(published)}),flush=True)
