"""Full original-to-production CPU metadata output replay; no CUDA or timing."""
import array, importlib.util, json, struct, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2
H=ROOT/'runs/D270-actual-metadata-CPU';h.pin(H/'protocol.json',sys.argv[1]);P=h.read(H/'protocol.json')
for path,digest in P['input_sha256'].items():h.pin(path,digest)
h.custody()
spec=importlib.util.spec_from_file_location('d267io',ROOT/'runs/D267b-model-io.py');io=importlib.util.module_from_spec(spec);spec.loader.exec_module(io)
fields=[n for n,t in h.read(P['schema_path'])['fields']]
nodefields=['node_player','node_na','node_data_off','node_children_start','node_twin','node_tlose','node_ttie','node_cdiv','node_river_slot','cc_start','cc_count','cfv_slot']
nodevalues=['action_nodes','chance_nodes','fold_nodes','show_nodes','chance_parents','chance_children','cc_child']
bits=[0,0x80000000,1,0x80000001,0x3f800000,0xbf800000,0x7f800000,0xff800000,0x7fc00123,0x7f800123,0xffc00456,0xff800456]
def enc(v):return struct.pack('<Q',len(v))+v.tobytes()
def pair(a,b):return struct.pack('<Q',2)+enc(a)+enc(b)
def read_array(path,code):
    a=array.array(code);a.frombytes(Path(path).read_bytes());return a
def arena_pair(before,after,forward,ordered,raw,player,nn):
    a=Path(before).read_bytes();b=Path(after).read_bytes();assert len(a)==len(b)
    assert a[:16]==b[:16]==b'D270-ARENA-v1\0\0\0';assert a[16] in[0,1]and a[:121]==b[:121]
    scalars=struct.unpack_from('<13Q',a,17);length,an,ac,cn,cc,inn,inc,init0,cap0,init1,cap1,zn,zc=scalars
    assert an<=ac and cn<=cc and inn<=inc and init0<=cap0 and init1<=cap1 and zn<=zc
    assert len(a)==121+an*32+cn*24+inn*40+4*(init0+init1+zn)
    na=io.vec(raw['node_na'],'I');players=io.vec(raw['node_player'],'I');data=io.vec(raw['node_data_off'],'Q')
    nh=struct.unpack('<QQQ',raw['nh']);assert nh[0]==2
    at=121;checks=0;seen=set();last=-1
    for x,y in zip(struct.Struct('<IIQQQ').iter_unpack(a[at:at+an*32]),struct.Struct('<IIQQQ').iter_unpack(b[at:at+an*32])):
        node=x[0];assert last<node<nn and node not in seen;last=node;seen.add(node)
        assert na[node]>0 and players[node]==player and data[node]!=0xffffffffffffffff
        assert x[3]==data[node] and x[4]==na[node]*nh[player+1]
        assert x[1]==node and y[0]==node and y[2:]==x[2:] and y[1]==(forward[node]if ordered else node)
        checks+=6
    at+=an*32
    assert a[at:at+cn*24]==b[at:at+cn*24];at+=cn*24;last=-1
    for x,y in zip(struct.Struct('<IIQQQQ').iter_unpack(a[at:at+inn*40]),struct.Struct('<IIQQQQ').iter_unpack(b[at:at+inn*40])):
        node=x[0];assert last<node<nn and node not in seen;last=node;seen.add(node)
        assert na[node]>0 and players[node]==player and data[node]==0xffffffffffffffff
        assert x[3]==na[node]*nh[player+1] and x[4:]==(0xffffffffffffffff,0xffffffffffffffff)
        assert x[1]==node and y[0]==node and y[2:]==x[2:] and y[1]==(forward[node]if ordered else node)
        checks+=6
    at+=inn*40;assert a[at:]==b[at:]
    expected={i for i in range(nn)if na[i]>0 and players[i]==player}if a[16]else set()
    assert seen==expected
    if not a[16]:assert an==cn==inn==init0==init1==zn==0
    return {'compact':bool(a[16]),'active':an,'inactive':inn,'all_records_exact_except_required_device_ID':True,'all_capacity_values_and_other_data_exact':True,'checks':checks,'bytes_both':len(a)+len(b)}

log=H/'execution/native.stdout.log'
events=[json.loads(line.split('D270_CASE ',1)[1])for line in log.read_text(encoding='utf-8').splitlines()if'D270_CASE 'in line]
assert len(events)==18
completed=[json.loads(line.split('D270_COMPLETE ',1)[1])for line in log.read_text(encoding='utf-8').splitlines()if'D270_COMPLETE 'in line]
assert completed==[{'cases':18,'CUDA_calls':0,'GPU_solves':0,'speed_samples':0}]
assert '1 passed; 0 failed;' in log.read_text(encoding='utf-8')
rows=[];negative=[];checks=plan_bytes=projection_words=arena_bytes=guards=0
for case in P['fixtures']:
    h.pin(case['original_plan_path'],case['original_plan_sha256'])
    original=io.plans(case['original_plan_path'],fields);nn,=struct.unpack('<Q',original['num_nodes'])
    assert nn==case['expected_nodes']
    for key in ['reference_projection','reference_maps']:h.pin(case[key]['path'],case[key]['sha256'])
    reference=io.read_projection(case['reference_maps']['path'])
    original_locks=read_array(case['locks_path'],'Q');original_children=read_array(case['children_path'],'I')
    assert len(original_locks)==nn
    for arm in P['arms']:
        name=case['id']+'--'+arm
        marker=next(e for e in events if e['id']==case['id']and e['arm']==arm)
        assert marker['nodes']==nn and marker['whole_plan_fields']==53 and marker['projected_arrays']==23
        assert marker['CUDA_calls']==marker['GPU_solves']==marker['speed_samples']==0
        ordered=arm!='selected'or marker['capable']
        assert marker['ordered']==ordered
        prefix=H/'output'/name
        before=Path(str(prefix)+'.before.plan.bin');after=Path(str(prefix)+'.after.plan.bin')
        h.pin(before,case['original_plan_sha256'])
        src={n:io.vec(original[n],'Q'if n=='node_data_off'else'I')for n in nodefields}
        reach=io.nested(original['reach_slot']);src['reach_slot[0]'],src['reach_slot[1]']=reach
        if arm=='exceptional':
            for field,n in enumerate(['node_twin','node_tlose','node_ttie','node_cdiv']):src[n]=array.array('I',(bits[(i+3*field)%len(bits)]for i in range(nn)))
            src['d_lock_off']=array.array('Q',(i*16 if i%3==0 else 0xffffffffffffffff for i in range(nn)))
        else:src['d_lock_off']=original_locks
        pernode=set(src)
        for n in nodevalues:src[n]=io.vec(original[n],'I')
        src['tree.children']=original_children
        actualmaps=io.read_projection(str(prefix)+'.maps.bin');assert set(actualmaps)=={'old_to_new','new_to_old'}
        forward,inverse=actualmaps['old_to_new'],actualmaps['new_to_old']
        assert len(forward)==len(inverse)==nn and forward[0]==inverse[0]==0
        if ordered:assert actualmaps==reference
        else:assert forward==inverse==array.array('I',range(nn))
        assert all(inverse[forward[i]]==i for i in range(nn));checks+=nn
        expected={}
        for n,v in src.items():
            if not ordered:new=v
            elif n in pernode:new=array.array(v.typecode,(v[old]for old in inverse))
            else:new=array.array('I',(old if old==0xffffffff else forward[old]for old in v))
            expected[n]=new
        actual=io.read_projection(str(prefix)+'.projection.bin');assert set(actual)==set(expected)and len(actual)==23
        for n,v in expected.items():
            assert actual[n].typecode==v.typecode and actual[n].tobytes()==v.tobytes(),(name,n)
            projection_words+=len(v)*(v.itemsize//4);checks+=len(v)
        want=dict(original)
        for n in nodefields:want[n]=enc(expected[n])
        want['reach_slot']=pair(expected['reach_slot[0]'],expected['reach_slot[1]'])
        for n in nodevalues:want[n]=enc(expected[n])
        if ordered:want['reach_src']=pair(forward,inverse)
        got=io.plans(after,fields);assert set(want)==set(got)and len(got)==53
        for n in fields:assert got[n]==want[n],(name,n)
        plan_bytes+=sum(len(v)for v in want.values());checks+=53
        arenas=[arena_pair(str(prefix)+f'.p{p}.before.arena.bin',str(prefix)+f'.p{p}.after.arena.bin',forward,ordered,original,p,nn)for p in range(2)]
        assert [a['compact']for a in arenas]==marker['compact']and marker['capable']==all(a['compact']for a in arenas)
        assert marker['record_lookup_checks']==2*nn;checks+=sum(a['checks']for a in arenas)
        if arm=='actual':assert marker['boundary_checks']==8
        else:assert marker['boundary_checks']==0
        written=max(nn*8,len(original_children)*4)if ordered else 0
        expected_guards=((marker['scratch_elements']+1)//2+32)*8-written
        assert marker['scratch_guard_bytes_checked']==expected_guards and expected_guards>0
        guards+=expected_guards;arena_bytes+=sum(a['bytes_both']for a in arenas)
        if ordered:
            n=next(n for n in nodefields if expected[n]!=src[n]);assert actual[n]!=src[n]
            negative.append({'case':name,'fixture':'unrelabelled_node_row_image','rejected':True})
            assert actual['tree.children']!=original_children
            negative.append({'case':name,'fixture':'unrelabelled_child_ID_values','rejected':True})
            wrong=array.array('I',(forward[v]if v<nn else v for v in expected['cfv_slot']))
            assert wrong!=actual['cfv_slot'];negative.append({'case':name,'fixture':'mistaken_relabel_of_physical_CFV_slot_values','rejected':True})
        else:
            assert actualmaps!=reference
            negative.append({'case':name,'fixture':'nonidentity_map_on_original_fallback','rejected':True})
        rows.append({'case':name,'ordered':ordered,'capable':marker['capable'],'whole_before53fields_match_original_hash':True,'whole_after53fields_and23arrays_every_word_exact':True,'nodes':nn,'actual_arena_records':arenas,'record_lookup_checks':marker['record_lookup_checks'],'boundary_checks':marker['boundary_checks'],'scratch_guard_bytes_checked':expected_guards})
        print('Full production CPU replay:',name,flush=True)
assert len(rows)==18 and sum(r['ordered']for r in rows)==16 and len(negative)==50
assert sum(r['boundary_checks']for r in rows)==48
extents=[{'path':str(p),'bytes':p.stat().st_size,'sha256':h.sha(p)}for p in sorted((H/'output').iterdir())]
assert sum(p['bytes']for p in extents)<=P['raw_output_reservation_bytes']
h.custody()
h.save(H/'root-report.json',{'id':'D270-root','at':h.now(),'status':'pass_full_actual_production_CPU_metadata_replay_only','protocol_sha256':sys.argv[1],'checks':checks,'cases':rows,'whole_plan_after_serialized_payload_bytes_compared':plan_bytes,'projected_words_compared':projection_words,'whole_arena_record_snapshot_bytes_both_arms_compared':arena_bytes,'scratch_guard_bytes_checked':guards,'negative_reader_fixtures':negative,'all_output_extents':extents,'raw_output_bytes':sum(p['bytes']for p in extents),'all18whole_before_plan_hashes_match_original':True,'all18after53fields_23arrays_maps_arena_records_and_capacities_exact':True,'actual_compiler_and_CPU_native_process_completed_once_each':True,'candidate_GPU_constructors_CUDA_APIs_kernels_CFR_iterations_solves_speed_samples':0,'accepted_main_live_protected_PTX_unchanged':True,'same_agent_replay_shared_frame_parser_not_external_audit':True,'limits':P['remaining']})
print(json.dumps({'status':'pass_actual_CPU_projection_only','cases':18,'ordered':16,'fallbacks':2,'negative_fixtures':50,'projected_words':projection_words,'raw_bytes':sum(p['bytes']for p in extents)}),flush=True)
