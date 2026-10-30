import json,struct,sys,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D276-single-positive-census';P=h.read(H/'protocol.json');assert len(sys.argv)==2;h.pin(H/'protocol.json',sys.argv[1])
for p,d in P['input_sha256'].items():h.pin(p,d)
checks=0;results=[]
def req(v):
    global checks
    assert v;checks+=1
def census(frame):
    path=Path(frame['path']);h.pin(path,frame['sha256']);h.pin(frame['kind_path'],frame['kind_sha256']);req(path.stat().st_size==frame['bytes']);fields={};maps=[]
    with path.open('rb')as f:
        req(f.read(16)==b'D166-GPU-RAW1\0\0\0')
        for name in['iteration','algorithm','hands']+P['device_inventory']:
            kind,n=struct.unpack('<II',f.read(8));req(0<n<512);req(f.read(n).decode()==name);words,=struct.unpack('<Q',f.read(8));req(kind in[0,2]and words<=2**31);start=f.tell()
            if kind==0:req(f.read(4)==b'\0'*4)
            else:f.seek(words*4,1)
            fields[name]=(kind,words,start)
        req(f.tell()==path.stat().st_size and not f.read(1))
    def array(name,dtype):
        kind,words,start=fields[name];dt=np.dtype(dtype);req(words*4%dt.itemsize==0)
        if kind==0:return np.zeros(words*4//dt.itemsize,dtype=dt)
        if words==0:return np.empty(0,dtype=dt)
        v=np.memmap(path,dtype=dt,mode='r',offset=start,shape=(words*4//dt.itemsize,));maps.append(v);return v
    try:
        nh=array('hands','<u4');req(len(nh)==2 and all(nh>0));iteration=int(array('iteration','<u4')[0]);kinds=np.frombuffer(Path(frame['kind_path']).read_bytes(),dtype='u1');nn=len(kinds)
        ids=array('d_action_nodes','<u4');player=array('d_node_player','<i4');arity=array('d_node_na','<i4');offset=array('d_node_data_off','<u8');locks=array('d_lock_off','<i8');regrets=[array('d_regrets['+str(p)+']','<f4')for p in range(2)]
        req(all(len(x)==nn for x in[player,arity,offset,locks]));req(len(np.unique(ids))==len(ids)and np.all(ids<nn)and np.all(kinds[ids]==0));req(np.all((player[ids]==0)|(player[ids]==1))and np.all((arity[ids]>0)&(arity[ids]<=250)))
        groups=[];visited=locked_nodes=unlocked_nodes=unlocked_hands=eligible=0;category_names=['finite_above_threshold_one_positive','finite_above_threshold_multiple_positive','finite_at_or_below_threshold','nonfinite_sum'];totals={n:0 for n in category_names}
        for p in range(2):
            for na in sorted(set(map(int,arity[ids[player[ids]==p]]))):
                nodes=ids[(player[ids]==p)&(arity[ids]==na)];visited+=len(nodes);locked=nodes[locks[nodes]>=0];nodes=nodes[locks[nodes]<0];locked_nodes+=len(locked);unlocked_nodes+=len(nodes);nhp=int(nh[p]);counts={n:0 for n in category_names};positive_hist=[0]*(na+1)
                req(np.all(offset[nodes]+na*nhp<=len(regrets[p])))
                for start in range(0,len(nodes),P['node_chunk']):
                    part=nodes[start:start+P['node_chunk']];indices=offset[part,None,None]+np.arange(na,dtype=np.uint64)[None,:,None]*nhp+np.arange(nhp,dtype=np.uint64)[None,None,:];values=regrets[p][indices];positive=values>np.float32(0);npositive=positive.sum(axis=1);hist=np.bincount(npositive.ravel(),minlength=na+1);positive_hist=[a+int(b)for a,b in zip(positive_hist,hist)];sums=np.zeros((len(part),nhp),dtype=np.float32)
                    with np.errstate(over='ignore',invalid='ignore'):
                        for a in range(na):np.add(sums,np.where(positive[:,a,:],values[:,a,:],np.float32(0)),out=sums)
                    finite=np.isfinite(sums);above=finite&(sums>np.float32(1e-12));one=above&(npositive==1);categories=[one,above&(npositive>1),finite&~above,~finite];req(np.all(sum(c.astype(np.uint8)for c in categories)==1))
                    for name,c in zip(category_names,categories):counts[name]+=int(np.count_nonzero(c))
                total=len(nodes)*nhp;req(sum(counts.values())==sum(positive_hist)==total);unlocked_hands+=total;eligible+=counts[category_names[0]]
                for name in totals:totals[name]+=counts[name]
                groups.append({'player':p,'actions':na,'active_locked_nodes':len(locked),'active_unlocked_nodes':len(nodes),'unlocked_node_hands':total,'positive_regret_count_histogram':positive_hist,'categories':counts})
                print(frame['fixture'],frame['stage'],'player',p,'actions',na,'nodes',len(nodes),'complete',flush=True)
        req(visited==locked_nodes+unlocked_nodes==len(ids));req(sum(totals.values())==unlocked_hands)
        return{'fixture':frame['fixture'],'stage':frame['stage'],'path':str(path),'whole_file_sha256':frame['sha256'],'whole_file_bytes':frame['bytes'],'iteration':iteration,'hands':list(map(int,nh)),'active_action_nodes':len(ids),'active_locked_nodes':locked_nodes,'active_unlocked_nodes':unlocked_nodes,'unlocked_node_hands':unlocked_hands,'categories':totals,'eligible_endpoint_node_hand_fraction':eligible/unlocked_hands if unlocked_hands else 0,'groups':groups,'all69field_headers_and_endpoints_verified':True,'every_active_unlocked_node_hand_classified_once':True}
    finally:
        for v in maps:v._mmap.close()
for frame in P['frames']:results.append(census(frame));h.custody()
req(len(results)==12);report={'id':'D276','at':h.now(),'status':'pass_scoped_retained_endpoint_census','protocol_sha256':sys.argv[1],'frames':results,'reader_checks':checks,'retained_raw_bytes_SHA256_verified':sum(x['whole_file_bytes']for x in results),'endpoint_unlocked_node_hands':sum(x['unlocked_node_hands']for x in results),'source_candidate_created':False,'new_compilers_native_GPU_CFR_solver_or_speed_samples':0,'scope_limits':P['scope']+' '+P['classification'],'next_requirements':P['prospective_implementation'],'all_owned_readers_terminal_after_parent_wait':False,'accepted_main_live_protected_PTX_unchanged':True};h.custody();h.save(H/'report.json',report);print(json.dumps({'status':report['status'],'snapshots':len(results),'node_hands':report['endpoint_unlocked_node_hands'],'by_frame':[{'fixture':r['fixture'],'stage':r['stage'],'eligible_endpoint_fraction':r['eligible_endpoint_node_hand_fraction']}for r in results]}),flush=True)
