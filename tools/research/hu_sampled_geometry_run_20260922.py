"""Bounded CPU correctness census for on-demand postflop transitions."""
import hashlib
import json
from pathlib import Path
import subprocess
import time
import psutil

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-geometry-v1'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    reg=OUT/(PREFIX+'-registration.json')
    assert not reg.exists()
    exe=ROOT/'target/release/examples/hu_sampled_geometry_probe.exe'
    context=OUT/'bb-context-candidate.json'
    manifests=[OUT/'capacity-texture-probe.json',OUT/'capacity-existing112-manifest.json']
    inputs=[exe,context,*manifests,Path(__file__),ROOT/'crates/solver/examples/hu_sampled_geometry_probe.rs',
        ROOT/'crates/solver/examples/research_sampled/state.rs',ROOT/'crates/solver/src/tree.rs',
        ROOT/'crates/solver/Cargo.toml',ROOT/'Cargo.lock']
    hashes={str(p.relative_to(ROOT)):sha(p) for p in inputs}
    assert psutil.virtual_memory().available>40*2**30
    registration=dict(inputs=hashes,created_at_unix=time.time(),maximum_seconds_per_run=300,
        minimum_free_ram_bytes=20*2**30,device_allocated=False,
        purpose='Compare lazy transitions/actions/payouts against all legal native public histories on all 112 fixed BB flops and all three continuation branches.',
        no_range_or_menu_reduction=True,no_strategy_allocation=True,no_automatic_retry=True)
    reg.write_text(json.dumps(registration,indent=2)+'\n',encoding='utf-8',newline='\n')
    summaries=[]
    for name,manifest in zip(['probe','panel'],manifests):
        target=OUT/(PREFIX+'-'+name+'-result.json');log=OUT/(PREFIX+'-'+name+'.log')
        assert not target.exists() and not log.exists()
        started=time.monotonic();minimum=psutil.virtual_memory().available
        with log.open('xb') as f:
            proc=subprocess.Popen([str(exe),str(context),str(manifest),str(target)],cwd=ROOT,
                stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            print('Started',name,'PID',proc.pid,flush=True)
            while proc.poll() is None:
                minimum=min(minimum,psutil.virtual_memory().available)
                if minimum<20*2**30 or time.monotonic()-started>300:
                    proc.kill();proc.wait();raise RuntimeError('Resource/deadline stop; retain evidence, no retry.')
                time.sleep(1)
        assert proc.returncode==0,str(log)
        result=json.loads(target.read_text());assert result['passed'] and not result['device_allocated']
        assert result['manifest']==json.loads(manifest.read_text())
        expected={(b['board'],leaf) for b in result['manifest']['boards'] for leaf in [2,5,8]}
        actual={(r['board'],r['preflop_leaf']) for r in result['rows']}
        assert actual==expected and len(result['rows'])==len(expected)
        for r in result['rows']:
            assert r['legal_nodes_checked']==r['actions_checked']+r['chance_checked']+r['terminals_checked']
            assert r['legal_nodes_checked']<=r['native_nodes_including_invalid_repeat_cards']
            assert r['stack_state_bytes_bound']==(r['max_depth']+1)*r['lazy_state_bytes']
        summary=dict(run=name,games=len(result['rows']),seconds=time.monotonic()-started,
            minimum_free_ram_bytes=minimum,legal_nodes_checked=sum(r['legal_nodes_checked'] for r in result['rows']),
            actions_checked=sum(r['actions_checked'] for r in result['rows']),
            terminals_checked=sum(r['terminals_checked'] for r in result['rows']),
            maximum_stack_state_bytes=max(r['stack_state_bytes_bound'] for r in result['rows']),
            maximum_depth=max(r['max_depth'] for r in result['rows']),
            maximum_actions=max(r['max_actions'] for r in result['rows']),result_sha256=sha(target))
        summaries.append(summary);print(json.dumps(summary),flush=True)
    assert all(sha(ROOT/p)==h for p,h in hashes.items())
    result=dict(passed=True,runs=summaries,inputs_verified=len(hashes),registration_sha256=sha(reg),
        production_modified=False,device_allocated=False,poker_trainer_qualified=False,
        limits='Public transition reference only. Stack bound excludes policies, keys, sample batches, evaluator and metadata. No convergence or full-memory-fit claim.')
    (OUT/(PREFIX+'-review.json')).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
