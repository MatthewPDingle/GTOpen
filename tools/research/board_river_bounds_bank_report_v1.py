"""Qualification readback; equivalence is not evidence of improved poker EV."""
import hashlib
import json
from pathlib import Path
import numpy as np

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='board-river-bounds-bank-v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())


def main():
    rp=OUT/(PREFIX+'-registration.json');result_path=OUT/(PREFIX+'-result.json')
    reg=read(rp);result=read(result_path)
    assert result['passed'] and result['complete'] and result['registration_sha256']==sha(rp)
    assert reg['query']['observations']==14547 and reg['query']['physical_deals']==32
    assert reg['chunks']==[1,8,78]
    assert not any(result[k] for k in ('new_deals','training_performed','target_loss_scored','payoffs_scored','accuracy_qualified','production_modified'))
    for p,h in reg['inputs'].items():assert sha(p)==h,p
    cp=OUT/(PREFIX+'-control.json');control=read(cp)
    assert control['passed'] and result['synthetic_control_sha256']==sha(cp)
    rows=result['banks'];assert len(rows)==2
    maximum=0.;timings=[]
    for row,identity in zip(rows,reg['banks']):
        assert row['arm']==identity['arm'] and row['models']==78
        assert [r['generation'] for r in identity['model_references']]==list(range(78))
        assert identity['unplayed_excluded']['generation']==78
        names={r['label'] for r in row['controls']}
        expected={'original_cpu_vs_disabled_adapter','original_cpu_vs_original_cuda',
            'cuda_chunk_invariance_8','cuda_chunk_invariance_78'}
        expected|={f'cuda_{kind}_chunk_{chunk}' for kind in ('disabled','bounded') for chunk in (1,8,78)}
        assert names==expected and len(row['controls'])==len(expected)
        assert max(x['maximum_policy_difference'] for x in row['controls'])<=1e-9
        maximum=max(maximum,max(x['maximum_policy_difference'] for x in row['controls']))
        c=row['changes'];assert sum(c[n]['queries'] for n in ('preflop','flop','turn','river'))==14547
        assert sum(c[n]['changed_queries'] for n in ('preflop','flop','turn','river'))==c['all']['changed_queries']
        for n in ('preflop','flop','turn'):
            assert c[n]['changed_queries']==0 and c[n]['maximum_query_tv']==0 and c[n]['maximum_reach_change']==0
        for n,v in c.items():
            assert 0<=v['changed_queries']<=v['queries']
            if v['queries']:assert 0<=v['mean_query_tv']<=v['maximum_query_tv']<=1+1e-12
        assert all(len(row['timing_seconds'][k])==3 and min(row['timing_seconds'][k])>0 for k in ('baseline','bounded'))
        base=float(np.median(row['timing_seconds']['baseline']));bounded=float(np.median(row['timing_seconds']['bounded']))
        assert abs(bounded/base-row['timing_median_ratio'])<1e-12
        timings.append(dict(arm=row['arm'],baseline_median=base,bounded_median=bounded,ratio=bounded/base))
    assert set(rows[0]['rejected'])=={'missing_model','reordered_models','invalid_scale','wrong_game','wrong_menu','wrong_actor','wrong_phase','missing_ancestor','self_ancestor'}
    lines=['# River bounds pass complete-bank numerical qualification','',
        f"Both complete 78-model histories passed CPU/CUDA and chunking comparisons on **14,547 queries from 32 already archived hands**. "
        f"Maximum observed probability discrepancy was **{maximum:.3g}**. No target loss or payoff was scored, and no new deals or training were performed. "
        'This qualifies the implementation for a separately registered strategy evaluation, not for production or a claim of better preflop ranges.','',
        '## What is preserved','',
        'Each bank contains played generations 0-77, weighted 1-78. The unplayed generation 78 remains excluded. '
        'Direct preflop tables and the board-root/BTN overrides are preserved. Every network uses its own saved player-specific scale for the correction. '
        'Model probabilities are then averaged using that model\'s corrected own-action reach, in the original generation order.','',
        'Preflop, flop and turn probabilities and averaging denominators stayed identical within each backend. '
        'CPU and CUDA agreed with projection enabled and disabled, for chunks of 1, 8 and all 78 models. '
        'The original typed CPU and GPU evaluators supplied baseline references. Hand-calculated controls covered unequal scales, upper/lower violations, '
        'negative scores, exact ties, nonuniform generation weights, direct-table overrides, zero reach, and a descendant changed only through its earlier action. '
        'Malformed game, model membership, scale, actor, phase, menu and ancestor inputs were rejected.','',
        '## Strategy changes on the fixed query archive','',
        '| Bank | Query category | Queries | Changed | Mean TV | Maximum TV |','|---|---|---:|---:|---:|---:|']
    for row in rows:
        for name in ('all','preflop','flop','turn','river','eligible','unprojected_reach_descendants'):
            v=row['changes'][name]
            mean='—' if v['mean_query_tv'] is None else f"{v['mean_query_tv']:.6f}"
            high='—' if v['maximum_query_tv'] is None else f"{v['maximum_query_tv']:.6f}"
            lines.append(f"| {row['arm']} | {name} | {v['queries']:,} | {v['changed_queries']:,} | {mean} | {high} |")
    lines += ['', 'TV is half the summed absolute differences between action probabilities. These figures give every archived query equal weight; '
        'they are not dealt-hand frequencies, game reach, or estimates of EV gain. Query categories overlap: eligible decisions and descendants are subsets of river. '
        'An unprojected descendant can change because an earlier corrected action changes its relative model weights.','',
        '## Cost of the correction','',
        '| Bank | Baseline median, seconds | Bounded median, seconds | Ratio |','|---|---:|---:|---:|']
    for t in timings:
        lines.append(f"| {t['arm']} | {t['baseline_median']:.4f} | {t['bounded_median']:.4f} | {t['ratio']:.3f}× |")
    lines += ['', 'Three warmed, paired repetitions per bank used identical prepared queries, cached tables and model chunk size 8. '
        'This isolates the inference cost of projection; it is not a production solve-speed benchmark. Initialization and the original CPU reference are separately recorded in the result JSON.','',
        f"End-to-end qualification took **{result['seconds']/60:.2f} minutes**, including global storage admission and audited model loading. "
        f"Peak own CUDA allocation was **{max(r['peak_cuda_allocated_bytes'] for r in rows)/1e9:.3f} GB**. "
        'The 800 GB allocated-storage cap, shared locks, production checks and light-desktop GPU sharing rule remained in force.','',
        '## Next decision','',
        'Compare unchanged and bounded complete policies on newly registered physical deals, with both player roles, paired payoff differences and fixed stopping. '
        'Keep preflop tables and entry ranges fixed for this inference-only comparison. Do not claim a retrained equilibrium, broad stack/position coverage, '
        'or a solved preflop model from this numerical qualification. A useful policy result would motivate a separate coadaptation experiment.','']
    report=OUT/'BOARD-RIVER-BOUNDS-BANK-FINDINGS.md';assert not report.exists();report.write_text('\n'.join(lines),encoding='utf-8')
    analysis=dict(inputs={str(Path(__file__)):sha(__file__),str(rp):sha(rp),str(result_path):sha(result_path)},
        maximum_policy_discrepancy=maximum,timings=timings,report_sha256=sha(report),
        qualifies_for_separate_policy_evaluation=True,better_poker_policy_demonstrated=False,production_adoption=False)
    with (OUT/(PREFIX+'-analysis.json')).open('x',encoding='utf-8') as f:json.dump(analysis,f,separators=(',',':'),allow_nan=False)
    print(json.dumps(dict(report=str(report),maximum_policy_discrepancy=maximum,timings=timings)))


if __name__=='__main__':main()
