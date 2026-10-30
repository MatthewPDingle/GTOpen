"""Separate reader of every selected star; include chance and terminal CFV writers."""
import array,importlib.util,json,struct,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'))
import common as h
H=ROOT/'runs/D313-action-star-ownership';P=h.read(H/'protocol.json');C=h.read(H/'root-protocol.json');R=h.read(H/'report.json')
assert len(sys.argv)==2;h.pin(H/'root-protocol.json',sys.argv[1])
for table in[P['input_sha256'],C['input_sha256']]:
    for path,digest in table.items():h.pin(path,digest)
spec=importlib.util.spec_from_file_location('d313rootio',P['IO_path']);io=importlib.util.module_from_spec(spec);spec.loader.exec_module(io)
schema=[x[0]for x in h.read(P['schema_path'])['fields']]
checks=0;out=[];negative=[]
def require(value,label):
    global checks
    assert value,label;checks+=1
def u32(raw):return np.asarray(io.vec(raw,'I'),dtype=np.uint32)
def safe_readers(readers,owned):assert set(readers)<=set(owned),'foreign next-level action reader'
def validate_shape(projection,depth,children,cs,arity,kinds,ids):
    heads=np.asarray(projection['selected_parent_ids'],dtype=np.uint32);hp=np.asarray(projection['selected_parent_phases'],dtype=np.uint32)
    offsets=np.asarray(projection['selected_child_offsets'],dtype=np.uint32);flat=np.asarray(projection['selected_action_child_ids'],dtype=np.uint32)
    rest=np.asarray(projection['remaining_action_ids'],dtype=np.uint32);rp=np.asarray(projection['remaining_action_phases'],dtype=np.uint32)
    assert np.array_equal(hp,depth[heads]+1)and np.array_equal(rp,depth[rest]),'every modeled phase'
    assert len(offsets)==len(heads)+1 and offsets[0]==0 and offsets[-1]==len(flat),'whole child projection extent'
    count=np.bincount(np.r_[heads,flat,rest],minlength=len(kinds))
    assert np.all(count[ids]==1)and np.count_nonzero(count)==len(ids),'one execution per original action node'
    for i,node in enumerate(heads):
        original=children[cs[node]:cs[node]+arity[node]];actual=flat[offsets[i]:offsets[i+1]]
        assert np.all(kinds[original]!=1)and np.array_equal(original[kinds[original]==0],actual)and len(actual)>0,'whole ordered action children'
    return heads,flat,rest
for index,(case,result)in enumerate(zip(P['cases'],R['cases'])):
    for key in['plan','kinds']:h.pin(case[key],case[key+'_sha256'])
    require(result['source_GPU_sha256']==case['gpu_sha256']and result['source_plan_sha256']==case['plan_sha256'],'source pins match original completed model')
    h.pin(result['projection'],result['projection_sha256']);projection=io.read_projection(result['projection'])
    raw=io.plans(case['plan'],schema);kind=np.frombuffer(Path(case['kinds']).read_bytes(),dtype=np.uint8);nn=len(kind)
    ids=u32(raw['action_nodes']);arity=u32(raw['node_na']);cs=u32(raw['node_children_start']);slot=u32(raw['cfv_slot']);blocks=struct.unpack('<Q',raw['cfv_blocks'])[0]
    child=np.asarray(io.gpu_metadata(case['gpu'])['d_children'],dtype=np.uint32)
    depth=np.full(nn,-1,dtype=np.int32);phase_ids={}
    visited=[]
    for name,span in[('action_nodes','action_spans'),('chance_nodes','chance_node_spans'),('fold_nodes','fold_spans'),('show_nodes','show_spans')]:
        nodes=u32(raw[name]);visited.extend(map(int,nodes))
        for level,(start,count)in enumerate(io.spans(raw[span])):
            part=nodes[start:start+count];require(np.all(depth[part]<0),'each whole visited writer has one original phase');depth[part]=level
            if name=='action_nodes':phase_ids[level]=part
    heads,flat,rest=validate_shape(projection,depth,child,cs,arity,kind,ids)
    require(len(heads)==result['selected_disjoint_stars']and len(flat)==result['selected_action_children'],'whole original model projection count')
    # Direct tree ownership and all chance-orbit references checked independently.
    direct={};children_by_node={}
    for node in ids:
        kids=child[cs[node]:cs[node]+arity[node]];children_by_node[int(node)]=kids
        for k in kids:direct.setdefault(int(k),[]).append(int(node))
    chance=set(map(int,u32(raw['cc_child'])));chance.discard(0xffffffff)
    bylevel={}
    for node in heads:bylevel.setdefault(int(depth[node]),[]).append(int(node))
    for level,parents in bylevel.items():
        reads={}
        for reader in phase_ids[level+1]:
            for c in children_by_node[int(reader)]:reads.setdefault(int(slot[c]),set()).add(int(reader))
        for parent in parents:
            kids=children_by_node[parent];ak=list(map(int,kids[kind[kids]==0]))
            require(all(direct[k]==[parent]and k not in chance and depth[k]==level+1 for k in ak),'unique action child ownership without chance references')
            safe_readers(reads.get(int(slot[parent]),set()),ak);checks+=1
        if index==0 and not negative:
            first=parents[0];owned=list(map(int,children_by_node[first][kind[children_by_node[first]]==0]))
            try:safe_readers(set(owned)|{nn+1},owned)
            except AssertionError:negative.append('foreign_reader_injected')
            else:raise AssertionError('foreign reader negative accepted')
    # Include EVERY original writer, not only action nodes. Distinct writes in each
    # candidate phase imply ordering inside the phase cannot hide a write conflict.
    visited=np.asarray(visited,dtype=np.uint32);require(len(visited)==len(np.unique(visited)),'complete visited writer inventory')
    old_phase=depth[visited].astype(np.int32);new_depth=depth.copy();new_depth[heads]+=1;new_phase=new_depth[visited]
    require(np.all(slot[visited]<blocks),'all original writer slots valid')
    for level in np.unique(new_phase):
        values=slot[visited[new_phase==level]]
        require(len(values)==len(np.unique(values)),'no two original or moved writers share a row in same new phase')
    # Last physical-row writer in reverse-level execution, with terminal/chance writes included.
    old_last={};new_last={}
    for node in sorted(map(int,visited),key=lambda x:(-int(depth[x]),x)):old_last[int(slot[node])]=node
    for node in sorted(map(int,visited),key=lambda x:(-int(new_depth[x]),x)):new_last[int(slot[node])]=node
    require(old_last==new_last,'all physical rows retain exact last writer including chance and terminals')
    # Private learning updates remain disjoint for all original action nodes.
    off=np.asarray(io.vec(raw['node_data_off'],'Q'),dtype=np.uint64);player=u32(raw['node_player']);nh=struct.unpack('<QQQ',raw['nh'])[1:]
    for p in[0,1]:
        nodes=ids[player[ids]==p];order=np.argsort(off[nodes]);nodes=nodes[order]
        require(np.all(off[nodes[:-1]]+arity[nodes[:-1]].astype(np.uint64)*nh[p]<=off[nodes[1:]]),'all original per-player regret/strategy update intervals disjoint')
    if index==0:
        for label,key,at in [('wrong_parent_phase','selected_parent_phases',0),('duplicate_action_execution','remaining_action_ids',0),('wrong_child_order_or_identity','selected_action_child_ids',0)]:
            corrupt={k:array.array(v.typecode,v)for k,v in projection.items()}
            if label=='wrong_parent_phase':corrupt[key][at]-=1
            elif label=='duplicate_action_execution':corrupt[key][at]=int(heads[0])
            else:corrupt[key][at]=int(heads[0])
            try:validate_shape(corrupt,depth,child,cs,arity,kind,ids)
            except AssertionError:negative.append(label)
            else:raise AssertionError('accepted '+label)
    out.append({'fixture':case['fixture'],'constructor':case['constructor'],'all_selected_stars_replayed':len(heads),'all_original_writer_nodes_including_chance_and_terminals':len(visited),
        'every_next_phase_foreign_reader_rule_pass':True,'every_action_updated_once':True,'all_physical_last_writers_unchanged':True,'same_phase_writes_disjoint':True,'all_learning_update_intervals_disjoint':True})
    print('D313_ROOT_CASE',json.dumps(out[-1]),flush=True);h.custody()
require(len(negative)==4,'all negative controls rejected')
h.save(H/'root-report.json',{'id':'D313-root','at':h.now(),'status':'pass_all_selected_stars_and_all_original_writer_classes',
    'model_report_sha256':h.sha(H/'report.json'),'checks':checks,'cases':out,'negative_corruption_controls_rejected':negative,
    'scope_correction':'Firstmodel last-writer check covered actionwrites only. This additive reader includes every original action/chance/fold/show writer and independently replays everyselectedstar and physicalrowlastwriter, same-phase disjointwrites and all learning intervals. Source/model/selection/inputs unchanged; no model/native/compiler/GPU repeats.',
    'limitations':'Finiteoriginal6CPUplans,nomemoryvisibility/devicefloat/controlflow/resource/material/capacity/speedproof. Countsnotremovabletimebound. No shader/hostcandidateadmittedyet.',
    'new_compilers_native_GPU_CFR_solver_or_speed_samples':0,'all_new_bulk_X_S_readonly_no_T':True})
print(json.dumps({'status':'pass','cases':len(out),'checks':checks,'negative':negative}),flush=True)
