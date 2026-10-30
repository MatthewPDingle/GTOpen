"""Prepare one distinct warp-per-node action mapping outside the checkout."""
from pathlib import Path
from collections import Counter,defaultdict
import ast,difflib,json,shutil,struct,subprocess,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E080-live-20261018';sys.path.insert(0,str(C));import common_e080_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3 and shutil.disk_usage('T:\\').free>=53687091200
D=R/'runs/D132-warp-action-mapping';S=R/'runs/E081-source';H=R/'runs/E081-resource';assert not D.exists()and not S.exists()and H.exists()and not(H/'protocol.json').exists();D.mkdir();S.mkdir()
history=[]
for command in[['git','log','--all','--oneline','-G','warp.*node|node.*warp|blockIdx.x.*warp|threadIdx.x.*>> 5','--','crates/solver/src/gpu/kernels.cu','crates/solver/src/gpu/mod.rs'],['rg','-n','-i','warp.{0,40}node|node.{0,40}warp|warp.{0,20}pack|pack.{0,20}warp','research/postflop-gpu-20261016/experiments.md']]:
    x=subprocess.run(command,cwd=old.REPO,text=True,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW);assert x.returncode in[0,1];history.append({'command':command,'returncode':x.returncode,'stdout':x.stdout,'stderr':x.stderr})
old.save(D/'history.json',{'at':old.now(),'bounded_local_history':history,'no_matching_history_lines':all(not x['stdout'].strip()for x in history),'limits':'Bounded current ledger and local all-ref GPU source history only; no exhaustive remote novelty claim. Different from closed fixed64/256thread action blocks, arity partition/specialization, early-store, register/load/helper and fold-fusion candidates.'})
cuda_rel='crates/solver/src/gpu/kernels.cu';mod_rel='crates/solver/src/gpu/mod.rs';base=(old.REPO/cuda_rel).read_bytes();text=base.decode();nl='\r\n'if b'\r\n'in base else'\n';a=text.index('template<int NA>'+nl+'__device__ __forceinline__ void up_action_impl(');b=text.index('extern "C" __global__ void up_action(',a);c=text.index('// Copy the first n floats',b);helper=text[a:b];wrapper=text[b:c]
node='int b = blockIdx.x * ((blockDim.x + 31u) >> 5) + (threadIdx.x >> 5);'
oldnode='int b = blockIdx.x;';assert helper.count(oldnode)==1
coords='    const int lane = threadIdx.x & 31u;'+nl+'    const int width = min(32u, blockDim.x - (threadIdx.x & ~31u));'+nl
newhelper=helper.replace(oldnode,node,1);needle='    if (b >= count) return;'+nl;assert newhelper.count(needle)==1;newhelper=newhelper.replace(needle,needle+coords,1)
oldloop='for (int i = threadIdx.x; i < nh_p; i += blockDim.x)';newloop='for (int i = lane; i < nh_p; i += width)';assert newhelper.count(oldloop)==3;newhelper=newhelper.replace(oldloop,newloop)
oldhead='    if (blockIdx.x >= (u32)count) return;'+nl+'    const int na = node_na[nodes[start + blockIdx.x]];';newhead='    '+node+nl+'    if (b >= count) return;'+nl+'    const int na = node_na[nodes[start + b]];';assert wrapper.count(oldhead)==1;newwrapper=wrapper.replace(oldhead,newhead,1)
candidate=text[:a]+newhelper+newwrapper+text[c:];reverse=candidate[:a]+newhelper.replace(coords,'',1).replace(node,oldnode,1).replace(newloop,oldloop)+newwrapper.replace(newhead,oldhead,1)+candidate[candidate.index('// Copy the first n floats',a):];assert reverse==text
assert '__syncthreads'not in helper and '__syncwarp'not in helper and 'atomic'not in helper;assert newhelper.replace(coords,'',1).replace(node,oldnode,1).replace(newloop,oldloop)==helper
mb=(old.REPO/mod_rel).read_bytes();mt=mb.decode();mn='\r\n'if b'\r\n'in mb else'\n';hook='    pub fn iterate(&mut self) -> Result<(), String> {';assert mt.count(hook)==1
addition=('    // Four independent action nodes per 128-thread block, one per warp.'+mn+'    fn action_cfg(nodes: u32) -> LaunchConfig {'+mn+'        Self::cfg(nodes.div_ceil(4), 0)'+mn+'    }'+mn+mn)
mc=mt.replace(hook,addition+hook,1);launch=mc.index('.launch_builder(&self.f_up_action)');end=mc.index('                prof_acc',launch);part=mc[launch:end];needle='.launch(Self::cfg(sp.count, 0))';assert part.count(needle)==1;mc=mc[:launch]+part.replace(needle,'.launch(Self::action_cfg(sp.count))',1)+mc[end:]
unit='''
    #[test]
    fn packed_action_launch_covers_every_node_and_tail() {
        for n in [0u32, 1, 2, 3, 4, 5, 7, 8, 9, 127, 128, 129, 1_346_813, u32::MAX] {
            let cfg = GpuSolver::action_cfg(n);
            assert_eq!(cfg.block_dim, (128, 1, 1));
            assert_eq!(cfg.shared_mem_bytes, 0);
            assert_eq!(cfg.grid_dim.1, 1);
            assert_eq!(cfg.grid_dim.2, 1);
            assert!(u64::from(cfg.grid_dim.0) * 4 >= u64::from(n));
            assert!(cfg.grid_dim.0 == 0 || u64::from(cfg.grid_dim.0 - 1) * 4 < u64::from(n));
        }
    }
'''.replace('\n',mn)
pos=mc.rfind(mn+'}');assert pos>0;mc=mc[:pos]+unit+mc[pos:];mr=mc.replace(unit,'',1).replace(addition,'',1).replace('.launch(Self::action_cfg(sp.count))',needle,1);assert mr==mt
owned={cuda_rel:{'base':str(S/'baseline.cu'),'candidate':str(S/'candidate.cu')},mod_rel:{'base':str(S/'baseline-mod.rs'),'candidate':str(S/'candidate-mod.rs')}}
for n,data in [('baseline.cu',base),('candidate.cu',candidate.encode()),('baseline-mod.rs',mb),('candidate-mod.rs',mc.encode())]:assert not(S/n).exists();(S/n).write_bytes(data)
for n,oldtext,newtext in [('kernels.cu.patch',text,candidate),('mod.rs.patch',mt,mc)]:
    (S/n).write_text(''.join(difflib.unified_diff(oldtext.splitlines(True),newtext.splitlines(True),fromfile='accepted/'+n,tofile='E081/'+n)),encoding='utf-8',newline='')
scope='Only training up_action assigns one independent action node to each physical warp; four nodes share the unchanged128thread CTA. Each lane processes its own hand indices with width32 (or last-partial-warp width for direct unusual launch controls). Every original per-hand ascending-action floating expression and mutable write is retained exactly. One host training launch uses ceil(nodecount/4) blocks. Node lists/order, buffers, CFV layout, all other kernels/evaluation launches, ABI, shared memory, math, quality, precision, saves and E080 setup remain unchanged. No warp collectives, implicit inter-thread synchronization or shared scratch.'
review={'at':old.now(),'scope':scope,'complete_source_reverse_exact':True,'floating_body_reverse_exact':True,'up_action_hand_loops_changed':3,'helper_has_no_collectives_or_atomics':True,'only_host_training_launch_changed':True,'new_host_unit_unexecuted':True,'candidate_ordinary_units_if_built':87,'risk':'Warp-level arity divergence, longer per-lane loops, register pressure, loss of locality or instruction overhead may erase any structural utilization benefit. No dynamic occupancy, bandwidth, speed or no-material-cost claim. Current parity-separated CFV schedule must retain cross-node independence; direct mixed-node controls and actual plan metadata audit remain before integration.','references':[{'title':'NVIDIA CUDA advanced kernel programming, thread/block/warp execution and synchronization','url':'https://docs.nvidia.com/cuda/cuda-programming-guide/03-advanced/advanced-kernel-programming.html'}],'frozen_production_thread_count':128,'nodes_per_default_CTA':4,'no_block_width_or_scope_variants':True};old.save(S/'source-review.json',review)
old.save(S/'manifest.json',{'id':'E081','at':old.now(),'owned':owned,'candidate_owned_sha256':{n:old.sha(v['candidate'])for n,v in owned.items()},'scope':scope,'source_activated':False,'candidate_accepted':False,'previous_accepted':'E080'})
# Decode the retained observation only; no new kernel or timing sample.
G=R/'runs/E080-graph-controls';gq=old.read(G/'report.json');trace=G/'execution/candidate/trace.bin';meta=G/'execution/candidate/collector.jsonl';old.pin(trace,gq['raw_sha256'][str(trace)]);old.pin(meta,gq['raw_sha256'][str(meta)]);rows=list(struct.Struct('<6I4Q10I80s').iter_unpack(trace.read_bytes()[16:]));marks=[json.loads(x)for x in meta.read_text().splitlines()];stamps={x['marker']:x['timestamp_ns']for x in marks if x['event']=='phase'};lo,hi=stamps[3],stamps[4];families=defaultdict(lambda:{'count':0,'summed_kernel_ms':0.0})
for row in rows:
    if row[0]in[3,10]and row[6]>=lo and row[7]<=hi:
        name=row[20].split(b'\0')[0].decode();families[name]['count']+=1;families[name]['summed_kernel_ms']+=(row[7]-row[6])/1e6
old.save(D/'retained-trace-scout.json',{'at':old.now(),'trace_sha256':old.sha(trace),'metadata_sha256':old.sha(meta),'source':'Exact E080 graph-control candidate, subsequently accepted. This observation was already inspected during exploratory source selection; not a newly frozen timing sample.','solve_phase_span_ms':(hi-lo)/1e6,'families':dict(sorted(families.items(),key=lambda x:x[1]['summed_kernel_ms'],reverse=True)),'largest_family':'up_action','new_native_processes':0,'limits':'Summed traced family intervals can overlap and have observer effects; these are neither uninstrumented wall attribution nor removable headroom or speed forecasts. Used only to focus a distinct hypothesis.'})
probe=(R/'runs/E074-resource/probe.rs').read_text().replace('E074_RESOURCE','E081_RESOURCE').replace(' let actual:', ' let actual:')
needle=' let shared_limit=';assert probe.count(needle)==1;probe=probe.replace(needle,' let output=std::path::PathBuf::from(std::env::args().nth(1).expect("fresh output directory"));\n'+needle,1);needle='open(format!("{variant}-{arch}.ptx"))';assert probe.count(needle)==1;probe=probe.replace(needle,'open(output.join(format!("{variant}-{arch}.ptx")))',1);(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
for name in['baseline.cu','candidate.cu']:shutil.copyfile(S/name,H/name)
M=old.read(R/'binaries/E080-postflop_autoresearch.manifest.json');deps=M['dependency_artifact_sha256'];libs={}
for name in['cudarc','serde_json']:
    paths=[p for p in deps if Path(p).suffix=='.rlib'and Path(p).name.startswith('lib'+name+'-')];assert len(paths)==1;libs[name]=paths[0]
for p,h in deps.items():old.pin(p,h)
cmd=['rustc',str(H/'probe.rs'),'--edition=2021','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-L','dependency='+str(Path(libs['cudarc']).parent)]
for name,path in libs.items():cmd+=['--extern',name+'='+path]
cmd+=['-o',str(H/'probe.exe')]
for p in H.glob('*.py'):ast.parse(p.read_text())
paths=[Path(__file__),*[p for directory in[S,D,H]for p in directory.iterdir()if p.is_file()],C/'common_e080_live.py',C/'protected-main.json',R/'binaries/E080-postflop_autoresearch.manifest.json',old.REPO/'tools/postflop_resource_feasibility.py',old.REPO/'tools/postflop_resource_admission.py',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md']
P={'id':'E081-resource','at':old.now(),'status':'FROZEN_PRE_COMPILER_AND_RESOURCE_PROBE','rustc_command':cmd,'input_sha256':deps|{str(p):old.sha(p)for p in paths},'gpu_uuid':'GPU-a5459b5a-632b-3e73-d7f1-a06e167102ee','expected_entries':['copy_root','down_action','down_chance','up_fold','up_show','up_chance','up_action','copy_span','up_action_eval'],'resource_gates':'Exact other8PTXentries modulo only compiler-local ordinal labels and exact20parameter globalABI on actualcompute120 plus compile-only75. Changed up_action body must emit lane/warp mapping. No local/dynamic/static shared increase, no lower maxthreads, all fixed64/128/256 occupancy positive, original default128occupancy not decreased, no stacklimit increase. Source floating body reversal exact; no static FP-opcode-count equality proxy.','scope':'One compiler, one resource-only process, four NVRTC compiles. No application kernel, solver, source activation, performance or accuracy result. Whole CPU/host/GPU memory/capacity/graph/application costs and full numerical/speed qualification remain mandatory.','failure_policy':'Close this exact mapping, node packing, host-grid and thread-stride form on a real failure. No node-per-warp/CTA, width, threshold, arity, helper, source/host scope, launch or placement variants/sweeps/retries/resampling rescue. Only observer bookkeeping repairs may replay retained evidence without new compiler/native observations.','candidate_accepted':False};old.save(H/'protocol.json',P)
pub=[]
for folder in[D,S,H]:
    for p in folder.iterdir():
        if not p.is_file():continue
        key=folder.name+'/'+p.name;dest=old.ar.DASHBOARD/'evidence'/key;dest.parent.mkdir(exist_ok=True,parents=True);assert not dest.exists();shutil.copyfile(p,dest)
        with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
        pub.append(key)
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    st=old.read(old.ar.STATUS);assert not any(x['id']in['D132','E081']for x in st['experiments']);st['experiments'].extend([{'id':'D132','at':old.now(),'title':'Action-node warp mapping source scout','status':'measured','correctness':'source_only','accepted':False,'reason':'Retained E080 activity identifies action updates as the largest summed kernel family. Source/history review supports a distinct warp-per-node mapping trial; this is not a speed forecast.','evidence':[{'label':'Retained trace scope and family counts','url':'evidence/'+D.name+'/retained-trace-scout.json'},{'label':'Bounded prior-history search','url':'evidence/'+D.name+'/history.json'}]},{'id':'E081','at':old.now(),'title':'Pack independent action nodes into warps','status':'running','stage':'Compiled resource prerequisite','correctness':'pending','accepted':False,'reason':'Keep 128 threads per block and the original floating arithmetic. Give each warp a separate node and launch four nodes per block. Compile and inspect resources before any application kernel or solver test.','evidence':[{'label':'Exact two-file source and synchronization review','url':'evidence/E081-source/source-review.json'},{'label':'Frozen compiler and resource gates','url':'evidence/E081-resource/protocol.json'}]}]);st.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E081',stage='E081 compiled resource prerequisite',activity='Testing a distinct action-node mapping: one independent node per warp in the unchanged 128-thread block. Exact floating arithmetic and all other kernels stay intact. No speed result yet; accepted E080 remains deployed at 14.74% cumulative gain.');old.ar.atomic_json(old.ar.STATUS,st)
old.save(D/'publication.json',{'at':old.now(),'HTTP_verified_artifacts':pub,'resource_protocol_sha256':old.sha(H/'protocol.json'),'new_native_processes':0,'source_activated':False});old.custody();print(old.sha(H/'protocol.json'),flush=True)
