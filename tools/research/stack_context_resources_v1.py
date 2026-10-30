"""Derive real context-local catalogs/matrices from the reviewed complete cache."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
import hashlib
import itertools
import json
import math
from pathlib import Path
import subprocess
import sys
import time
import traceback
import numpy as np
import psutil
from sampled_allin_protocol_v3 import AllinCache
from sampled_physical_deals_v1 import PhysicalDeals
from storage_strategic_common_prior_20260920 import PAIRS,MASKS,CLASSES
from preflop_allin_matrix_v1 import build,AllinMatrix
from sampled_physical_root_evaluation_v1 import save,sha,hand_class
from stack_context_inputs_v1 import digest
from stack_context_board_components_v1 import routes
from board_study_storage_v1 import create,measure
from global_research_inventory_v3 import measure as inventory
from bounded_parallel_evaluation_archive_v2 import production_available

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
GEOMETRY=Path('S:/GTOpen-research/stack-geometry-control-v1')
NAME='stack-context-resources-v1';STORE=Path('S:/GTOpen-research')/NAME
REG,ATTEMPT,RESULT,FAILURE=(OUT/(NAME+s+'.json') for s in ('-registration','-attempt','-result','-failure'))
LOCK=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER=ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'
EXE=ROOT/'target/release/examples/hu_preflop_visible_catalog_v1.exe'
DEPTHS=(20,40,60,100,150,200,400)


def read(p):return json.loads(Path(p).read_bytes())


def population(source,keys,orbit_sizes):
    sampler=PhysicalDeals(source,mode='full_deck',seed=0)
    by_pair={tuple(map(int,h)):i for i,h in enumerate(PAIRS)}
    indices=np.array([(by_pair[k[:2]],by_pair[k[2:]]) for k in keys])
    joint=sampler.weights[0,:,None]*sampler.weights[1,None,:]*((MASKS[:,None]&MASKS[None,:])==0)
    total=math.fsum(joint.ravel())
    if total<=0:raise ValueError('Nonempty incoming population required')
    weights=orbit_sizes*joint[indices[:,0],indices[:,1]]/total
    if abs(math.fsum(weights)-1)>1e-12:raise ValueError('Canonical probabilities do not cover original ranges')
    groups=CLASSES[:,None]*169+CLASSES[None,:]
    direct=np.bincount(groups.ravel(),weights=joint.ravel()/total,minlength=169*169).reshape(169,169)
    aggregate=np.bincount(CLASSES[indices[:,0]]*169+CLASSES[indices[:,1]],weights=weights,minlength=169*169).reshape(169,169)
    if np.max(abs(aggregate-direct))>1e-12:raise ValueError('Canonical and physical class probabilities disagree')
    rows=[dict(private_cards=list(k),probability=float(w),physical_pairs=int(n)) for k,w,n in zip(keys,weights,orbit_sizes) if w>0]
    return dict(context_sha256=digest(source),player_roles_fixed=True,physical_pairs=int(np.count_nonzero(joint)),rows=rows),direct


def catalog(source,physical,matrix):
    if physical['context_source']!=source:raise ValueError('Native catalog source mismatch')
    context=json.loads(source);routes(context);response=context['nodes'][0]['children'][3]
    physical_keys={i:set() for i,n in enumerate(context['nodes']) if n['children']};selected={}
    for row in physical['rows']:
        node=row['node'];hand=tuple(row['hand']);o=row['observation']
        if node not in physical_keys or hand in physical_keys[node]:raise ValueError('Unknown/duplicate physical catalog row')
        physical_keys[node].add(hand)
        if (o['actor']!=context['nodes'][node]['actor'] or o['phase']!=0 or o['hi']!=str(node+1)
                or hand_class([(int(o['lo'])>>(6*j))&63 for j in range(2)])!=hand_class(hand)):
            raise ValueError('Native catalog node/class mismatch')
        if node not in (0,response):continue
        actor=o['actor'];c=hand_class(hand)
        if actor==1 and matrix.btn_mass[c]==0:continue
        key=(actor,c)
        if key in selected and selected[key]!=o:raise ValueError('Suit-dependent canonical preflop observation')
        selected[key]=o
    legal={tuple(map(int,h)) for h in PAIRS}
    if any(h!=legal for h in physical_keys.values()):raise ValueError('Every preflop decision needs all private holdings')
    expected={(0,c) for c in range(169)}|{(1,int(c)) for c in np.flatnonzero(matrix.btn_mass>0)}
    if set(selected)!=expected:raise ValueError('Incomplete supported initial catalog')
    return dict(format=1,context_source=source,native_observations=[dict(player=a,hand_class=c,
        observation=dict(selected[(a,c)],own_history=[])) for a,c in sorted(selected)])


def independent_matrix(source,pop,cache,matrix,direct):
    context=json.loads(source);root=context['nodes'][0];response=context['nodes'][root['children'][3]]
    called=context['nodes'][response['children'][1]];pot=called['pot'];rake=pot*context['rake_fraction']
    if context['rake_cap']>0:rake=min(rake,context['rake_cap'])
    labels=[cache.rows[tuple(r['private_cards'])] for r in pop['rows']]
    chance=np.array([r['probability'] for r in pop['rows']])
    group=np.array([hand_class(r['private_cards'][:2])*169+hand_class(r['private_cards'][2:]) for r in pop['rows']])
    bshare=np.array([(r['wins']+.5*r['ties'])/r['boards'] for r in labels])
    tshare=np.array([(r['losses']+.5*r['ties'])/r['boards'] for r in labels])
    b=np.bincount(group,weights=chance*((pot-rake)*bshare-called['invested'][0]),minlength=169*169).reshape(169,169)
    t=np.bincount(group,weights=chance*((pot-rake)*tshare-called['invested'][1]),minlength=169*169).reshape(169,169)
    error=max(float(np.max(abs(b-matrix.bb))),float(np.max(abs(t-matrix.btn))),float(np.max(abs(direct-matrix.mass))))
    if error>1e-11:raise ValueError('Independent payoff/mass reconstruction disagrees')
    if matrix.bb_fold!=context['nodes'][root['children'][0]]['leaf']['utilities'][0]:raise ValueError('Wrong fold payoff')
    if matrix.bb_win!=context['nodes'][response['children'][0]]['leaf']['utilities'][0]:raise ValueError('Wrong uncontested payoff')
    if matrix.btn_fold!=context['nodes'][response['children'][0]]['leaf']['utilities'][1]:raise ValueError('Wrong response fold payoff')
    return error


def main():
    if any(p.exists() for p in (REG,ATTEMPT,RESULT,FAILURE,STORE,LOCK,OTHER)):raise ValueError('Existing attempt or resource owner')
    if not production_available() or psutil.virtual_memory().available<28_000_000_000 or psutil.disk_usage('S:/').free<40_000_000_000:
        raise ValueError('Resource admission unavailable')
    accounting=inventory()
    if sum(r['allocated_file_bytes'] for r in accounting)+256_000_000>800_000_000_000:raise ValueError('Global allocated cap')
    review_path=OUT/'stack-context-complete-allin-cache-v1-readback.json';review=read(review_path)
    main_path=OUT/'stack-context-complete-allin-cache-v1-result.json'
    if not review['complete'] or not review['passed'] or review['result_sha256']!=sha(main_path):raise ValueError('Cache readback required')
    proof_path=OUT/'stack-geometry-control-v1-result.json';proof=read(proof_path)
    if not proof.get('passed'):raise ValueError('Qualified geometry sources required')
    paths={Path(__file__).resolve(),review_path,main_path,proof_path,Path(review['cache_artifact']),EXE,
           ROOT/'crates/solver/examples/hu_preflop_visible_catalog_v1.rs',OUT/'STACK-CONTEXT-RESOURCE-PLAN.md'}
    for d in DEPTHS:
        p=GEOMETRY/'fixtures'/f'stack-{d}-context.json'
        if sha(p)!=proof['artifacts'][str(p)]:raise ValueError('Geometry source changed')
        paths.add(p)
    for module in list(sys.modules.values()):
        p=getattr(module,'__file__',None)
        if p and Path(p).is_relative_to(ROOT) and Path(p).suffix=='.py':paths.add(Path(p))
    inputs={str(p):sha(p) for p in sorted(paths)}
    create(STORE);save(STORE/'admission.json',accounting)
    save(REG,dict(inputs=inputs,depths=list(DEPTHS),maximum_seconds=600,maximum_new_bytes=256_000_000,
        cache_sha256=review['cache_sha256'],training_started=False,
        scope='Unsolved BB/BTN geometry fixtures with their declared incoming ranges. Real exact initial/all-in resources, not learned ranges or a chosen scientific training population.'))
    with LOCK.open('x') as stream:stream.write(str(os.getpid()))
    began=time.monotonic()
    def guard():
        if (time.monotonic()-began>600 or not production_available() or OTHER.exists()
                or psutil.virtual_memory().available<24_000_000_000 or psutil.disk_usage('S:/').free<40_000_000_000):
            raise RuntimeError('Context resource preparation limit/activity')
    try:
        save(ATTEMPT,dict(pid=os.getpid(),process_created=psutil.Process().create_time(),registration_sha256=sha(REG)))
        cache=AllinCache(review['cache_artifact'],review['cache_sha256']);keys=sorted(cache.rows)
        sizes=[]
        for i,key in enumerate(keys):
            if i%4096==0:guard()
            sizes.append(len({tuple(sorted(4*(c//4)+p[c%4] for c in key[:2])+sorted(4*(c//4)+p[c%4] for c in key[2:]))
                              for p in itertools.permutations(range(4))}))
        sizes=np.array(sizes);records={}
        for d in DEPTHS:
            guard();cp=GEOMETRY/'fixtures'/f'stack-{d}-context.json';source=cp.read_text();key=digest(source)
            folder=STORE/f'stack-{d}';folder.mkdir();population_doc,direct=population(source,keys,sizes)
            save(folder/'population.json',population_doc)
            doc=build(source,population_doc,cache.rows);matrix=AllinMatrix(doc,source);save(folder/'matrix.json',doc)
            error=independent_matrix(source,population_doc,cache,matrix,direct)
            result=subprocess.run([str(EXE),str(cp)],timeout=30,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
            if result.returncode:raise RuntimeError(result.stderr.decode(errors='replace')[-2000:])
            physical=json.loads(result.stdout)
            with (folder/'physical-catalog.json').open('xb') as stream:stream.write(result.stdout)
            initial=catalog(source,physical,matrix);save(folder/'initial-catalog.json',initial)
            records[key]=dict(depth=d,context_path=str(cp),context_sha256=key,
                matrix=str(folder/'matrix.json'),matrix_sha256=sha(folder/'matrix.json'),
                initial_catalog=str(folder/'initial-catalog.json'),physical_catalog=str(folder/'physical-catalog.json'),
                population=str(folder/'population.json'),maximum_independent_error=error,
                physical_private_pairs=population_doc['physical_pairs'],canonical_keys=len(population_doc['rows']),
                incoming_class_support=[int(np.count_nonzero(matrix.bb_mass)),int(np.count_nonzero(matrix.btn_mass))],
                artifacts={str(p):sha(p) for p in folder.iterdir()})
            print(json.dumps(dict(prepared_depth=d,maximum_error=error)),flush=True)
        for path,h in inputs.items():
            if sha(path)!=h:raise ValueError('Prepared source changed')
        guard();size=measure(STORE)
        if size['logical_bytes']>256_000_000:raise ValueError('Resource storage limit')
        save(RESULT,dict(complete=True,passed=True,registration_sha256=sha(REG),contexts=records,
            cache_sha256=cache.sha256,storage=size,seconds=time.monotonic()-began,
            native_catalogs_verified=True,independent_matrix_arithmetic=True,training_started=False,
            scientific_population_selected=False,accuracy_qualified=False,production_modified=False))
        print(json.dumps(dict(passed=True,seconds=time.monotonic()-began,storage=size)))
    except BaseException as error:
        save(FAILURE,dict(error=repr(error),traceback=traceback.format_exc(),retry_allowed=False));raise
    finally:
        if LOCK.exists() and LOCK.read_text()==str(os.getpid()):LOCK.unlink()


if __name__=='__main__':main()
