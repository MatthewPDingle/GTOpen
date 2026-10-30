"""Independent saved-root readback and Decimal reductions for trajectory output."""
import hashlib
import json
from decimal import Decimal, localcontext
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='board-root-trajectory-v1'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text())
def D(x):return Decimal.from_float(float(x))


def mean(history,lo,hi):
    denominator=Decimal((lo+1+hi)*(hi-lo)//2)
    return [[float(sum((Decimal(g+1)*D(history[g][c][a]) for g in range(lo,hi)),Decimal(0))/denominator)
             for a in range(4)] for c in range(169)]


def distance(a,b,mass):
    return float(sum((D(mass[c])*sum((abs(D(a[c][k])-D(b[c][k])) for k in range(4)),Decimal(0))/2
                      for c in range(169)),Decimal(0)))


def main():
    rp=OUT/f'{PREFIX}-registration.json';sp=OUT/f'{PREFIX}-result.json'
    reg,result=read(rp),read(sp)
    assert result['passed'] and result['registration_sha256']==sha(rp)
    for p,h in reg['inputs'].items():assert sha(Path(p))==h,p
    evaluation=read(OUT/'weighted-complete-board-root-study-v1-result.json')
    store=Path(evaluation['store']);ids=read(store/'bank-identities.json');roots=read(store/'root-stability.json')
    assert sha(store/'bank-identities.json')==evaluation['bank_identities_sha256']
    assert sha(store/'root-stability.json')==evaluation['root_stability_sha256']
    mass=roots['entry_masses'];worst=0.;original_models=0
    def close(a,b):
        nonlocal worst
        error=abs(a-b);worst=max(worst,error);assert error<1e-12,(a,b)
    with localcontext() as ctx:
        ctx.prec=40
        for index,candidate in zip((1,3),result['candidates'],strict=True):
            identity=ids[index];assert candidate['arm']==identity['arm']
            for p,h in candidate['inputs'].items():assert sha(Path(p))==h,p
            objects=Path('S:/GTOpen-research/board-root-matched-prefix-v1')/candidate['arm']/'objects'
            history=candidate['policies_by_generation'];regrets=candidate['regrets_by_generation']
            assert len(history)==len(regrets)==79
            for g,ref in enumerate([*identity['model_references'],identity['unplayed_excluded']]):
                p=objects/ref['file'];assert sha(p)==ref['sha256']
                model=read(p);assert model['generation']==g and model['board_root_state']['regret_sums']==regrets[g]
                original_models+=1
                for c,row in enumerate(regrets[g]):
                    if g:
                        pos=[max(Decimal(0),D(v)) for v in row];total=sum(pos)
                        if total:expected=[float(v/total) for v in pos]
                        else:
                            chosen=row.index(max(row));expected=[float(a==chosen) for a in range(4)]
                        for a,b in zip(expected,history[g][c]):close(a,b)
            complete=mean(history,0,78)
            for a,b in zip(complete,roots['root_probabilities'][index]):
                for x,y in zip(a,b):close(x,y)
            windows=[mean(history,lo,hi) for lo,hi in ((0,26),(26,52),(52,78))]
            for supplied,computed in zip(candidate['windows'],windows):
                for p,q in zip(supplied,computed):
                    for a,b in zip(p,q):close(a,b)
            close(candidate['first_middle_window_tv'],distance(windows[0],windows[1],mass))
            close(candidate['middle_last_window_tv'],distance(windows[1],windows[2],mass))
            close(candidate['final_current_vs_played_average_tv'],distance(history[78],complete,mass))
            steps=[]
            for g,step in enumerate(candidate['updates'],1):
                assert step['generation']==g
                computed=distance(history[g-1],history[g],mass);steps.append(computed)
                close(step['weighted_policy_step_tv'],computed)
                close(step['cumulative_average_tv_to_complete'],distance(mean(history,0,g),complete,mass))
            close(candidate['mean_step_tv_last_26'],float(sum(map(D,steps[52:]))/26))
            for row in candidate['classes']:
                c=row['native_class_index']
                for a,b in zip(row['played_probabilities'],complete[c]):close(a,b)
                for key,x,y in [('first_middle_window_tv',windows[0][c],windows[1][c]),
                                ('middle_last_window_tv',windows[1][c],windows[2][c]),
                                ('final_current_vs_played_average_tv',history[78][c],complete[c])]:
                    close(row[key],float(sum(abs(D(a)-D(b)) for a,b in zip(x,y))/2))
        a,b=[c['policies_by_generation'] for c in result['candidates']]
        cross=result['candidate_cross_seed_trajectory']
        for n,row in enumerate(cross['played_prefixes'],1):
            assert row['played_generations']==n
            close(row['weighted_tv'],distance(mean(a,0,n),mean(b,0,n),mass))
        for (lo,hi),row in zip(((0,26),(26,52),(52,78)),cross['windows']):
            assert row['generations']==[lo,hi-1]
            close(row['weighted_tv'],distance(mean(a,lo,hi),mean(b,lo,hi),mass))
    destination=OUT/f'{PREFIX}-review.json'
    assert not destination.exists()
    output=dict(passed=True,registration_sha256=sha(rp),source_result_sha256=sha(sp),
        reviewer_source_sha256=sha(Path(__file__)),original_model_files_checked=original_models,
        classes_per_arm=169,states_per_arm=79,transitions_per_arm=78,
        decimal_precision=40,maximum_reduction_error=worst,new_deals=0,gpu_used=False,
        limitations='Replays saved roots and descriptive reductions; no new neural forward pass, poker engine, payoff test, or convergence certificate.')
    with destination.open('x',encoding='utf-8') as f:json.dump(output,f,indent=2);f.write('\n')
    print(json.dumps(output),flush=True)


if __name__=='__main__':main()
