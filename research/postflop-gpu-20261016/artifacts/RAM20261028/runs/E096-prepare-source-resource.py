import ast,hashlib,json,re,shutil,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();assert not(ROOT/'gpu-run.lock').exists();h.ar.refuse_active(h.ar.live_status());S=ROOT/'runs/E096-source';S.mkdir(exist_ok=False);name='crates/solver/src/gpu/kernels.cu';original=(h.REPO/name).read_bytes();text=original.decode();replacements=[]
def function_span(source,n):
 m=re.search(r'void\s+'+n+r'\(',source);assert m;a=source.index('{',m.end());j=a+1;depth=1
 while depth:
  if source[j]=='{':depth+=1
  elif source[j]=='}':depth-=1
  j+=1
 return a,j
for function in ['up_chance','up_action_impl','up_action_eval']:
 a,z=function_span(text,function);body=text[a:z];pos=0;parts=[];last=0;count=0
 while True:
  i=body.find('cfv[',pos)
  if i<0:break
  j=i+4;depth=1
  while depth:
   if body[j]=='[':depth+=1
   elif body[j]==']':depth-=1
   j+=1
  expression=body[i:j];index=expression[4:-1];after=body[j:].lstrip();pos=j
  if after.startswith('='):continue
  assert 'cfv_slot[' in index and ('children[' in index or 'cc_child[' in index)
  replacement='__ldcg(cfv + '+index+')';parts.append(body[last:i]+replacement);last=j;count+=1;replacements.append({'function':function,'original':expression,'candidate':replacement})
 parts.append(body[last:]);new=''.join(parts);text=text[:a]+new+text[z:];assert count=={'up_chance':1,'up_action_impl':4,'up_action_eval':5}[function]
reverse=text
for row in reversed(replacements):
 # Identical expressions may occur repeatedly; reverse all10 replacements by consuming one match each.
 assert row['candidate'] in reverse;reverse=reverse.replace(row['candidate'],row['original'],1)
assert reverse.encode()==original and len(replacements)==10 and text.count('__ldcg(')==10
(S/'baseline.cu').write_bytes(original);(S/'candidate.cu').write_bytes(text.encode())
queries=[['git','log','--all','--oneline','-G',r'__ldcg|ld\.global\.cg','--',name],['rg','-l',r'__ldcg|ld\.global\.cg',r'S:\GTOpen-research\postflop-gpu-20261016\runs','-g','*.cu','-g','*.rs']];history=[]
for command in queries:
 p=subprocess.run(command,cwd=h.REPO,capture_output=True,text=True);assert p.returncode in [0,1] and not p.stderr and not p.stdout.strip();history.append({'command':command,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
h.save(S/'history-review.json',{'at':h.now(),'exact_form_queries':history,'scope':'Bounded all-local-ref CUDA history and retained old-epoch CU/RS source query; no matching explicit .cg CFVload. Current ledger E033/E034 are context-reservationmetadata policies; E085 changes strategy store cacheoperator, E075 uniform immutable metadata load. These stayclosed and are not composed. Not exhaustive remote semantic uniqueness.'})
h.save(S/'manifest.json',{'id':'E096','at':h.now(),'status':'STAGED_OFF_TREE_NOT_ACTIVATED','owned':{name:{'base':str(S/'baseline.cu'),'candidate':str(S/'candidate.cu'),'base_sha256':h.sha(S/'baseline.cu'),'candidate_sha256':h.sha(S/'candidate.cu')}},'accepted_source_sha256':h.custody(),'candidate_owned_sha256':{name:h.sha(S/'candidate.cu')},'tracked_owned_paths':[name],'new_owned_paths':[],'byte_exact_reverse':True})
h.save(S/'source-review.json',{'id':'E096','at':h.now(),'status':'one_hint_form_staged_for_compile_prerequisites','scope':'Exactly10 child-CFV RHS reads in3 sourcefunctions/3 compiled entrypoints up_chance/up_action/up_action_eval become CUDA __ldcg on identicalu64 address expression. EveryCFVstore and allfloat expressions/order/sourceotherwiseunchanged. Nohost/planner/allocation/ABI/launch/capture/cadence/quality/precision/format change. Fullsourcebyte reversal exact.','source_replacements':replacements,'official_contracts':[{'url':'https://docs.nvidia.com/cuda/archive/12.9.1/cuda-c-programming-guide/index.html#load-functions-using-cache-hints','paraphrase':'CUDA12.9 documents typed load intrinsics with the named PTX cache operator on supported devices.'},{'url':'https://docs.nvidia.com/cuda/parallel-thread-execution/index.html#cache-operators','paraphrase':'.cg requests L2 and lower cache levels while bypassingL1. These operators are performance hints and preserve memory-consistency behavior. Intrinsic/API support alone proves neither intended codegen nor speed.'}],'coherence':'Same globalCFVallocation, alignedf32 addresses, originalordered kernels and graph dependencies. This is coherentglobal .cg, not incoherentreadonly .nc or new restrict assumption. Sourceoperands identify alreadycomputed child rows; no newlyassertedimmutability or alias contract and no reordering/bypassbarrier. Originalplainloads/streamordering preserve read-after-write acrosskernels; cacheoperator doesnotweaken memorymodel. FullphysicalCFVpoison/raw/lifetime controls remain mandatory, including generic action paths where values reload afterregret/stratwrites.','hypothesis':'Streamingchildvalue loads may evict usefulL1metadata or see little reuse; L2only could helporhurt. No measuredheadroom or guaranteed gain. Current originalactualPTX shows no .cg; first require param-origin candidateCFV.cg32 loads inall3entries and unchanged6otherentry bodies/ABI/barriers, no resourcefeasibility failure.','resource_gate':'D108 feasibility: sameglobalpayload/allfixedshapes, no newlocal/spill or dynamicshared, maxthreadsnotlowered, positive64/128/256occupancy/defaultlimits/stack. Disclose anyreg/shared/occupancy difference. Resourcesonly, no kernel/solve/speed beforepass.','failure':'Any genuine mechanism/ABI/resource/numeric/cost/speed failure closes form without cacheop/entrysubset/flags/source/shape/precision/sample rescue. All later exactness/1%/strictfixture/fresh16/broad/material/capacity/holdout/freshoriginal/application gates unchanged.','candidate_accepted':False})
H=ROOT/'runs/E096-resource';H.mkdir(exist_ok=False);parent=ROOT/'runs/D170-offset-width/probe.rs';code=parent.read_text(encoding='utf-8').replace('D170_RESOURCE','E096_RESOURCE').replace('["down_action","up_action","up_action_eval"]','["up_chance","up_action","up_action_eval"]');assert code!=parent.read_text(encoding='utf-8');(H/'probe.rs').write_text(code,encoding='utf-8',newline='\n')
for variant in ['baseline','candidate']:shutil.copyfile(S/(variant+'.cu'),H/(variant+'.cu'))
deps=ROOT/'reference/accepted-e080-deps';cmd=['rustc',str(H/'probe.rs'),'--edition=2021','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-L','dependency='+str(deps)]
for n,f in [('cudarc','libcudarc-ba3140064b5903a3.rlib'),('serde_json','libserde_json-83a0670a02a34a4d.rlib')]:cmd+=['--extern',n+'='+str(deps/f)]
cmd+=['-o',str(H/'probe.exe')];files=[Path(__file__),ROOT/'runs/E096-resource-execute.py',S/'manifest.json',S/'source-review.json',S/'history-review.json',ROOT/'runs/D175-CFV-load-policy-scope/scope-review.json',ROOT/'runs/D175-CFV-load-policy-scope/history-attribution-addendum.json',ROOT/'epoch/common.py',parent]+[p for p in H.iterdir() if p.is_file()]+[p for p in deps.iterdir() if p.is_file()];ast.parse((ROOT/'runs/E096-resource-execute.py').read_text(encoding='utf-8'))
h.save(H/'protocol.json',{'id':'E096-resource','at':h.now(),'status':'FROZEN_PRE_COMPILER_AND_MODULE_QUERY','measurement_epoch':'RAM20261028','GPU_uuid':'GPU-a5459b5a-632b-3e73-d7f1-a06e167102ee','rustc_command':cmd,'required_free_bytes':16*1024**3,'expected_entries':h.read(ROOT/'runs/E091-resource/protocol.json')['expected_entries'],'targets':{'up_chance':{'cfv_param':12,'parameters':15},'up_action':{'cfv_param':16,'parameters':20},'up_action_eval':{'cfv_param':14,'parameters':17}},'input_sha256':{str(p):h.sha(p) for p in files},'scope':'Onecompiler/one no-application-kernel module/resourceprocess,4actual12.9NVRTCcompiles current120andcompat75. ExactABI/barrier/other6entries; param-originCFVloadchangesandD108resourcefeasibilityprerequisites. No sourceactivation/numeric/solve/speed/adoption. Any genuine failure closesformwithoutintrinsic/cacheop/source/flags/entrysubsetrescue.'})
for folder,names in [(S,['manifest.json','source-review.json','history-review.json']),(H,['protocol.json'])]:
 for filename in names:
  p=folder/filename;dst=h.ar.DASHBOARD/'evidence'/folder.name/filename;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
  with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+folder.name+'/'+filename,timeout=20) as response:assert response.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);next(x for x in s['experiments'] if x['id']=='D175').update(status='measured',stage='Bounded history/source review completed; one cache hint form staged',correctness='no_numeric_or_speed_claim',reason='No matching explicitCFV.cg loads found in boundedhistory. Officialcoherent cachehint contract; only10childreads and nohostwork/payloadchange. Compileprerequisite first.');s['experiments'].append({'id':'E096','title':'L2-only child CFV loads','kind':'optimization','status':'running','accepted':False,'measurement_epoch':'RAM20261028','correctness':'pending_resource_and_raw_controls','stage':'Frozen no-launch compiler/resource prerequisite','reason':'Ten child-value reads use documented coherentL2-only hint, sameaddresses/floatorder/host/payloads/quality. Couldhelp orhurt; no speedresult.','evidence':[{'label':'Source and coherence contract','url':'evidence/'+S.name+'/source-review.json'},{'label':'Frozen compiler prerequisite','url':'evidence/'+H.name+'/protocol.json'}]});s.update(updated_at=h.now(),active_experiment='E096',stage='Child CFV load compiler prerequisite',activity='One documented cachehint form staged after boundedhistory audit. Verify actualintendedloads/ABI/unaffectedkernels/resources before any applicationkernel. E080/16 unchanged.');h.ar.atomic_json(h.ar.STATUS,s)
print(h.sha(H/'protocol.json'),flush=True)
