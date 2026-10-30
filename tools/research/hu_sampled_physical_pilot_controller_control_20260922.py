"""Exercise the real pilot worker with tiny CPU settings before queueing CUDA."""
import json
from pathlib import Path
import time
import numpy as np
import hu_sampled_physical_pilot_20260922 as pilot
from sampled_physical_checkpoint_v1 import restore_checkpoint, model_document


def main():
    assert pilot.idle()
    pilot.PREFIX='sampled-physical-pilot-controller-v1'
    pilot.STORE=Path('S:/GTOpen-research')/pilot.PREFIX
    assert not pilot.STORE.exists()
    context=pilot.OUT/'bb-context-candidate.json'
    source=Path(pilot.__file__)
    dependencies=[Path(__file__),source,context,pilot.ROOT/'target/release/examples/hu_sampled_batch_bridge_v2.exe']
    dependencies += [pilot.ROOT/'tools/research'/n for n in (
        'sampled_batch_model_v1.py','sampled_batch_protocol_v2.py','sampled_physical_deals_v1.py',
        'sampled_physical_reservoir_v1.py','sampled_physical_fit_v1.py','sampled_physical_checkpoint_v1.py',
        'storage_strategic_common_prior_20260920.py','hu_sampled_neural_residual_diagnostic_20260922.py',
        'loopback_research_validation.py')]
    dependencies += [pilot.ROOT/'crates/solver/examples'/n for n in ('hu_sampled_batch_bridge_v2.rs',
        'research_sampled/state.rs','research_sampled/poker_reference_v1.rs','research_sampled/observation_v1.rs',
        'research_sampled/policy_walk_v1.rs','research_sampled/batch_queries_v1.rs')]
    reg=dict(inputs={p.relative_to(pilot.ROOT).as_posix():pilot.sha(p) for p in dependencies},
        maximum_seconds=180,host_reserve_bytes=20_000_000_000,disk_reserve_bytes=40_000_000_000,
        config=dict(max_iterations=2,deals_per_iteration=2,query_limit=100000,fit_steps=8,
            fit_seed_base=29301,reservoir_capacity=32,sampler_seed=27301,action_seed=28301,
            reservoir_seeds=[28302,28303],chance='full_deck',device='cpu',threads=2,tf32=False,
            architecture=[269,64,64,4],chunk_size=31,learning_rate=.003,iteration_weights='equal'),
        scope='Real pilot worker orchestration with two tiny CPU iterations. No CUDA, resource-scale, strength, or queue-lifecycle qualification.',
        production_modified=False)
    regpath=pilot.output('registration');pilot.save(regpath,reg);started=time.monotonic()
    pilot.worker(reg)
    result=json.loads(pilot.output('result').read_text());assert result['terminal'] and result['completed_iterations']==2
    pointer=json.loads((pilot.STORE/'latest.json').read_text());assert pointer['completed_iterations']==2
    assert pointer['checkpoint']==result['checkpoint']
    restored=restore_checkpoint(pilot.STORE/'checkpoint-objects',pointer['checkpoint'],context_source=context.read_text(),config=pointer['config'])
    assert restored['completed_iterations']==2
    assert [p['generation'] for p in restored['played_bank']]==[0,1] and restored['next_model']['generation']==2
    assert restored['sampler'].checkpoint()['draws']==4
    artifacts={}
    for iteration in (1,2):
        folder=pilot.STORE/f'iteration-{iteration:04d}';row=json.loads((folder/'metrics.json').read_text())
        for name,digest in row['artifacts'].items():assert pilot.sha(folder/name)==digest
        updates=json.loads((folder/'updates.json').read_text())
        assert updates['verified_traversals']==4 and updates['maximum_reference_error']==0
        artifacts[str(folder/'metrics.json')]=pilot.sha(folder/'metrics.json')
    for r in restored['reservoirs']:
        assert 0<r.size<=32 and np.max(r.iterations[:r.size])<=2
    for reference in [*restored['played_bank'],restored['next_model']]:model_document(pilot.STORE/'checkpoint-objects',reference)
    for name,digest in reg['inputs'].items():assert pilot.sha(pilot.ROOT/name)==digest,name
    review=dict(passed=True,inputs_verified=len(reg['inputs']),registration_sha256=pilot.sha(regpath),
        result_sha256=pilot.sha(pilot.output('result')),completed_iterations=2,verified_traversals=8,
        checkpoint_restore_verified=True,unused_next_model_excluded=True,store=str(pilot.STORE),artifacts=artifacts,
        seconds=time.monotonic()-started,no_gpu=True,physical_poker_convergence_qualified=False,
        scope=reg['scope'],production_modified=False)
    pilot.save(pilot.output('review'),review);print(json.dumps(review))


if __name__=='__main__':main()
