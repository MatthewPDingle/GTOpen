"""Read-only exact phase/ownership model for safe two-level action stars, no GPU execution."""
import importlib.util,json,struct,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'))
import common as h
H=ROOT/'runs/D313-action-star-ownership';P=h.read(H/'protocol.json')
assert len(sys.argv)==2
h.pin(H/'protocol.json',sys.argv[1])
for path,digest in P['input_sha256'].items():h.pin(path,digest)
spec=importlib.util.spec_from_file_location('d313io',P['IO_path']);io=importlib.util.module_from_spec(spec);spec.loader.exec_module(io)
schema=[x[0]for x in h.read(P['schema_path'])['fields']]
checks=0
def req(test,message):
    global checks
    assert test,message;checks+=1
def words(raw):return np.asarray(io.vec(raw,'I'),dtype=np.uint32)
def last_writer(phases,slots):
    out={}
    for phase,node in sorted(phases,key=lambda p:(-p[0],p[1])):out[int(slots[node])]=node
    return out
# Fixed negative examples expose the actual cross-block hazard; safe own reads precede parent write.
req(not ({7}<= {8}),'foreign reader must reject')
req({7}<={7},'own CTA reader is allowed')
def safe_for(parent,slot,read_slots,read_owners):
    selected=np.asarray(read_owners)[np.asarray(read_slots)==slot]
    return bool(np.all(selected==parent))
req(not safe_for(3,5,[5,5],[3,4]),'shared slot foreign reader rejects')
req(not safe_for(3,5,[5],[4]),'single foreign reader rejects')
req(safe_for(3,5,[5,5],[3,3]),'all own readers allowed')
req(safe_for(3,5,[6],[4]),'unread output slot allowed')
results=[];verified_gpu={}
for case in P['cases']:
    name=case['fixture']+'-'+case['constructor'];print('D313_START',name,flush=True)
    for key in['plan','kinds']:
        h.pin(case[key],case[key+'_sha256'])
    gpu=case['gpu']
    if gpu not in verified_gpu:
        h.pin(gpu,case['gpu_sha256']);verified_gpu[gpu]=True
    req(Path(gpu).stat().st_size==case['gpu_bytes'],'whole original GPU extent')
    raw=io.plans(Path(case['plan']),schema);gm=io.gpu_metadata(gpu);children=np.asarray(gm['d_children'],dtype=np.uint32)
    kind=np.frombuffer(Path(case['kinds']).read_bytes(),dtype=np.uint8)
    nn=struct.unpack('<Q',raw['num_nodes'])[0];levels=struct.unpack('<Q',raw['num_levels'])[0];blocks=struct.unpack('<Q',raw['cfv_blocks'])[0]
    req(len(kind)==nn,'all node kinds present')
    ids=words(raw['action_nodes']);arity=words(raw['node_na']);cs=words(raw['node_children_start']);slot=words(raw['cfv_slot'])
    spans=io.spans(raw['action_spans']);req(len(spans)==levels,'all action phases present')
    depth=np.full(nn,-1,dtype=np.int32)
    for node_key,span_key in[('action_nodes','action_spans'),('chance_nodes','chance_node_spans'),('fold_nodes','fold_spans'),('show_nodes','show_spans')]:
        nodeids=words(raw[node_key]);partspans=io.spans(raw[span_key]);req(len(partspans)==levels,'complete phase inventory')
        for level,(start,count)in enumerate(partspans):
            part=nodeids[start:start+count];req(len(part)==count and np.all(part<nn),'phase IDs in range')
            req(np.all(depth[part]==-1),'one phase per visited node');depth[part]=level
    req(np.all(kind[ids]==0)and len(np.unique(ids))==len(ids),'every actual action node visited once')
    req(np.all((arity[ids]>=1)&(arity[ids]<=250)),'valid original action arities')
    req(np.all(cs[ids].astype(np.uint64)+arity[ids]<=len(children)),'all action child spans in bounds')
    edge_parent=[];edge_child=[]
    for a in range(int(arity[ids].max(initial=0))):
        parent=ids[arity[ids]>a];edge_parent.append(parent);edge_child.append(children[cs[parent]+a])
    ep=np.concatenate(edge_parent)if edge_parent else np.array([],dtype=np.uint32)
    ec=np.concatenate(edge_child)if edge_child else np.array([],dtype=np.uint32)
    req(np.all(ec<nn)and np.all(depth[ec]==depth[ep]+1),'every direct action child at next original level')
    req(np.all(slot[ec]<blocks)and np.all(slot[ep]<blocks),'all physical input/output rows valid')
    parents=np.full(nn,-1,dtype=np.int64);parent_count=np.bincount(ec,minlength=nn)
    parents[ec]=ep
    chance_ref=np.zeros(nn,dtype=np.bool_);cc=words(raw['cc_child']);valid=cc[cc!=0xffffffff]
    req(np.all(valid<nn),'all original chance references valid');chance_ref[valid]=True
    # Shape obligations apply to complete stars: at least one action child, no chance child,
    # every action child uniquely owned and absent from all chance-orbit references.
    action_edge=kind[ec]==0
    child_action_count=np.bincount(ep[action_edge],minlength=nn)
    bad=np.zeros(nn,dtype=np.bool_)
    np.logical_or.at(bad,ep,kind[ec]==1)
    np.logical_or.at(bad,ep[action_edge],(parent_count[ec[action_edge]]!=1)|chance_ref[ec[action_edge]])
    shape=ids[(child_action_count[ids]>0)&~bad[ids]]
    safe=[];unsafe=[];witnesses=[];level_rows=[]
    for level in range(levels-1):
        heads=shape[depth[shape]==level]
        start,count=spans[level+1];readers=ids[start:start+count]
        mask=depth[ep]==level+1;rs=slot[ec[mask]];reader=ep[mask];owners=parents[reader]
        if len(rs):
            order=np.argsort(rs,kind='stable');keys=rs[order];owner=owners[order]
            begins=np.r_[0,np.flatnonzero(keys[1:]!=keys[:-1])+1]
            unique=keys[begins];minimum=np.minimum.reduceat(owner,begins);maximum=np.maximum.reduceat(owner,begins)
            pos=np.searchsorted(unique,slot[heads]);present=pos<len(unique);present[present]=unique[pos[present]]==slot[heads[present]]
            own=np.zeros(len(heads),dtype=np.bool_);own[present]=(minimum[pos[present]]==heads[present])&(maximum[pos[present]]==heads[present])
            allowed=~present|own
        else:allowed=np.ones(len(heads),dtype=np.bool_)
        safe.extend(map(int,heads[allowed]));unsafe.extend(map(int,heads[~allowed]))
        for head in heads[~allowed][:max(0,8-len(witnesses))]:
            matches=np.flatnonzero((rs==slot[head])&(owners!=head));req(len(matches)>0,'concrete foreign reader exists')
            at=int(matches[0]);witnesses.append({'parent':int(head),'parent_level':level,'output_slot':int(slot[head]),'foreign_action_reader':int(reader[at]),'reader_owner_parent':int(owners[at]),'read_slot':int(rs[at]),'reader_level':level+1})
        level_rows.append({'parent_level':level,'shape_candidate_heads':len(heads),'safe_heads':int(np.count_nonzero(allowed)),'unsafe_heads':int(np.count_nonzero(~allowed)),'original_next_level_action_nodes':len(readers)})
    req(len(safe)+len(unsafe)==len(shape),'every structurally eligible head classified')
    # Fixed deterministic maximal disjoint-star selection, deepest parent level first,
    # then ascending original node ID. No shape/threshold/fixture/sample tuning.
    used=np.zeros(nn,dtype=np.bool_);heads=[];flat=[];offsets=[0]
    for parent in sorted(safe,key=lambda node:(-int(depth[node]),node)):
        kids=children[cs[parent]:cs[parent]+arity[parent]];ak=kids[kind[kids]==0]
        if used[parent]or np.any(used[ak]):continue
        req(len(ak)>0 and np.all(parents[ak]==parent),'whole selected star has unique child ownership')
        used[parent]=True;used[ak]=True;heads.append(parent);flat.extend(map(int,ak));offsets.append(len(flat))
    heads=np.asarray(heads,dtype=np.uint32);flat=np.asarray(flat,dtype=np.uint32);offsets=np.asarray(offsets,dtype=np.uint32)
    remaining=ids[~used[ids]];executed=np.concatenate([remaining,heads,flat]);counts=np.bincount(executed,minlength=nn)
    req(len(executed)==len(ids)and np.all(counts[ids]==1)and np.count_nonzero(counts)==len(ids),'all original action nodes execute exactly once')
    req(len(flat)+len(heads)==int(np.count_nonzero(used)),'disjoint whole stars')
    # Original CFV write aliases occur only at different levels of the same parity.
    # Moving selected heads one phase earlier preserves that writer order.
    old=[];new=[]
    selected=np.zeros(nn,dtype=np.bool_);selected[heads]=True
    for node in ids:old.append((int(depth[node]),int(node)));new.append((int(depth[node])+int(selected[node]),int(node)))
    req(last_writer(old,slot)==last_writer(new,slot),'whole physical scratch last-writer node unchanged')
    for level in range(levels):
        part=ids[depth[ids]==level];req(len(np.unique(slot[part]))==len(part),'same-level action writes disjoint')
    projection=H/(name+'.model.bin')
    import array
    io.write_projection(projection,{key:array.array('I',map(int,value))for key,value in{
        'selected_parent_ids':heads,'selected_parent_phases':depth[heads]+1,'selected_child_offsets':offsets,'selected_action_child_ids':flat,
        'remaining_action_ids':remaining,'remaining_action_phases':depth[remaining]}.items()})
    old_ctas=len(ids);new_ctas=len(remaining)+len(heads)
    row={'fixture':case['fixture'],'constructor':case['constructor'],'original_action_nodes':old_ctas,'structural_candidate_stars':len(shape),
        'safe_before_nonoverlap_selection':len(safe),'unsafe_foreign_reader_stars':len(unsafe),'selected_disjoint_stars':len(heads),'selected_action_children':len(flat),
        'remaining_action_nodes':len(remaining),'modeled_old_up_action_CTAs':old_ctas,'modeled_new_up_action_CTAs':new_ctas,
        'modeled_CTA_reduction_pct':100*(old_ctas-new_ctas)/old_ctas if old_ctas else 0,
        'extra_GPU_worklist_payload_if_one_remaining_plus_head_list_bytes':4*(len(remaining)+len(heads)),
        'original_all_action_immutable_buffer_bytes':4*len(ids),'new_FP_operations_removed':0,'CFV_payload_or_mapping_changed':False,
        'all_action_updates_once':True,'physical_scratch_last_writer_identity_exact':True,'foreign_read_witnesses':witnesses,'levels':level_rows,
        'projection':str(projection),'projection_sha256':h.sha(projection),'source_plan_sha256':case['plan_sha256'],'source_GPU_sha256':case['gpu_sha256']}
    results.append(row);print('D313_CASE',json.dumps({k:row[k]for k in['fixture','constructor','safe_before_nonoverlap_selection','selected_disjoint_stars','selected_action_children','modeled_CTA_reduction_pct']}),flush=True)
    h.custody()
h.save(H/'report.json',{'id':'D313','at':h.now(),'status':'pass_finite_ownership_phase_and_original_CFV_writer_model',
    'protocol_sha256':sys.argv[1],'checks':checks,'cases':results,'full_GPU_files_SHA256_verified':len(verified_gpu),
    'negative_ownership_controls':['single_foreign_reader_rejected','mixed_own_foreign_reader_rejected'],
    'scope':'Read-only finite six original accepted plans/frames. Structural CTA count reductions and ownership proofs are not dynamic GPU operation/occupancy/speed/headroom/capacity/material or numerical equivalence evidence. No shader/host candidate created, new native/compiler/GPU/CFR/solver/speed samples0.',
    'next_obligations':'Full source scheduling/FP/locks/graphs/continuation/representation/CFV live-byte proof, actual CUDA resource/local/stack/maxthread/defaultlimits and true emitted two-stage mechanism before any numerical kernels. All fullraw/device/ordinary/fullcycle1%strictfixture/fresh16/broad/material/capacity/holdout/freshoriginal/app adoption gates remain.',
    'all_new_bulk_X_S_readonly_no_T':True,'goal_active':True})
print(json.dumps({'status':'pass','cases':len(results),'checks':checks,'shader_or_host_candidate_created':False}),flush=True)
