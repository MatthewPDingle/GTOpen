import array, collections, json, shutil, struct, sys, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2
H=ROOT/'runs/D194-parent-chance-census';h.pin(H/'protocol.json',sys.argv[1]);P=h.read(H/'protocol.json')
for p,digest in P['input_sha256'].items():h.pin(p,digest)
schema=h.read(P['schema_path']);expected_fields=[x[0] for x in schema['fields']]
def vec(data,code):
    count,=struct.unpack_from('<Q',data);v=array.array(code);v.frombytes(data[8:]);assert len(v)==count
    if sys.byteorder!='little':v.byteswap()
    return v
def spans(data):
    count,=struct.unpack_from('<Q',data);assert len(data)==8+count*8
    return list(struct.Struct('<II').iter_unpack(data[8:]))
def read_plan(path):
    result={}
    with path.open('rb') as f:
        assert f.read(17)==b'D183_PLAN_RAW1\0\0\0'
        for expected in expected_fields:
            length,=struct.unpack('<I',f.read(4));name=f.read(length).decode();assert name==expected
            size,=struct.unpack('<Q',f.read(8))
            if name in P['selected_fields']:
                raw=f.read(size);assert len(raw)==size;result[name]=raw
            else:f.seek(size,1)
        assert not f.read(1)
    return result
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
    h.custody();h.ar.refuse_active(h.ar.live_status());rows=[];checks=0
    for item in P['raw_inputs']:
        path=Path(item['path']);assert path.stat().st_size==item['bytes'];h.pin(path,item['sha256']);raw=read_plan(path)
        levels,=struct.unpack('<Q',raw['num_levels']);nn,=struct.unpack('<Q',raw['num_nodes']);nh=list(vec(raw['nh'],'Q'))
        d={name:vec(raw[name],'I') for name in ['chance_nodes','chance_parents','chance_children','chance_cards','cc_start','cc_count','cc_card','cc_child','cc_perm']}
        parents=spans(raw['chance_node_spans']);edges=spans(raw['chance_spans']);assert len(parents)==len(edges)==levels
        n_outer,=struct.unpack_from('<Q',raw['reach_slot']);assert n_outer==2;offset=8;slots=[]
        for p in range(2):
            length,=struct.unpack_from('<Q',raw['reach_slot'],offset);assert length==nn
            size=8+length*4;slots.append(vec(raw['reach_slot'][offset:offset+size],'I'));offset+=size
        assert offset==len(raw['reach_slot']);blocks=list(vec(raw['reach_blocks'],'Q'));assert len(blocks)==2
        assert len(d['chance_parents'])==len(d['chance_children'])==len(d['chance_cards'])
        assert len(d['cc_start'])==len(d['cc_count'])==nn and len(d['cc_card'])==len(d['cc_child'])==len(d['cc_perm'])
        level_rows=[];total_old=total_new=0
        for level,((ps,pc),(es,ec)) in enumerate(zip(parents,edges)):
            pn=d['chance_nodes'][ps:ps+pc]
            original=list(zip(d['chance_parents'][es:es+ec],d['chance_children'][es:es+ec],d['chance_cards'][es:es+ec]))
            regrouped=[];selected_cc=[]
            for node in pn:
                begin=d['cc_start'][node];end=begin+d['cc_count'][node];assert begin<=end<=len(d['cc_card'])
                for t in range(begin,end):
                    if d['cc_perm'][t]==0:
                        child=d['cc_child'][t];card=d['cc_card'][t]
                        assert 0<=node<child<nn and card<52
                        regrouped.append((node,child,card));selected_cc.append(t);checks+=3
            assert collections.Counter(original)==collections.Counter(regrouped)
            assert len(original)==len(set(original)) and len(pn)==len(set(pn))
            ownership=[]
            for p in range(2):
                sources={slots[p][node] for node in pn};destinations=[slots[p][child] for _,child,_ in original]
                assert len(destinations)==len(set(destinations)) and sources.isdisjoint(destinations)
                assert all(x<blocks[p] for x in sources) and all(x<blocks[p] for x in destinations)
                ownership.append({'player':p,'source_slots':len(sources),'unique_output_slots':len(destinations),'sources_outputs_disjoint':True,'within_actual_allocated_blocks':True})
                checks+=len(sources)+len(destinations)+3
            level_rows.append({'level':level,'old_edge_CTAs':ec,'proposed_parent_CTAs':pc,'cc_representatives_selected':len(selected_cc),'exact_triplet_multiset':True,'ownership':ownership})
            total_old+=ec;total_new+=pc;checks+=3
        assert total_old==len(d['chance_parents']) and total_new==len(d['chance_nodes'])
        rows.append({'id':item['fixture']['id'],'fixture':item['fixture']['fixture'],'use_iso':item['fixture']['use_iso'],'hands':nh,'node_count':nn,'edge_CTAs_per_full_down_sweep':total_old,'parent_CTAs_per_full_down_sweep':total_new,'levels':level_rows,'input_sha256':item['sha256'],'input_bytes':item['bytes']})
    assert len(rows)==P['required_cases']
    h.custody()
R=ROOT/'comparisons/D194-parent-chance-census';R.mkdir(exist_ok=False)
h.save(R/'report.json',{'id':'D194','at':h.now(),'status':'pass_scoped_source_and_integer_mapping_admit_one_resource_prototype','protocol_sha256':sys.argv[1],'checks':checks,'cases':rows,'all6_original_baseline_metadata_inputs_hash_verified':True,'new_plan_builds_compilers_CUDA_contexts_kernels_solvers_or_timing_samples':0,'D183_phase_timings_used':False,'optimization_accepted':False,'scope':'Complete selected existing plan arrays for canonical iso on/off geometry and per-level write ownership, not GPU arithmetic/layout/speed or an occupancy benefit. Zero-hand/reuse and broader/continuation native cases remain required. Exactly one prospective parent-fanout source form may advance to resource proof; no gain or final adoption.'})
dst=h.ar.DASHBOARD/'evidence'/R.name/'report.json';dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(R/'report.json',dst)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+R.name+'/report.json',timeout=20) as response:assert response.read()==(R/'report.json').read_bytes()
print(json.dumps({'status':'pass_scoped_integer_fanout_mapping','checks':checks,'counts':[{k:x[k] for k in ['id','edge_CTAs_per_full_down_sweep','parent_CTAs_per_full_down_sweep']} for x in rows],'new_native_processes':0,'speed_claim':False}),flush=True)
