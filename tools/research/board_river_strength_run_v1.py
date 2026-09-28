"""Registered original/geometry/visible-strength comparison; final test closed."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
import argparse
import concurrent.futures
import gc
import json
import multiprocessing
from pathlib import Path
import time
import traceback
import numpy as np
import psutil
from board_later_fit_holdout_run_v1 import ROOT,OUT,LOCK,OTHER,Guard,inputs,read,sha,verify,prepared_dataset
from board_later_fit_holdout_train_v1 import configure,curve as original_curve
from board_river_strength_features_v1 import prepare_features,NAMES
from board_river_strength_fit_v1 import curve,RiverEvaluation,control
from board_prefix_publication_v1 import atomic_json

PREFIX='board-river-strength-fit-v1'
STORE=Path('S:/GTOpen-research')/PREFIX
ARMS=('original','geometry','strength')


def fixed_inputs():
    source,prepared,hashes=inputs()
    old_path=OUT/'board-later-fit-holdout-v1-result.json';old=read(old_path)
    old_registration=OUT/'board-later-fit-holdout-v1-registration.json'
    assert old['passed'] and old['complete'] and old['selection']['selected_steps']==512
    assert old['registration_sha256']==sha(old_registration)
    reference_reg=OUT/'board-river-value-reference-v1-registration.json'
    reference_path=OUT/'board-river-value-reference-v1-result.json';reference=read(reference_path)
    assert reference['passed'] and reference['complete'] and reference['registration_sha256']==sha(reference_reg)
    verify(read(reference_reg)['inputs']);hashes.update(read(reference_reg)['inputs'])
    files=[Path(__file__),ROOT/'tools/research/board_river_strength_features_v1.py',
        ROOT/'tools/research/board_river_strength_fit_v1.py',ROOT/'tools/research/board_later_error_audit_math_v1.py',
        ROOT/'tools/research/bounded_parallel_evaluation_archive_v2.py',old_path,old_registration,
        reference_reg,reference_path,OUT/'BOARD-RIVER-STRENGTH-FIT-PLAN.md']
    for row in old['datasets']:
        point=row['checkpoints'][0];assert point['step']==512 and sha(point['weights'])==point['weights_sha256']
        files.append(Path(point['weights']))
    hashes.update({str(p):sha(p) for p in files})
    return source,prepared,hashes,old,reference,read(OUT/'board-later-public-state-catalog-v1.json')


def training_and_validation(item,catalog):
    data=prepared_dataset(item);del data['raw']['test']
    # This child has no CUDA work; the parent retains the desktop-sharing guard.
    def cpu_guard():
        from bounded_parallel_evaluation_archive_v2 import production_available
        assert psutil.virtual_memory().available>24_000_000_000 and production_available() and not OTHER.exists()
    packs,metadata=prepare_features({'train':data['train'],'validation':data['raw']['validation']},catalog,cpu_guard,threads=4)
    data.update(packs=packs,feature_preparation=metadata)
    return data


def gate(records):
    scores={metric:{arm:float(np.mean([r['arms'][arm]['validation']['postflop']['normalized_loss']
        if metric=='postflop' else r['arms'][arm]['contrast'][metric]['mse_bb2'] for r in records])) for arm in ARMS}
        for metric in ('postflop','all','under_50bb')}
    comparisons={}
    for reference in ('original','geometry'):
        comparisons[reference]=dict(
            river_mean_change_percent=100*(scores['all']['strength']/scores['all'][reference]-1),
            under_50bb_mean_change_percent=100*(scores['under_50bb']['strength']/scores['under_50bb'][reference]-1))
    every=all(r['arms']['strength']['contrast']['all']['mse_bb2']<r['arms']['original']['contrast']['all']['mse_bb2'] for r in records)
    small=all(r['arms']['strength']['contrast']['under_50bb']['mse_bb2']<=r['arms']['original']['contrast']['under_50bb']['mse_bb2'] for r in records)
    mean_safe=scores['postflop']['strength']<=scores['postflop']['original']
    each_safe=all(r['arms']['strength']['validation']['postflop']['normalized_loss']<=1.01*r['arms']['original']['validation']['postflop']['normalized_loss'] for r in records)
    rules=dict(lower_river_error_every_dataset=every,no_small_pot_regression_any_dataset=small,
        mean_postflop_does_not_increase=mean_safe,no_postflop_dataset_more_than_one_percent_worse=each_safe,
        river_mean_at_least_one_percent_below_both=all(c['river_mean_change_percent']<=-1 for c in comparisons.values()),
        small_pot_mean_at_least_five_percent_below_both=all(c['under_50bb_mean_change_percent']<=-5 for c in comparisons.values()))
    return scores,comparisons,rules,all(rules.values())


def main(mode):
    source,prepared,hashes,old,reference,catalog=fixed_inputs()
    if mode=='ready':
        print(json.dumps(dict(ready=True,datasets=4,arms=ARMS,steps=512,final_test_closed=True)));return
    guard=Guard();acquired=False;pool=None
    cp=OUT/(PREFIX+'-control.json');rp=OUT/(PREFIX+'-registration.json');destination=OUT/(PREFIX+'-result.json')
    assert not LOCK.exists() and not OTHER.exists()
    if mode=='control':assert not cp.exists()
    else:
        qualification=read(cp);assert qualification['passed'] and qualification['inputs']==hashes
        hashes[str(cp)]=sha(cp);assert not rp.exists() and not destination.exists() and not STORE.exists()
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True;guard();assert psutil.cpu_percent(interval=1)<50
        configure()
        import torch
        assert torch.cuda.is_available() and os.environ.get('CUDA_VISIBLE_DEVICES')!='-1'
        if mode=='control':
            data=prepared_dataset(source['datasets'][0]);del data['raw'];assert data['proof']==prepared['datasets'][0]['split']
            proof=control(data['train'],data['item']['fit_seed'],guard,catalog);verify(hashes)
            atomic_json(cp,dict(**proof,inputs=hashes,seconds=time.monotonic()-guard.started,resource_probes=guard.probes))
            print(json.dumps(proof),flush=True);return
        from global_research_inventory_v2 import measure
        inventory=measure();guard()
        assert sum(row['allocated_file_bytes'] for row in inventory)+100_000_000<800_000_000_000
        registration=dict(inputs=hashes,datasets=source['datasets'],arms=ARMS,steps=512,
            architecture={'original':[302,64,64,4],'geometry':[307,64,64,4],'strength':[307,64,64,4]},
            features=NAMES,feature_domain='Only river decisions with Fold and Call; five zeroes elsewhere.',
            feature_formula='1, (P+C-R)/T, C/T, 2E-1, (E*(P+C-R)-C)/T; E=0.5 control or exact uniform 990-pair equity.',
            initialization='All original weights and seeds preserved; only new first-layer columns initialized to zero.',
            objective='Original grouped source-weighted normalized legal-action squared error plus original variance constant.',
            evaluation='Original raw-row action errors and Call-minus-Fold contrast in bb; no arity denominator in contrast.',
            learning_rate=.003,optimizer='Adam',chunk_size=4096,tf32=False,cpu_preparation_workers=4,
            native_threads_per_preparation_worker=4,persistent_feature_cache=False,
            baseline_check='All four original-arm weights and full validation losses reproduce within 1e-7 before changed fits.',
            gate='River contrast mean >=1% below both controls and below original in every dataset; pooled under50 mean >=5% below both and no dataset worse than original; full postflop mean not higher and no dataset >1% worse.',
            scope='Exploratory fitting on reused validation from two runs of one restricted 200bb BB-vs-BTN tree; no policy promotion.',
            final_test_evaluated=False,new_deals=0,production_modified=False,accuracy_qualified=False,
            maximum_seconds=1800,maximum_retained_bytes=100_000_000,maximum_device_bytes=8_000_000_000,
            storage_admission=inventory,resource_sharing='Light desktop/video allowed; yield to active solves and heavy GPU workloads.',
            created_unix=time.time(),pid=os.getpid(),process_created=psutil.Process().create_time())
        atomic_json(rp,registration);STORE.mkdir();identity=sha(rp)
        atomic_json(STORE/'owner.json',dict(root=str(STORE),registration_sha256=identity))
        pool=concurrent.futures.ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('spawn'))
        futures=[pool.submit(training_and_validation,item,catalog) for item in source['datasets']];datasets=[]
        for i,future in enumerate(futures):
            while True:
                guard()
                try:data=future.result(timeout=2);break
                except concurrent.futures.TimeoutError:pass
            assert data['proof']==prepared['datasets'][i]['split'] and set(data['raw'])=={'validation'}
            assert set(data['packs'])=={'train','validation'} and not data['feature_preparation']['final_test_features_created']
            datasets.append(data)
        pool.shutdown(wait=True);pool=None
        records=[dict(dataset=d['item']['name'],feature_preparation=d['feature_preparation'],arms={}) for d in datasets]
        for arm in ARMS:
            for data,prior,diagnostic,record in zip(datasets,old['datasets'],reference['datasets'],records):
                guard.desktop_probe();item=data['item'];name=item['name']
                assert name==prior['dataset']==record['dataset']==diagnostic['dataset']
                evaluation=RiverEvaluation(data['raw']['validation'],data['train']['scale'],guard,data['packs']['validation'],arm)
                torch.cuda.reset_peak_memory_stats();point={}
                def checkpoint(model,training):
                    assert training['step']==512;value=evaluation.score(model,guard)
                    if arm=='original':
                        previous=prior['checkpoints'][0];assert sha(previous['weights'])==previous['weights_sha256']
                        original=torch.load(previous['weights'],weights_only=True,map_location='cpu')
                        difference=max(float((model.state_dict()[k].detach().cpu()-v).abs().max()) for k,v in original.items())
                        loss_error=max(abs(value['metrics'][k]['normalized_loss']-previous['validation'][k]['normalized_loss']) for k in value['metrics'])
                        assert difference<1e-7 and loss_error<1e-7,(difference,loss_error)
                        expected=diagnostic['comparison']['all']['predictions']['network']['mse_bb2']
                        contrast_error=abs(value['contrast']['all']['mse_bb2']-expected)
                        assert contrast_error<max(1e-4,expected*1e-6)
                        assert value['contrast']['all']['rows']==diagnostic['eligible_validation_rows']
                        point['baseline_reproduction']=dict(maximum_parameter_difference=difference,
                            maximum_validation_loss_difference=loss_error,contrast_cpu_gpu_difference_bb2=contrast_error)
                    path=STORE/(name+'-'+arm+'.pt')
                    with path.open('xb') as f:torch.save({k:v.detach().cpu() for k,v in model.state_dict().items()},f)
                    point.update(**training,validation=value['metrics'],contrast=value['contrast'],weights=str(path),weights_sha256=sha(path))
                    atomic_json(STORE/(name+'-'+arm+'.json'),point)
                    print(json.dumps(dict(dataset=name,arm=arm,postflop_loss=point['validation']['postflop']['normalized_loss'],
                        river_contrast_mse_bb2=point['contrast']['all']['mse_bb2'],under50_contrast_mse_bb2=point['contrast']['under_50bb']['mse_bb2'])),flush=True)
                if arm=='original':timing=original_curve(data['train'],item['fit_seed'],(512,),checkpoint,guard)
                else:timing=curve(data['train'],item['fit_seed'],(512,),checkpoint,guard,data['packs']['train'],arm)
                record['arms'][arm]=dict(**point,timing=timing)
                del evaluation;gc.collect();torch.cuda.empty_cache()
            atomic_json(STORE/(arm+'-completed.json'),dict(registration_sha256=identity,datasets=records))
        scores,comparisons,rules,qualifies=gate(records);verify(hashes)
        retained=sum(p.stat().st_size for p in STORE.iterdir() if p.is_file());assert retained<100_000_000
        result=dict(passed=True,complete=True,registration_sha256=identity,scores=scores,comparisons=comparisons,gate_rules=rules,
            datasets=records,qualifies_for_policy_comparison=qualifies,final_test_evaluated=False,new_deals=0,
            accuracy_qualified=False,production_modified=False,seconds=time.monotonic()-guard.started,
            retained_bytes=retained,resource_probes=guard.probes)
        atomic_json(destination,result)
        print(json.dumps(dict(complete=True,scores=scores,comparisons=comparisons,gate_rules=rules,
            qualifies_for_policy_comparison=qualifies,seconds=result['seconds'])),flush=True)
    except Exception as error:
        failure=OUT/(PREFIX+'-'+mode+'-failure.json')
        if not failure.exists():atomic_json(failure,dict(type=type(error).__name__,message=str(error),
            traceback=traceback.format_exc(),seconds=time.monotonic()-guard.started))
        raise
    finally:
        if pool is not None:
            for p in list(pool._processes.values()):
                if p.is_alive():p.terminate()
            pool.shutdown(wait=True,cancel_futures=True)
        if acquired and LOCK.read_text()==str(os.getpid()):LOCK.unlink()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=('ready','control','run'),default='ready')
    main(parser.parse_args().mode)
