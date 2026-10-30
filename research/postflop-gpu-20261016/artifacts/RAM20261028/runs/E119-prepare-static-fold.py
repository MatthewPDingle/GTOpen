"""Freeze one default-width fold ladder, retaining every original CTA barrier."""
import ast,hashlib,json,re,shutil,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists()
D=ROOT/'runs/D288-static-fold-scout';D.mkdir(exist_ok=False);history=[];seen={};hits=[]
for folder in [Path(r'S:\GTOpen-research\postflop-gpu-20261016\runs'),ROOT/'runs']:
 r=subprocess.run(['rg','--files',str(folder),'-g','*.cu'],capture_output=True,text=True,check=True);paths=r.stdout.splitlines()
 for p in paths:
  data=Path(p).read_bytes();digest=hashlib.sha256(data).hexdigest()
  if digest in seen:seen[digest].append(p);continue
  seen[digest]=[p];text=data.decode('utf-8');a=text.find('extern "C" __global__ void up_fold(')
  if a<0:continue
  b=text.find('extern "C" __global__',a+20);body=text[a:b if b>=0 else len(text)];offsets=sorted(set(int(x)for x in re.findall(r'total_parts\[\s*(?:threadIdx\.x|tid)\s*\+\s*(\d+)\s*\]',body)))
  if offsets:hits.append({'path':p,'sha256':digest,'literal_offsets':offsets,'CTA_barrier_intrinsics':len(re.findall(r'__syncthreads(?:_or|_and|_count)?\s*\(',body)),'has_shuffle':'__shfl'in body,'contains_full64_to1_ladder':all(v in offsets for v in [64,32,16,8,4,2,1])})
 history.append({'root':str(folder),'CUDA_files':len(paths)})
revs=subprocess.check_output(['git','log','--all','--format=%H','--','crates/solver/src/gpu/kernels.cu'],cwd=h.REPO,text=True).splitlines();localhits=[]
for rev in revs:
 data=subprocess.check_output(['git','show',rev+':crates/solver/src/gpu/kernels.cu'],cwd=h.REPO);t=data.decode('utf-8');a=t.find('extern "C" __global__ void up_fold(')
 if a>=0:
  b=t.find('extern "C" __global__',a+20);body=t[a:b if b>=0 else len(t)];off=sorted(set(int(x)for x in re.findall(r'total_parts\[\s*(?:threadIdx\.x|tid)\s*\+\s*(\d+)\s*\]',body)))
  if off:localhits.append({'revision':rev,'offsets':off})
assert not any(x['contains_full64_to1_ladder']for x in hits),'Matching retained form requires manual semantic review before source admission'
h.save(D/'history.json',{'at':h.now(),'inventories':history,'unique_CUDA_hashes':len(seen),'local_all_ref_CUDA_revisions':len(revs),'static_offset_hits':hits,'local_static_offset_hits':localhits,'semantic_classification':'Existing E019 is a fewer-barrier warp-shuffle tail, including original64/32sharedsteps; it removes4CTAbarriers. Proposed form keepsall7CTAbarriers andall7sharedmemoryadds, changesonly dynamicstep loopcontrol into fixed128step ladder. No shuffle,warp-tail cut,partialcopy fusion or sharedlayout hunk. E108 changes showdownceil division, notthisfoldreduction. D062 identity-key foldreuse declined again withoutcensus because unchanged action-alternation/reach-owner source proves no duplicates. Bounded literal/local history is not exhaustive remote/semantic novelty proof.'})
shapes=[]
for width in range(1,257):
 steps=[];v=width>>1
 while v>0:steps.append(v);v>>=1
 candidate=[64,32,16,8,4,2,1]if width==128 else steps.copy();assert steps==candidate
 groups=[[(tid,tid+step)for tid in range(step)]for step in steps];assert all(0<=a<b<width for phase in groups for a,b in phase)
 shapes.append({'width':width,'original_steps':steps,'candidate_steps':candidate,'CTA_barriers':len(steps),'ordered_pairs':groups})
h.save(D/'dependency-model.json',{'at':h.now(),'all256widths':shapes,'scope':'Exactorderedsharedaddress dependency pairs andoneCTAbarrier aftereachphase. Initialization/card/partial/payout loops unchanged.128ladder7samephases; allotherwidthsgenericoriginalbody. Not compiledfloating/IEEE/NaN orGPUresultproof.'})
S=ROOT/'runs/E119-source';S.mkdir(exist_ok=False);original=(h.REPO/'crates/solver/src/gpu/kernels.cu').read_bytes();text=original.decode('utf-8');assert original.count(b'\n')==original.count(b'\r\n');a=text.index('extern "C" __global__ void up_fold(');b=text.index('extern "C" __global__ void up_show(',a);body=text[a:b]
old='''    for (int step = blockDim.x >> 1; step > 0; step >>= 1) {
        if (threadIdx.x < (u32)step)
            total_parts[threadIdx.x] += total_parts[threadIdx.x + step];
        __syncthreads();
    }'''.replace('\n','\r\n');assert body.count(old)==1
ladder='#if __CUDA_ARCH__ == 1200\r\n    if (blockDim.x == 128) {\r\n'
for step in [64,32,16,8,4,2,1]:ladder+=f'        if (threadIdx.x < {step}u)\r\n            total_parts[threadIdx.x] += total_parts[threadIdx.x + {step}];\r\n        __syncthreads();\r\n'
ladder+='    } else\r\n#endif\r\n'+old
candidate=(text[:a]+body.replace(old,ladder,1)+text[b:]).encode('utf-8');assert candidate.replace(ladder.encode(),old.encode(),1)==original
(S/'baseline.cu').write_bytes(original);(S/'candidate.cu').write_bytes(candidate)
h.save(S/'manifest.json',{'id':'E119','at':h.now(),'status':'FROZEN_OFF_TREE_PRE_COMPILER','baseline_sha256':h.sha(S/'baseline.cu'),'candidate_sha256':h.sha(S/'candidate.cu'),'single_edit':{'old':old,'new':ladder},'entire_CRLF_source_inverse_exact':True,'target':'up_fold only, compute120 actualblock128 only','all7originalsharedadds_andCTAbarriers_retained':True,'original_generic_otherwidth_body_byte_exact':True,'other_architectures_original_source_tokens':True,'host_ABI_arrays_payload_grid_width_arithmetic_quality_unchanged':True,'risks':'Extrauniformbranch/code, register allocation/scheduling/JIT effects maylose. No occupancy/speed/numerical/material claim. Exactsourcebound/width/ladder/fallback/helper/flags/quality/sample form closes after genuine failure.','history_and_dependency_sha256':{n:h.sha(D/n)for n in ['history.json','dependency-model.json']}})
h.save(D/'report.json',{'id':'D288','at':h.now(),'status':'pass_scoped_static_step_source_and_dependency_review','history_sha256':h.sha(D/'history.json'),'dependency_model_sha256':h.sha(D/'dependency-model.json'),'source_manifest_sha256':h.sha(S/'manifest.json'),'kernel_source_inverse_exact':True,'all256supportedwidthcontrol_models_exact':True,'seven128threadCTAbarriers_retained':True,'new_compilers_GPU_kernels_solvers_or_speed_samples':0,'limits':'Source/integer recurrence only. Actual128branch/7sameadd andbarriercodegen/fallback stillmustinspect before unchanged full360foldGPUcorpus. No rescueofE019fewerbarriers orD062identitycache; no rawIEEEor speed proof.'})
R=ROOT/'runs/E119-resource';R.mkdir(exist_ok=False);shutil.copyfile(S/'candidate.cu',R/'candidate.cu')
for arch in ['compute_120','compute_75']:shutil.copyfile(ROOT/'runs/E118-resource'/('baseline-'+arch+'.ptx'),R/('baseline-'+arch+'.ptx'))
(R/'probe.rs').write_bytes((ROOT/'runs/E118-resource/probe.rs').read_bytes().replace(b'E118_RESOURCE',b'E119_RESOURCE'))
code=(ROOT/'runs/E118-resource-execute.py').read_text(encoding='utf-8').replace('E118','E119').replace("tables[arch]['up_show']","tables[arch]['up_fold']")
oldgate="gates[arch+':'+name+':barriers_exact']=len(re.findall(r'\\bbar\\.(?:sync|red)\\b',b[name]))==len(re.findall(r'\\bbar\\.(?:sync|red)\\b',c[name]))";assert code.count(oldgate)==1
code=code.replace(oldgate,"gates[arch+':'+name+':static_barrier_inventory_expected']=c[name].count('bar.sync')==b[name].count('bar.sync') if arch=='compute_75'else c[name].count('bar.sync')>=b[name].count('bar.sync') # Staticunroll hasmorestaticbarriers; same7dynamic128phases mustpassseparateactualCFGproof.",1)
code=code.replace('zero-tie fastpath and FP mechanism pending','static reduction-loop mechanism pending').replace('Finite zero-tie output prefix; actual guarded absence of tot_c/same/valid/tied work and exact baseline-prefix FP provenance plus barrier/caller reviews remain','Same originalfoldreduction, explicit128step control; actualuniform128branch, ordered7sharedadd/barrier recurrence andunchangedgenericfallback proofs remain').replace('changed up_show entry','changed up_fold entry')
ast.parse(code);script=ROOT/'runs/E119-resource-execute.py';assert not script.exists();script.write_bytes(code.encode('utf-8'))
oldP=h.read(ROOT/'runs/E118-resource/protocol.json');cmd=[x.replace('E118-resource','E119-resource')for x in oldP['rustc_command']]
files=[Path(__file__),script,ROOT/'epoch/common.py',h.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',h.REPO/'research/postflop-gpu-20261016/resource-feasibility-policy-20261017.md',ROOT/'runs/E118-resource-execute.py',ROOT/'runs/E118-resource/probe.rs']+[p for folder in[D,S,R]for p in folder.iterdir()if p.is_file()]+[p for p in(ROOT/'reference/accepted-e080-deps').iterdir()if p.is_file()]
h.save(R/'protocol.json',{'id':'E119-resource','at':h.now(),'status':'FROZEN_PRE_ONE_COMPILER_AND_MODULE_ONLY_PROCESS','rustc_command':cmd,'GPU_uuid':oldP['GPU_uuid'],'original_entries':oldP['original_entries'],'target_entries':['up_fold'],'required_free_bytes':16*1024**3,'input_sha256':{str(p):h.sha(p)for p in files},'resource_gates':'All9headers/8otherentrybodiesandresourcesexact,120foldbodychanged,75all9normalizedbodiesexact. No local/constant/dynamic/stackgrowth/maxthreadloss/defaultlimitloss;positive64/128/256occupancy, register/static/residency changesdisclosed underD108. Staticbarriercount onlyinventory, notdynamicbarrierproof.','mechanism_prerequisite':'Afterresourcepass, actualPTX128branch mustexecute7originalorderedsharedadds/barriers withfixed64..1offsets andretainedgenericloop. No fewerbarrier/shuffle/partialcopy/otherwidthspecialization. Then entireoriginal360foldcases includingall14actualinputbuffers/wholeoutputs/guards/widths/exceptionalbitpatterns.','prospective_speed_screen_order':'BeforeanyE119numericortimingresults: directexactfoldcontrols andordinary86units precede initialfrozen3pairfullcycle(whole-science/fingerprint/EV/stops/checkpoints exact). Broaderfullrawcanonical/engine/material/compatibility remainmandatory beforeadoption; theymayfollowaninitialspeedpass toavoidbulkrawoutputforalreadyfailedspeedforms. All1%strictfixture/fresh16/holdout/currentRAMcumulative/appgatesunchanged. Noexistingfrozenprotocol/result alteredorloosened.','no_application_kernel_solver_or_speed_samples_yet':True,'failure':'Closefixedladder/block/architecture/loop/helper/guard/source/flags/quality/sample form afteranygenuinefailure; no rescue variants. No sourceactivation/mainserverchange.'})
verified=[]
for folder,names in [(D,['report.json','history.json','dependency-model.json']),(S,['manifest.json']),(R,['protocol.json'])]:
 for name in names:
  p=folder/name;rel=folder.name+'/'+name;dst=h.ar.DASHBOARD/'evidence'/rel;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
  with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+rel,timeout=20)as z:assert z.read()==p.read_bytes()
  verified.append({'path':rel,'sha256':h.sha(p)})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);assert not any(x['id']in['D288','E119']for x in s['experiments']);s['experiments'] +=[{'id':'D288','title':'Fold reduction control and dependency review','kind':'diagnostic','status':'measured','accepted':False,'stage':'Source and 256-width dependency models passed','reason':'A fixed 128-thread ladder keeps every original shared addition and CTA barrier. Other widths and architectures retain the original loop. Compiled mechanism and numerical results remain unproven.','evidence':[{'label':n,'url':'evidence/'+D.name+'/'+n}for n in ['report.json','history.json','dependency-model.json']]},{'id':'E119','title':'Static fold-reduction steps with unchanged barriers','kind':'candidate','status':'staged','accepted':False,'stage':'Frozen compiler/resource prerequisite','reason':'One CUDA-only change, default128-thread fold control oncompute120; same math and all7barriers. Directexactcontrols/units precede earlyspeed screen; fulladoptiongates unchanged.','evidence':[{'label':'Fixed source','url':'evidence/'+S.name+'/manifest.json'},{'label':'Prospective compiled gates','url':'evidence/'+R.name+'/protocol.json'}]}];s.update(updated_at=h.now(),state='running',goal_status='active',active_experiment='E119',stage='Static fold steps: resource and emitted-code gate',activity='D287 closed. E119 preserves all additions and barriers; no numerical or performance claim yet. E080 remains live.');h.ar.atomic_json(h.ar.STATUS,s)
h.save(R/'preparation-publication.json',{'at':h.now(),'HTTP_byte_verified':verified,'protocol_sha256':h.sha(R/'protocol.json')});h.custody();print(json.dumps({'protocol_sha256':h.sha(R/'protocol.json'),'retained_unique_CUDA':len(seen),'static_offset_history_hits':len(hits),'candidate_sha256':h.sha(S/'candidate.cu')}),flush=True)
