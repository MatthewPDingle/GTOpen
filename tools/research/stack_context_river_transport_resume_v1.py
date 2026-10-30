"""Resume only missing deterministic transport outputs for one retained target.

Scientific posterior/draw/evaluation math is unchanged from transport v1.
Existing bytes are authenticated and never overwritten. Missing native outputs
complete their identical immutable requests; this does not restart a cycle.
"""
import hashlib,json,os,subprocess
from pathlib import Path
import numpy as np
from exact_initial_training_ingest_v2 import digest
from river_weighted_overlay_ingest_v1 import METHOD,binding
from river_posterior64_v1 import posterior,draw
from river_selected_native_values_v1 import evaluate


def file_sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()



def require(ok,message):
    if not ok:raise ValueError(message)


def retained_write(path,value,*,expected,allow_missing):
    path=Path(path)
    if path.exists():
        require(expected.get(str(path))==file_sha(path),'Unbound retained output: '+str(path))
        require(json.loads(path.read_bytes())==value,'Reconstructed output differs: '+str(path))
    else:
        require(allow_missing and str(path) not in expected,'Missing retained output: '+str(path))
        from sampled_physical_root_evaluation_v1 import save
        save(path,value)


def retained_export(folder,name,request,*,source,executable,context_path,guard,write,
                    expected,allow_missing,native_runner):
    guard();rp=folder/(name+'-request.json');write(rp,request);raw=rp.read_bytes()
    require(len(raw)<=64*1024,'Native request byte budget exceeded')
    pp=folder/(name+'-process.json');npth=folder/(name+'-native.json')
    require(pp.exists()==npth.exists(),'Incomplete native receipt/output pair needs review')
    if npth.exists():
        require(expected.get(str(pp))==file_sha(pp) and expected.get(str(npth))==file_sha(npth),
                'Unbound retained native output')
        receipt=json.loads(pp.read_bytes());out=npth.read_bytes()
    else:
        require(allow_missing and str(pp) not in expected and str(npth) not in expected,
                'Missing retained native output')
        if native_runner is None:
            result=subprocess.run([str(executable),str(context_path)],input=raw,capture_output=True,
                timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
        else:result=native_runner(raw)
        require(len(result.stdout)<=64_000_000,'Native output byte budget exceeded')
        receipt=dict(code=result.returncode,stdout_bytes=len(result.stdout),
            stdout_sha256=hashlib.sha256(result.stdout).hexdigest(),stderr=result.stderr.decode('utf-8'))
        write(pp,receipt)
        if result.returncode:raise RuntimeError(result.stderr.decode('utf-8'))
        out=result.stdout
        with npth.open('xb') as f:f.write(out);f.flush();os.fsync(f.fileno())
    require(receipt['code']==0 and receipt['stdout_bytes']==len(out)<=64_000_000
            and receipt['stdout_sha256']==hashlib.sha256(out).hexdigest(),'Native receipt differs')
    doc=json.loads(out);guard()
    require(doc.get('format')==3 and doc['context_source']==source and doc['mode']==request['mode'],
            'Native transport context or mode changed')
    require(doc['request_source']==rp.read_text() and doc['queries']['context_source']==source
            and doc['queries']['batch_source']==doc['request_source'],'Native request/query binding changed')
    return doc

def generate(queries,updates,policies,trace,*,generation,start,iteration,policy_id,case_id,
             engine,entry,executable,context_path,folder,guard,write,expected,allow_missing=False,native_runner=None):
    """Build all target evidence before asking the ingester to mutate anything."""
    folder=Path(folder);folder.mkdir(exist_ok=True);source=queries['context_source']
    if Path(context_path).read_text()!=source or engine.context_source!=source:
        raise ValueError('Context mismatch')
    native_hash=file_sha(executable)
    obs=queries['observations'];p=np.asarray([r['probabilities'] for r in policies['policies']])
    visits=[(i,r) for i,r in enumerate(updates['records']) if r[2]>0 and obs[r[0]]['phase']==3]
    keys=list(dict.fromkeys((obs[r[0]]['hi'],obs[r[0]]['lo']) for i,r in visits))
    lookup={(o['hi'],o['lo']):i for i,o in enumerate(obs)};values={};masses={};chunks=[]
    def export(name,request):
        return retained_export(folder,name,request,source=source,executable=executable,
            context_path=context_path,guard=guard,write=write,expected=expected,
            allow_missing=allow_missing,native_runner=native_runner)
    for offset in range(0,len(keys),32):
        requested=keys[offset:offset+32];name=f'chunk-{offset//32:03d}'
        history=export(name+'-history',dict(format=1,mode='history',targets=[dict(format=1,hi=a,lo=b) for a,b in requested]))
        hp=engine.infer(engine.prepare(history['queries']));plans=[];targets=[]
        if [(d['target']['hi'],d['target']['lo']) for d in history['targets']]!=requested:
            raise ValueError('Native target identities changed')
        for key,doc in zip(requested,history['targets']):
            t=doc['target'];qi=lookup[key];sigma=hp[t['query_index']]
            if t['actor']!=obs[qi]['actor'] or t['n']!=obs[qi]['n'] or np.max(abs(sigma-p[qi]))>1e-10 or not np.array_equal(sigma>0,p[qi]>0):
                raise ValueError('Conditional target differs from original current-policy row')
            post,mass,own=posterior(doc,history['queries']['observations'],hp,entry)
            draws=draw(post,case_id+'|'+policy_id+'|'+key[0]+'|'+key[1]);cards=[doc['pairs'][int(i)]['cards'] for i in draws]
            targets.append(dict(format=1,hi=key[0],lo=key[1],selected_pairs=[list(c) for c in sorted(set(map(tuple,cards)))]))
            plans.append(dict(key=list(key),draws=draws.tolist(),cards=cards,posterior_sha256=digest(post.tolist()),opponent_mass=mass,own_reach=own))
            masses[key]=mass
        selected=export(name+'-selected',dict(format=1,mode='selected',targets=targets));sp=engine.infer(engine.prepare(selected['queries']))
        if [(d['target']['hi'],d['target']['lo']) for d in selected['targets']]!=requested:
            raise ValueError('Selected target identities changed')
        hr={(o['hi'],o['lo']):hp[i] for i,o in enumerate(history['queries']['observations'])}
        for i,o in enumerate(selected['queries']['observations']):
            key=(o['hi'],o['lo'])
            if key in hr and (np.max(abs(sp[i]-hr[key]))>1e-10 or not np.array_equal(sp[i]>0,hr[key]>0)):
                raise ValueError('Current policy changed between native stages')
        for key,doc,plan in zip(requested,selected['targets'],plans):
            result=evaluate(doc,sp,plan['cards']);row=np.zeros(4);row[:doc['target']['n']]=result['regrets'];values[key]=row.tolist()
        pp=folder/(name+'-policies.npz')
        if pp.exists():
            require(expected.get(str(pp))==file_sha(pp),'Unbound retained policy arrays')
            with np.load(pp,allow_pickle=False) as arrays:
                require(set(arrays.files)=={'history','selected'} and np.array_equal(arrays['history'],hp)
                    and np.array_equal(arrays['selected'],sp),'Retained policy arrays differ')
        else:
            require(allow_missing and str(pp) not in expected,'Missing retained policy arrays')
            with pp.open('xb') as f:np.savez_compressed(f,history=hp,selected=sp);f.flush();os.fsync(f.fileno())
        chunks.append(dict(targets=plans,history_queries=len(hp),selected_queries=len(sp),policy_arrays_sha256=file_sha(pp)))
    if file_sha(executable)!=native_hash:raise ValueError('Native executable changed during generation')
    evidence=dict(format=1,method='native-posterior64-training-targets-stream-v1',raw_export_retention='Exact native JSON retained with request, policies and hashes',case_id=case_id,policy_id=policy_id,K=64,
                  native_sha256=native_hash,entry_sha256=digest([[[list(k),v] for k,v in sorted(e.items())] for e in entry]),chunks=chunks,
                  artifacts={p.name:file_sha(p) for p in folder.iterdir() if p.is_file() and p.name not in ('evidence.json','overlay.json')})
    write(folder/'evidence.json',evidence)
    overlay=dict(format=1,method=METHOD,K=64,binding=binding(queries,updates,policies,trace,generation,start,iteration,policy_id),
                 evidence_sha256=digest(evidence),rows=[])
    for i,r in visits:
        qi,actor,_,_=r;key=(obs[qi]['hi'],obs[qi]['lo'])
        overlay['rows'].append(dict(record=i,query=qi,updater=actor,key=list(key),draw_count=64,opponent_mass=masses[key],advantages=values[key]))
    write(folder/'overlay.json',overlay)
    return overlay,evidence
