"""Root replay and immutable closure of a compiled no-op; never run solves."""
import json,re,shutil,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists();R=ROOT/'runs/E113-resource';q=h.read(R/'report.json');p=h.read(R/'protocol.json');h.pin(R/'protocol.json',q['protocol_sha256'])
for name,d in p['input_sha256'].items():h.pin(name,d)
assert q['status']=='rejected_closed_resource_or_ABI_gate';failed=[k for k,v in q['gates'].items()if not v];assert failed==['compute_120:hot_action_emitted_change','compute_75:hot_action_emitted_change'];assert not q['resource_warnings']
for label in ['rustc','probe']:
 x=h.read(R/'execution'/(label+'.exit.json'));assert x['returncode']==0 and x['error']is x['cleanup']is None
def entries(path):
 text=path.read_text(encoding='utf-8');out={}
 for m in re.finditer(r'\.visible\s+\.entry\s+(\w+)\s*\(',text):
  a=text.index('{',m.end());i=a+1;depth=1
  while depth:
   depth+=(text[i]=='{')-(text[i]=='}');i+=1
  out[m.group(1)]=text[m.start():i]
 return out
def alpha(text):
 return re.sub(r'\$L__func_(begin|end)\d+',r'$L__func_\1_FUNCTION',re.sub(r'__local_depot\d+','__local_depot_FUNCTION',re.sub(r'\$L__BB\d+_(\d+)',r'$L__BB_FUNCTION_\1',text)))
checks=0
for arch in ['compute_120','compute_75']:
 b=entries(R/('baseline-'+arch+'.ptx'));c=entries(R/'execution'/('candidate-'+arch+'.ptx'));assert set(b)==set(c)==set(p['original_entries'])
 for name in b:assert alpha(b[name])==alpha(c[name]);assert b[name].split('{',1)[0]==c[name].split('{',1)[0];checks+=2
rows={(x['variant'],x['kernel']):x for x in q['resource_rows']};keys=['registers','local_bytes_per_thread','constant_bytes','static_shared_bytes','dynamic_shared_bytes','max_threads','occupancy_by_threads','device_shared_limit','device_thread_limit','context_stack_before','context_stack_after']
for name in p['original_entries']:
 b,c=rows['baseline',name],rows['candidate',name]
 for key in keys:assert b[key]==c[key];checks+=1
 assert b['application_kernels']==c['application_kernels']==0
S=ROOT/'runs/E113-source';m=h.read(S/'manifest.json');s=h.read(S/'source-review.json');assert s['qualifiers_added']==19 and s['all_function_bodies_byte_exact']and s['reverse_byte_exact']and not m['source_activated'];assert h.read(ROOT/'runs/D259-writable-alias-scout/unexecuted-broader-drafts.json')['native_tests']==0
O=ROOT/'runs/E113-compiler-checkpoint';O.mkdir(exist_ok=False);reason='All19writablefloatqualifiers produced identical9entryPTX oncompute120/75 and identical actualdriver resources. Required hot-action emitted change absent; close entirefixedform before applicationkernels/solves. No subset/flags/helper/source/sample rescue. E080 remains live.'
h.save(O/'root-replay.json',{'at':h.now(),'status':'confirmed_compiled_noop_rejection','checks':checks,'all18entry_bodies_alpha_exact':True,'all18headers_ABI_exact':True,'all9actual_resource_rows_exact':True,'failed_gates':failed,'report_sha256':h.sha(R/'report.json'),'same_agent_root_replay_not_external_audit':True,'application_kernels':0,'solver_executions':0,'performance_samples':0,'candidate_accepted':False})
h.save(O/'report.json',{'id':'E113-compiler-checkpoint','at':h.now(),'status':'rejected_closed_compiled_mechanism_absent','reason':reason,'resource_report_sha256':h.sha(R/'report.json'),'source_manifest_sha256':h.sha(S/'manifest.json'),'root_replay_sha256':h.sha(O/'root-replay.json'),'both_owned_children_terminal':True,'locks_absent':True,'accepted_main_live_protected_PTX_unchanged':True,'candidate_adopted':False,'goal_active':True,'all_new_bulk_X_S_read_only_no_T_access':True,'last_primary_baseline':'B356','next_unused_baseline':'B357'})
pub=[]
for folder in [S,R,R/'execution',O]:
 for path in folder.iterdir():
  if not path.is_file()or path.suffix not in['.json','.py','.rs','.log']:continue
  if folder==R/'execution':key='E113-resource-execution/'+path.name
  else:key=folder.name+'/'+path.name
  dst=h.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists():assert dst.read_bytes()==path.read_bytes()
  else:shutil.copyfile(path,dst)
  with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==path.read_bytes()
  pub.append({'url':'evidence/'+key,'sha256':h.sha(path)})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 status=h.read(h.ar.STATUS);e=next(x for x in status['experiments']if x['id']=='E113');e.update(status='rejected',accepted=False,stage='Closed: identical compiled code',correctness='No candidate application kernels; compiled form identical',reason=reason);e['evidence']+=[{'label':'Root replay of all18entries and9resources','url':'evidence/'+O.name+'/root-replay.json'},{'label':'Compiled no-op closure','url':'evidence/'+O.name+'/report.json'}];status.update(updated_at=h.now(),state='running',goal_status='active',active_experiment='E113',stage='Compiler no-op closed; distinct lead scouting next',activity='E112 failed fresh16 at0.212947% withriverguard; E113 adds no emitted kernel change. Both closed; E080/GPU/compressed/16/defaultaffinity remains best qualified/live. No new gain adopted.');h.ar.atomic_json(h.ar.STATUS,status)
ledger=h.REPO/'research/postflop-gpu-20261016/experiments.md';prefix=ledger.read_bytes();assert b'\n### D259 and E113 writable CUDA formal contract'not in prefix;assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=h.REPO,text=True).strip()
entry=f'''

### D259 and E113 writable CUDA formal contract - compiled no-op closure

Prior turn E112 initial3pair screen passed2.021265664%; current separatefixed16pair confirmation rejected at0.212946995320%,11/16improvingpairs,two negativeblockmedians andriver3.856718319196%slower in10/16pairs. All96records/736checkpoints exact; fullall66/physicalCFV canonicalproof remainsretained. Confirmation andall32reports published/HTTPbyteverified,all35children terminal,E080live. Entireconstantformclosed withoutrescue. Two preparatory broaderdrafts formed whilewaiting butneverexecuted; no broaderprotocol/compiler/native test created, conditionalpreparer refusesfailedconfirmation. Their hashes andunexecuted disposition recordedadditively.

D259 bounded28localCUDArevisions/818retainedCUDAfiles/198uniquehashes found nopriorwritableoriginalactionformal restrictions. Exactcaller design coversseparateownedCudaSlices andsame-formalwithin-CFV/reach reuse. NVIDIA12.9primaryrestrictdocumentation recordsprogrammeraliaspromise andregister-pressure risk; documentation/source arenotnumerical/costproof. SourceprototypeE113 adds exactly19qualifiers to9entries+2existinginlinehelpers withallbodies/ABItypes/order/counts/host/allocations/graphs/flags/quality untouched; CRLF andpositioninverse byteexact. NoE112constant,E075ldu,E099pairedmemory,E054earlystore orregister-cap formcomposed.

Frozenmodule-only protocol {h.sha(R/'protocol.json')} completedoneRustcompiler/onehelperprocess/twocandidateNVRTC12.9targets120/75; sealedE080baselinePTX reused. All18entry bodiesalphaexact,all18headers/ABIs exact,andall9actualdriverregister/local/constant/shared/occupancy/stack/maxthread/defaultlimitrows exact. Requiredhot-action emittedchangeabsentonbotharchitectures; originalqualifierformrejectedandclosedbeforeanyapplicationkernel/solver/speed/numericaltrial. Noqualifier/entrysubset/helper/flags/source/sample rescue. RootCPUreplay {h.sha(O/'root-replay.json')} has{checks}checks; sameagentreview,notexternalindependentaudit. IdenticalPTX isnot universal compiler/aliasing/no-tradeoff proof. Allsource/protocol/logs/errors preservedonX;{len(pub)}newartifactsHTTPbyteverified. Allownedchildren terminal,locksabsent,accepted/main/live/protected2PTX unchanged. E080/GPU/compressed/16/defaultaffinity remainslive,no newgainadopted,lastprimaryB356,nextB357. NewbulkX,Sarchivereadonly,noTaccess,priorledgerprefix byteexact,goalactive.
'''
ledger.write_bytes(prefix+entry.encode());assert ledger.read_bytes()[:len(prefix)]==prefix;h.custody();subprocess.run(['git','add','--','research/postflop-gpu-20261016/experiments.md'],cwd=h.REPO,check=True);assert subprocess.check_output(['git','diff','--cached','--name-only'],cwd=h.REPO,text=True).splitlines()==['research/postflop-gpu-20261016/experiments.md'];subprocess.run(['git','-c','gc.auto=0','commit','-m','research: close ineffective writable alias qualifier form'],cwd=h.REPO,check=True);h.save(O/'publication.json',{'at':h.now(),'HTTP_byte_verified_artifacts':pub,'local_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=h.REPO,text=True).strip(),'candidate_adopted':False,'all_owned_children_terminal':True,'goal_active':True});h.custody();print(json.dumps({'status':'closed_compiled_noop','root_checks':checks,'published_artifacts':len(pub),'candidate_adopted':False}),flush=True)
