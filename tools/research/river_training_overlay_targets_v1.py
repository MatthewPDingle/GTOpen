"""Bounded research generator using qualified native posterior64 transport."""
import hashlib,json,os,subprocess
from pathlib import Path
import numpy as np
from exact_initial_training_ingest_v2 import digest
from river_weighted_overlay_ingest_v1 import METHOD,binding
from river_posterior64_v1 import posterior,draw
from river_selected_native_values_v1 import evaluate


def file_sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def generate(queries,updates,policies,trace,*,generation,start,iteration,policy_id,case_id,
             engine,entry,executable,context_path,folder,guard,write):
    """Build all target evidence before asking the ingester to mutate anything."""
    folder=Path(folder);folder.mkdir();source=queries['context_source']
    if Path(context_path).read_text()!=source or engine.context_source!=source:
        raise ValueError('Context mismatch')
    native_hash=file_sha(executable)
    obs=queries['observations'];p=np.asarray([r['probabilities'] for r in policies['policies']])
    visits=[(i,r) for i,r in enumerate(updates['records']) if r[2]>0 and obs[r[0]]['phase']==3]
    keys=list(dict.fromkeys((obs[r[0]]['hi'],obs[r[0]]['lo']) for i,r in visits))
    lookup={(o['hi'],o['lo']):i for i,o in enumerate(obs)};values={};masses={};chunks=[]
    def export(name,request):
        guard();rp=folder/(name+'-request.json');output=folder/(name+'-export.json');write(rp,request)
        result=subprocess.run([str(executable),str(context_path),str(rp),str(output)],capture_output=True,text=True,
                              timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
        write(folder/(name+'-process.json'),dict(code=result.returncode,stdout=result.stdout,stderr=result.stderr))
        if result.returncode:raise RuntimeError(result.stderr)
        guard();doc=json.loads(output.read_bytes())
        if doc.get('format')!=3 or doc['context_source']!=source or doc['mode']!=request['mode']:
            raise ValueError('Native transport context or mode changed')
        if doc['request_source']!=rp.read_text() or doc['queries']['context_source']!=source or doc['queries']['batch_source']!=doc['request_source']:
            raise ValueError('Native request/query binding changed')
        return doc
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
        with pp.open('xb') as f:np.savez_compressed(f,history=hp,selected=sp);f.flush();os.fsync(f.fileno())
        chunks.append(dict(targets=plans,history_queries=len(hp),selected_queries=len(sp),policy_arrays_sha256=file_sha(pp)))
    if file_sha(executable)!=native_hash:raise ValueError('Native executable changed during generation')
    evidence=dict(format=1,method='native-posterior64-training-targets-v1',case_id=case_id,policy_id=policy_id,K=64,
                  native_sha256=native_hash,entry_sha256=digest([[[list(k),v] for k,v in sorted(e.items())] for e in entry]),chunks=chunks,
                  artifacts={p.name:file_sha(p) for p in folder.iterdir() if p.is_file()})
    write(folder/'evidence.json',evidence)
    overlay=dict(format=1,method=METHOD,K=64,binding=binding(queries,updates,policies,trace,generation,start,iteration,policy_id),
                 evidence_sha256=digest(evidence),rows=[])
    for i,r in visits:
        qi,actor,_,_=r;key=(obs[qi]['hi'],obs[qi]['lo'])
        overlay['rows'].append(dict(record=i,query=qi,updater=actor,key=list(key),draw_count=64,opponent_mass=masses[key],advantages=values[key]))
    write(folder/'overlay.json',overlay)
    return overlay,evidence
