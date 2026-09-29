"""Analyze retained outcomes after a failed readback; no inference or retry."""
import ast,hashlib,json,math
from datetime import datetime,timezone
from pathlib import Path

OUT=Path('T:/Dev/GTOpen/research/preflop-evolution/blind-defense-20260922')
NAME='stack-board-balanced-learning-v1'
def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mean(xs):return math.fsum(xs)/len(xs)

def main():
    rp,mainp,attempt,status=(OUT/(NAME+s+'.json') for s in ('-registration','-result','-readback-attempt','-readback-status'))
    failures=list(OUT.glob(NAME+'-readback-interruption-*.json'));assert len(failures)==1
    failp=failures[0]
    reg,result,error=read(rp),read(mainp),read(failp)
    assert result['complete'] and result['passed'] and not result['diagnostic_gate_passed']
    assert result['registration_sha256']==sha(rp)
    assert read(status)['state']=='terminal_error'
    assert not (OUT/(NAME+'-readback-v1.json')).exists()
    assert not Path('T:/Dev/GTOpen/research/preflop-evolution/representative-coverage-20260919/running.lock').exists()
    assert error['error'].startswith('AssertionError(')
    seed,arm,width,split,stack,comparison=ast.literal_eval(error['error'][len('AssertionError('):-1])
    assert (seed,arm,width,split,stack)==(9297101,'random',362,'test',40.0)
    assert not comparison['passed'] and comparison['failures']
    inputs={str(p):sha(p) for p in (rp,mainp,attempt,status,failp)}
    # Identity inspection only; this is not a second prediction readback.
    for mapping in (reg['inputs'],result['artifacts']):
        for path,digest in mapping.items():
            assert sha(path)==digest,path
            inputs[path]=digest
    assert sha(result['selection']['file'])==result['selection']['sha256']
    fits={(f['seed'],f['arm'],f['width']):f for f in result['fits']}
    for fit in fits.values():
        best=min(fit['checkpoints'],key=lambda c:(c['validation']['context_balanced_mean_regret_stack_fraction'],c['step']))
        assert fit['selected']==best
    tests={(t['seed'],t['arm'],t['width'],t['split']):t for t in result['tests']}
    assert len(tests)==16
    cs={key:{c['stack']:c for c in t['score']['contexts']} for key,t in tests.items()}
    failure_context=cs[(seed,arm,width,split)][stack]
    differences=[]
    for f in comparison['failures']:
        assert f['path'].startswith('per_board[') and f['path'].endswith('].majority_action_error_rate')
        index=int(f['path'].split('[')[1].split(']')[0])
        row=failure_context['per_board'][index]
        denominator=row['decisions_outside_indifference_band']
        before=round(f['original']*denominator);after=round(f['computed']*denominator)
        assert abs(before-f['original']*denominator)<1e-8 and abs(after-f['computed']*denominator)<1e-8
        assert abs(before-after)==1
        differences.append(dict(**f,board_index=index,denominator=denominator,gpu_error_count=before,cpu_error_count=after))
    primary=[];arms=[];partitions=[];cell_rows=[]
    for seed in reg['seeds']:
        a,b=(cs[(seed,arm,387,'test')] for arm in reg['arms'])
        before,after=(mean([group[d]['mean_regret_stack_fraction'] for d in reg['heldout_depths']]) for group in (a,b))
        gate=next(g for g in result['diagnostic_gates'] if g['seed']==seed)
        absolute=all(b[d]['mean_regret_stack_fraction']<=.001 for d in reg['heldout_depths'])
        passed=before>0 and after<=.8*before and absolute
        assert gate['passed']==passed and gate['absolute_gate']==absolute
        assert abs(gate['baseline']-before)<1e-12 and abs(gate['candidate']-after)<1e-12
        primary.append(dict(seed=seed,gpu_recorded_gate=gate,depths=[dict(stack=d,random_mean_bb=a[d]['mean_regret_bb'],
            structured_mean_bb=b[d]['mean_regret_bb'],required_maximum_bb=d*.001,
            random_p99_bb=a[d]['p99_regret_bb'],structured_p99_bb=b[d]['p99_regret_bb'],
            random_maximum_bb=a[d]['maximum_regret_bb'],structured_maximum_bb=b[d]['maximum_regret_bb']) for d in reg['heldout_depths']]))
        for name in ('seats','price_bands','hand_groups'):
            for i,row in enumerate(a[reg['heldout_depths'][0]][name]):
                identity={k:row[k] for k in ('actor','name','minimum_equity','maximum_equity') if k in row}
                v={arm:mean([group[d][name][i].get('mean_regret_bb',0)*group[d][name][i]['rows']/d/group[d]['rows'] for d in reg['heldout_depths']]) for arm,group in zip(reg['arms'],(a,b))}
                partitions.append(dict(seed=seed,partition=name,identity=identity,normalized_loss_contribution=v,
                    structured_minus_random=v['structured']-v['random'],unsupported=not row['rows']))
    for key,t in tests.items():
        seed,arm,width,split=key
        arms.append(dict(seed=seed,arm=arm,width=width,split=split,selected_step=t['selected_step'],
            validation_normalized_mean=fits[(seed,arm,width)]['selected']['validation']['context_balanced_mean_regret_stack_fraction'],
            heldout_normalized_mean=mean([cs[key][d]['mean_regret_stack_fraction'] for d in reg['heldout_depths']])))
        boards=sorted((b for b in result['board_records'] if b['split']==split),key=lambda b:b['index'])
        for d,c in cs[key].items():
            items=[]
            for cell in reg['structured_cells']:
                ids=[i for i,b in enumerate(boards) if b['cell']==cell]
                records=[c['per_board'][i] for i in ids];n=sum(r['rows'] for r in records)
                item=dict(cell=cell,boards=len(ids),rows=n)
                if n:item.update(mean_regret_bb=sum(r['mean_regret_bb']*r['rows'] for r in records)/n,maximum_regret_bb=max(r['maximum_regret_bb'] for r in records))
                items.append(item)
            assert sum(v['rows'] for v in items)==c['rows']
            assert abs(sum(v.get('mean_regret_bb',0)*v['rows'] for v in items)/c['rows']-c['mean_regret_bb'])<1e-10
            cell_rows.append(dict(seed=seed,arm=arm,width=width,split=split,stack=d,cells=items))
    analysis=dict(created_utc=datetime.now(timezone.utc).isoformat(),source_sha256=sha(__file__),inputs=inputs,
        status='Main comparison finished; independent numerical qualification FAILED',
        main_complete=True,independent_readback_passed=False,readback_retried=False,thresholds_changed=False,
        first_preserved_failure=dict(seed=ast.literal_eval(error['error'][len('AssertionError('):-1])[0],arm='random',width=362,split='test',stack=40),
        classification_differences=differences,failed_context_maximum_metric_errors=comparison['maximum_absolute_error_by_metric'],
        failed_context_mean_error_bb=comparison['absolute_errors']['context.mean_regret_bb'],
        primary_gpu_results=primary,all_arm_gpu_summaries=arms,primary_gpu_partitions=partitions,board_cell_gpu_summaries=cell_rows,
        interpretation='Balanced board coverage fails the declared primary GPU gate; complete independent qualification remains unavailable.',
        diagnostic_cause_status='One-row classification differences are proven; exact affected holdings and raw-score cause are not established by retained failure evidence.',
        decision_rows_are_not_independent_samples=True,full_preflop_accuracy_qualified=False,
        new_training=False,new_inference=False,new_test_data=False,production_modified=False,promotion=False,
        main_seconds=result['total_work_seconds'],failed_readback_seconds=read(status)['unix']-read(attempt)['process_created'],
        peak_cuda_allocated_bytes=result['peak_cuda_allocated_bytes'],peak_cuda_reserved_bytes=result['peak_cuda_reserved_bytes'])
    dest=OUT/(NAME+'-terminal-analysis-v1.json');note=OUT/'STACK-BOARD-BALANCED-TERMINAL-FINDINGS.md'
    assert not dest.exists() and not note.exists()
    with dest.open('x',encoding='utf-8',newline='\n') as f:json.dump(analysis,f,indent=2);f.write('\n')
    lines=['# Balanced board coverage did not improve this comparison','',
        'The main GPU comparison completed, but the independent CPU verification',
        'failed its fixed classification tolerance. Treat the numbers below as',
        'retained GPU results, not a fully independently qualified improvement.',
        'Nothing is promoted, deployed, retrained or retried. The original failed',
        'verification and its thresholds remain unchanged.','',
        '## Main result','',
        'Both training sets used 1,024 boards, the same eight fixed training runs,',
        'and shared validation. The primary comparison is structured versus random',
        'training boards with 387 inputs. Stress boards and the 362-input diagnostic',
        'remain separate. All models were selected before final-test labels existed.','',
        '| Seed | Random loss / stack | Structured loss / stack | Change in error | Required result |',
        '| --- | ---: | ---: | ---: | --- |']
    for p in primary:
        g=p['gpu_recorded_gate'];lines.append(f"| {p['seed']} | {g['baseline']:.5%} | {g['candidate']:.5%} | {-g['relative_reduction']:+.2%} | Fail |")
    lines += ['', 'Lower loss is better. The required reduction was at least 20% in BOTH seeds,',
        'plus mean loss at most 0.001 starting stacks at EACH of 60bb and 150bb.',
        'Structured training did not clear either combined gate. The slight increase',
        'in the first seed and substantial increase in the second do not support',
        'adopting this board-balancing recipe. This is a finite two-seed comparison,',
        'not proof that every structured sampling approach is ineffective.','',
        '| Seed | Stack | Random mean, bb | Structured mean, bb | Required maximum, bb | Structured p99, bb | Structured maximum, bb |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for p in primary:
        for d in p['depths']:lines.append(f"| {p['seed']} | {d['stack']} | {d['random_mean_bb']:.5f} | {d['structured_mean_bb']:.5f} | {d['required_maximum_bb']:.3f} | {d['structured_p99_bb']:.4f} | {d['structured_maximum_bb']:.4f} |")
    lines += ['', 'Loss here is per evaluated terminal river decision, not bb/100 or whole-game',
        'exploitability. The opponent is uniform over legal hands. These diagnostic',
        'weights are not an all-street policy and do not establish preflop accuracy.','',
        '## Why independent verification failed','',
        'The first preserved failure is seed 9297101, random training, 362 inputs,',
        'random test boards, 40bb. Two board-level majority-action error rates',
        'differed by one classified decision each:','',
        '| Board index | Eligible decisions | GPU errors | CPU errors | Rate difference | Fixed limit |',
        '| --- | ---: | ---: | ---: | ---: | ---: |']
    for d in differences:lines.append(f"| {d['board_index']} | {d['denominator']} | {d['gpu_error_count']} | {d['cpu_error_count']} | {d['absolute_error']:.8f} | {d['tolerance']:.5f} |")
    lines += ['', f"The context-wide mean loss differed by {analysis['failed_context_mean_error_bb']:.8g}bb.",
        'All other recorded metric checks in this failing context stayed within their',
        'fixed tolerances, including board-level cash means and tails. Nevertheless,',
        'the full verification did not pass and remaining comparisons were not all',
        'completed. Do not label the entire study independently verified.',
        'The count difference is proven; the exact affected holdings/raw scores were',
        'not retained in this failure and their numerical cause remains unconfirmed.',
        'No thresholds are relaxed after observing the outcome.','',
        '## Diagnostic arms and stress test','',
        '| Seed | Training | Inputs | Test | Selected update | Validation loss/stack | Held-out-depth loss/stack |',
        '| --- | --- | ---: | --- | ---: | ---: | ---: |']
    for r in sorted(arms,key=lambda r:(r['seed'],r['split'],r['width'],r['arm'])):lines.append(f"| {r['seed']} | {r['arm']} | {r['width']} | {r['split']} | {r['selected_step']} | {r['validation_normalized_mean']:.5%} | {r['heldout_normalized_mean']:.5%} |")
    lines += ['', 'The companion JSON preserves every hand/actor/price contribution and every',
        'board-cell count/mean, including empty cells and adverse results. It never',
        'combines deliberately rare stress boards into the natural-frequency test.',
        'Fresh boards and seeds differ from prior studies, so cross-study reductions',
        'must not be claimed as a matched effect of adding more random boards.','',
        '## Next recommendation','',
        'Keep natural-frequency random board sampling as the research baseline.',
        'Do not spend another long run extending this balanced recipe unchanged.',
        'First propose a small, separately registered numerical diagnostic on frozen',
        'weights that records the exact decisions and probabilities near the 50%',
        'classification boundary. It should explain this verification failure without',
        'relabeling the failed attempt as a success. No such diagnostic is launched here.',
        'Then choose the next accuracy study using the retained error breakdown, with',
        'fresh evaluation boards and unchanged separation from any tuning data.',
        'Action-conditioned opponent ranges and multiple decisions remain essential',
        'before these results can improve practical preflop ranges.','',
        '## Resources and disposition','',
        f"Main work took {analysis['main_seconds']:.1f}s; failed CPU verification ended after {analysis['failed_readback_seconds']:.1f}s.",
        f"Peak CUDA allocation/reservation was {analysis['peak_cuda_allocated_bytes']/1e9:.3f}/{analysis['peak_cuda_reserved_bytes']/1e9:.3f}GB.",
        'Both processes exited and the research lock was released. All failures and',
        'scientific artifacts remain intact. Production 56708 is unchanged.',
        'No GitHub push, deployment or claim of broad preflop-goal completion.','']
    with note.open('x',encoding='utf-8',newline='\n') as f:f.write('\n'.join(lines))
    print(json.dumps(dict(analysis=str(dest),findings=str(note),independent_readback_passed=False,classification_differences=differences)))

if __name__=='__main__':main()
