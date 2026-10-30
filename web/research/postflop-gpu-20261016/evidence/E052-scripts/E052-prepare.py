"""Freeze one 16-bit shared showdown position-cache hypothesis on accepted E051."""
import difflib,json,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(ROOT).free>=54*1024**3
S=ROOT/'runs/E052-source';H=ROOT/'runs/E052-resource';S.mkdir();H.mkdir()
cu=old.REPO/'crates/solver/src/gpu/kernels.cu';mod=old.REPO/'crates/solver/src/gpu/mod.rs';a=cu.read_bytes();b=mod.read_bytes()
before=b'u32* card_pos_sh = (u32*)(prefix + m_o); // 2*m_o immutable position indices'
after=b'unsigned short* card_pos_sh = (unsigned short*)(prefix + m_o); // 2*m_o positions, each <1326'
assert a.count(before)==1 and b.count(b'* 16 + nh_o as usize * 4')==2
c=a.replace(before,after);d=b.replace(b'* 16 + nh_o as usize * 4',b'* 12 + nh_o as usize * 4')
for name,data in [('baseline.cu',a),('candidate.cu',c),('baseline-mod.rs',b),('candidate-mod.rs',d)]:
 (S/name).write_bytes(data)
for name,data in [('baseline.cu',a),('candidate.cu',c)]: (H/name).write_bytes(data)
patch=''.join(difflib.unified_diff(a.decode().splitlines(True),c.decode().splitlines(True),fromfile='a/crates/solver/src/gpu/kernels.cu',tofile='b/crates/solver/src/gpu/kernels.cu'))+''.join(difflib.unified_diff(b.decode().splitlines(True),d.decode().splitlines(True),fromfile='a/crates/solver/src/gpu/mod.rs',tofile='b/crates/solver/src/gpu/mod.rs'))
(S/'candidate.patch').write_text(patch,encoding='utf-8',newline='\n')
review={'id':'D083-showdown-local-position-width','at':old.now(),'root_source_review_only':True,'proposal':'Only the per-CTA immutable position cache uses16bit unsigned elements; global u32metadata/ABI stay unchanged. Both existing host up_show shared reservations change16*m+4*nh to12*m+4*nh.','bound_proof':['cards::NUM_COMBOS is1326. Spot::new_impl enumerates exactly0..NUM_COMBOS, so hands contain at most1326unique combos.','RiverTable::new filters/enumerates existing hands; sorted slot has m<=nh<=1326. GpuPlan::build emits each enumerated pos asu32 into its two distinct card lists;0<=pos<m. Thus every copied position is0..1325, exactly representable in unsignedshort.','Cache starts at4*(nh_o+2*m_o), aligned for16bit access; length2*m_o consumes4*m_o bytes. Float regions end before it, unchanged. New bound4*nh_o+12*m_o covers all actual slots because host uses per-player maximum m. Empty list performs no cache access.','Every float value, operation order, predicate, sorted/card traversal, barrier, zeroing store, scan and payout expression remains byte-identical. Only implicit narrowing store and promoted unsigned16load differ.'],'risk':['Smaller cache can change shared bank access pattern and add integer conversions; no speed inference follows.','Logical register/local/static shared pressure must not increase, occupancy/maxthreads must not fall for all fixed shapes and64/128/256threads.','Source bounds do not prove actual GPU exactness. If resources pass, freeze direct full-raw comparisons including empty/full/tail/nonzero-base/guard/nonfinite cases before solver timing.'],'novelty':'Scoped current ledger and D037/D058 reference search found no local shared position-width candidate. This is independent of rejected E050 async staging: no async, copy-subset/zero-placement variant, factor sweep or fallback transformation. No revival of53offset cache or changed scan/arithmetic.','references':[{'title':'NVIDIA CUDA Best Practices Guide shared memory','url':'https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html?highlight=bank','use':'32-bit bank organization means smaller width alone does not establish faster access.'},{'title':'NVIDIA CUTLASS memory primitives','url':'https://github.com/NVIDIA/cutlass/blob/main/include/cutlass/arch/memory.h','use':'Official implementation includes shared16bit loads/stores; actual target PTX still inspected.'}],'resource_gate':'One unchanged candidate only. Actual up_show PTX body changes; same27parameter ABI; other8entries exact oncompute120and75; expected shared16bit load/store emitted. No increased regs/local/staticshared; exact prescribed dynamic reduction; no maxthread/occupancy loss. If any gate fails, close without native numerical/solve work; no width variant rescue.','performance_gate':'Current1%policy: complete-cycle initial3pairs then separately frozen16confirmation, strict fixture guards, exact full states/checkpoints, broad/F32/save/resume/continuation/capacity/holdout and fresh-original cumulative before adoption. No narrowing of evaluator or accuracy.','owned_candidate_sha256':{'crates/solver/src/gpu/kernels.cu':old.sha(S/'candidate.cu'),'crates/solver/src/gpu/mod.rs':old.sha(S/'candidate-mod.rs')},'candidate_accepted':False}
old.save(S/'source-review.json',review)
old.save(S/'manifest.json',{'at':old.now(),'baseline':'E051','baseline_source_sha256':old.BASE,'artifact_sha256':{p.name:old.sha(p) for p in S.iterdir()},'candidate_owned_sha256':review['owned_candidate_sha256'],'no_production_activation':True})
parent=ROOT/'runs/E050-resource';probe=(parent/'probe.rs').read_text().replace('E050_RESOURCE','E052_RESOURCE').replace('let dynamic=4*nh_o+16*m;','let dynamic=4*nh_o+if variant=="candidate" {12*m} else {16*m};')
(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
runner=(parent/'execute.py').read_text().replace('E050','E052').replace("sys.path.insert(0,str(HERE.parent/'small-gain-confirmation-plan'));import common as old","sys.path.insert(0,str(HERE.parent/'accepted-E051'));import common_e051 as old")
start=runner.index(" gates={'other8_entries_exact'");end=runner.index('\n details={};abi={}',start)
runner=runner[:start]+" gates={'other8_entries_exact':set(unchanged)==set(be)-{'up_show'},'other8_sm75_entries_exact':all(bf[k]==cf[k] for k in bf if k!='up_show'),'sm75_show_changed':bf['up_show']!=cf['up_show'],'shared16load_emitted':bool(re.search(r'ld\\.shared(?:\\.[a-z]+)*\\.u16',ce['up_show'])),'shared16store_emitted':bool(re.search(r'st\\.shared(?:\\.[a-z]+)*\\.(?:u16|b16)',ce['up_show']))}\n"+runner[end:]
runner=runner.replace("'dynamic_shared_exact':c['dynamic_shared_bytes']==b['dynamic_shared_bytes']","'dynamic_shared_reduced_as_prescribed':c['dynamic_shared_bytes']==b['dynamic_shared_bytes']-4*P['shape_dimensions'][shape][1]")
(H/'execute.py').write_text(runner,encoding='utf-8',newline='\n')
P=old.read(parent/'protocol.json');P.update(id='E052-resource',at=old.now(),source_manifest_sha256=old.sha(S/'manifest.json'),status='FROZEN_PRE_EXECUTION_NO_LAUNCH',fixed_gates=review['resource_gate'])
P['shape_dimensions']={k:[nh,m] for k,nh,m in [('rainbow_p0',319,314),('rainbow_p1',257,252),('two_tone_p0',320,315),('two_tone_p1',258,253),('river_p0',280,280),('river_p1',233,233),('wide_turn',1128,1081),('full_hand_upper_bound',1326,1326),('empty_sorted_opponent',319,0),('single_sorted_opponent',319,1)]}
P['rustc_command']=[x.replace(str(parent),str(H)) for x in P['rustc_command']]
# Use the immutable measured E051 primary dependency family, not mutable old shared build outputs.
deps=old.read(ROOT/'binaries/E051-postflop_autoresearch.manifest.json')['dependency_artifact_sha256']
bindings={n:next(p for p in deps if Path(p).name.startswith('lib'+n+'-') and Path(p).suffix=='.rlib') for n in ['cudarc','serde_json']}
cmd=P['rustc_command'];cmd[cmd.index('-L')+1]='dependency='+str(Path(bindings['cudarc']).parent)
for i,x in enumerate(cmd):
 for n,p in bindings.items():
  if x.startswith(n+'='):cmd[i]=n+'='+p
inputs=[*S.iterdir(),H/'probe.rs',H/'execute.py',H/'baseline.cu',H/'candidate.cu',old.REPO/'crates/solver/src/cards.rs',old.REPO/'crates/solver/src/range.rs',old.REPO/'crates/solver/src/game.rs',old.REPO/'crates/solver/src/gpu/plan.rs',ROOT/'runs/accepted-E051/baseline.json',parent/'execute.py',parent/'probe.rs']
P['input_sha256']={str(p):old.sha(p) for p in inputs if p.is_file()}|deps;old.save(H/'protocol.json',P)
published={}
for directory in [S,H]:
 for p in directory.iterdir():
  key=directory.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(p.read_bytes())
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
  published[key]=old.sha(p)
old.save(H/'pre-execution-publication.json',{'at':old.now(),'artifact_sha256':published,'kernel_launches':0,'candidate_accepted':False})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);assert not any(x['id']=='E052' for x in st['experiments']);links=[{'label':'D083/E052 width proof and source review','url':'evidence/E052-source/source-review.json'},{'label':'E052 fixed no-launch resource protocol','url':'evidence/E052-resource/protocol.json'}]
 st['experiments'].append({'id':'E052','title':'16-bit shared showdown position cache','kind':'candidate','status':'preparing','stage':'Compiled resource gate','reason':'Exact bounded local position representation; same global metadata/ABI and float order. Resource probe precedes numerical/performance work.','evidence':links,'accepted':False});st['evidence']+=links;st.update(updated_at=old.now(),stage='E052 compiled resource gate',activity='One bounded unsigned16shared position cache candidate on acceptedE051; no kernel or solver launch yet.',active_experiment='E052');old.ar.atomic_json(old.ar.STATUS,st)
print(old.sha(H/'protocol.json'),flush=True)
