"""Parallel double-precision normalization, rank incidence and centering."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import importlib.util
import sys
from types import SimpleNamespace
import numpy as np
import continuation_shrunk_mixed_gpu as mixed

double=mixed.double
study=double.study
runtime=double.runtime
OUT=double.OUT.parent/'pair-reductions-20260916'


def source(original,helper):
    substitutions={
        'extern "C" __global__ void interface_prepare(':helper+'\nextern "C" __global__ void interface_prepare(',
        'if(threadIdx.x==0)ranks(d+169,r);':'if(threadIdx.x<13)r[threadIdx.x]=pair_rank_mass(threadIdx.x,d+169);',
        'if(threadIdx.x<2)ranks(d+threadIdx.x*169,rankmass+threadIdx.x*13);':
            'if(threadIdx.x<26)rankmass[threadIdx.x]=pair_rank_mass(threadIdx.x%13,d+(threadIdx.x/13)*169);',
        ' if(threadIdx.x==0){z=0.;for(int h=0;h<169;h++)z+=d[h]*legal(h,d+169,rankmass+13);}':
            ' double pair_value=threadIdx.x<169?d[threadIdx.x]*legal(threadIdx.x,d+169,rankmass+13):0.;\n double pair_total=pair_block_sum(pair_value);if(threadIdx.x==0)z=pair_total;',
        ' __syncthreads();if(threadIdx.x==0){center=0.;for(int x=0;x<338;x++)center+=mass[x]/z*correction[x]/2.;}__syncthreads();':
            ' __syncthreads();double center_value=0.;for(int x=threadIdx.x;x<338;x+=blockDim.x)center_value+=mass[x]/z*correction[x]/2.;\n double center_total=pair_block_sum(center_value);if(threadIdx.x==0)center=center_total;__syncthreads();',
    }
    for before,after in substitutions.items():
        assert original.count(before)==1,before
        original=original.replace(before,after)
    return original


def rank_mass(d):
    result=np.zeros(13)
    for rank in range(13):
        result[rank]=.5*d[rank*14]
        for other in range(13):
            if rank!=other:result[rank]+=.25*d[rank*13+other]+.25*d[other*13+rank]
    return result


def export():
    double.export();mixed.export()
    helper_path=study.ROOT/'tools/research/continuation_pair_reductions.cuh';helper=helper_path.read_text()
    hashes={}
    files=[helper_path,study.ROOT/'tools/research/continuation_pair_reductions.py',OUT/'README.md']
    for name,parent in [('double',double.OUT),('mixed',mixed.OUT)]:
        hashes.update(study.read(parent/'manifest.json')['files']);files.append(parent/'manifest.json')
        folder=OUT/name;folder.mkdir(parents=True,exist_ok=True);target=folder/'interface.cu'
        generated=source((parent/'warp/interface.cu').read_text(),helper).encode()
        if target.exists():assert target.read_bytes()==generated
        else:target.write_bytes(generated)
        files.append(target)
    hashes.update({str(p.relative_to(study.ROOT)).replace('\\','/'):study.pilot.sha(p) for p in files})
    study.freeze(OUT/'manifest.json',dict(files=hashes,production_enabled=False,candidate_sha256=study.pilot.sha(double.shrunk.OUT/'candidate.json')))


def command(args,log,optimized=True,warm=0):
    for p in mixed.transfer.queue.processes():
        if p['ProcessId']!=os.getpid() and p['Name'].lower() in ['python.exe','pythonw.exe']:
            assert not any(t in (p['CommandLine'] or '').lower() for t in ['continuation_pair_reductions.py oracle',
                'continuation_pair_reductions.py benchmark']),'Another pair-reduction GPU controller is active'
    return mixed.command(args,log,optimized=optimized,warm=warm)


def oracle():
    export();double.qualified();assert study.read(double.OUT/'oracle-check.json')['passed']
    differences=[]
    for variant in ['double','mixed']:
        directory=OUT/('oracle-'+variant);directory.mkdir(exist_ok=True)
        generated=(OUT/variant/'interface.cu').read_bytes();target=directory/'interface.cu'
        if target.exists():assert target.read_bytes()==generated
        else:target.write_bytes(generated)
        spec=importlib.util.spec_from_file_location('_pair_reduction_oracle_'+variant,runtime.interface.__file__)
        driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)
        driver.OUT=directory;driver.BIN=runtime.BIN;driver.night=SimpleNamespace(OUT=double.shrunk.OUT)
        driver.fit=SimpleNamespace(**study.fit.__dict__);driver.fit.predict=double.shrunk.network.predict
        driver.command=command;driver.oracle()
        for path in directory.glob('oracle-*.json'):
            if path.name=='oracle-check.json':continue
            a=study.read(path);b=study.read(double.OUT/'oracle-warp'/path.name);maximum=0.
            assert a['config']==b['config'] and len(a['frontier']['rows'])==len(b['frontier']['rows'])
            for x,y in zip(a['frontier']['rows'],b['frontier']['rows']):
                assert x['node']==y['node'] and x['actor']==y['actor']
                av=np.array([h['action_values_counterfactual_bb'] for h in x['hands']]);bv=np.array([h['action_values_counterfactual_bb'] for h in y['hands']])
                maximum=max(maximum,float(abs(av-bv).max()))
            assert maximum<(2e-6 if variant=='double' else 2e-4)
            differences.append(dict(variant=variant,case=path.stem,max_action_change_bb=maximum))
    assert len(differences)==24
    study.freeze(OUT/'oracle-check.json',dict(passed=True,comparisons=differences,production_enabled=False))


def benchmark():
    export();double.qualified();assert study.read(OUT/'oracle-check.json')['passed']
    source_game=study.ROOT/'saves/preflop/balanced-sb05-continuation-20260915.gtop';rows=[];comparisons=[]
    for repeat,arms in enumerate([['original','double','mixed'],['mixed','original','double'],['double','mixed','original']]):
        for arm in arms:
            folder=OUT/f'repeat-{repeat}'/arm;folder.mkdir(parents=True,exist_ok=True);path=folder/'iteration-150.json'
            if not path.exists():
                command(['solve',source_game,folder,'original' if arm=='original' else 'candidate',100,
                    OUT/('double' if arm=='original' else arm)/'interface.cu'],folder/'run.log',optimized=arm!='original',warm=50)
            result=study.read(path);assert result['start_iteration']==result['warmup_iterations']==50 and result['iteration']==150
            rows.append(dict(repeat=repeat,arm=arm,seconds_per_iteration=result['learning_seconds']/100,sha256=study.pilot.sha(path)))
        root=OUT/f'repeat-{repeat}'
        original=double.warp.saves.compare(runtime.OUT/f'repeat-{repeat}/original/policy.gtop',root/'original/policy.gtop')
        study.night.dump(root/'original-state-parity.json',original);assert original['all_numeric_entries_equal']
        for arm in ['double','mixed']:
            if repeat:
                stable=double.warp.saves.compare(OUT/f'repeat-0/{arm}/policy.gtop',root/arm/'policy.gtop')
                study.night.dump(root/(arm+'-repeat-parity.json'),stable);assert stable['all_numeric_entries_equal']
        arena=double.warp.compare(root/'double/policy.gtop',root/'mixed/policy.gtop')
        study.night.dump(root/'arithmetic-arena-comparison.json',arena)
        a=study.read(root/'double/iteration-150.json');b=study.read(root/'mixed/iteration-150.json')
        assert a['config']==b['config'] and [v['path'] for v in a['views']]==[v['path'] for v in b['views']]
        change=max(float(abs(np.array(x['view']['strategy'])-y['view']['strategy']).max()) for x,y in zip(a['views'],b['views']))
        ev_change=float(abs(np.array(a['evs'])-b['evs']).max())
        comparisons.append(dict(repeat=repeat,max_inspected_strategy_change=change,max_player_ev_change_bb=ev_change))
        assert change<=.001 and ev_change<=.001
        print('N17 repeat',repeat+1,'passed',flush=True)
    medians={a:float(np.median([r['seconds_per_iteration'] for r in rows if r['arm']==a])) for a in ['original','double','mixed']}
    study.night.dump(OUT/'timing.json',dict(repeats=rows,median_seconds_per_iteration=medians,comparisons=comparisons,
        overhead_vs_original={a:medians[a]/medians['original']-1 for a in ['double','mixed']},
        within_runtime_target=min(medians[a] for a in ['double','mixed'])<=1.1*medians['original'],production_enabled=False,
        caveat='Fixed-work timing and limited arithmetic comparisons. Changed-policy checks remain; no convergence or deployment claim.'))


if __name__=='__main__':{'export':export,'oracle':oracle,'benchmark':benchmark}[sys.argv[1]]()
