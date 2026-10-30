"""Seal one off-tree strategy-only store-cache experiment before compilation."""
import ast
import difflib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
C=R/'runs/accepted-E080-live-20261018'
sys.path.insert(0,str(C))
import common_e080_live as old
old.custody()
assert not(R/'gpu-run.lock').exists()
old.ar.refuse_active(old.ar.live_status())
assert shutil.disk_usage(R).free>=66*1024**3 and shutil.disk_usage('T:\\').free>=53687091200
D,S,H=[R/('runs/'+n)for n in ['D136-strategy-streaming-store','E085-source','E085-resource']]
assert not any(p.exists()for p in [D,S,H])
for p in [D,S,H]:p.mkdir()
history=[]
for cmd in [
    ['git','log','--all','--oneline','-G','st.global.cs|__stcs|strategy.*streaming','--','crates/solver/src/gpu/kernels.cu'],
    ['rg','-n','-i','st\\.global\\.cs|__stcs|streaming.store|store.*cache|cache.*store|strategy.*cache','research/postflop-gpu-20261016/experiments.md'],
    ['rg','-l','st\\.global\\.cs|__stcs',str(R/'runs'),'-g','*.cu'],
]:
    p=subprocess.run(cmd,cwd=old.REPO,text=True,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
    assert p.returncode in [0,1]
    history.append({'command':cmd,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
old.save(D/'history.json',{'at':old.now(),'bounded_local_search':history,
    'distinct_scope':'Only strategy output cache policy. Original E051 assignment location/value and CFV store location remain unchanged. E033/E034 context persisting metadata cache, E054 early parent-CFV publication, E075 immutable uniform loads and E084 first-card sum reuse remain closed, with none of their hunks composed.',
    'declined_leads':'River-list linear construction already implemented; historical D044 isolated river-rank work summed6.9594ms, so union ranking deduplication not implemented or retimed.',
    'limits':'Bounded matching and source-history inspection only; no exhaustive remote/semantic novelty or measured cache-miss attribution.'})
rel='crates/solver/src/gpu/kernels.cu'
raw=(old.REPO/rel).read_bytes();base=raw.decode();nl='\r\n'if b'\r\n'in raw else'\n'
before='                strat_p[idx] = strat_p[idx] * ds + reach * sig;'
after='''                float updated_strategy = strat_p[idx] * ds + reach * sig;
                // Strategy is streamed across the arena; prefer evicting these
                // output lines before metadata with normal cache priority.
                asm volatile ("st.global.cs.f32 [%0], %1;"
                    :: "l"(strat_p + idx), "f"(updated_strategy) : "memory");'''.replace('\n',nl)
assert base.count(before)==1
candidate=base.replace(before,after,1)
assert candidate.replace(after,before,1)==base
start=base.index('template<int NA>\r\n__device__ __forceinline__ void up_action_impl('if nl=='\r\n'else'template<int NA>\n__device__ __forceinline__ void up_action_impl(')
end=base.index('extern "C" __global__ void up_action(',start)
assert candidate[:start]==base[:start]
assert candidate[candidate.index('extern "C" __global__ void up_action(',start):]==base[end:]
for name,data in [('baseline.cu',raw),('candidate.cu',candidate.encode())]:
    (S/name).write_bytes(data);shutil.copyfile(S/name,H/name)
(S/'kernels.cu.patch').write_text(''.join(difflib.unified_diff(base.splitlines(True),candidate.splitlines(True),fromfile='accepted/kernels.cu',tofile='E085/kernels.cu')),encoding='utf-8',newline='')
scope='Only unlocked own-node up_action strategy store uses st.global.cs.f32. Identical original expression computes its value at the same location; all regret/CFV stores, arithmetic/reduction order, locks/opponent paths, host/ABI/allocations/launch/graph/quality/save remain unchanged.'
old.save(S/'source-review.json',{'at':old.now(),'scope':scope,'source_reverse_exact':True,
    'value_and_ownership':'Original binary32 strategy expression and pointer offset preserved. Actual strategy buffers are separate CUDA global allocations, with disjoint owned node/action/hand words. No new memory operation or synchronization and no read of an uninitialized value. Inline value operand f and64bit pointer operand l; volatile and memory clobber expose hidden global write to the compiler.',
    'reuse_hypothesis':'Strategies stream over the large action arenas on each iteration and are consumed by evaluation, next update and final readback. An evict-first hint may preserve metadata/reach/CFV lines with shorter reuse distances. Actual cache misses and benefits are unmeasured; the next iteration still needs every strategy value, so streaming can hurt.',
    'risks':'Assembly memory clobber can alter compiler scheduling/register pressure; eviction may increase later reads. PTX hints can be ignored. No causal hint-only, no-tradeoff or speed claim. Actual resources, complete raw direct images and whole-solve checks required.',
    'primary_sources':[
        {'url':'https://docs.nvidia.com/cuda/parallel-thread-execution/index.html#cache-operators','paraphrase':'Cache operators are performance hints; consistency is unchanged. Streaming stores use evict-first to limit pollution.'},
        {'url':'https://docs.nvidia.com/cuda/archive/12.4.0/inline-ptx-assembly/index.html','paraphrase':'Use correctly typed operands, volatile and memory clobbers for hidden indirect memory side effects.'}],
    'candidate_not_a_variant_rescue':'No early CFV publication, LDU load, context cache reservation, terminal cache, first-card sum or failed-node mapping change is included.'})
old.save(S/'manifest.json',{'id':'E085','at':old.now(),'owned':{rel:{'base':str(S/'baseline.cu'),'candidate':str(S/'candidate.cu')}},'candidate_owned_sha256':{rel:old.sha(S/'candidate.cu')},'scope':scope,'source_activated':False,'candidate_accepted':False,'previous_accepted':'E080'})

prior=R/'runs/E081-resource'
probe=(prior/'probe.rs').read_text().replace('E081','E085')
(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
code=(prior/'execute.py').read_text().replace('E081','E085')
code=code.replace('pass_compiled_warp_mapping_prerequisites','pass_compiled_strategy_streaming_prerequisites')
code=code.replace('lane/node correctness','strategy-value/store-ownership correctness')
# Require actual cache-store emission in each common specialization and generic
# implementation at both targets, without treating opcode counts as math proof.
needle="passed=all(gates.values());report="
assert code.count(needle)==1
insert="""for arch in ['compute_120','compute_75']:
    bt=tables['baseline',arch]['up_action'];ct=tables['candidate',arch]['up_action']
    gates[arch+':streaming_stores_emitted_all4paths']=bt.count('st.global.cs.f32')==0 and ct.count('st.global.cs.f32')==4
passed=all(gates.values());report="""
code=code.replace(needle,insert,1);ast.parse(code)
(H/'execute.py').write_text(code,encoding='utf-8',newline='\n')
P0=old.read(prior/'protocol.json')
deps={p:h for p,h in P0['input_sha256'].items()if Path(p).suffix in ['.rlib','.rmeta','.lib','.dll']}
paths=[Path(__file__),C/'common_e080_live.py',C/'protected-main.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',*[p for folder in [D,S,H]for p in folder.iterdir()if p.is_file()]]
P={'id':'E085-resource','at':old.now(),'status':'FROZEN_PRE_COMPILER_AND_RESOURCE_PROBE',
    'rustc_command':[x.replace('E081-resource','E085-resource')for x in P0['rustc_command']],
    'input_sha256':deps|{str(p):old.sha(p)for p in paths},'gpu_uuid':P0['gpu_uuid'],
    'expected_entries':P0['expected_entries'],'target_kernel':'up_action','expected_parameters':20,
    'resource_gates':'Other8normalized PTXentries and20parameter ABI exact at120/75; all4strategy streaming stores emitted. Actual120 local/static/dynamic shared not increased; no lower maxthreads; fixed64/128/256 legal and positive; default128 residency not reduced; no stack increase.',
    'scope':'OneRustcompiler,one resource-only process,fourNVRTCcompiles; no application kernels,solves,performance score or production source activation.',
    'failure_policy':'Close this exact strategy streaming-store form on actual resource,numerical,performance or material failure. No cache operators, other output/input arrays, thresholds, helper/clobber/source-scope/placement variants or extra samples to rescue. Reader-only repairs may replay retained observations.',
    'candidate_accepted':False}
old.save(H/'protocol.json',P)
pub=[]
for folder in [D,S,H]:
    for p in folder.iterdir():
        if not p.is_file():continue
        key=folder.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
        assert not dst.exists();shutil.copyfile(p,dst)
        with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as response:assert response.read()==p.read_bytes()
        pub.append(key)
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=old.read(old.ar.STATUS)
    assert not any(x['id']in ['D136','E085']for x in s['experiments'])
    s['experiments'].extend([
        {'id':'D136','at':old.now(),'title':'Strategy output cache-priority source audit','status':'measured','correctness':'source_only','accepted':False,'reason':'A distinct strategy-output evict-first hypothesis; original values and locations preserved. Actual resource/accuracy/speed proof remains. Historical small river-ranking lead declined.','evidence':[{'label':'Bounded local history','url':'evidence/D136-strategy-streaming-store/history.json'}]},
        {'id':'E085','at':old.now(),'title':'Stream cumulative-strategy output stores','status':'running','stage':'Compiled resource prerequisite','correctness':'pending','accepted':False,'reason':'Identical strategy expression and output location with a streaming cache hint. Cache retention or compiler scheduling may hurt. No speed result.','evidence':[{'label':'Value, ownership and compiler review','url':'evidence/E085-source/source-review.json'},{'label':'Frozen compiler/resource gates','url':'evidence/E085-resource/protocol.json'}]}])
    s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E085',stage='E085 compiled resource prerequisite',activity='Testing a strategy-output cache hint with original arithmetic and addresses. Actual compiled resources precede numerical and full-solve tests. Accepted/live E080 remains14.74% faster on registered benchmarks.')
    old.ar.atomic_json(old.ar.STATUS,s)
old.save(D/'publication.json',{'at':old.now(),'HTTP_verified_artifacts':pub,'resource_protocol_sha256':old.sha(H/'protocol.json'),'new_native_processes':0})
old.custody()
print(old.sha(H/'protocol.json'),flush=True)
