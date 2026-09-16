"""N36 fresh references for the fixed blend, only after N35 settling passes."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import collections
import datetime as dt
import hashlib
import importlib.util
from pathlib import Path
import sys
import numpy as np
import continuation_paired_blend_gpu as gpu
import continuation_paired_blend as blend
import continuation_prediction_bounds as bounds

study=gpu.study
BASE=gpu.BASE
OUT=BASE/'paired-blend-prospective-20260916'
bridge=gpu.control.transfer.original.bridge

def idle():
    gpu.control.idle()
    for p in gpu.control.transfer.original.queue.processes():
        if p['ProcessId']==os.getpid():continue
        command=(p['CommandLine'] or '').lower()
        assert not (p['Name'].lower() in ['python.exe','pythonw.exe'] and any(x in command for x in [
            'continuation_zero_fallback.py run','continuation_paired_blend_gpu.py run',
            'continuation_paired_blend_prospective.py run'])),'Another GPU controller is alive'

def adapter():
    spec=importlib.util.spec_from_file_location('_n36_reference',bridge.__file__)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.OUT=OUT;module.other_research=lambda:(idle() or [])
    return module

def sample(fixtures,excluded):
    groups=collections.defaultdict(list)
    for board,iso in fixtures:
        if board in excluded:continue
        cards=[board[i:i+2] for i in range(0,6,2)]
        key=('paired' if len({c[0] for c in cards})<3 else 'unpaired')+'/'+str(len({c[1] for c in cards}))+'suits'
        groups[key].append((board,iso))
    assert len(groups)==5
    result=[]
    for key,rows in sorted(groups.items()):
        assert len(rows)>=4
        rows.sort(key=lambda x:hashlib.sha256(('N36-paired-blend'+x[0]).encode()).digest())
        result += [dict(board=b,iso_weight=i,stratum=key,inclusion_probability=4/len(rows)) for b,i in rows[:4]]
    assert len(result)==len({r['board'] for r in result})==20
    return result

def prepare():
    result=study.read(gpu.OUT/'result.json')
    assert result['changes']['blend']['signal_passed'] and result['desired_time_ratio_met'],'N35 did not qualify for this stage'
    if (OUT/'prospective/manifest.json').exists():return adapter().checked('prospective')
    assert not list((OUT/'prospective/jobs').glob('*.json'))
    OUT.mkdir(parents=True,exist_ok=True)
    inputs=dict(study.read(gpu.OUT/'protocol-freeze.json')['inputs'])
    paths=[Path(__file__),OUT/'README.md',OUT/'implementation-freeze.json',Path(blend.__file__),Path(bounds.__file__),Path(bridge.__file__),
           gpu.OUT/'result.json',gpu.OUT/'oracle-linearity.json',BASE/'shrunk-residual-20260916/candidate.json']
    snapshots={}
    for arm in ['control','blend']:
        p=gpu.OUT/arm/'1000/iteration-1000.json';paths.append(p);snapshots[arm]=study.read(p)
        assert snapshots[arm]['iteration']==1000 and len(snapshots[arm]['leaves'])==2
    assert snapshots['control']['config']==snapshots['blend']['config']
    assert [l['path'] for l in snapshots['control']['leaves']]==[l['path'] for l in snapshots['blend']['leaves']]
    for p in paths:inputs[str(p.resolve().relative_to(study.ROOT)).replace('\\','/')]=study.pilot.sha(p)
    cases=[]
    for arm,snapshot in snapshots.items():
        for leaf in snapshot['leaves']:
            w,removed,added=study.night.clean_weights(leaf['weights'])
            assert np.isfinite(w).all() and (w>=0).all() and (w.sum(axis=1)>0).all()
            assert 1<=leaf['stack']/leaf['pot']<=20
            text=lambda side:','.join(f'{study.pilot.LABELS[h]}:{v:.9f}' for h,v in enumerate(w[side]) if v>0)
            cases.append(dict(leaf,id=arm+'-'+leaf['id'],family='changed-policy-'+arm,partition='test',weights=w.tolist(),
                              range_oop=text(0),range_ip=text(1),removed_mass_fraction=removed,probe_added_mass_fraction=added,source_policy=arm))
    excluded=set()
    for p in sorted(set(BASE.rglob('manifest.json'))):
        if OUT in p.parents:continue
        m=study.read(p)
        excluded.update(b['board'] for b in m.get('boards',[]) if isinstance(b,dict) and 'board' in b)
        excluded.update(j['board'] for j in m.get('jobs',[]) if 'board' in j)
        inputs[str(p.relative_to(study.ROOT)).replace('\\','/')]=study.pilot.sha(p)
    fixtures=study.pilot.AUDIT/'fixtures.json';inputs[str(fixtures.relative_to(study.ROOT)).replace('\\','/')]=study.pilot.sha(fixtures)
    boards=sample(study.read(fixtures)['canonical_flops'],excluded);jobs=[]
    for b in boards:
        for c in cases:
            size={'bet':[{'PotPct':50}],'donk':[{'PotPct':50}],'raise':[{'PotPct':100}]}
            cfg=dict(board=b['board'],range_oop=c['range_oop'],range_ip=c['range_ip'],tree=dict(starting_pot=c['pot'],effective_stack=c['stack'],
                rake_pct=0,rake_cap=0,oop=[size]*3,ip=[size]*3,max_raises=1,add_allin=False,allin_threshold=.85))
            jobs.append(dict(**b,case=c['id'],id=c['id']+'-'+b['board'],config=cfg))
    original=study.night.checked_manifest();inputs[original['binary_path']]=original['binary_sha256']
    model=dict(kind='paired_balanced_blend',alpha=.25,learned=study.read(BASE/'shrunk-residual-20260916/candidate.json'),
               paired_class_base=study.read(study.ROOT/'cache/realization_fit.json')['class_base'],production_enabled=False)
    study.freeze(OUT/'candidate.json',model)
    manifest=study.signed(dict(cases=cases,boards=boards,jobs=jobs,partition='prospective',inputs=inputs,
        binary_path=original['binary_path'],binary_sha256=original['binary_sha256'],target_gap_pct=.1,max_iterations=2000,protocol='N36 README.md; all 80 references required.'))
    study.freeze(OUT/'prospective/manifest.json',manifest)
    study.freeze(OUT/'candidate-freeze.json',dict(frozen_at=study.night.now(),sha256=study.pilot.sha(OUT/'candidate.json'),manifest_id=manifest['id'],references_at_freeze=0))
    return manifest

def evaluate():
    runner=adapter();m=runner.checked('prospective');contexts=runner.contexts('prospective')
    frozen=study.read(OUT/'candidate-freeze.json');model=study.read(OUT/'candidate.json')
    assert frozen['manifest_id']==m['id'] and frozen['references_at_freeze']==0 and frozen['sha256']==study.pilot.sha(OUT/'candidate.json')
    counts,eq=study.pilot.matrices();base=np.array(model['paired_class_base']);rows=[];hashes={};physical=[]
    stamp=dt.datetime.fromisoformat(frozen['frozen_at']).timestamp()
    for j in m['jobs']:
        p=OUT/'prospective/jobs'/f"{j['id']}.json";assert p.stat().st_mtime>=stamp
        hashes[str(p.relative_to(study.ROOT)).replace('\\','/')]=study.pilot.sha(p)
    assert len(hashes)==80
    for c in contexts:
        full=blend.shrunk.network.predict(c,model['learned']);paired=blend.paired_baseline(c,counts,eq,base)
        predicted=.75*paired+.25*full
        error=study.pilot.metrics(c,predicted);error['paired_balanced']=study.pilot.metrics(c,paired)['candidate'];error['full_N15']=study.pilot.metrics(c,full)['candidate']
        bs=study.fit.bootstrap(c,predicted)['candidate'];bp=study.fit.bootstrap(c,paired)['candidate']
        ci=np.quantile(1-bs/bp,[.05,.95]).tolist();physical.append(bounds.inspect(c,predicted))
        passed=error['candidate']<=.85*error['balanced'] and error['candidate']<=.85*error['paired_balanced'] and ci[0]>0 and physical[-1]['passed']
        rows.append(dict(case=c['case']['id'],mae_pct_pot=error,paired_90_improvement_ci=ci,passed=bool(passed),
                         max_reference_gap_pct=max(r['gap_pct'] for r in c['rows']),max_gpu_gap_pct=max(r['gpu_gap_pct'] for r in c['rows'])))
    result=dict(cases=rows,accuracy_screen_passed=all(r['passed'] for r in rows),reference_hashes=hashes,physical_predictions=physical,
                production_enabled=False,candidate_sha256=frozen['sha256'],manifest_id=m['id'],
                caveat='Fresh boards in four generated contexts, limited fixed menu. Not full-game accuracy or repeated end-to-end performance qualification.')
    study.freeze(OUT/'evaluation.json',result);return result

def run():
    idle();prepare()
    try:
        adapter().run_partition('prospective');r=evaluate()
        study.night.dump(OUT/'status.json',dict(stage='complete',accuracy_screen_passed=r['accuracy_screen_passed'],updated=study.night.now(),production_enabled=False))
    except Exception as error:
        study.night.dump(OUT/'status.json',dict(stage='failed',error=str(error),updated=study.night.now(),production_enabled=False));raise

if __name__=='__main__':{'prepare':prepare,'run':run,'evaluate':evaluate}[sys.argv[1]]()
