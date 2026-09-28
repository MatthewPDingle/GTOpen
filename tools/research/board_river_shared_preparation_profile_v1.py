"""CPU-only byte-equivalence/timing of shared river-bank query preparation.

Not connected to the live collector. Uses already inspected training archives.
Model-dependent tables and all GPU prediction/accumulation are excluded.
"""
import os
os.environ.update(CUDA_VISIBLE_DEVICES='-1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
from collections import Counter
import cProfile
from dataclasses import fields
import json
from pathlib import Path
import pstats
import time
import numpy as np
import psutil
from board_river_deal_coverage_common_v1 import ROOT,OUT,OLD_PREFIX,OLD_STORE,CONTEXT,read,sha,verify,BANDS
from board_river_target_archive_v1 import read_archive
from board_prefix_publication_v1 import atomic_json
from board_river_bounds_bank_v1 import prepare_queries
from board_training_bank_layout_v1 import validate_queries
from board_training_checkpoint_v1 import model_document,validate_model
from preflop_allin_matrix_v1 import AllinMatrix

NAME='board-river-shared-preparation-profile-v1'


def shared(query,layouts,catalog):
    assert layouts
    prepared=prepare_queries(query,layouts[0],catalog)
    for layout in layouts[1:]:validate_queries(layout,prepared['queries'])
    for key in ('arity','phase','eligible','public','reach_affected'):
        prepared[key].flags.writeable=False
    return [prepared]*len(layouts)


def equivalent(a,b):
    assert a['queries']==b['queries'] and a['history']==b['history']
    for key in ('arity','phase','eligible','public','reach_affected'):
        assert a[key].dtype==b[key].dtype and a[key].shape==b[key].shape and a[key].tobytes()==b[key].tobytes()
    for field in fields(a['arrays']):
        x=getattr(a['arrays'],field.name);y=getattr(b['arrays'],field.name)
        assert x.dtype==y.dtype and x.shape==y.shape and x.tobytes()==y.tobytes()


def main():
    started=time.monotonic();reg=OUT/(NAME+'-registration.json');result=OUT/(NAME+'-result.json')
    assert not reg.exists() and not result.exists()
    assert psutil.virtual_memory().available>24_000_000_000 and psutil.cpu_percent(interval=1)<50
    old_result_path=OUT/(OLD_PREFIX+'-collection.json');old_result=read(old_result_path)
    identities=OLD_STORE/'bank-identities.json';assert sha(identities)==old_result['bank_identities_sha256']
    selection_path=OUT/(OLD_PREFIX+'-selection.json');selection=read(selection_path)
    assert old_result['passed'] and old_result['complete'] and selection['passed'] and selection['complete']
    catalog_path=OUT/'board-later-public-state-catalog-v1.json';catalog=read(catalog_path)
    preflop_catalog=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
    matrix=OUT/'preflop-allin-matrix-control-v1-matrix.json';source=CONTEXT.read_text()
    base=dict(context_source=source,catalog_source=preflop_catalog.read_text(),matrix_sha256=sha(matrix),
        entry_mass=AllinMatrix(read(matrix),source).btn_mass)
    paths=[Path(__file__),old_result_path,identities,selection_path,catalog_path,preflop_catalog,matrix,CONTEXT]
    paths += [ROOT/'tools/research'/n for n in ('board_river_bounds_bank_v1.py','board_training_bank_layout_v1.py',
        'board_training_checkpoint_v1.py','shared_visible_query_arrays_v1.py','sampled_visible_features_bulk_v1.py',
        'sampled_visible_poker_features_v1.py','board_river_strength_features_v1.py','sampled_physical_bank_v1.py',
        'exact_btn_policy_table_v1.py','board_river_target_archive_v1.py')]
    layouts=[]
    for bank in read(identities)['source_banks']:
        objects=Path('S:/GTOpen-research/board-root-matched-prefix-v1')/bank['arm']/'objects'
        ref=bank['model_references'][0];assert ref['generation']==0
        args=dict(base,root_config=bank['root_config']);doc=model_document(objects,ref,**args)
        exact=validate_model(doc,**args)[2];layouts.append(dict(context_source=source,exact_geometry=exact))
        paths.append(objects/ref['file'])
    fixtures=[]
    for actor in (0,1):
        for band_index,(band,_,_) in enumerate(BANDS):
            deal=(actor*5+band_index)*7
            matches=[c for c in selection['cases'] if c['deal_index']==deal and c['split']=='train' and c['actor']==actor and c['pot_band']==band]
            case=min(matches,key=lambda c:c['selection_sha256']);case_id=case['case_id']
            mp=OLD_STORE/'cases'/(case_id+'.manifest.json');archive=OLD_STORE/'cases'/(case_id+'.zip')
            route=old_result['routes'][case_id];assert sha(mp)==route['manifest_sha256'] and sha(archive)==route['archive_sha256']
            paths += [mp,archive];fixtures.append((case,mp,archive))
    hashes={str(p):sha(p) for p in paths}
    atomic_json(reg,dict(inputs=hashes,case_ids=[x[0]['case_id'] for x in fixtures],source_split='old training only',
        mode='CPU-only preparation; neither GPU inference nor live collector changed',order=['separate','shared','shared','separate'],
        maximum_seconds=180,maximum_result_bytes=1_000_000,created_unix=time.time()))
    queries=[];timings=[];maximum_queries=0
    for case,mp,archive in fixtures:
        raw=read_archive(archive,read(mp));doc=json.loads(raw['export.json']);q=doc['queries']
        assert json.loads(raw['record.json'])['case']==case and q['context_source']==source
        queries.append(q);maximum_queries=max(maximum_queries,len(q['observations']))
        original=json.dumps(q,sort_keys=True)
        separate=[prepare_queries(q,layout,catalog) for layout in layouts];together=shared(q,layouts,catalog)
        for a,b in zip(separate,together):equivalent(a,b)
        assert json.dumps(q,sort_keys=True)==original
        wrong=dict(layouts[1],context_source='wrong context');rejected=False
        try:shared(q,[layouts[0],wrong],catalog)
        except ValueError:rejected=True
        assert rejected
        del separate,together
    for mode in ('separate','shared','shared','separate'):
        wall=time.perf_counter();cpu=time.process_time()
        for q in queries:
            assert time.monotonic()-started<180 and psutil.virtual_memory().available>24_000_000_000
            if mode=='separate':prepared=[prepare_queries(q,layout,catalog) for layout in layouts]
            else:prepared=shared(q,layouts,catalog)
            del prepared
        timings.append(dict(mode=mode,wall_seconds=time.perf_counter()-wall,cpu_seconds=time.process_time()-cpu))
    profile=cProfile.Profile();profile.enable()
    for q in queries:
        for layout in layouts:prepare_queries(q,layout,catalog)
    profile.disable();stats=pstats.Stats(profile)
    functions=[]
    for (file,line,name),(cc,nc,tt,ct,callers) in stats.stats.items():
        functions.append(dict(file=file,line=line,name=name,primitive_calls=cc,total_calls=nc,self_seconds=tt,cumulative_seconds=ct))
    functions.sort(key=lambda r:r['cumulative_seconds'],reverse=True)
    verify(hashes);assert time.monotonic()-started<180
    separate=sum(r['wall_seconds'] for r in timings if r['mode']=='separate')
    together=sum(r['wall_seconds'] for r in timings if r['mode']=='shared')
    proof=dict(passed=True,complete=True,registration_sha256=sha(reg),fixtures=len(queries),maximum_queries=maximum_queries,
        query_counts=[len(q['observations']) for q in queries],byte_equal_common_arrays=True,source_queries_unchanged=True,
        both_bank_contexts_validated=True,wrong_context_rejected=True,model_specific_tables_tested=False,
        gpu_inference_tested=False,gpu_used=False,live_collector_modified=False,
        timings=timings,cpu_stage_speedup=separate/together,saved_seconds_per_case=(separate-together)/(2*len(queries)),
        cumulative_profile_top=functions[:30],self_time_profile_top=sorted(functions,key=lambda r:r['self_seconds'],reverse=True)[:15],
        scope='Cached CPU-only timings under concurrent collection. No claim of end-to-end or GPU equivalence.',
        seconds=time.monotonic()-started)
    atomic_json(result,proof);assert result.stat().st_size<1_000_000
    print(json.dumps({k:v for k,v in proof.items() if 'profile_top' not in k}),flush=True)


if __name__=='__main__':main()
