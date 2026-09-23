"""Replay fixed-budget visible-feature trial; no neural fitting or inference rerun."""
import argparse
import json
from pathlib import Path
import time
import sys
import numpy as np
import psutil
from reboot_research_idle_v1 import idle
from sampled_visible_hybrid_checkpoint_v1 import read_object, model_document, restore_checkpoint, FEATURE_SPEC
from sampled_physical_deals_v1 import PhysicalDeals, digest
from sampled_physical_reservoir_v1 import PhysicalReservoir
from sampled_allin_protocol_v3 import AllinCache, ingest, ESTIMATOR
from sampled_physical_preflop_table_v1 import build
from sampled_physical_root_evaluation_v1 import ROOT, sha, save

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-visible-hybrid-resume-pilot-v1'


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--prefix',type=int); parser.add_argument('--control',action='store_true'); args = parser.parse_args()
    started = time.monotonic()
    def guard():
        assert time.monotonic()-started < 1200 and idle(), 'Audit deadline or production activity'
        assert psutil.virtual_memory().available >= 20_000_000_000
    guard()
    regpath = OUT/f'{PREFIX}-registration.json'; reg = json.loads(regpath.read_text()); cfg = reg['config']
    for path,h in reg['inputs'].items(): assert sha(ROOT/path) == h, path
    assert cfg['architecture'] == [302,64,64,4] and cfg['representation'] == FEATURE_SPEC
    assert not reg['control_only'] and cfg['max_iterations'] == 78
    from visible_hybrid_resume_support_v1 import verify_lineage
    verify_lineage(reg)
    store = Path(reg['store']); objects = store/'checkpoint-objects'
    baseline_regpath = OUT/'sampled-physical-hybrid-allin-control-v1-registration.json'
    baseline_reviewpath = OUT/'sampled-physical-hybrid-allin-control-v1-independent-review.json'
    baseline_review = json.loads(baseline_reviewpath.read_text())
    assert baseline_review['passed'] and baseline_review['terminal_complete']
    assert baseline_review['source_registration_sha256'] == sha(baseline_regpath)
    baseline_store = Path(json.loads(baseline_regpath.read_text())['store'])
    baseline_metricpath = baseline_store/'iteration-0001'/'metrics.json'
    assert sha(baseline_metricpath) == baseline_review['steps'][0]['metrics_sha256']
    baseline_metric = json.loads(baseline_metricpath.read_text())
    completed = args.prefix if args.prefix is not None else cfg['max_iterations']
    assert type(completed) is int and 1 <= completed <= cfg['max_iterations']
    assert completed <= json.loads((store/'latest.json').read_text())['completed_iterations']
    evidence = {str(regpath):sha(regpath),str(Path(__file__)):sha(Path(__file__))}
    terminal = args.prefix is None
    if terminal:
        for process in psutil.process_iter(['pid','name','cmdline']):
            if (process.info['name'] or '').lower().startswith('python'):
                assert not any(Path(a).name == 'hu_visible_hybrid_resume_pilot_20260923.py'
                    for a in (process.info['cmdline'] or [])[1:]), ('Trainer still live',process.info['pid'])
        paths = [OUT/f'{PREFIX}-{s}.json' for s in ('status','resources','result','admission')]
        stat,resources,result,admission = [json.loads(p.read_text()) for p in paths]
        assert stat['state'] == 'complete' and stat['exit_code'] == 0 and stat['error'] is None
        assert result['completed_iterations'] == completed and result['terminal']
        assert admission['registration_sha256'] == sha(regpath)
        assert 0 < stat['execution_seconds'] < reg['maximum_seconds']
        assert stat['execution_seconds'] + reg['prior_execution_seconds'] < 10800
        assert resources and all(a['seconds'] < b['seconds'] for a,b in zip(resources,resources[1:]))
        assert all(r['free_host_bytes'] >= reg['host_reserve_bytes'] and r['free_gpu_bytes'] >= reg['gpu_reserve_bytes']
            and r['free_disk_bytes'] >= reg['disk_reserve_bytes'] and r['store_bytes'] <= reg['maximum_store_bytes'] for r in resources)
        evidence.update({str(p):sha(p) for p in paths})
    context = (OUT/'bb-context-candidate.json').read_text()
    cache = AllinCache.from_review(OUT/'sampled-physical-allin-training-cache-v1-independent-review.json')
    assert cache.sha256 == cfg['allin_cache_sha256'] and cfg['terminal_estimator'] == ESTIMATOR
    sampler = PhysicalDeals(context,mode='full_deck',seed=cfg['sampler_seed'])
    rng = np.random.Generator(np.random.PCG64(cfg['action_seed']))
    reservoirs = [PhysicalReservoir(cfg['reservoir_capacity'],p,cfg['reservoir_seeds'][p],context) for p in (0,1)]
    previous = json.loads(read_object(objects,json.loads((store/'checkpoint-0000.json').read_text())))
    assert previous['completed_iterations'] == 0 and previous['played_bank'] == []
    assert previous['sampler'] == sampler.checkpoint() and previous['action_rng'] == rng.bit_generator.state
    expected_config = previous['config']; model_document(objects,previous['next_model'],context_source=context)
    for k,v in cfg.items(): assert expected_config[k] == v,k
    rows = []; traversals = 0; total_covered = [0,0]; nonuniform_covered = [0,0]
    for iteration in range(1,completed+1):
        guard(); folder = store/f'iteration-{iteration:04d}'; metricpath = folder/'metrics.json'
        metric = json.loads(metricpath.read_text())
        assert metric['iteration'] == iteration and metric['deals'] == cfg['deals_per_iteration']
        assert len(metric['subbatches']) == cfg['subbatches_per_iteration']
        counts = [0,0]; observations = 0
        used_model = model_document(objects,previous['next_model'],context_source=context)
        tables = [None if t is None else {(int(r['hi']),int(r['lo'])):r for r in t['rows']}
                  for t in used_model['preflop_tables']]
        for chunk,record in enumerate(metric['subbatches']):
            guard(); part = folder/f'batch-{chunk:02d}'
            assert record['chunk'] == chunk and record['used_model'] == previous['next_model']
            assert set(record['artifacts']) == {'batch.json','queries.json','policies.json','updates.json'}
            for name,h in record['artifacts'].items(): assert sha(part/name) == h, str(part/name)
            batch = json.loads((part/'batch.json').read_text())
            assert batch['batch_id'] == f'sampled-visible-hybrid-trial-pilot-v1-iteration-{iteration}-batch-{chunk}'
            assert batch['seed'] == int(rng.integers(0,2**63))
            assert batch['format'] == 3 and batch['query_limit'] == cfg['query_limit']
            assert batch['deals'] == sampler.sample(cfg['deals_per_subbatch'])['deals']
            queries = json.loads((part/'queries.json').read_text()); updates = json.loads((part/'updates.json').read_text())
            assert queries['context_source'] == context and queries['batch_source'] == (part/'batch.json').read_text()
            assert len(queries['observations']) == record['observations']
            policy = json.loads((part/'policies.json').read_text())
            assert policy['format'] == 3 and policy['terminal_estimator'] == ESTIMATOR and policy['context_source'] == context and policy['batch_source'] == queries['batch_source']
            assert len(policy['policies']) == len(queries['observations'])
            if iteration == 1:
                # Before any fitting, zero appended columns must preserve the
                # old model's complete initial trajectory and numerical targets.
                baseline_part = baseline_store/'iteration-0001'/f'batch-{chunk:02d}'
                for name,h in baseline_metric['subbatches'][chunk]['artifacts'].items():
                    assert sha(baseline_part/name) == h
                old_batch = json.loads((baseline_part/'batch.json').read_text())
                assert batch['deals'] == old_batch['deals'] and batch['seed'] == old_batch['seed']
                assert queries['observations'] == json.loads((baseline_part/'queries.json').read_text())['observations']
                assert policy['policies'] == json.loads((baseline_part/'policies.json').read_text())['policies']
                assert updates['records'] == json.loads((baseline_part/'updates.json').read_text())['records']
            covered = [0,0]
            for o,p in zip(queries['observations'],policy['policies']):
                assert all(o[k] == p[k] for k in ('hi','lo','actor','n'))
                actual = np.asarray(p['probabilities']); assert actual.shape == (4,)
                assert np.isfinite(actual).all() and (actual >= 0).all() and abs(actual.sum()-1) < 1e-12 and not np.any(actual[o['n']:])
                table = tables[o['actor']]; key = (int(o['hi']),int(o['lo']))
                if o['phase'] == 0 and table is not None and key in table:
                    r = table[key]; values = np.asarray(r['mean_regret'])
                    expected = np.maximum(values,0.)
                    if expected.sum() > 0: expected /= expected.sum()
                    else:
                        expected[:] = 0.; expected[int(np.argmax(values[:o['n']]))] = 1.
                    assert np.array_equal(actual,expected), (iteration,chunk,key)
                    covered[o['actor']] += 1
                    if np.max(actual[:o['n']])-np.min(actual[:o['n']]) > 1e-8: nonuniform_covered[o['actor']] += 1
            assert covered == record['preflop_table_queries']
            total_covered = [a+b for a,b in zip(total_covered,covered)]
            cache.check_batch(batch)
            assert updates['verified_query_lookup_traversals'] == updates['verified_cashflow_traversals'] == 2*cfg['deals_per_subbatch']
            assert updates['maximum_query_lookup_error'] == 0 and updates['maximum_cashflow_error'] < 1e-9
            inserted = ingest(queries,updates,reservoirs,iteration,cache)
            assert inserted == record['advantage_records']
            counts = [a+b for a,b in zip(counts,inserted)]; observations += len(queries['observations'])
            traversals += updates['verified_cashflow_traversals']
        assert counts == metric['advantage_records'] and observations == metric['observations']
        assert [r.summary() for r in reservoirs] == metric['reservoirs']
        ref = json.loads((store/f'checkpoint-{iteration:04d}.json').read_text()); assert ref == metric['checkpoint']
        checkpoint = json.loads(read_object(objects,ref))
        assert checkpoint['completed_iterations'] == iteration and checkpoint['context_sha256'] == digest(context)
        assert checkpoint['config'] == expected_config and checkpoint['sampler'] == sampler.checkpoint()
        assert checkpoint['action_rng'] == rng.bit_generator.state
        assert checkpoint['played_bank'] == [*previous['played_bank'],previous['next_model']]
        model = model_document(objects,checkpoint['next_model'],context_source=context); assert model['generation'] == iteration
        assert model['preflop_tables'] == [build(r,context) for r in reservoirs]
        assert len(metric['fits']) == 2
        for player,fit in enumerate(metric['fits']):
            assert fit['representation'] == FEATURE_SPEC
            assert fit['player'] == player and fit['device'] == 'cuda' and fit['prepared_once']
            assert fit['steps'] == cfg['fit_steps'] and fit['chunk_size'] == cfg['chunk_size']
            assert fit['seed'] == cfg['fit_seed_base']+iteration*200003+player
            assert fit['learning_rate'] == cfg['learning_rate'] and fit['retained_examples'] == reservoirs[player].size
            assert fit['advantage_scale'] == model['advantage_scales'][player]
        for reference in checkpoint['reservoirs']: read_object(objects,reference)
        rows.append(dict(iteration=iteration,metrics_sha256=sha(metricpath),checkpoint=ref,observations=observations))
        previous = checkpoint
    restored = restore_checkpoint(objects,ref,context_source=context,config=expected_config)
    inherited_review = json.loads(Path(reg['prefix_review']).read_text())
    assert rows[:min(completed,48)] == inherited_review['steps'][:min(completed,48)]
    imported = json.loads((store/'imported-prefix.json').read_text())
    assert imported['completed_iterations'] == 48 and imported['checkpoint'] == reg['resume_checkpoint']
    for relative, expected_hash in imported['immutable_files'].items():
        guard()
        assert sha(store/relative) == expected_hash, relative
    evidence[str(store/'imported-prefix.json')] = sha(store/'imported-prefix.json')
    for replayed,saved in zip(reservoirs,restored['reservoirs']):
        assert replayed.summary() == saved.summary() and replayed.rng.bit_generator.state == saved.rng.bit_generator.state
        for name in ('keys','active','arity','values','iterations'):
            assert np.array_equal(getattr(replayed,name)[:replayed.size],getattr(saved,name)[:saved.size]),name
    assert restored['sampler'].checkpoint() == sampler.checkpoint() and restored['action_rng'].bit_generator.state == rng.bit_generator.state
    if terminal:
        latest = json.loads((store/'latest.json').read_text())
        assert latest['checkpoint'] == ref == result['checkpoint'] and latest['completed_iterations'] == completed
        assert len(result['steps']) == completed
        for i,step in enumerate(result['steps'],1): assert step == json.loads((store/f'iteration-{i:04d}'/'metrics.json').read_text())
    for p,h in evidence.items(): assert sha(p) == h,p
    for p,h in reg['inputs'].items(): assert sha(ROOT/p) == h,p
    guard()
    if completed >= 4:
        assert min(total_covered) > 0 and min(nonuniform_covered) > 0, 'Must exercise learned tables for both players'
    destination = OUT/(f'{PREFIX}-independent-review.json' if terminal else f'{PREFIX}-prefix-{completed:04d}-review.json')
    document = dict(passed=True,terminal_complete=terminal,completed_iterations=completed,checkpoint=ref,
        registered_inputs_verified=len(reg['inputs']),covered_table_rows=total_covered,nonuniform_table_rows=nonuniform_covered,fresh_deals_replayed=sampler.draws,verified_traversals=traversals,
        retained_records=[r.size for r in reservoirs],seen_records=[r.seen for r in reservoirs],
        final_reservoir_arrays_and_rng_exact=True,all_generated_tables_reconstructed=True,all_supported_preflop_policy_rows_exact=True,all_subbatches_use_same_frozen_generation=True,
        played_generations=list(range(completed)),unused_next_generation=completed,
        source_registration_sha256=sha(regpath),evidence_hashes=evidence,steps=rows,seconds=time.monotonic()-started,
        initial_uniform_trajectory_and_targets_match_269_input_control=True,
        control_only=False,accuracy_qualified=False,production_modified=False,
        scope='Replayed all dealt cards, action RNGs and reservoir insertions. Verified native reference evidence, immutable artifact hashes and frozen model-bank progression. Reconstructed each preflop table and checked every supported preflop policy row. Neural fitting/inference not rerun. A prefix review does not admit the candidate for evaluation.')
    save(destination,document)
    print(json.dumps({k:v for k,v in document.items() if k not in ('steps','evidence_hashes','played_generations')}))


if __name__ == '__main__': main()
