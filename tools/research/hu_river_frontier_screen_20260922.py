"""Freeze, run and independently reconcile a CPU-only river frontier census."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time
import psutil

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
EXE=ROOT/'target/release/examples/hu_river_frontier_capacity.exe'


def sha(path):
    with path.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()


def run(kind, manifest):
    target=OUT/f'river-frontier-{kind}-result.json'
    log=OUT/f'river-frontier-{kind}.log'
    assert not target.exists() and not log.exists()
    assert psutil.virtual_memory().available>40*2**30
    start=time.monotonic();free_min=psutil.virtual_memory().available
    with log.open('wb') as output:
        proc=subprocess.Popen([str(EXE),str(OUT/'bb-context-candidate.json'),str(manifest),str(target)],
            cwd=ROOT,stdout=output,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        while proc.poll() is None:
            free_min=min(free_min,psutil.virtual_memory().available)
            if free_min<20*2**30 or time.monotonic()-start>1200:
                proc.kill();proc.wait();raise RuntimeError('reserve/deadline; no retry')
            time.sleep(1)
    assert proc.returncode==0,log
    return json.loads(target.read_text()),{'seconds':time.monotonic()-start,'minimum_free_host_bytes':free_min,'exit_code':proc.returncode}


def validate(result, prior):
    old={(r['board'],r['preflop_leaf']):r for r in prior['rows']}
    assert len(result['rows'])==len(old)
    for r in result['rows']:
        p=old[(r['board'],r['preflop_leaf'])]
        street=[sum(h['state_bytes'] for h in p['histogram'] if h['depth']==d) for d in range(3)]
        assert r['trunk_state_bytes']==street[:2]
        assert r['river_state_bytes']==street[2]
        assert r['trunk_action_nodes']+r['river_action_nodes']==p['canonical_actions']
        hs=r['histogram'];count=r['river_subgames'];nh=sum(r['full_flop_hand_counts'])
        assert sum(h['subgames'] for h in hs)==count
        assert sum(h['subgames']*h['state_bytes'] for h in hs)==r['river_state_bytes']
        assert sum(h['subgames']*h['action_nodes'] for h in hs)==r['river_action_nodes']
        assert sum(h['subgames'] for h in hs if h['constant_sum_local_subgame'])==r['constant_sum_local_subgames']
        assert r['constant_sum_local_subgames']+r['variable_sum_local_subgames']==count
        assert r['boundary_f64_values_only_bytes']==count*nh*8
        assert r['boundary_f64_values_and_denominators_plus_headers_bytes']==count*(nh*16+64)
        assert r['max_river_state_bytes']==max(h['state_bytes'] for h in hs)
        for h in hs:
            # There is a check/check route, so the smallest matched pot is the
            # root pot. Other terminals can reach the cap; verify reported extrema.
            assert abs(h['min_terminal_rake']-min(0.05*h['starting_pot'],2))<1e-8
            assert h['max_terminal_rake']<=2+1e-8
            assert h['constant_sum_local_subgame']==(abs(h['max_terminal_rake']-h['min_terminal_rake'])<1e-9)
            assert h['tree_nodes']==h['action_nodes']+h['terminals']


def main():
    registration=OUT/'river-frontier-registration.json';review=OUT/'river-frontier-review.json'
    assert not registration.exists() and not review.exists()
    files=[EXE,Path(__file__),ROOT/'crates/solver/examples/hu_river_frontier_capacity.rs',ROOT/'Cargo.lock',ROOT/'crates/solver/Cargo.toml']
    files+=list((ROOT/'crates/solver/src').rglob('*.rs'))+list((ROOT/'crates/solver/src').rglob('*.cu'))
    files+=[OUT/n for n in ['bb-context-candidate.json','capacity-texture-probe.json','capacity-existing112-manifest.json',
        'capacity-existing112-result.json','public-chance-v2-probe-result.json','public-chance-v2-panel-result.json']]
    frozen={str(p.relative_to(ROOT)):sha(p) for p in files}
    record={'inputs':frozen,'created_at_unix':time.time(),'maximum_seconds_per_plan':1200,
        'minimum_free_host_bytes':20*2**30,'no_automatic_retry':True,
        'purpose':'Measure actual canonical river subgames and local rake sums before implementing decomposition',
        'boundary_layout_allowance':'Both players full flop-hand f64 value vector and f64 denominator vector, plus 64-byte record header',
        'no_geometry_or_range_changes':True,'no_cuda_allocation':True}
    with registration.open('x') as f: json.dump(record,f,indent=2)
    probe,probe_stats=run('probe',OUT/'capacity-texture-probe.json')
    validate(probe,json.loads((OUT/'public-chance-v2-probe-result.json').read_text()))
    panel,panel_stats=run('panel',OUT/'capacity-existing112-manifest.json')
    validate(panel,json.loads((OUT/'public-chance-v2-panel-result.json').read_text()))
    for p,h in frozen.items(): assert sha(ROOT/p)==h,p
    rows=panel['rows'];total=lambda key:sum(r[key] for r in rows)
    trunk=sum(sum(r['trunk_state_bytes']) for r in rows)
    boundary=total('boundary_f64_values_and_denominators_plus_headers_bytes')
    retained_host=json.loads((OUT/'capacity-existing112-result.json').read_text())['totals']['host_retained_payload_bytes']
    games=total('river_subgames')
    result={'passed':True,'source_hashes_verified':len(frozen),'registration_sha256':sha(registration),
        'probe_games':len(probe['rows']),'panel_games':len(rows),'river_subgames':games,
        'constant_sum_local_subgames':total('constant_sum_local_subgames'),
        'variable_sum_local_subgames':total('variable_sum_local_subgames'),
        'trunk_state_bytes':trunk,'river_state_bytes':total('river_state_bytes'),
        'boundary_f64_values_only_bytes':total('boundary_f64_values_only_bytes'),
        'boundary_planning_allowance_bytes':boundary,'trunk_plus_boundary_allowance_bytes':trunk+boundary,
        'plus_old_retained_host_payload_bytes':trunk+boundary+retained_host,
        'max_river_state_bytes':max(r['max_river_state_bytes'] for r in rows),
        'selected_largest_river':max(rows,key=lambda r:r['max_river_state_bytes'])['max_river'],
        'optimistic_2000_outer_iterations_hours_by_complete_river_solve_us':{
            str(us):games*2000*us/1e6/3600 for us in [1,10,100,1000]},
        'complete_river_solve_us_for_four_hours_at_2000_outer':4*3600*1e6/(games*2000),
        'runtime_limitations':'Arithmetic only: assumes one full mutual subgame solve per outer iteration, no trunk/transfer/reconstruction cost. Alternating trunk updates may require two. Not measured GPU throughput.',
        'resources':{'probe':probe_stats,'panel':panel_stats},
        'resource_snapshot':{'free_ram_bytes':psutil.virtual_memory().available,'free_disk_bytes':shutil.disk_usage('S:/').free},
        'full_study_admitted':False,'strategic_accuracy_claim':False,'production_modified':False}
    with review.open('x') as f:json.dump(result,f,indent=2)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
