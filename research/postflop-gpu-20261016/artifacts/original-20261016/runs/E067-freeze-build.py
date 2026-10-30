"""Direct raw-word replay and integrated-build freeze for E067."""
import array,ast,contextlib,json,struct,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
K=ROOT/'runs/E067-kernel-control';RES=ROOT/'runs/E067-resource';S=ROOT/'runs/E067-source';P=old.read(K/'execution-plan.json');q=old.read(K/'report.json');checks=0
assert sys.byteorder=='little'
def check(v):
 global checks
 assert v;checks+=1
for p,h in P['input_sha256'].items():old.pin(p,h);checks+=1
for label in ['rustc','probe']:
 x=old.read(K/'execution'/(label+'.exit.json'));check(x['returncode']==0 and x['error'] is x['cleanup'] is None)
check(q['cases']==1196 and q['kernel_launches']==2392 and q['status']=='pass_scoped_down_action_full_raw_equivalence')
for v in ['baseline','candidate']:check((K/(v+'.ptx')).read_bytes()==(RES/'execution'/(v+'-compute_120.ptx')).read_bytes())
for name,v in q['raw_files'].items():old.pin(name,v['sha256']);check(Path(name).stat().st_size==v['bytes'])
corpus=old.read(K/'corpus.json');check(len(corpus['cases'])==1196)
markers=[json.loads(x.split('E067_DOWN_RAW ',1)[1]) for x in (K/'execution/probe.stdout.log').read_text().splitlines() if x.startswith('E067_DOWN_RAW ')];check(len(markers)==1197)
class Reader:
 def __init__(self,f,magic):self.f=f;check(f.read(16)==magic)
 def id(self):
  b=self.f.read(4);check(len(b)==4);return struct.unpack('<I',b)[0]
 def vec(self):
  b=self.f.read(8);check(len(b)==8);n=struct.unpack('<Q',b)[0];check(n<=1000000);raw=self.f.read(n*4);check(len(raw)==n*4);a=array.array('I');a.frombytes(raw);return a
outputs=immutable=guards=0
with contextlib.ExitStack() as stack:
 readers={}
 for name,magic in [('inputs',b'E067-DOWN-IN1\0\0\0'),('baseline',b'E067-DOWN-OUT1\0\0'),('candidate',b'E067-DOWN-OUT1\0\0'),('baseline-inputs',b'E067-DOWN-IM1\0\0\0'),('candidate-inputs',b'E067-DOWN-IM1\0\0\0')]:readers[name]=Reader(stack.enter_context((K/'evidence'/(name+'.bin')).open('rb')),magic)
 for index,c in enumerate(corpus['cases']):
  for reader in readers.values():check(reader.id()==index)
  check(c['id']==index);d=list(readers['inputs'].vec());expected=[c[k] for k in ['nh0','nh1','actions','threads','actor','locked','value_mode','count','sigma_offset']]+[2,3,13];expected[4]&=0xffffffff;check(d==expected)
  src=[readers['inputs'].vec() for _ in range(12)];seeds=[readers['inputs'].vec() for _ in range(2)]
  b=[readers['baseline'].vec() for _ in range(2)];n=[readers['candidate'].vec() for _ in range(2)];check(b==n and list(map(len,b))==list(map(len,seeds)));outputs+=2*sum(map(len,b))
  for arm in ['baseline','candidate']:
   post=[readers[arm+'-inputs'].vec() for _ in range(12)];check(post==src);immutable+=sum(map(len,post))
  nh0,nh1,na=c['nh0'],c['nh1'],c['actions'];nn=na+9;actor=c['actor'];selected=0 if actor==0 else 1;nhs=[nh0,nh1];parent=3;count=c['count'];loff=c['sigma_offset'];a=nhs[selected]
  check(list(src[0])==[0xdeadbeef,0xdeadbeef,3,0xdeadbeef,0xdeadbeef])
  players=[0xfffffff9]*nn;players[parent]=actor&0xffffffff;check(list(src[1])==players)
  arity=[0xfffffff9]*nn;arity[parent]=na;check(list(src[2])==arity)
  offsets=[0]*(2*nn);offsets[2*parent]=13;check(list(src[3])==offsets)
  starts=[0]*nn;starts[parent]=2;check(list(src[4])==starts)
  children=[0xdeadbeef]*(na+4);children[2:2+na]=list(range(4,4+na));check(list(src[5])==children)
  map0=[0]*nn;map1=[0]*nn;map0[parent]=3;map1[parent]=5
  for j in range(na):map0[4+j]=8+2*(na-1-j);map1[4+j]=9+2*j
  check(list(src[6])==map0 and list(src[7])==map1)
  check(len(src[8])==30+na*nh0 and len(src[9])==30+na*nh1 and len(src[11])==loff+na*a+17)
  locks=[0xffffffff]*(2*nn)
  if c['locked']:locks[2*parent:2*parent+2]=[loff,0]
  check(list(src[10])==locks)
  for arm in range(2):
   check(len(seeds[arm])==(10+2*na)*max(nhs[arm],1)+17)
   owned=bytearray(len(seeds[arm]));mapping=[map0,map1][arm];nh=nhs[arm]
   if count and arm==selected and nh:
    ranges=[(mapping[4+j]*nh,(mapping[4+j]+1)*nh) for j in range(na)]
    check(len(set(mapping[4:4+na]))==na and all(hi<=len(owned) and not (lo<=mapping[parent]*nh<hi) for lo,hi in ranges))
    for lo,hi in ranges:owned[lo:hi]=b'\1'*(hi-lo)
   for j,active in enumerate(owned):
    if not active:check(b[arm][j]==n[arm][j]==seeds[arm][j]);guards+=2
  record=markers[index];check(record['stage']=='case' and record['id']==index and all(record[k]==c[k] for k in ['nh0','nh1','actions','threads','actor','locked','value_mode','count','sigma_offset']))
  check(record['output_words_per_arm']==sum(map(len,seeds)) and record['immutable_words_per_arm']==sum(map(len,src)) and record['all_raw_exact'] and record['guards_exact'])
 for reader in readers.values():check(reader.f.read()==b'')
check(outputs==q['output_words_both_arms']==30261968 and immutable==q['actual_immutable_words_both_arms']==13853760 and guards==q['guard_words_both_arms']==25889108)
R=ROOT/'comparisons/E067-kernel-control-root-check';assert not R.exists();R.mkdir()
old.save(R/'report.json',{'id':R.name,'at':old.now(),'status':'pass_scoped_down_action_full_raw_equivalence','checks':checks,'cases':1196,'kernel_launches':2392,'full_output_words_both_arms':outputs,'full_actual_device_input_words_both_arms':immutable,'guard_word_checks_both_arms':guards,'all_full_outputs_inputs_guards_exact':True,'resource_and_raw_ptx_byte_identical':True,'raw_files':q['raw_files'],'corpus_sha256':q['corpus_sha256'],'original_source_form':'D049/E043','current_source_candidate':'E067','source_activated':False,'performance_measured':False,'candidate_accepted':False,'limits':'Root separately parses retained raw files, reconstructs all integer metadata/argument dimensions/ownership, compares every actualinput and fulloutput/guard word. FPstress seeds are retained declared inputs, not an independent CPUfloat reference. Finite matrix, not fullsolver/graphs/compatibility/material/holdout/speed proof or external independent review. compute75compile is supplementary/unqualifiedforperformance; originalfailedextramechanismgate and pre-numericalscopeamendment retained.'})
old.save(K/'execution/terminal.json',{'at':old.now(),'native_child_receipt_sha256':old.sha(K/'execution/probe.exit.json'),'returncode':0,'all_children_terminal':True,'complete_sha256':old.sha(K/'execution/complete.json'),'root_report_sha256':old.sha(R/'report.json'),'no_native_reexecution':True})
H=ROOT/'runs/E067-build-plan';assert not H.exists();H.mkdir();prior=ROOT/'runs/E066-build-plan'
code=(prior/'build.py').read_text().replace('E066','E067');ast.parse(code);(H/'build.py').write_text(code,encoding='utf-8',newline='\n')
B=old.read(prior/'build-protocol.json');B.update(id='E067-final-build',at=old.now(),status='FROZEN_PRE_INTEGRATED_BUILD',accepted_source_sha256=old.BASE,original_source_form='D049/E043',owned={'crates/solver/src/gpu/kernels.cu':{'base':str(S/'baseline.cu'),'base_sha256':old.sha(S/'baseline.cu'),'candidate':str(S/'candidate.cu'),'candidate_sha256':old.sha(S/'candidate.cu')}})
B['phases']=[{**x,'target':x['target'].replace('e066','e067'),'outputs':{k:v.replace('E066','E067') for k,v in x['outputs'].items()}} for x in B['phases']]
for phase in B['phases']:check(not Path(phase['target']).exists())
paths=[H/'build.py',*S.iterdir(),RES/'protocol.json',RES/'report.json',K/'execution-plan.json',K/'report.json',K/'execution/complete.json',K/'execution/terminal.json',R/'report.json',Path(B['protected_main']),ROOT/'runs/accepted-E051/common_e051.py',ROOT/'runs/D108-resource-feasibility-audit/report.json',ROOT/'runs/D108-resource-feasibility-audit/docket.json',ROOT/'runs/D108-resource-feasibility-audit/commit.json',ROOT/'comparisons/E067-resource-mechanism-root-check/report.json',ROOT/'comparisons/E067-resource-mechanism-root-check/pre-numerical-scope-amendment.json',ROOT/'comparisons/E067-resource-mechanism-root-check/original-extra-gate-failure.json',old.REPO/'research/postflop-gpu-20261016/resource-feasibility-policy-20261017.md',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',old.REPO/'tools/postflop_resource_feasibility.py',old.REPO/'tools/postflop_autoresearch.py',Path(__file__)]
B['input_sha256']={str(p):old.sha(p) for p in paths if p.is_file()};old.save(H/'build-protocol.json',B)
published={}
for folder in [H,R,K,RES,ROOT/'comparisons/E067-resource-mechanism-root-check']:
 for p in folder.rglob('*'):
  if not p.is_file() or '__pycache__' in p.parts or p.suffix in ['.exe','.pdb','.bin']:continue
  key='evidence/'+folder.name+'/'+p.relative_to(folder).as_posix();dst=old.ar.DASHBOARD/key;dst.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists():check(dst.read_bytes()==p.read_bytes())
  else:dst.write_bytes(p.read_bytes())
  with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=20) as response:check(response.read()==p.read_bytes())
  published[key]=old.sha(p)
old.save(H/'pre-build-publication.json',{'at':old.now(),'artifact_sha256':published,'http_bytes_verified':True,'integrated_solver_executions':0,'raw_binaries_kept_on_S_registered_by_full_sha256':True})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);e=next(e for e in st['experiments'] if e['id']=='E067');e.update(stage='Full raw numerical matrix passed; fresh integrated builds',reason='1196pairs/2392launches:30,261,968fulloutput words,13,853,760actualinput words,25,889,108guards exact. Rootrawreplay passes; actualresource-qualifiedPTXsame. Freshfeature/primarybinaries next; no solve-speed measurement yet.');e['evidence'].extend([{'label':'Direct full raw root replay','url':'evidence/'+R.name+'/report.json'},{'label':'Fresh integrated build protocol','url':'evidence/'+H.name+'/build-protocol.json'}]);st.update(updated_at=old.now(),stage='E067 fresh integrated solver builds',activity='Exact original selected-map form passes fullraw GPUcontrols and separate retained-file replay. Accepted E051restored betweenbuildphases.');old.ar.atomic_json(old.ar.STATUS,st)
old.custody();print(json.dumps({'build_protocol_sha256':old.sha(H/'build-protocol.json'),'root_checks':old.read(R/'report.json')['checks'],'full_output_words':outputs,'actual_input_words':immutable,'guards':guards,'published':len(published)}),flush=True)