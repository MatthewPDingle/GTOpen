"""Replay scalar/kernel evidence and admit fresh integrated E060 artifacts."""
import array,ast,json,struct,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
SC=ROOT/'runs/E060-scalar-control';K=ROOT/'runs/E060-kernel-control';RES=ROOT/'runs/E060-resource';D=ROOT/'runs/E060-source'
scalar=old.read(SC/'execution/raw/report.json');root=old.read(ROOT/'comparisons/E060-kernel-control-root-check/report.json')
assert scalar['mismatches']==0 and root['checks']==63899 and root['full_raw_files_equal'] and root['all_parent_child_cfv_rows_disjoint']
for p,h in root['raw_file_sha256'].items():old.pin(p,h)
for home in [SC,K]:
 for label in ['rustc','probe']:
  r=old.read(home/'execution'/(label+'.exit.json'));assert r['returncode']==0 and r['error'] is r['cleanup'] is None
old.save(K/'execution/terminal.json',{'at':old.now(),'exec_chunk_id':'f3306f','returncode':0,'all_children_terminal':True,'complete_sha256':old.sha(K/'execution/complete.json'),'root_report_sha256':old.sha(ROOT/'comparisons/E060-kernel-control-root-check/report.json'),'no_native_rerun':True})
checks=0
def check(x):
 global checks
 assert x;checks+=1
def readwords(path,magic):
 b=path.read_bytes();check(b.startswith(magic));n=struct.unpack_from('<Q',b,len(magic))[0];check(len(b)==len(magic)+8+4*n);v=array.array('I');v.frombytes(b[len(magic)+8:]);check(len(v)==n);return v
raw=SC/'execution/raw';inputs=readwords(raw/'inputs.bin',b'E060SCALIN1');after=readwords(raw/'inputs-after.bin',b'E060SCALIN1');check(inputs==after)
base=readwords(raw/'scalar_baseline.bin',b'E060SCALOUT1');cand=readwords(raw/'scalar_candidate.bin',b'E060SCALOUT1');check(base==cand)
n=scalar['cases'];check(len(inputs)==2*n and len(base)==n+32)
check(list(base[:16])==[0xa55a06e0]*16 and list(base[-16:])==[0xa55a06e0]*16)
f=memoryview(inputs).cast('B').cast('f');threshold=struct.unpack('<f',struct.pack('<I',0x2b8cbccc))[0];low=2.0**-60;high=2.0**60
counts={'shared':0,'fallback':0,'uniform':0}
for i in range(n):
 r,den=f[2*i:2*i+2];num=r if r>0.0 else 0.0
 if den>threshold and den<=high and (num==0.0 or num>=low):check(0.0<=num<=den and den<=high);counts['shared']+=1
 elif den>threshold:counts['fallback']+=1
 else:counts['uniform']+=1
check(counts=={'shared':scalar['shared_refinement_cases'],'fallback':scalar['native_fallback_cases'],'uniform':scalar['uniform_cases']})
R=ROOT/'comparisons/E060-scalar-root-check';R.mkdir()
old.save(R/'report.json',{'id':R.name,'at':old.now(),'status':'pass_scoped_scalar_bit_equivalence','checks':checks,'cases':n,'path_counts':counts,'full_outputs_byte_identical':True,'all_input_words_unchanged':True,'all_guard_words_exact':True,'raw_artifact_sha256':{str(p):old.sha(p) for p in raw.iterdir() if p.is_file()},'source_expression_extraction_verified':True,'limits':'Differential result bits from two separate compiled CUDA entry functions and sampled caller-valid float pairs. Not exhaustive all-float or other-GPU proof; baseline is the original native division, candidate expressions extracted from fixed source.','root_review_only':True,'performance_measured':False,'candidate_accepted':False})
H=ROOT/'runs/E060-build-plan';H.mkdir();prior=ROOT/'runs/E055-build-plan'
s=(prior/'build-r2.py').read_text(encoding='utf-8').replace('E055','E060').replace('build-protocol-r2.json','build-protocol.json').replace('E060-final-build-r2','E060-final-build').replace("sha(HERE/'build-r2.py')","sha(HERE/'build.py')")
ast.parse(s);(H/'build.py').write_text(s,encoding='utf-8',newline='\n')
P=old.read(prior/'build-protocol-r2.json');P.pop('original_protocol_sha256',None);P.pop('repair',None)
P.update(id='E060-final-build',at=old.now(),status='FROZEN_PRE_INTEGRATED_BUILD',accepted_source_sha256=old.BASE,protected_main=str(ROOT/'runs/accepted-E051/protected-main.json'),owned={'crates/solver/src/gpu/kernels.cu':{'base':str(D/'baseline.cu'),'base_sha256':old.sha(D/'baseline.cu'),'candidate':str(D/'candidate.cu'),'candidate_sha256':old.sha(D/'candidate.cu')}})
P['phases']=[{**x,'target':x['target'].replace('e055','e060'),'outputs':{k:v.replace('E055','E060') for k,v in x['outputs'].items()}} for x in P['phases']]
for x in P['phases']:assert not Path(x['target']).exists()
paths=[H/'build.py',*D.iterdir(),R/'report.json',SC/'protocol.json',SC/'execution/complete.json',SC/'execution/raw/report.json',K/'protocol.json',K/'execution/complete.json',K/'execution/terminal.json',ROOT/'comparisons/E060-kernel-control-root-check/report.json',RES/'protocol.json',RES/'report.json',Path(P['protected_main']),ROOT/'runs/accepted-E051/common_e051.py',old.REPO/'tools/postflop_autoresearch.py',Path(__file__)]
P['input_sha256']={str(p):old.sha(p) for p in paths if p.is_file()};old.save(H/'build-protocol.json',P)
published=[]
def put(p,prefix):
 key='evidence/'+prefix+'/'+p.name;dst=old.ar.DASHBOARD/key;dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert dst.read_bytes()==p.read_bytes(),key
 else:dst.write_bytes(p.read_bytes())
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
 published.append({'path':str(p),'url':key,'sha256':old.sha(p)})
for folder in [D,H,R,ROOT/'comparisons/E060-kernel-control-root-check']:
 for p in folder.iterdir():
  if p.is_file():put(p,folder.name)
for folder in [RES,SC,K]:
 for p in folder.iterdir():
  if p.is_file() and p.suffix in ['.json','.py','.rs','.cu']:put(p,folder.name)
 for p in (folder/'execution').iterdir():
  if p.is_file() and p.suffix in ['.json','.log']:put(p,folder.name+'-native')
old.save(H/'pre-build-publication.json',{'at':old.now(),'published':published,'http_bytes_verified':True,'candidate_accepted':False,'raw_binary_evidence_retained_on_S_not_copied_to_web':True})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);e=next(e for e in st['experiments'] if e['id']=='E060')
 e.update(stage='Raw scalar and complete action-kernel controls passed; building solver',reason='2,130,758scalar outputs exact;819full kernel cases/1,638launches exact,12,375,858output words/5,199,114immutable words/10,240,828guards. Compiled allocation and local storage unchanged. No timing claim yet.')
 e['evidence'].extend([{'label':'Fixed exact CUDA transform','url':'evidence/'+D.name+'/candidate.patch'},{'label':'Scalar raw root replay','url':'evidence/'+R.name+'/report.json'},{'label':'Whole-kernel raw root replay','url':'evidence/E060-kernel-control-root-check/report.json'},{'label':'Resource attributes and allocation','url':'evidence/E060-resource/report.json'},{'label':'Fresh integrated build protocol','url':'evidence/'+H.name+'/build-protocol.json'}])
 st.update(updated_at=old.now(),state='running',active_experiment='E060',stage='E060 fresh integrated builds',activity='Exact scalar/kernel controls passed. Building fresh feature and primary binaries; restore accepted E051 source after each compile.');old.ar.atomic_json(old.ar.STATUS,st)
old.custody();print(json.dumps({'build_protocol_sha256':old.sha(H/'build-protocol.json'),'scalar_checks':checks,'kernel_root_checks':root['checks'],'published':len(published)}),flush=True)
