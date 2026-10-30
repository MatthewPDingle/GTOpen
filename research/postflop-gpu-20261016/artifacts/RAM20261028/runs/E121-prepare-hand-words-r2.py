"""Freeze lossless terminal hand words; no production source activation."""
import ast,hashlib,json,re,shutil,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists()
def save_reuse(path,value):
 if path.exists():
  old=h.read(path);assert {k:v for k,v in old.items()if k!='at'}=={k:v for k,v in value.items()if k!='at'}
 else:h.save(path,value)

D=ROOT/'runs/D295-hand-word-scout';D.mkdir(exist_ok=True);seen={};hits=[];inventories=[]
pattern=re.compile(r'(?:hand_(?:word|desc)|(?:packed|encode)\w*_(?:hand|same)|same_p\s*\[[^\]]+\]\s*>>|(?:pc1|pc2)\s*\[[^\]]+\]\s*<<)',re.I)
for folder in [Path(r'S:\GTOpen-research\postflop-gpu-20261016\runs'),ROOT/'runs']:
 paths=subprocess.check_output(['rg','--files',str(folder),'-g','*.cu'],text=True).splitlines();inventories.append({'root':str(folder),'CUDA_files':len(paths)})
 for name in paths:
  data=Path(name).read_bytes();digest=hashlib.sha256(data).hexdigest()
  if digest in seen:continue
  seen[digest]=name;t=data.decode();regions=[]
  for entry in ['up_fold','up_show']:
   a=t.find('extern "C" __global__ void '+entry+'(')
   if a>=0:
    b=t.find('extern "C" __global__',a+20);regions.append(t[a:b if b>=0 else len(t)])
  found=[m.group()for body in regions for m in pattern.finditer(body)]
  if found:hits.append({'path':name,'sha256':digest,'hits':found})
local=[]
for name in ['kernels.cu','mod.rs']:
 revs=subprocess.check_output(['git','log','--all','--format=%H','--','crates/solver/src/gpu/'+name],cwd=h.REPO,text=True).splitlines();found=[]
 for rev in revs:
  t=subprocess.check_output(['git','show',rev+':crates/solver/src/gpu/'+name],cwd=h.REPO).decode()
  if pattern.search(t):found.append({'revision':rev,'matches':[m.group()for m in pattern.finditer(t)]})
 local.append({'path':name,'revisions':len(revs),'hits':found})
assert not hits and not any(v['hits']for v in local),'Prior matching form requires semantic review before admission'
refs=subprocess.check_output(['rg','-n','d_same|same_combo|d_hand_c1|d_hand_c2',str(h.REPO/'crates/solver/src/gpu'),'-g','*.rs'],text=True)
save_reuse(D/'history-and-callers.json',{'at':h.now(),'inventories':inventories,'unique_CUDA_hashes':len(seen),'retained_matches':hits,'all_local_ref_history':local,'pattern':pattern.pattern,'current_GPU_references':refs.splitlines(),'semantic_classification':'Private immutable per-hand descriptor, not E070 nodeplayer/arity byteencoding,E046 chance-recordAoS,E073 boundarynarrowing,E094 nodeoffsetnarrowing,E048 dealtcardmask rewrite or E115 node-row reorder. Closed mechanisms remain closed, no hunk composed. Sourcehistory boundedliteral/local, not exhaustive semantic/remote novelty proof.','caller_contract':'Only4terminal launch sites inmod.rs consume d_same(2training/evalpaths eachfold/show); d_hand_c1/c2stillallocated/uploaded/passed butterminalkernelstoppointees unused. Continuation wrappers route common GpuSolver; capacity accounting uses sameu32length. update_locks/iterate/sync do not rewrite immutable hand metadata. PublicGpuPlan/Spot same_combo/handcards andsaveformats remain original.'})
fields={'card1':{'bits':[0,5],'mask':63,'domain':[0,51]},'card2':{'bits':[6,11],'mask':63,'domain':[0,51]},'same':{'bits':[12,22],'mask':2047,'valid_index_domain':[0,1325],'absent_original':4294967295,'absent_encoded':2047}}
assert 52*51//2==1326 and 1325<2047 and (63|(63<<6)|(2047<<12))==0x7fffff
boundary=[]
for c1,c2 in [(0,1),(0,51),(25,26),(50,51)]:
 for same in [0,1,1325,0xffffffff]:
  word=c1|(c2<<6)|((2047 if same==0xffffffff else same)<<12);assert word&63==c1 and(word>>6)&63==c2 and(0xffffffff if word>>12==2047 else word>>12)==same;boundary.append([c1,c2,same,word])
save_reuse(D/'encoding-contract.json',{'at':h.now(),'fields':fields,'boundary_examples':boundary,'legal_tuple_count':1326*1327,'injectivity':'Three disjointbitfields; exactdecode recovers every legalc1/c2/same tuple. Sentinel2047 is outside all1326possibleopponentindices. Allhigh9bits zero. No float conversion or rounding operation. A private11bitsame domain isnot publicGpuPlan narrowing.','physical_changes':'Only d_same[0]andd_same[1] values become packedwords; sameu32type/length/allocation. Otherphysicalarraysincludinglegacyd_hand_c1/c2 remain identical. Direct/rawengine readers must independently decode every changedword; no field/padding exceptions or blanket comparison omission. EntireCFV/solver state requiredexact.','host_cost':'Two constructor-local Vecu32(ownhandcounts<=1326 each), nominalpayload<=10608B plusheaders/allocatoroverhead. No persistentnewCPU/GPUfield/globalallocation/graphnode/kernel/ABIparam. Allpacking/allocation/drop/upload/runtimecompile costs included in completecycles; actualmaterialqualificationstillrequired.','required_before_numerical':'Compiled actual resources and both27/21ABIs; intendedonehandwordload/decode andabsencepc1/pc2globaldependencies; original floatinginstructions/order,barriers/widths. Actual compiledhosthelper fulllegalintegerdomain andmixedvectors. Original allfold/show directcorpora with onlyindependentlyspecifiedmetadataencoding changed perarm. Full rawengine/canonical/broad/material/fresh16/holdout/cumulative/app beforeadoption.'})
helper='''fn terminal_hand_words(c1: &[u32], c2: &[u32], same: &[u32]) -> Vec<u32> {
    c1.iter().zip(c2).zip(same).map(|((&a, &b), &s)| {
        let index = if s == u32::MAX { 0x7ff } else { s };
        a | (b << 6) | (index << 12)
    }).collect()
}
'''
S=ROOT/'runs/E121-source';S.mkdir(exist_ok=True);assert not any(S.iterdir());orig=(h.REPO/'crates/solver/src/gpu/kernels.cu').read_bytes();text=orig.decode();assert orig.count(b'\n')==orig.count(b'\r\n');edits=[]
def part(entry,nextentry,replacements):
 global text
 a=text.index('extern "C" __global__ void '+entry+'(');b=text.index('extern "C" __global__ void '+nextentry+'(',a);body=text[a:b]
 for old,new in replacements:
  old=old.replace('\n','\r\n');new=new.replace('\n','\r\n');assert body.count(old)==1;body=body.replace(old,new,1);edits.append({'entry':entry,'old':old,'new':new})
 text=text[:a]+body+text[b:]
part('up_fold','up_show',[("        u32 sc = same_p[i];\n        float same_r = sc != SENTINEL ? ro[sc] : 0.f;\n        float valid = (float)(T - s[pc1[i]] - s[pc2[i]]) + same_r;","        u32 hand_word = same_p[i];\n        u32 sc = hand_word >> 12;\n        float same_r = sc != 0x7ffu ? ro[sc] : 0.f;\n        float valid = (float)(T - s[hand_word & 63u] - s[(hand_word >> 6) & 63u]) + same_r;")])
part('up_show','up_chance',[("        u32 cc[2] = { pc1[i], pc2[i] };","        u32 hand_word = same_p[i];\n        u32 cc[2] = { hand_word & 63u, (hand_word >> 6) & 63u };"),("        u32 sc = same_p[i];\n        float same_r = sc != SENTINEL ? ro[sc] : 0.f;","        u32 sc = hand_word >> 12;\n        float same_r = sc != 0x7ffu ? ro[sc] : 0.f;")])
cand=text.encode();inverse=cand
for e in reversed(edits):
 a=inverse.index(('extern "C" __global__ void '+e['entry']+'(').encode());b=inverse.find(b'extern "C" __global__',a+20);b=len(inverse)if b<0 else b;body=inverse[a:b];assert body.count(e['new'].encode())==1;inverse=inverse[:a]+body.replace(e['new'].encode(),e['old'].encode(),1)+inverse[b:]
assert inverse==orig;(S/'baseline.cu').write_bytes(orig);(S/'candidate.cu').write_bytes(cand)
mb=(h.REPO/'crates/solver/src/gpu/mod.rs').read_bytes();mt=mb.decode();assert b'\r\n'not in mb;medits=[]
def hostedit(old,new):
 global mt
 assert mt.count(old)==1;mt=mt.replace(old,new,1);medits.append({'old':old,'new':new})
hostedit('pub struct GpuSolver {',helper+'\npub struct GpuSolver {')
hostedit('    d_same: [CudaSlice<u32>; 2],','    // Terminal word: card1/card2 in 6+6 bits, same index in 11 bits (2047 absent).\n    d_same: [CudaSlice<u32>; 2],')
hostedit('        Ok(GpuSolver {','        let terminal_words = [\n            terminal_hand_words(&plan.hand_c1[0], &plan.hand_c2[0], &plan.same_combo[0]),\n            terminal_hand_words(&plan.hand_c1[1], &plan.hand_c2[1], &plan.same_combo[1]),\n        ];\n\n        Ok(GpuSolver {')
hostedit('            d_same: [up32(&plan.same_combo[0])?, up32(&plan.same_combo[1])?],','            d_same: [up32(&terminal_words[0])?, up32(&terminal_words[1])?],')
mc=mt.encode();inverse=mc
for e in reversed(medits):assert inverse.count(e['new'].encode())==1;inverse=inverse.replace(e['new'].encode(),e['old'].encode(),1)
assert inverse==mb;(S/'baseline-mod.rs').write_bytes(mb);(S/'candidate-mod.rs').write_bytes(mc);(S/'host-encode.rs').write_bytes(helper.encode())
owned={'crates/solver/src/gpu/kernels.cu':{'base':str(S/'baseline.cu'),'candidate':str(S/'candidate.cu'),'base_sha256':h.sha(S/'baseline.cu'),'candidate_sha256':h.sha(S/'candidate.cu')},'crates/solver/src/gpu/mod.rs':{'base':str(S/'baseline-mod.rs'),'candidate':str(S/'candidate-mod.rs'),'base_sha256':h.sha(S/'baseline-mod.rs'),'candidate_sha256':h.sha(S/'candidate-mod.rs')}}
h.save(S/'manifest.json',{'id':'E121','at':h.now(),'status':'FROZEN_OFF_TREE_PRE_COMPILER','owned':owned,'CUDA_edits':edits,'host_edits':medits,'entire_CUDA_CRLF_and_Rust_LF_inverse_exact':True,'contract_sha256':h.sha(D/'encoding-contract.json'),'history_sha256':h.sha(D/'history-and-callers.json'),'unchanged':'Allfloatingexpressions/operandvalues/order/precision/barriers/launchshape/dynamicshared/publicplan/capacityformula/save/quality/cadence. Earlyreadpackedintegerinshow replaces2cardloadsandlateindexload; originalsamefloatread/payoutposition retained. Other7CUDAentriesunchanged.','risks':'Integerdecode/longerwordlifetime/changedregisterallocation/JIT/hostpacking/temporaryvectors may erase load saving. No speed/material/equivalence claim. Onefixedencoding/source/masks/sentinel/width/architecture/helper/flags/quality/sampleform closesaftergenuinefailure.'})
h.save(D/'report.json',{'id':'D295','at':h.now(),'status':'pass_scoped_private_hand_word_source_and_integer_contract','source_manifest_sha256':h.sha(S/'manifest.json'),'bounded_unique_CUDA':len(seen),'all_local_ref_history':local,'legal_tuple_domain':1326*1327,'new_compilers_application_kernel_solver_or_speed_samples':0,'candidate_adopted':False,'limits':'Source/integerfieldcontract/callerreference audit only; actualcompiledresources/hosthelper/semanticloads/fullphysicalmetadata/rawGPU/engine/fullcyclequalification remainunproven.'})
R=ROOT/'runs/E121-resource';R.mkdir(exist_ok=False);shutil.copyfile(S/'candidate.cu',R/'candidate.cu');shutil.copyfile(S/'host-encode.rs',R/'host-encode.rs')
for arch in ['compute_120','compute_75']:shutil.copyfile(ROOT/'runs/E118-resource'/('baseline-'+arch+'.ptx'),R/('baseline-'+arch+'.ptx'))
# The separately frozen resource preparer will bind the actual host-domain probe and all readers before execution.
for folder,names in [(D,['report.json','history-and-callers.json','encoding-contract.json']),(S,['manifest.json'])]:
 for name in names:
  p=folder/name;key=folder.name+'/'+name;dst=h.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
  with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);assert not any(e['id']in['D295','E121']for e in s['experiments']);s['experiments'] +=[{'id':'D295','title':'Lossless terminal hand-word source and caller review','kind':'diagnostic','status':'measured','accepted':False,'stage':'Source and integer-field contract passed','reason':'Three original immutable per-hand fields fit losslessly in23bits. Publicplan unchanged; onlyprivate d_same values packed, allarraylengths/ABIs unchanged. Compiled/GPU correctness and speed unproven.','evidence':[{'label':n,'url':'evidence/'+D.name+'/'+n}for n in ['report.json','history-and-callers.json','encoding-contract.json']]},{'id':'E121','title':'Packed immutable terminal hand word','kind':'candidate','status':'staged','accepted':False,'stage':'Fixed source staged; compiler/host-domain prerequisite next','reason':'OneRust/CUDA form; terminalkernels use one packedmetadataword instead of3loads. Extra integerdecode/wordlifetime/hosttemporary/JIT costs remain unqualified.','evidence':[{'label':'Fixed source and exact inverse','url':'evidence/'+S.name+'/manifest.json'}]}];s.update(updated_at=h.now(),active_experiment='E121',stage='Terminal hand words: host encoding and compiled resources',activity='E120 stays closed. E121 is a distinct private per-hand encoding; E080 remains live, no new gain adopted.');h.ar.atomic_json(h.ar.STATUS,s)
h.custody();print(json.dumps({'CUDA_sha256':h.sha(S/'candidate.cu'),'Rust_sha256':h.sha(S/'candidate-mod.rs'),'unique_CUDA':len(seen),'legal_tuples':1326*1327}),flush=True)
