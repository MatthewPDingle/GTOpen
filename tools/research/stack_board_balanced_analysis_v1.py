"""Reporting only: summarize the completed, independently verified comparison."""
from datetime import datetime,timezone
from pathlib import Path
import hashlib,json,math

OUT=Path('T:/Dev/GTOpen/research/preflop-evolution/blind-defense-20260922')
NAME='stack-board-balanced-learning-v1'
LOCK=Path('T:/Dev/GTOpen/research/preflop-evolution/representative-coverage-20260919/running.lock')

def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mean(values):return math.fsum(values)/len(values)
def reduction(before,after):return 1-after/before if before>0 else None

def analyze(reg,result,review):
    assert result['complete'] and result['passed'] and review['passed']
    assert review['all_reported_context_subgroup_board_and_tail_metrics_reconstructed']
    assert not result['production_modified'] and not review['production_modified']
    tests={(r['seed'],r['arm'],r['width'],r['split']):r for r in result['tests']}
    fits={(r['seed'],r['arm'],r['width']):r for r in result['fits']}
    assert len(tests)==16 and len(fits)==8
    contexts={key:{c['stack']:c for c in t['score']['contexts']} for key,t in tests.items()}
    boards={split:sorted((b for b in result['board_records'] if b['split']==split),key=lambda b:b['index']) for split in ('test','stress')}
    primary=[]
    for seed in reg['seeds']:
        by_arm={arm:contexts[(seed,arm,387,'test')] for arm in reg['arms']}
        norm={arm:mean([by_arm[arm][d]['mean_regret_stack_fraction'] for d in reg['heldout_depths']]) for arm in reg['arms']}
        before,after=norm['random'],norm['structured']
        absolute=all(by_arm['structured'][d]['mean_regret_stack_fraction']<=.001 for d in reg['heldout_depths'])
        relative=before>0 and after<=.8*before
        gate=next(g for g in result['diagnostic_gates'] if g['seed']==seed)
        assert gate['passed']==bool(relative and absolute)
        assert abs(gate['baseline']-before)<1e-12 and abs(gate['candidate']-after)<1e-12
        assert gate['passed']==next(g for g in review['diagnostic_gates'] if g['seed']==seed)['passed']
        depths=[]
        for depth in reg['heldout_depths']:
            a,b=(by_arm[arm][depth] for arm in reg['arms'])
            depths.append(dict(stack=depth,random_mean_bb=a['mean_regret_bb'],structured_mean_bb=b['mean_regret_bb'],
                required_maximum_bb=.001*depth,random_p99_bb=a['p99_regret_bb'],structured_p99_bb=b['p99_regret_bb'],
                random_maximum_bb=a['maximum_regret_bb'],structured_maximum_bb=b['maximum_regret_bb']))
        validation={arm:fits[(seed,arm,387)]['selected']['validation']['context_balanced_mean_regret_stack_fraction'] for arm in reg['arms']}
        # Show every partition, including empty cells and adverse differences.
        partitions={}
        for name in ('seats','price_bands','hand_groups'):
            items=[]
            first=by_arm['random'][reg['heldout_depths'][0]][name]
            for i,item in enumerate(first):
                identity={k:item[k] for k in ('name','actor','minimum_equity','maximum_equity') if k in item}
                values={}
                for arm in reg['arms']:
                    pieces=[(by_arm[arm][d],by_arm[arm][d][name][i]) for d in reg['heldout_depths']]
                    values[arm]=dict(rows=sum(v['rows'] for c,v in pieces),contribution_to_equal_depth_normalized_mean=
                        mean([v.get('mean_regret_bb',0)*v['rows']/c['stack']/c['rows'] for c,v in pieces]))
                delta=values['structured']['contribution_to_equal_depth_normalized_mean']-values['random']['contribution_to_equal_depth_normalized_mean']
                items.append(dict(identity=identity,measures=values,structured_minus_random=delta))
            for arm in reg['arms']:
                assert abs(sum(v['measures'][arm]['contribution_to_equal_depth_normalized_mean'] for v in items)-norm[arm])<1e-12
            partitions[name]=items
        primary.append(dict(seed=seed,baseline_normalized_mean=before,candidate_normalized_mean=after,
            relative_reduction=reduction(before,after),relative_gate=relative,absolute_gate=absolute,
            combined_gate=relative and absolute,heldout_depths=depths,validation_means=validation,
            validation_test_direction_disagrees=(validation['structured']<validation['random'])!=(after<before),partitions=partitions))
    assert result['diagnostic_gate_passed']==all(p['combined_gate'] for p in primary)
    diagnostics=[]
    cells=[]
    worst=[]
    for (seed,arm,width,split),t in tests.items():
        cs=contexts[(seed,arm,width,split)]
        diagnostics.append(dict(seed=seed,arm=arm,width=width,split=split,selected_step=t['selected_step'],
            validation_normalized_mean=fits[(seed,arm,width)]['selected']['validation']['context_balanced_mean_regret_stack_fraction'],
            heldout_normalized_mean=mean([cs[d]['mean_regret_stack_fraction'] for d in reg['heldout_depths']]),
            full_context_normalized_mean=t['score']['context_balanced_mean_regret_stack_fraction']))
        assert t['board_keys']==[dict(index=b['index'],canonical_group=b['canonical_group']) for b in boards[split]]
        for depth,c in cs.items():
            assert [b['board_index'] for b in c['per_board']]==list(range(len(boards[split])))
            rows=[]
            for cell in reg['structured_cells']:
                indices=[i for i,b in enumerate(boards[split]) if b['cell']==cell]
                pieces=[c['per_board'][i] for i in indices]
                n=sum(b['rows'] for b in pieces)
                values=dict(boards=len(indices),rows=n,cell=cell)
                if n:
                    values.update(mean_regret_bb=sum(b['mean_regret_bb']*b['rows'] for b in pieces)/n,
                        maximum_regret_bb=max(b['maximum_regret_bb'] for b in pieces))
                rows.append(values)
            assert sum(r['rows'] for r in rows)==c['rows']
            assert abs(sum(r.get('mean_regret_bb',0)*r['rows'] for r in rows)/c['rows']-c['mean_regret_bb'])<1e-10
            cells.append(dict(seed=seed,arm=arm,width=width,split=split,stack=depth,cells=rows))
        if width==387 and arm=='structured':
            scores=[mean([cs[d]['per_board'][i]['mean_regret_stack_fraction'] for d in reg['heldout_depths']]) for i in range(len(boards[split]))]
            worst.append(dict(seed=seed,split=split,boards=[dict(board=boards[split][i]['board'],canonical_group=boards[split][i]['canonical_group'],
                cell=boards[split][i]['cell'],mean_regret_stack_fraction=scores[i]) for i in sorted(range(len(scores)),key=lambda i:scores[i],reverse=True)[:8]]))
    errors={}
    for trial in review['cpu_replayed']:
        for comparison in trial['metric_comparisons']:
            assert comparison['passed'] and not comparison['failures']
            for metric,value in comparison['maximum_absolute_error_by_metric'].items():errors[metric]=max(errors.get(metric,0),value)
    return dict(primary_comparisons=primary,diagnostic_gate_passed=result['diagnostic_gate_passed'],
        all_arm_summaries=diagnostics,board_cell_summaries=cells,worst_structured_model_boards=worst,
        maximum_cpu_cuda_metric_errors=errors,rows_replayed=review['rows_replayed'],verified_files=review['verified_files'],
        main_work_seconds=result['total_work_seconds'],readback_seconds=review['seconds'],
        peak_cuda_allocated_bytes=result['peak_cuda_allocated_bytes'],peak_cuda_reserved_bytes=result['peak_cuda_reserved_bytes'],
        historical_comparison_limit='Fresh boards and seeds differ from prior studies; no paired across-study accuracy claim.',
        independence_limit='Decision rows reuse boards, hands and prices; they are not independent real poker hands.',
        scope='Restricted terminal river Fold/Call versus a uniform legal opponent, not all-street or preflop accuracy.',
        full_preflop_accuracy_qualified=False,new_training=False,new_test_data=False,production_modified=False,promotion=False)

def render(analysis):
    verdict='passed' if analysis['diagnostic_gate_passed'] else 'did not pass'
    text=[f'# Balanced board coverage: the predeclared accuracy test {verdict}',
        '', 'The comparison and independent CPU reconstruction completed. These results',
        'test how well a small model learns a restricted river call-or-fold decision.',
        'They do not yet establish accurate preflop ranges or justify a deployment.',
        '', 'Both training groups contain 1,024 boards. Half are shared original fitting',
        'boards; the added 512 are either random or balanced across 13 visible board',
        'structures. Both input widths and both seeds use the same fixed training',
        'budget. 128 fresh random boards select checkpoints. All eight checkpoint',
        'identities freeze before 128 primary random and 64 separate stress boards',
        'receive labels. There is no post-test tuning.',
        '', '## Primary comparison: structured versus random training, 387 inputs',
        '', '| Seed | Random loss / stack | Structured loss / stack | Reduction | Relative 20% | Absolute target | Combined |',
        '| --- | ---: | ---: | ---: | --- | --- | --- |']
    for p in analysis['primary_comparisons']:
        text.append(f"| {p['seed']} | {p['baseline_normalized_mean']:.5%} | {p['candidate_normalized_mean']:.5%} | {format(p['relative_reduction'],'.2%') if p['relative_reduction'] is not None else 'n/a'} | {'Pass' if p['relative_gate'] else 'Fail'} | {'Pass' if p['absolute_gate'] else 'Fail'} | {'Pass' if p['combined_gate'] else 'Fail'} |")
    text += ['', 'The mean weights 60bb and 150bb equally after dividing loss by starting stack.',
        'The absolute target is 0.001 starting stacks at EACH depth. Loss is per',
        'evaluated terminal decision, not bb/100 or whole-game exploitability.', '',
        '| Seed | Stack | Random mean,bb | Structured mean,bb | Required maximum,bb | Structured p99,bb | Structured worst,bb |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for p in analysis['primary_comparisons']:
        for d in p['heldout_depths']:
            text.append(f"| {p['seed']} | {d['stack']} | {d['random_mean_bb']:.5f} | {d['structured_mean_bb']:.5f} | {d['required_maximum_bb']:.3f} | {d['structured_p99_bb']:.4f} | {d['structured_maximum_bb']:.4f} |")
    text += ['', '## All arms, including the separately reported stress test', '',
        '| Seed | Training boards | Inputs | Test | Selected update | Validation loss/stack | Held-out-depth loss/stack |',
        '| --- | --- | ---: | --- | ---: | ---: | ---: |']
    for r in sorted(analysis['all_arm_summaries'],key=lambda r:(r['seed'],r['split'],r['width'],r['arm'])):
        text.append(f"| {r['seed']} | {r['arm']} | {r['width']} | {r['split']} | {r['selected_step']} | {r['validation_normalized_mean']:.5%} | {r['heldout_normalized_mean']:.5%} |")
    text += ['', 'The stress boards are deliberately unrepresentative of natural frequencies.',
        'Their scores are never averaged into the primary random-test result.',
        'The 362-input arms diagnose the interaction; they cannot replace the',
        'predeclared 387-input comparison after seeing results.', '', '## Adverse evidence and coverage', '']
    for p in analysis['primary_comparisons']:
        text.append(f"Seed {p['seed']}: validation/test direction disagreement: {p['validation_test_direction_disagrees']}.")
        for name,rows in p['partitions'].items():
            worse=[str(r['identity']) for r in rows if r['structured_minus_random']>0]
            empty=[str(r['identity']) for r in rows if not r['measures']['random']['rows']]
            text.append(f"- {name}: worse with structured training: {', '.join(worse) if worse else 'none'}; unsupported: {', '.join(empty) if empty else 'none'}.")
        text.append('')
    text += ['The companion JSON retains every board-cell mean, its sample count, the',
        'worst boards and all partition contributions. Empty cells provide no evidence.',
        'Two seeds and correlated decision rows do not establish a population guarantee.',
        'Prior studies used different fresh boards/seeds; absolute cross-study numbers',
        'must not be described as a matched treatment effect.', '', '## Verification and resources', '',
        f"CPU reconstruction checked {analysis['verified_files']:,} file identities and {analysis['rows_replayed']:,} rows.",
        'It independently rebuilt means, subgroup and per-board statistics, tails,',
        'model selections, suit-group separation and the primary gate outcomes.',
        f"Largest reconstructed context/subgroup/board mean difference: {analysis['maximum_cpu_cuda_metric_errors']['mean_regret_bb']:.8g}bb.",
        f"Main work: {analysis['main_work_seconds']:.1f}s; independent CPU verification: {analysis['readback_seconds']:.1f}s.",
        f"Peak allocated/reserved CUDA memory: {analysis['peak_cuda_allocated_bytes']/1e9:.3f}/{analysis['peak_cuda_reserved_bytes']/1e9:.3f}GB.",
        'These are sequential study timings, not an isolated speed benchmark.',
        'Production 56708 was unchanged. No GitHub push, deployment, subsequent',
        'scientific experiment or broad-goal completion follows from this report.','']
    return '\n'.join(text)

def main():
    assert not LOCK.exists(),'Wait for scientific/readback lock release'
    paths=[OUT/(NAME+suffix+'.json') for suffix in ('-registration','-result','-readback-v1')]
    reg,result,review=map(read,paths)
    assert result['registration_sha256']==sha(paths[0])
    for p in paths[:2]:assert review['inputs'][str(p)]==sha(p)
    analysis=analyze(reg,result,review)
    analysis.update(created_utc=datetime.now(timezone.utc).isoformat(),source_sha256=sha(__file__),inputs={str(p):sha(p) for p in paths})
    dest=OUT/(NAME+'-analysis-v1.json')
    note=OUT/'STACK-BOARD-BALANCED-LEARNING-FINDINGS.md'
    assert not dest.exists() and not note.exists()
    with dest.open('x',encoding='utf-8',newline='\n') as f:json.dump(analysis,f,indent=2);f.write('\n')
    with note.open('x',encoding='utf-8',newline='\n') as f:f.write(render(analysis))
    print(json.dumps(dict(analysis=str(dest),findings=str(note),diagnostic_gate_passed=analysis['diagnostic_gate_passed'])))

if __name__=='__main__':main()
