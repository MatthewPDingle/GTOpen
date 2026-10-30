"""Fixed-fixture validation of conditional preflop-all-in profile evaluation."""
import copy
import json
import math
from pathlib import Path
import random
import subprocess
import time
import numpy as np
import psutil
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT,sha,save,hand_class
from sampled_allin_protocol_v3 import AllinCache
from hu_sampled_physical_dense_btn_jam_diagnosis_20260923 import showdown

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-physical-allin-evaluation-control-v1'
STORE=Path('S:/GTOpen-research')/PREFIX


def correction(context,deal,rows,equity):
    """Independent forward preflop reach and actual-investment cashflows."""
    policies={}
    for row in rows:
        if int(row['hi'])>=2**63:continue
        code=int(row['lo']);c=hand_class([code&63,(code>>6)&63])
        key=(int(row['hi'])-1,row['actor'],c)
        assert key not in policies
        policies[key]=row['probabilities']
    win=showdown(deal);delta=np.zeros(2);allin_mass=0.;queue=[(0,1.)]
    while queue:
        index,reach=queue.pop();node=context['nodes'][index]
        if node['children']:
            actor=node['actor'];c=hand_class(deal[2*actor:2*actor+2]);policy=policies[index,actor,c]
            for a,child in enumerate(node['children']):queue.append((child,reach*policy[a]))
        elif node['leaf']['type']=='showdown':
            assert node['leaf']['effective_stack']==0
            pot=node['pot'];gross=pot*context['rake_fraction'];cap=context['rake_cap']
            rake=min(gross,cap) if cap>0 else gross
            sampled=np.array([.5 if win<0 else float(win==i) for i in range(2)])
            expected=np.array([equity,1-equity])
            delta+=reach*(expected-sampled)*(pot-rake);allin_mass+=reach
    assert abs(delta.sum())<1e-10
    return delta,allin_mass


def make_profiles(queries,context):
    obs=queries['observations'];profiles=[]
    for mode in ('uniform','fold','call','raise','jam','hand-aware'):
        rows=[]
        for o in obs:
            n=o['n'];p=[1/n]*n+[0.]*(4-n)
            if o['phase']==0 and mode=='hand-aware':
                code=int(o['lo']);rank=max((code&63)//4,((code>>6)&63)//4)
                weights=[1+((rank+2*a+o['actor'])%7) for a in range(n)];total=sum(weights)
                p=[w/total for w in weights]+[0.]*(4-n)
            if o['phase']==0 and int(o['hi'])==1 and mode in ('fold','call','raise','jam'):
                action=('fold','call','raise','jam').index(mode);p=[0.]*4;p[action]=1.
            rows.append({**{k:o[k] for k in ('hi','lo','actor','n')},'probabilities':p})
        profiles.append(dict(name=mode,policies=rows))
    return dict(format=1,context_source=queries['context_source'],batch_source=queries['batch_source'],profiles=profiles)


def main():
    started=time.monotonic()
    def guard():
        assert idle() and time.monotonic()-started<600
        assert psutil.virtual_memory().available>20_000_000_000 and psutil.disk_usage(str(STORE.parent)).free>40_000_000_000
    guard();assert not STORE.exists();STORE.mkdir()
    context_path=OUT/'bb-context-candidate.json';context=json.loads(context_path.read_text())
    cache_review_path=OUT/'sampled-physical-allin-training-cache-v1-independent-review.json'
    cache=AllinCache.from_review(cache_review_path)
    dense_reg_path=OUT/'sampled-physical-dense-pilot-v1-registration.json'
    dense_reg=json.loads(dense_reg_path.read_text())
    batch_source_path=Path(dense_reg['store'])/'iteration-0001/batch-00/batch.json'
    metric_path=batch_source_path.parent.parent/'metrics.json';metric=json.loads(metric_path.read_text())
    assert sha(batch_source_path)==metric['subbatches'][0]['artifacts']['batch.json']
    privates=[d[:4] for d in json.loads(batch_source_path.read_text())['deals'][:16]]
    assert len(privates)==16
    executables={name:ROOT/f'target/release/examples/{name}.exe' for name in
        ('hu_sampled_bank_bridge','hu_sampled_profile_evaluation','hu_sampled_profile_allin_evaluation_v1')}
    paths=[Path(__file__),context_path,cache_review_path,dense_reg_path,batch_source_path,metric_path,
        ROOT/'tools/research/sampled_allin_protocol_v3.py',
        ROOT/'tools/research/hu_sampled_physical_dense_btn_jam_diagnosis_20260923.py',
        ROOT/'crates/solver/examples/hu_sampled_profile_allin_evaluation_v1.rs',
        ROOT/'crates/solver/examples/hu_sampled_profile_evaluation.rs',
        ROOT/'crates/solver/examples/research_sampled/allin_counts_v1.rs',*executables.values()]
    registration=dict(inputs={str(p):sha(p) for p in paths},private_pairs=privates,replicates=16,seed=932701,
        scope='Six fixed synthetic policies on 16 old training private pairs and 16 new board runouts per pair. Correctness and conditional-board variability only; no learned-bank strength, fresh population evaluation or policy selection.',production_modified=False)
    regpath=OUT/f'{PREFIX}-registration.json';save(regpath,registration)
    rng=random.Random(registration['seed']);records=[];artifacts={};maximum_error=0.;maximum_rake_error=0.
    error=None
    def invoke(exe,arguments,expected_success=True):
        guard();done=subprocess.run([str(executables[exe]),*map(str,arguments)],cwd=ROOT,
            capture_output=True,text=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        assert (done.returncode==0)==expected_success,done.stderr[-2000:]
    try:
        for rep in range(16):
            guard();folder=STORE/f'runout-{rep:02d}';folder.mkdir()
            deals=[h+rng.sample([c for c in range(52) if c not in h],5) for h in privates]
            oldbatch=dict(format=2,batch_id=f'{PREFIX}-{rep}',query_limit=100000,seed=0,deals=deals)
            batch2=folder/'batch-2.json';batch3=folder/'batch-3.json';queries_path=folder/'queries.json'
            save(batch2,oldbatch);labelled=cache.batch(oldbatch);save(batch3,labelled)
            invoke('hu_sampled_bank_bridge',['queries',context_path,batch2,'-',queries_path])
            queries=json.loads(queries_path.read_text());profiles=make_profiles(queries,context)
            old_profiles=folder/'profiles-2.json';new_profiles=folder/'profiles-3.json'
            save(old_profiles,profiles);conditional=copy.deepcopy(profiles);conditional['batch_source']=batch3.read_text();save(new_profiles,conditional)
            old_result=folder/'sampled.json';new_result=folder/'conditional.json'
            invoke('hu_sampled_profile_evaluation',[context_path,batch2,old_profiles,old_result])
            invoke('hu_sampled_profile_allin_evaluation_v1',[context_path,batch3,new_profiles,new_result])
            old=json.loads(old_result.read_text());new=json.loads(new_result.read_text())
            assert new['format']==2 and new['terminal_estimator']=='conditional-preflop-allin-v1' and new['postflop_outcomes']=='sampled-board'
            for profile,a,b in zip(profiles['profiles'],old['profiles'],new['profiles']):
                assert profile['name']==a['name']==b['name']
                for i,(u,v) in enumerate(zip(a['deals'],b['deals'])):
                    label=labelled['allin_counts'][i];equity=(label['wins']+.5*label['ties'])/label['boards']
                    delta,mass=correction(context,deals[i],profile['policies'],equity)
                    discrepancy=float(np.max(np.abs(np.asarray(u['values'])+delta-np.asarray(v['values']))))
                    maximum_error=max(maximum_error,discrepancy)
                    maximum_rake_error=max(maximum_rake_error,abs(u['expected_rake']-v['expected_rake']))
                    assert discrepancy<1e-9 and u['terminal_mass']==v['terminal_mass']
                    if profile['name'] in ('fold','call'):assert mass==0 and u['values']==v['values']
                    records.append(dict(replicate=rep,pair=i,profile=profile['name'],
                        original=u['values'],conditional=v['values'],correction=delta.tolist(),allin_mass=mass))
            artifacts.update({str(p):sha(p) for p in folder.iterdir() if p.is_file()})
        assert maximum_rake_error==0
        # Constant preflop policies/private cards: a pure initial jam has no board-dependent value left.
        variance=[]
        for name in ('uniform','fold','call','raise','jam','hand-aware'):
            ratios=[];raw=[];adjusted=[]
            for i in range(16):
                subset=[r for r in records if r['pair']==i and r['profile']==name]
                assert len(subset)==16
                a=np.asarray([r['original'] for r in subset]);b=np.asarray([r['conditional'] for r in subset])
                va=float(a[:,0].var(ddof=1));vb=float(b[:,0].var(ddof=1));raw.append(va);adjusted.append(vb)
                if name=='jam':assert np.max(np.ptp(b,axis=0))<1e-10
                if va>0:ratios.append(vb/va)
            total_raw=sum(raw);total_new=sum(adjusted)
            variance.append(dict(profile=name,sum_within_pair_variance_sampled=total_raw,
                sum_within_pair_variance_conditional=total_new,ratio=total_new/total_raw if total_raw>0 else None))
        # Reject incorrect estimator transport; never accept a silent fallback.
        folder=STORE/'invalid';folder.mkdir();rejected=[]
        base_batch=labelled;base_profiles=conditional
        cases=[('old-format',lambda b:b.update(format=2)),
            ('missing-counts',lambda b:b.pop('allin_counts')),
            ('wrong-total',lambda b:b['allin_counts'][0].update(boards=1)),
            ('wrong-private-order',lambda b:b['allin_counts'][0]['private_cards'].reverse()),
            ('negative-wins',lambda b:b['allin_counts'][0].update(wins=-1)),
            ('unknown-count-field',lambda b:b['allin_counts'][0].update(unexpected=1))]
        for name,mutate in cases:
            altered=copy.deepcopy(base_batch);mutate(altered);bp=folder/f'{name}-batch.json';save(bp,altered)
            pp=folder/f'{name}-profiles.json';prof=copy.deepcopy(base_profiles);prof['batch_source']=bp.read_text();save(pp,prof)
            invoke('hu_sampled_profile_allin_evaluation_v1',[context_path,bp,pp,folder/f'{name}-result.json'],False);rejected.append(name)
        for p,h in registration['inputs'].items():assert sha(p)==h,p
        rows_path=STORE/'paired-control-rows.json';save(rows_path,records);artifacts[str(rows_path)]=sha(rows_path)
        report=dict(passed=True,registration_sha256=sha(regpath),artifacts=artifacts,paired_profile_deals=len(records),
            independently_reconstructed_player_values=2*len(records),maximum_correction_error_bb=maximum_error,
            maximum_expected_rake_change_bb=maximum_rake_error,no_preflop_allin_profiles_unchanged=True,
            pure_preflop_jam_board_variance_removed=True,within_pair_variance=variance,rejected_cases=rejected,
            seconds=time.monotonic()-started,production_modified=False,scope=registration['scope'])
        save(OUT/f'{PREFIX}-result.json',report);print(json.dumps({k:v for k,v in report.items() if k!='artifacts'},indent=2))
    except Exception as exc:error=str(exc);raise
    finally:save(OUT/f'{PREFIX}-status.json',dict(state='stopped' if error is not None else 'complete',error=error,seconds=time.monotonic()-started,production_modified=False))


if __name__=='__main__':main()
