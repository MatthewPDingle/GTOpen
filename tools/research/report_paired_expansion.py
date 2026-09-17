"""Report the frozen completed screen without fitting or changing its gates."""
import numpy as np
import paired_continuation_expansion as expansion
from run_paired_expansion import metadata_adapter


def report():
    s=expansion.pilot;out=expansion.OUT;m=expansion.checked()
    corrections={};validate=metadata_adapter(s.native.previous.old.validate,corrections)
    rows=[];hashes={}
    for j in m['jobs']:
        path=out/'jobs'/(j['id']+'.json');r=s.read(path);validate(r,j,m);rows.append(r)
        hashes[j['id']]=s.pilot.sha(path)
    for name in ['runner-freeze.json','screen-implementation-freeze.json']:
        for path,h in s.read(out/name)['inputs'].items():assert s.pilot.sha(s.ROOT/path)==h,path
    screen=s.read(out/'training-screen.json')
    for path,h in screen['inputs'].items():assert s.pilot.sha(s.ROOT/path)==h,path
    assert len(screen['scores'])==72
    eligible=[r for r in screen['scores'] if r['eligible']]
    assert not eligible and screen['selected'] is None
    assert not (out/'candidate.json').exists()
    best=min(screen['scores'],key=lambda r:r['mean_action_mae_bb'])
    guarded=min((r for r in screen['scores'] if r['worst_family_ratio']<=1.05 and r['leaf_guard_passed']),key=lambda r:r['mean_action_mae_bb'])
    result=dict(checked_at=s.now(),manifest_id=m['id'],reference_count=len(rows),reference_sha256=hashes,
        max_cpu_gap_pct=max(r['gap_pct'] for r in rows),max_gpu_gap_pct=max(r['gpu_gap_pct'] for r in rows),
        solver_seconds=sum(r['seconds'] for r in rows),choices=72,selected=None,passed=False,
        best_mean=best,best_guarded=guarded,metadata_roundtrips=corrections,
        frozen_inputs_verified=True,quality_checks_passed=True,production_enabled=False)
    s.write(out/'completion.json',result)
    lines=['# Paired continuation: completed development screen','',
        '**No candidate passed. The existing production model is unchanged.**','',
        f"All {len(rows)} new postflop reference solves passed the CPU and GPU accuracy limits.",
        f"Maximum gaps: {result['max_cpu_gap_pct']:.5f}% and {result['max_gpu_gap_pct']:.5f}% of pot.",
        f"Recorded solver time: {result['solver_seconds']/60:.1f} minutes, excluding pauses and process overhead.",'',
        'The frozen screen compared 72 corrections, leaving each of four policy families',
        'out in turn. The unchanged baseline was retained for every comparison. The',
        'original and shallow-policy audits were development data in this experiment.',
        'Two new synthetic policies added coherent reaching ranges across called opens,',
        'called 3-bets and called 4-bets. They are not claimed GTO or real-player policies.','',
        '## Result','',
        f"Mean adjusted call-versus-3-bet error: baseline {best['baseline_mean_action_mae_bb']:.4f}bb; best screened mean {best['mean_action_mae_bb']:.4f}bb.",
        f"That is only {100*best['improvement']:.2f}% improvement, below the required 5%.",
        f"The same choice worsened its weakest family by {100*(best['worst_family_ratio']-1):.2f}% and failed the leaf-error guard.",
        'The best choice satisfying both nonregression guards was slightly worse than',
        f"baseline overall ({guarded['mean_action_mae_bb']:.4f}bb, {100*(-guarded['improvement']):.2f}% worse).",'',
        '| Family held out | Baseline adjusted MAE | Best-mean correction (rejected) | Qualified classes | Decision mass |',
        '|---|---:|---:|---:|---:|']
    for f in best['folds']:
        lines.append(f"| {f['family']} | {f['baseline_action_mae_bb']['corrected']:.4f}bb | {f['action_mae_bb']['corrected']:.4f}bb | {f['qualified_classes']} | {100*f['qualified_mass']:.1f}% |")
    lines += ['', 'No choice reached the required 5% improvement. Fourteen satisfied the',
        'per-family action guard and 46 satisfied the leaf guard, but none passed all',
        'requirements. No new candidate was exported and no prospective test or native',
        'integration was launched. The original compact candidate remains only as a',
        'record of the earlier failed screen.','', '## Interpretation and next step','',
        'Broader development data filled the action-support gaps in the synthetic',
        'families: all 169 classes qualified there. This did not produce a correction',
        'that transferred reliably across families. Stronger fitting or more features',
        'alone was insufficient in this bounded experiment.','',
        'This is not proof that learned continuation values cannot work. There are',
        'only four related policy families, and each new family uses ten stratified',
        'boards per branch. Development selection is not an independent accuracy test.',
        'The two older audits have different coverage and more boards; family averages',
        'are weighted equally, not in proportion to sample count or a real-game mix.',
        'Sampling noise, limited range diversity and the shared residual form remain',
        'plausible explanations. This screen does not establish which dominates.','',
        'The recommended next experiment is an uncertainty audit before another model',
        'search: quantify paired board-sampling variation in the action-value targets,',
        'then preregister one independent panel repeat for the unstable contexts.',
        'If discrepancies persist beyond that noise, test a representation with',
        'explicit interactions between both complete ranges rather than another',
        'global hand-feature correction. That is a new study; do not reinterpret',
        'additional samples as a way to turn this failed screen into a pass.','',
        'Port 56708 remains the existing build. Serena automatic dashboard opening',
        'was disabled separately at the user\'s request. See completion.json for label',
        'hashes, training-screen.json for every result and PROTOCOL.md for frozen gates.']
    (out/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8',newline='\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(9,4.5));x=np.arange(4)
    for off,key,color,label in [(-.18,'baseline_action_mae_bb','#777e88','Unchanged baseline'),(.18,'action_mae_bb','#bd6744','Best mean correction — rejected')]:
        bars=ax.bar(x+off,[f[key]['corrected'] for f in best['folds']],.34,color=color,label=label)
        ax.bar_label(bars,fmt='%.3f',padding=3,fontsize=9)
    ax.set_xticks(x,[f['family'].capitalize() for f in best['folds']]);ax.set_ylim(0,.29)
    ax.set_ylabel('Adjusted action-value MAE (bb)');ax.set_xlabel('Entire policy family held out during fitting')
    ax.set_title('None of the 72 corrections passed the development screen')
    ax.legend(frameon=False,fontsize=9);ax.spines[['top','right']].set_visible(False)
    fig.text(.5,.02,'60 new reference solves · paired contexts · no independent test or deployment',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.04,1,1));fig.savefig(out/'comparison.png',dpi=160);plt.close(fig)
    print('Validated 60 references and frozen inputs; completed report records no passing candidate.')


if __name__=='__main__':report()
