"""Resource-only v4 transport; exact v2 posterior64 math and native contracts."""
import hashlib,json,os
from pathlib import Path
import numpy as np
from exact_initial_training_ingest_v2 import digest
from river_weighted_overlay_ingest_v1 import METHOD,binding
from river_posterior64_v1 import posterior,draw
from river_selected_native_values_v1 import evaluate
from preflop_expected_native_execution_v2 import run_native, verify_native, METHOD as NATIVE_EXECUTION_METHOD
import preflop_expected_python_artifacts_v1 as artifacts
import preflop_expected_archived_comparison_io_v4 as profile_io

MAX_NATIVE_OUTPUT_BYTES = 64_000_000
FAILURE_RESERVE = 256
OUTPUT_LIMIT_ARGUMENT = '--output-byte-limit=64000000'


def file_sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def generate(queries,updates,policies,trace,*,generation,start,iteration,policy_id,case_id,
             engine,entry,executable,context_path,folder,guard,write,
             expected_identities,native_timeout_seconds,native_invocations):
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
        guard();rp=folder/(name+'-request.json');write(rp,request);request_bytes=rp.read_bytes()
        if len(request_bytes)>64*1024:raise ValueError('Native request byte budget exceeded')
        if (type(native_timeout_seconds) not in (int,float) or isinstance(native_timeout_seconds,bool)
                or not 0<native_timeout_seconds<=60):
            raise ValueError('Explicit bounded river-native timeout required')
        identities=dict(expected_identities)
        identities.update({str(Path(executable).resolve()):native_hash,
                           str(Path(context_path).resolve()):file_sha(context_path),
                           str(rp.resolve()):file_sha(rp)})
        arguments=[str(context_path),OUTPUT_LIMIT_ARGUMENT]
        result=run_native(executable,arguments,folder=folder,label=name,
            expected_identities=identities,guard=guard,timeout=native_timeout_seconds,
            max_output_bytes=MAX_NATIVE_OUTPUT_BYTES,stdin_path=rp,direct_outputs=[])
        verify_native(result,executable=executable,arguments=arguments,
            expected_identities=identities,stdin_path=rp,timeout=native_timeout_seconds,
            max_output_bytes=MAX_NATIVE_OUTPUT_BYTES,direct_outputs=[])
        output=Path(result['stdout_path']).read_bytes()
        error=Path(result['stderr_path']).read_bytes()
        if len(output)+len(error)>MAX_NATIVE_OUTPUT_BYTES:raise ValueError('Native aggregate output byte budget exceeded')
        write(folder/(name+'-process.json'),dict(code=result['receipt']['returncode'],stdout_bytes=len(output),
            stdout_sha256=hashlib.sha256(output).hexdigest(),stderr=error.decode('utf-8')))
        native_invocations.append(dict(label=name,executable=str(Path(executable).resolve()),
            arguments=list(map(str,arguments)),expected_identities=identities,
            stdin_path=str(rp.resolve()),result=result))
        guard();doc=json.loads(output)
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
        profile_io.save_npz(pp,compressed=True,history=hp,selected=sp)
        chunks.append(dict(targets=plans,history_queries=len(hp),selected_queries=len(sp),policy_arrays_sha256=file_sha(pp)))
    if file_sha(executable)!=native_hash:raise ValueError('Native executable changed during generation')
    evidence=dict(format=1,method='native-posterior64-training-targets-stream-v1',raw_export_retention='Exact native JSON retained with request, policies and hashes',case_id=case_id,policy_id=policy_id,K=64,
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
