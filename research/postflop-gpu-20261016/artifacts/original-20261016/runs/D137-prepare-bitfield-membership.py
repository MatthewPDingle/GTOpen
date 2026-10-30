"""Freeze one up_chance bit-field extraction form, without source activation."""
import ast
import difflib
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
C=R/'runs/accepted-E080-live-20261018'
sys.path.insert(0,str(C));import common_e080_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
assert shutil.disk_usage(R).free>=66*1024**3 and shutil.disk_usage('T:\\').free>=53687091200
D,S,H=[R/('runs/'+n)for n in ['D137-bitfield-membership','E086-source','E086-resource']]
assert not any(p.exists()for p in [D,S,H])
for p in [D,S,H]:p.mkdir()
history=[]
for cmd in [
    ['git','log','--all','--oneline','-G','bfe.u64|bit.field.*extract','--','crates/solver/src/gpu/kernels.cu'],
    ['rg','-n','-i','bfe\\.u64|bit.field.extract|bitfield.*membership','research/postflop-gpu-20261016/experiments.md'],
    ['rg','-l','bfe\\.u64',str(R/'runs'),'-g','*.cu'],
]:
    p=subprocess.run(cmd,cwd=old.REPO,text=True,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
    assert p.returncode in [0,1]
    history.append({'command':cmd,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
ptx=R/'runs/E080-graph-controls/execution/resources/baseline.ptx'
t=ptx.read_text();start=t.index('.visible .entry up_chance(');end=t.find('.visible .entry',start+1)
entry=t[start:end if end>=0 else len(t)]
old.save(D/'history.json',{'at':old.now(),'bounded_local_history':history,
    'accepted_current_private_PTX_sha256':old.sha(ptx),
    'accepted_up_chance_bit_ops':[l.strip()for l in entry.splitlines()if any(x in l for x in ['shr.u64','and.b64','bfe.u64'])],
    'declined_source_equivalence_lead':'Original left-onehot/AND is already lowered to right-shift/AND in retained accepted PTX; ordinary source-direction rewrite not implemented.',
    'distinct_form':'Explicit unsigned64bit length1 bit-field extraction in up_chance only. Original hand-mask buffers, card IDs, public and private metadata, ABI and host unchanged. No E048card-ID comparisons/removed masks, E039sharedmetadata, E046packing or E085cache hunk composed.',
    'limits':'Local matched history and retained PTX only. No exhaustive semantic/remote novelty, actual SASS count, timing or removable-overhead claim.'})
checks=0
for c1 in range(52):
    for c2 in range(c1+1,52):
        mask=(1<<c1)|(1<<c2)
        for c in range(52):
            original=bool(mask & (1<<c))
            extracted=(mask>>c)&1
            assert original==bool(extracted)==(c in [c1,c2]);checks+=1
for bit in range(64):
    for card in range(64):
        for mask in [0,1<<bit,((1<<64)-1)^(1<<bit),(1<<64)-1]:
            assert bool(mask&(1<<card))==bool((mask>>card)&1);checks+=1
old.save(D/'integer-control.json',{'at':old.now(),'status':'pass_canonical_and_basis_bit_selection',
    'checks':checks,'canonical_hands':1326,'legal_cards':52,
    'ordered_predicate':'For unsigned64 mask and card0..51, bit-field positioncard length1 yields(mask>>card)&1 and the same branch as mask&(1<<card). Basis/complement tests also cover indices0..63.',
    'kernel_launches':0,'limits':'CPU integer identity and documented instruction semantics; no compiled GPU numerical/performance proof.'})
rel='crates/solver/src/gpu/kernels.cu';raw=(old.REPO/rel).read_bytes();base=raw.decode();nl='\r\n'if b'\r\n'in raw else'\n'
before='''            u64 cm = 1ull << cc_card[t];
            if (hm & cm) continue;'''.replace('\n',nl)
after='''            u64 blocked;
            // Extract the dealt-card bit without materializing a one-hot mask.
            asm ("bfe.u64 %0, %1, %2, 1;"
                : "=l"(blocked) : "l"(hm), "r"(cc_card[t]));
            if (blocked != 0) continue;'''.replace('\n',nl)
assert base.count(before)==1
candidate=base.replace(before,after,1);assert candidate.replace(after,before,1)==base
a=base.index('extern "C" __global__ void up_chance(');b=base.index('// Up sweep, action nodes:',a)
assert base[:a]==candidate[:a] and base[b:]==candidate[candidate.index('// Up sweep, action nodes:',a):]
for n,data in [('baseline.cu',raw),('candidate.cu',candidate.encode())]:
    (S/n).write_bytes(data);shutil.copyfile(S/n,H/n)
(S/'kernels.cu.patch').write_text(''.join(difflib.unified_diff(base.splitlines(True),candidate.splitlines(True),fromfile='accepted/kernels.cu',tofile='E086/kernels.cu')),encoding='utf-8',newline='')
scope='Only up_chance card-blocker predicate uses explicit bfe.u64 at positioncc_card[t],length1. Same mask/card inputs, branch decision for supported cards, original ordered floating accumulations, permutation, payout, buffers, host/ABI/launch/graph, quality and save behavior.'
old.save(S/'source-review.json',{'at':old.now(),'scope':scope,'source_reverse_exact':True,
    'constraints':'Unsigned64 input/output use l operands; bit position is u32 r and fixed length1. Pure register operation has no hidden memory effects and does not need volatile or memory clobber. Existing cc_card load remains an ordinary immutable input.',
    'source_identity':'No floating expression, selected child, loop ordering or guard span changes. Public/private plan encodings and every caller retain exact bytes. Legal card IDs0..51 fit documented8bit position domain.',
    'risks':'bfe.u64 is a virtual instruction and may lower to equivalent or slower native operations. Register pressure and scheduling may worsen. No static instruction-count speed inference, actual occupancy measurement or no-tradeoff claim.',
    'primary_sources':[{'url':'https://docs.nvidia.com/cuda/parallel-thread-execution/index.html#integer-arithmetic-instructions-bfe','paraphrase':'Unsigned32/64bit field extraction zero-extends the selected field; position/length are32bit operands restricted to0..255; supported fromsm20.'}],
    'required_controls':'Actual resource feasibility, full original/candidate chance-kernel raw outputs/immutable inputs/guards, ordinary units and complete-solve qualification.'})
old.save(S/'manifest.json',{'id':'E086','at':old.now(),'owned':{rel:{'base':str(S/'baseline.cu'),'candidate':str(S/'candidate.cu')}},'candidate_owned_sha256':{rel:old.sha(S/'candidate.cu')},'scope':scope,'source_activated':False,'candidate_accepted':False,'previous_accepted':'E080'})
prior=R/'runs/E081-resource'
probe=(prior/'probe.rs').read_text().replace('E081','E086').replace('["up_action"]','["up_chance"]')
(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
code=(prior/'execute.py').read_text().replace('E081','E086').replace("'up_action'","'up_chance'")
code=code.replace("count('.param ')==20","count('.param ')==15").replace('global20parameter_ABI_exact','global15parameter_ABI_exact')
code=code.replace('pass_compiled_warp_mapping_prerequisites','pass_compiled_bitfield_prerequisites').replace('lane/node correctness','bit-extraction/numerical correctness')
needle='passed=all(gates.values());report='
assert code.count(needle)==1
replacement="""for arch in ['compute_120','compute_75']:
    gates[arch+':bitfield_emitted']=tables['baseline',arch]['up_chance'].count('bfe.u64')==0 and tables['candidate',arch]['up_chance'].count('bfe.u64')>=1
passed=all(gates.values());report="""
code=code.replace(needle,replacement,1);ast.parse(code)
(H/'execute.py').write_text(code,encoding='utf-8',newline='\n')
P0=old.read(prior/'protocol.json');deps={p:h for p,h in P0['input_sha256'].items()if Path(p).suffix in ['.rlib','.rmeta','.lib','.dll']}
paths=[Path(__file__),ptx,C/'common_e080_live.py',C/'protected-main.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',*[p for folder in [D,S,H]for p in folder.iterdir()if p.is_file()]]
P={'id':'E086-resource','at':old.now(),'status':'FROZEN_PRE_COMPILER_AND_RESOURCE_PROBE',
    'rustc_command':[x.replace('E081-resource','E086-resource')for x in P0['rustc_command']],
    'input_sha256':deps|{str(p):old.sha(p)for p in paths},'gpu_uuid':P0['gpu_uuid'],
    'expected_entries':P0['expected_entries'],'target_kernel':'up_chance','expected_parameters':15,
    'resource_gates':'Other8normalized entries and15parameter ABI exact120/75; explicit bitfield emitted. Actual120 local/static/dynamic bytes not increased,maxthreads not lower,fixed64/128/256 legal/positive,default128residency not lower,no context stack increase.',
    'scope':'OneRustcompiler/one resource-only process/fourNVRTCcompiles; no application kernels,solves,performance scores or production source activation.',
    'failure_policy':'Close exact unsigned64length1 bit-field up_chance form on actual resource,numerical,performance or material failure. No width,other-kernel,metadata packing,operator/precision/helper/threshold/clobber/source-scope/placement variants or extra samples to rescue. Reader-only bookkeeping may replay retained observations.',
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
    s=old.read(old.ar.STATUS);assert not any(x['id']in ['D137','E086']for x in s['experiments'])
    s['experiments'].extend([
        {'id':'D137','at':old.now(),'title':'Chance bit-field source and integer control','status':'measured','correctness':'source_only','accepted':False,'reason':'CPU canonical/basis predicates match. Ordinary source right-shift rewrite declined because compiler already emits it. Test explicit bit-field instruction separately, without source/math/layout changes elsewhere.','evidence':[{'label':'Integer relation control','url':'evidence/D137-bitfield-membership/integer-control.json'},{'label':'Bounded history and retained compiler evidence','url':'evidence/D137-bitfield-membership/history.json'}]},
        {'id':'E086','at':old.now(),'title':'Extract chance blocker with a bit-field instruction','status':'running','stage':'Compiled resource prerequisite','correctness':'pending','accepted':False,'reason':'Replace only the up_chance integer blocker predicate with length1 unsigned64 bit extraction. Native work and speed unknown.','evidence':[{'label':'Source and instruction semantics','url':'evidence/E086-source/source-review.json'},{'label':'Frozen resource controls','url':'evidence/E086-resource/protocol.json'}]}])
    s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E086',stage='E086 compiled resource prerequisite',activity='Test one explicit chance bit-field instruction before numerical/whole-solve qualification. Same ordered floating arithmetic and original buffers. E080 remains live at14.74% registered gain.')
    old.ar.atomic_json(old.ar.STATUS,s)
old.save(D/'publication.json',{'at':old.now(),'HTTP_verified_artifacts':pub,'resource_protocol_sha256':old.sha(H/'protocol.json'),'new_native_processes':0})
old.custody();print(old.sha(H/'protocol.json'),flush=True)
