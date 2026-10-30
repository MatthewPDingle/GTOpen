"""Read-only analysis of all saved candidate fit metrics; no model fitting."""
import hashlib
import json
import math
from pathlib import Path
import statistics

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())


def main():
    source=OUT/'board-root-matched-continuation-v1-result.json'
    registration=OUT/'board-root-matched-continuation-v1-registration.json'
    result,reg=read(source),read(registration)
    assert result['passed'] and result['training_complete'] and result['registration_sha256'] == sha(registration)
    objective=ROOT/'tools/research/weighted_visible_objective_v1.py'
    assert sha(objective) == reg['inputs'][str(objective)]
    inputs={str(p):sha(p) for p in (source,registration,objective,Path(__file__))}
    all_rows=[];windows=[]
    for arm in result['arms']:
        progress_path=Path(arm['progress_path']);assert sha(progress_path) == arm['progress_sha256']
        inputs[str(progress_path)]=sha(progress_path);progress=read(progress_path)
        assert progress['completed'] == 78 and len(progress['generations']) == 78
        rows=[]
        for generation,ref in enumerate(progress['generations'],1):
            path=Path(ref['path']);assert sha(path) == ref['sha256'];inputs[str(path)]=ref['sha256']
            metrics=read(path);assert metrics['iteration'] == generation
            assert len(metrics['fits']) == len(metrics['reservoirs']) == 2
            for player,fit in enumerate(metrics['fits']):
                reservoir=metrics['reservoirs'][player]
                assert fit['player'] == reservoir['player'] == player
                assert fit['advantage_scale'] > .01
                assert fit['retained_examples'] == reservoir['retained']
                # scale^2 = sum(w * all four squared targets)/(4*sum(w));
                # illegal targets are zero. Subtract grouped within-key variance.
                zero=4*reservoir['retained_weight']/fit['weighted_legal_target_mass']-fit['normalized_within_observation_variance']
                after=fit['normalized_grouped_loss_after'];before=fit['normalized_grouped_loss_before']
                assert math.isfinite(zero) and zero > 0 and min(after,before) >= 0
                row=dict(arm=arm['arm'],generation=generation,player=player,
                    played_in_evaluation=generation <= 77,zero_prediction_grouped_loss=zero,
                    fitted_grouped_loss=after,initial_grouped_loss=before,
                    fraction_zero_prediction_loss_removed=1-after/zero,
                    grouped_observations=fit['grouped_observations'],retained_examples=fit['retained_examples'],
                    advantage_scale=fit['advantage_scale'],fit_steps=fit['steps'],
                    learning_rate=fit['learning_rate'],optimizer_seconds=fit['optimizer_seconds'],
                    setup_seconds=fit['setup_seconds'],within_observation_variance=fit['normalized_within_observation_variance'])
                rows.append(row);all_rows.append(row)
        for player in (0,1):
            for name,lo,hi in (('early_played',1,25),('middle_played',26,51),('late_played',52,77),('unplayed_endpoint',78,78)):
                selected=[r for r in rows if r['player']==player and lo <= r['generation'] <= hi]
                assert len(selected)==hi-lo+1
                windows.append(dict(arm=arm['arm'],player=player,window=name,first_generation=lo,last_generation=hi,
                    median_fraction_removed=statistics.median(r['fraction_zero_prediction_loss_removed'] for r in selected),
                    median_grouped_loss=statistics.median(r['fitted_grouped_loss'] for r in selected),
                    median_grouped_observations=statistics.median(r['grouped_observations'] for r in selected),
                    median_optimizer_seconds=statistics.median(r['optimizer_seconds'] for r in selected)))
    output=dict(format=1,passed=True,inputs=inputs,all_fits=all_rows,windows=windows,
        formula='zero grouped MSE = 4*retained_weight/weighted_legal_target_mass - normalized_within_observation_variance; scale must exceed its .01 floor',
        new_training=False,gpu_used=False,accuracy_qualified=False,
        meaning='Reduction of grouped training-target squared error relative to predicting zero; not test accuracy, explained poker skill, policy error or EV loss.',
        endpoint='Fit 78 created an unplayed model and is separated from played-fit summaries.')
    target=OUT/'board-later-fit-diagnostic-v1.json';report=OUT/'BOARD-LATER-FIT-DIAGNOSTIC.md'
    assert not target.exists() and not report.exists()
    lines=['# Saved later-play fits: training loss diagnostic','',
        'This checks every saved fit from both board-root candidate runs, without fitting another model. Generation 0 used a uniform policy; fits 1–77 supplied played models, and fit 78 is an unplayed endpoint shown separately.', '',
        'The quantity below is the reduction in grouped training-target squared error relative to always predicting zero. It is not held-out accuracy, a fraction of correct poker decisions, or an EV-loss estimate. Noise and changing training data prevent treating these windows as a controlled capacity experiment.', '',
        '| Arm / player | Early played fits | Middle played fits | Late played fits | Late distinct observations |',
        '| --- | ---: | ---: | ---: | ---: |']
    for arm in result['arms']:
        for player in (0,1):
            group=[w for w in windows if w['arm']==arm['arm'] and w['player']==player and w['window']!='unplayed_endpoint']
            percentages=' | '.join(f"{w['median_fraction_removed']*100:.1f}%" for w in group)
            lines.append(f"| {arm['arm']} / {('BB','BTN')[player]} | {percentages} | {group[-1]['median_grouped_observations']:,.0f} |")
    lines+=['','The windows are fits 1–25, 26–51, and 52–77, matching the played-policy history except for its unfitted initial uniform state. Each cell is the median over the stated fits. All individual records and the unplayed endpoint are retained in [the complete diagnostic](board-later-fit-diagnostic-v1.json).', '',
        'The zero-prediction reference is reconstructed from the actual objective normalization: four times retained source weight, divided by weighted legal-action mass, minus within-observation variance. It is not assumed to equal one. Saved source hashes and all 156 generation-metric files were checked.', '',
        'The saved metrics alone cannot separate limited optimization, network capacity, target noise and lack of generalization. A useful follow-up is a fixed-data, grouped-observation holdout comparison of additional fitting against the current fit budget. Lower training error alone would not qualify a range improvement. The root-action evaluation and paired later-policy comparisons should guide whether that experiment is warranted.','']
    for p,h in inputs.items():assert sha(p)==h,p
    with target.open('x',encoding='utf-8') as f:json.dump(output,f,indent=2,allow_nan=False);f.write('\n')
    with report.open('x',encoding='utf-8') as f:f.write('\n'.join(lines))
    print(json.dumps(dict(passed=True,fits=len(all_rows),windows=windows,outputs={str(p):sha(p) for p in (target,report)})))


if __name__ == '__main__':main()
