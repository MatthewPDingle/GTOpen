"""Summarize completed records only; never turn a partial trial into a success."""
from run_experiment import HERE
import json

def read(p): return json.loads(p.read_text())

def main():
    previous=HERE.parent/'05-preflop-convergence-20260911/raw'
    bases={k:read(previous/f'{v}-result.json') for k,v in
           [('eight','eight-native-a'),('modeled','modeled-native-a'),('six','six-native-b')]}
    trials=[]
    for path in sorted((HERE/'raw').glob('followup-*-result.json')):
        name=path.name.removesuffix('-result.json')
        exit_path=HERE/'raw'/f'{name}-exit.json'
        if not exit_path.exists(): continue
        r=read(path); e=read(exit_path)
        if not r.get('checks'): continue
        last=r['checks'][-1]; fixture=name.split('-')[1]
        base=bases[fixture]['checks'][-1]['elapsed_seconds']
        row=dict(name=name,normal_exit=e.get('returncode')==0 and e.get('reason') is None,
                 two_full_passes=r['converged_twice'],roundtrip_exact=r['roundtrip_exact'],
                 iterations=r['iteration'],seconds_to_two_checks=last['elapsed_seconds'],
                 total_seconds=r['total_seconds'],full_check_seconds=last['check_seconds'],
                 global_gap_bb=last['gap'],baseline_speedup=base/last['elapsed_seconds'])
        audit=HERE/'raw'/f'{name}-local-v3.json'
        if audit.exists():
            d=read(audit)
            row['local_nodes']=[dict(position=x['candidate_self'].get('position'),path=x['candidate_self']['path'],
                status=x['candidate_self']['status'],passes=x['candidate_self'].get('passes_local_tail_gate'),
                weighted_loss_bb=x['candidate_self'].get('weighted_action_loss_bb')) for x in d['rows']]
        trials.append(row)
    result=dict(scope='Time to two canonical global checks, with separate conditional local gates. Not deployment qualification.',trials=trials)
    (HERE/'RESULTS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    for r in trials:
        gates=[n['passes'] for n in r.get('local_nodes',[]) if n['passes'] is not None]
        print(r['name'],r['iterations'],round(r['seconds_to_two_checks'],3),round(r['baseline_speedup'],2),f'local {sum(gates)}/{len(gates)}')

if __name__=='__main__': main()
