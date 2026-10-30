"""Prove newly unconditional chance loads valid before any CUDA candidate run."""
import array,difflib,hashlib,json,re,shutil,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(ROOT).free>=54*1024**3
D=ROOT/'runs/D097-chance-selection';S=ROOT/'runs/E059-source';assert not D.exists() and not S.exists();D.mkdir();S.mkdir()
cu=old.REPO/'crates/solver/src/gpu/kernels.cu';base=cu.read_bytes();a=base.index(b'extern "C" __global__ void up_chance(');z=base.index(b'// Up sweep, action nodes:',a);body=base[a:z]
before=b'            if (hm & cm) continue;';after=b'            u32 keep = (hm & cm) ? 0xffffffffu : 0u;';assert body.count(before)==1;body=body.replace(before,after)
before=b'            acc += cfv[(u64)cfv_slot[cc_child[t]] * nh_max + idx];'
after=(b'            float next = acc + cfv[(u64)cfv_slot[cc_child[t]] * nh_max + idx];\r\n'
       b'            u32 old_bits = __float_as_uint(acc);\r\n'
       b'            u32 next_bits = __float_as_uint(next);\r\n'
       b'            acc = __uint_as_float((old_bits & keep) | (next_bits & ~keep));')
assert body.count(before)==1;body=body.replace(before,after);candidate=base[:a]+body+base[z:]
for name,data in [('baseline.cu',base),('candidate.cu',candidate)]:(S/name).write_bytes(data)
(S/'candidate.patch').write_text(''.join(difflib.unified_diff(base.decode().splitlines(True),candidate.decode().splitlines(True),fromfile='a/crates/solver/src/gpu/kernels.cu',tofile='b/crates/solver/src/gpu/kernels.cu')),encoding='utf-8',newline='')
duplicates=[];files=0
for p in (ROOT/'runs').rglob('*.cu'):
    if any(part in ['vendor','workspaces','E059-source'] for part in p.parts):continue
    files+=1
    if old.sha(p)==old.sha(S/'candidate.cu'):duplicates.append(str(p))
assert not duplicates
metadata=old.read(ROOT/'runs/D092-action-arity-order/report.json');schema=old.read(ROOT/'runs/D092-action-arity-order/field-schema.json')['fields']
protocol={'id':'D097-chance-selection','at':old.now(),'status':'FROZEN_PRE_CPU_ADDRESS_REPLAY','candidate':'E059','candidate_sha256':old.sha(S/'candidate.cu'),'source_delta':'Retain original64bit hm&cm predicate. Remove continue, compute original child-add unconditionally, select ORIGINAL acc bits when blocked using all-ones u32mask; otherwise select the new sum bits. This is not add-zero, a reciprocal, precision change or a summation reorder. Final acc*inv unchanged.','semantics':'For every blocked card keep all32old accumulator bits, including signedzero/NaN payload; unblocked adds the identical original operands in the original t order. Extra ignored arithmetic has no supported observable CUDA floating-exception status. New reads must be valid/initialized/race-free even where the old branch skipped them. Invalid/trapping custom raw pointers are outside the supported GpuPlan contract.','source_address_proof':['Spot hand_perm tables are admitted only when EVERY root hand maps into the same range; missing entries discard the entire suit permutation. Every retained k table is total and in bounds for both players. Identity is table0.','GpuPlan records only valid chance cards, maps each to a valid orbit representative child and its retained permutation k. All representative children are reached at parent depth+1.','CFVslot assignment gives unique scratch rows for all current-level nonterminals and separate adjacent parity scratch; terminal slots are persistent outside scratch. Thus every extra child read is disjoint from all current-level writes.','GpuSolver d_cfv is allocated with alloc_zeros over cfv_blocks*nh_max. Reverse-level traversal and stream ordering initialize/produce child rows before parent loads. Extra reads use indices<nh_p<=nh_max and cannot enter prefix/suffix memory. Cached evaluation/continuation does not change these owned buffer bounds.'],'concrete_replay':'All12retained CPU metadata cases:3canonical configurations xiso off/on xcompact/full arenas. Stream every required complete metadata field from raw images, verify all hand permutation entries, all reached node levels, all active nonterminal row ownership and all chance card/k/child addresses regardless of blockers. No CUDA execution or timing in this control.','history_scope':'No matching acc bit-selection found by scoped retained postflop CU/patch/review search; exact byte hash is new among checked files. Different from closed E039/E046 shared/packed metadata and E048 membership predicates. No metadata, predicate, factor or width variant of those candidates is composed.','checked_cuda_files':files,'hash_duplicates':duplicates,'reference':{'url':'https://docs.nvidia.com/cuda/cuda-math-api/cuda_math_api/group__CUDA__MATH__INTRINSIC__CAST.html','use':'NVIDIA documents __float_as_uint and __uint_as_float as bit reinterpretations, not numerical conversions.'},'next_gates':'Actual compiler/resource inspection with D094 allocation proof; require blocker-dependent branch removal rather than a source-only claim. Then complete raw GPU outputs/input/guards with signedzero/nonfinite/extreme/permutation/empty/tail cases. Then unchanged complete3fixture1%guard/fresh16/broad/F32/state/save/resume/continuation/material/holdout/cumulative gates. No mask-expression/control/placement/factor variants or extra timing to rescue a failed candidate.','raw_input_sha256':{c['raw_file']:c['raw_sha256'] for c in metadata['cases']},'source_sha256':{str(old.REPO/n):old.sha(old.REPO/n) for n in ['crates/solver/src/game.rs','crates/solver/src/gpu/plan.rs','crates/solver/src/gpu/mod.rs','crates/solver/src/gpu/kernels.cu']},'reviewer':'Root source/ownership replay, not an external independent review','source_activated':False,'kernel_launches':0,'performance_measured':False}
old.save(D/'protocol.json',protocol)
def readvec(f,keep):
    n,=struct.unpack('<Q',f.read(8));assert n<100000000
    if not keep:f.seek(n*8,1);return None
    v=array.array('Q');v.fromfile(f,n)
    if sys.byteorder!='little':v.byteswap()
    return v
def scalar(v):assert len(v)==1;return v[0]
def vector(v):assert v[0]==len(v)-1;return v[1:]
def pair(v):
    assert v[0]==2;n=v[1];x=v[2:2+n];k=2+n;m=v[k];y=v[k+1:];assert len(y)==m;return [x,y]
results=[]
for case in metadata['cases']:
    p=Path(case['raw_file']);old.pin(p,case['raw_sha256']);wanted={'num_nodes','num_levels','nh','nh_max','cfv_blocks','cfv_slot','cc_start','cc_count','cc_card','cc_child','cc_perm','hand_perm_flat',*(s for family in ['action','chance_node','fold','show'] for s in [family+'_spans']), 'action_nodes','chance_nodes','fold_nodes','show_nodes'};maps={};checks=0
    with p.open('rb') as f:
        assert f.read(16)==b'D092-PLAN-RAW1\0\0';identity,n=struct.unpack('<II',f.read(8));assert identity==case['id'] and n==53;f.read(16)
        for j,d in enumerate(schema):
            fieldid,=struct.unpack('<I',f.read(4));assert fieldid==j
            for arm in range(4):
                value=readvec(f,arm==2 and d['name'] in wanted)
                if value is not None:maps[d['name']]=value
    n=scalar(maps['num_nodes']);levels=scalar(maps['num_levels']);blocks=scalar(maps['cfv_blocks']);nh=list(maps['nh'][1:]);nhmax=scalar(maps['nh_max']);slots=vector(maps['cfv_slot']);assert len(nh)==2 and all(0<x<=nhmax for x in nh) and len(slots)==n
    depth=array.array('i',[-1])*n;bydepth=[[] for _ in range(levels)];chance_bydepth=[[] for _ in range(levels)]
    reached=0
    for family,nodefield in [('action','action_nodes'),('chance_node','chance_nodes'),('fold','fold_nodes'),('show','show_nodes')]:
        nodes=vector(maps[nodefield]);sp=maps[family+'_spans'];assert sp[0]==levels and len(sp)==1+2*levels;covered=0
        for level in range(levels):
            start,count=sp[1+2*level:3+2*level];assert start==covered;covered+=count
            for node in nodes[start:start+count]:
                assert node<n and depth[node]==-1;depth[node]=level;reached+=1;checks+=1
                if family in ['action','chance_node']:bydepth[level].append(node)
                if family=='chance_node':chance_bydepth[level].append(node)
        assert covered==len(nodes)
    cs=vector(maps['cc_start']);cc=vector(maps['cc_count']);cards=vector(maps['cc_card']);children=vector(maps['cc_child']);perms=vector(maps['cc_perm']);hp=pair(maps['hand_perm_flat']);assert len(cs)==len(cc)==n and len(cards)==len(children)==len(perms)
    permutation_words=0;tables=[]
    for player in [0,1]:
        assert len(hp[player])%nh[player]==0;nt=len(hp[player])//nh[player];assert nt>0;tables.append(nt)
        for k in range(nt):
            values=hp[player][k*nh[player]:(k+1)*nh[player]];assert sorted(values)==list(range(nh[player]));permutation_words+=len(values);checks+=1
        assert list(hp[player][:nh[player]])==list(range(nh[player]))
    assert tables[0]==tables[1]
    chance_edges=0;unconditional_hand_loads=0;chance_nodes=0
    for level in range(levels):
        outputs=set()
        for node in bydepth[level]:
            slot=slots[node];assert slot<blocks and slot not in outputs;outputs.add(slot);checks+=1
        inputs=set()
        for node in chance_bydepth[level]:
            chance_nodes+=1;start=cs[node];count=cc[node];assert start+count<=len(cards)
            for t in range(start,start+count):
                child=children[t];k=perms[t]
                assert cards[t]<52 and child<n and depth[child]==level+1 and k<tables[0]
                childslot=slots[child];assert childslot<blocks;inputs.add(childslot)
                for player in [0,1]:
                    # Total table bounds above prove every i and every skipped
                    # hand loads inside this row, without a blocker assumption.
                    assert (childslot*nhmax+nh[player]-1)<blocks*nhmax
                    unconditional_hand_loads+=nh[player]
                chance_edges+=1;checks+=3
        assert not outputs.intersection(inputs);checks+=1
    result={'case':case['id'],'fixture_index':case['fixture_index'],'board':case['board'],'iso_requested':case['iso_requested'],'full_arenas':case['full_arenas'],'nodes':n,'reached_nodes':reached,'chance_nodes':chance_nodes,'chance_edges':chance_edges,'all_hand_load_addresses_covered_by_factored_bounds':unconditional_hand_loads,'hand_permutation_words_checked':permutation_words,'permutation_tables':tables,'root_checks':checks,'all_child_depths_addresses_and_same_level_independence_pass':True,'raw_metadata_sha256':case['raw_sha256']}
    results.append(result);print(json.dumps({k:result[k] for k in ['case','chance_nodes','chance_edges','root_checks']}),flush=True)
assert len(results)==12
report={'id':'D097-chance-selection','at':old.now(),'status':'pass_source_contract_and_concrete_address_ownership','protocol_sha256':old.sha(D/'protocol.json'),'cases':results,'root_checks':sum(r['root_checks'] for r in results),'hand_permutation_words_checked':sum(r['hand_permutation_words_checked'] for r in results),'factored_all_hand_load_address_coverage':sum(r['all_hand_load_addresses_covered_by_factored_bounds'] for r in results),'source_activated':False,'kernel_launches':0,'performance_measured':False,'optimization_accepted':False,'limits':'Producer invariants plus finite canonical metadata corpus. Does not validate malformed custom raw pointer arguments or numerical CUDA/codegen/performance behavior. New ignored arithmetic/load legality must also hold in each concrete raw GPU test before timing.'}
old.save(D/'report.json',report)
old.save(S/'source-review.json',{'at':old.now(),'id':'E059','root_source_review_only':True,'proposal':protocol,'address_report_sha256':old.sha(D/'report.json'),'candidate_accepted':False})
old.save(S/'manifest.json',{'at':old.now(),'baseline':'E051','baseline_source_sha256':old.BASE,'candidate_owned_sha256':{'crates/solver/src/gpu/kernels.cu':old.sha(S/'candidate.cu')},'artifact_sha256':{p.name:old.sha(p) for p in S.iterdir()},'no_production_activation':True})
old.custody();print(json.dumps({'status':report['status'],'cases':12,'root_checks':report['root_checks'],'candidate_sha256':old.sha(S/'candidate.cu'),'kernel_launches':0}),flush=True)
