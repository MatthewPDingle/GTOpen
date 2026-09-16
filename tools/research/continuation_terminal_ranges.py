"""N37 read-only terminal-range discrepancy, after timed GPU work ends."""
import datetime as dt
import os
from pathlib import Path
import subprocess
import continuation_zero_reach as old

ROOT, BASE = old.ROOT, old.BASE
OUT = BASE/'terminal-ranges-20260916'
BIN = ROOT/'target/learned-interface-filtered/release/examples/continuation_terminal_ranges.exe'


def prepare():
    OUT.mkdir(exist_ok=True)
    cases = [(f'eight-{a}', BASE/f'policy-stability-20260916/{a}/1500/policy.gtop') for a in ['original','candidate']]
    cases += [(f'hu{k}-{a}',BASE/f'heads-up-settling-20260916/{k}/{a}/1500/policy.gtop')
              for k in [40,100] for a in ['original','balanced','candidate']]
    files = [Path(__file__), OUT/'README.md', ROOT/'crates/solver/examples/continuation_terminal_ranges.rs',
             ROOT/'crates/solver/examples/continuation_zero_reach.rs',
             ROOT/'crates/solver/src/preflop/mod.rs', ROOT/'crates/solver/src/preflop/convergence_quality.rs',
             ROOT/'cache/preflop_eq169.bin',ROOT/'cache/realization_fit.json']
    files += [p for _,p in cases]
    record = dict(registered_at=dt.datetime.now(dt.timezone.utc).isoformat(),
        inputs={str(p.relative_to(ROOT)).replace('\\','/'):old.sha(p) for p in files},
        cases=[dict(name=n,path=str(p.relative_to(ROOT)).replace('\\','/')) for n,p in cases],
        production_enabled=False)
    p=OUT/'input-freeze.json'
    if p.exists():
        frozen=old.read(p)
        assert record['inputs']==frozen['inputs'] and record['cases']==frozen['cases']
        return frozen
    old.write(p,record)
    return record


def summarize(data):
    rows=data['range_rows']
    supported=[r for r in rows if r['tv'] is not None]
    assert all(0<=r['tv']<=1.000001 for r in supported)
    def weighted(kind, values):
        mass=sum(kind(r) for r in values)
        return sum(kind(r)*r['tv'] for r in values)/mass if mass else None
    weight=lambda r:(r['current_opponents_mass']+r['average_opponents_mass'])*.5
    total=sum(weight(r) for r in supported)
    ranked=sorted(supported,key=lambda r:weight(r)*r['tv'],reverse=True)
    return dict(eligible_hu_terminals=data['eligible_hu_terminals'],terminal_player_pairs=len(rows),
        defined_pairs=len(supported),undefined_pairs=len(rows)-len(supported),
        mean_tv=sum(r['tv'] for r in supported)/len(supported) if supported else None,
        max_tv=max((r['tv'] for r in supported),default=None),
        opponent_weighted_tv=weighted(weight,supported),
        defined_opponent_diagnostic_weight=total,
        undefined_opponent_diagnostic_weight=sum(weight(r) for r in rows if r['tv'] is None),
        diagnostic_weight_fraction_tv_above_10pct=sum(weight(r) for r in supported if r['tv']>.1)/total if total else None,
        top_twenty_by_weighted_discrepancy=ranked[:20])


def run():
    import continuation_paired_blend_gpu as gpu
    gpu.control.idle()
    state=old.read(BASE/'final-queue-20260916/status.json')['stage']
    assert state in ['N35_gate_failed','complete','N36_deferred_deadline','deferred_N35_deadline'],state
    for p in gpu.control.transfer.original.queue.processes():
        assert p['Name'].lower() not in ['learned_interface.exe','postflop_reference.exe'], 'Wait for GPU work to end'
        assert not (p['ProcessId']!=os.getpid() and p['Name'].lower() in ['python.exe','pythonw.exe']
                    and any(t in (p['CommandLine'] or '') for t in ['continuation_paired_blend_gpu.py run','continuation_paired_blend_prospective.py run']))
    deadline=dt.datetime(2026,9,16,20,49,2,tzinfo=dt.timezone.utc)
    assert (deadline-dt.datetime.now(dt.timezone.utc)).total_seconds()>180
    m=prepare();assert not (OUT/'result.json').exists()
    old.write(OUT/'binary-freeze.json',dict(path=str(BIN.relative_to(ROOT)).replace('\\','/'),sha256=old.sha(BIN)))
    old.write(OUT/'empty-paths.json',[])
    rows=[];hashes={}
    for c in m['cases']:
        assert dt.datetime.now(dt.timezone.utc)<deadline
        output=OUT/f"{c['name']}.json"
        assert not output.exists()
        with (OUT/f"{c['name']}.log").open('w',encoding='utf-8',newline='\n') as log:
            subprocess.run([str(BIN),str(ROOT/c['path']),str(OUT/'empty-paths.json'),str(output)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
        data=old.read(output)
        previous=old.read(BASE/f"zero-reach-20260916/{c['name']}.json")
        for key in ['nodes','eligible_hu_terminals','current_learned_enabled','average_learned_enabled','current_own_zero_positive_opponents','average_own_zero_positive_opponents','flips']:
            assert data[key]==previous[key],(c['name'],key)
        r=dict(case=c['name'],**summarize(data));rows.append(r);hashes[output.name]=old.sha(output)
        print({k:v for k,v in r.items() if not isinstance(v,list)},flush=True)
    prepare()
    old.write(OUT/'result.json',dict(rows=rows,output_hashes=hashes,all_N31_counts_and_flips_reproduced=True,production_enabled=False,
        caveat='Single-checkpoint conditional-range discrepancy. Independent-class opponent products are diagnostic weights, not exact legal-card probability or additive gap attribution. Undefined empty ranges are reported separately. No payoff, new solve, accuracy or causal claim.'))


if __name__=='__main__':
    import sys
    {'prepare':prepare,'run':run}[sys.argv[1]]()
