"""Concise human report of completed evidence; does not deploy or end the goal."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'research/preflop-evolution/continuation'
OUT=BASE/'night-shift-20260916'


def read(p):return json.loads((BASE/p).read_text())


def main():
    n19=read('policy-stability-20260916/result.json')
    n21=read('flop-menu-20260916/evaluation.json')
    n32=read('zero-fallback-20260916/result.json')
    n35=read('paired-blend-gpu-20260916/result.json')
    n37=read('terminal-ranges-repaired-20260916/result.json')
    n38=read('blend-extension-repaired-20260916/result.json')
    assert not n19['both_signals_passed'] and n21['accuracy_screen_passed']
    assert not n32['interesting_reduction'] and not n35['changes']['blend']['signal_passed']
    gains=[100*(1-r['mae_pct_pot']['candidate']/r['mae_pct_pot']['balanced']) for r in n21['cases']]
    times=n19['additional_learning_seconds']
    deep={r['case']:r for r in n37['rows']}
    last=n38['rows'][-1]
    lines=['# Preflop accuracy research: night-shift findings','',
        '**No candidate is ready to replace the live version.** The research produced better hand-value estimates, '
        'but the tested alternatives did not establish both improved accuracy and practical solve performance. '
        'The app on port 56708 was not deployed or restarted by this research.','',
        '## What improved','',
        f"The strongest predictor reduced hand-value error by **{min(gains):.0f}–{max(gains):.0f}%** "
        'in the latest fresh-flop comparison, including a wider flop bet menu. All eight comparisons '
        'passed their accuracy screens. These are errors in estimated hand values, not a measured '
        'percentage improvement in full-game ranges. Some hand groups still regress.','',
        '## What prevents deployment','',
        f"The full predictor's solve measure stayed near **0.078 bb** after 1,500 iterations, "
        f"versus **0.00062 bb** for ordinary Balanced. The same additional 1,000 iterations took "
        f"**{times['candidate']/60:.1f} minutes versus {times['original']/60:.1f} minutes** "
        f"({100*(times['candidate']/times['original']-1):.1f}% longer). "
        'A short iteration benchmark had looked better, which is why the longer test mattered.','',
        f"Keeping only 25% of the learned prediction did not pass the fixed practical screen either: "
        f"its 1,000-iteration gap was **{n35['changes']['blend']['gap_total_bb']:.5f} bb**, "
        f"and the same amount of learning work took **{100*(n35['learning_time_ratio']-1):.1f}% longer** "
        'than the paired-accounting control in one ordered comparison. That control also remained '
        'slightly above the gap target; it is distinct from ordinary production Balanced.','',
        f"A separately registered extension kept the blend unchanged and reached iteration "
        f"**{last['end']}**, with gap **{last['gap_total_bb']:.5f} bb**, "
        f"{'passing' if last['signal_passed'] else 'still missing'} the registered settling screen. Its cumulative learning work from the common 500-step "
        f"starting point was **{n38['learning_seconds_since_common_500_start']/60:.1f} minutes**. "
        'This extra work is charged to the blend; different final iteration counts do not make it '
        'a fair throughput comparison. No fresh-range accuracy result exists for this blend, because '
        'the prerequisite test failed.','',
        '## Most useful new lead','',
        f"The full predictor's current and averaged hand ranges differ much more deep in the tree "
        f"than the visible charts suggest: **{100*deep['eight-candidate']['opponent_weighted_tv']:.1f}% "
        f"versus {100*deep['eight-original']['opponent_weighted_tv']:.1f}%** on the registered weighted "
        'diagnostic. This suggests investigating the inputs seen during search. It is not proof of '
        'the cause or a measurement of range error. The empty-range fallback change did not help.','',
        '**Recommended next step:** compare a full small game with the same game using directly '
        'solved continuation values. Then introduce prediction. This separates prediction error '
        'from search integration and checks whether our stopping measure tracks true improvement '
        'in that controlled game. [Concrete follow-up](NEXT-STEPS.md).','',
        '## Scope and retained evidence','',
        'The accuracy tests use fresh boards in familiar range contexts and restricted postflop '
        'trees. They do not establish full-game equilibrium accuracy, unseen-family generalization, '
        'or exact multiplayer card removal. Frozen-value gaps are not full-game exploitability. '
        'Training screens, prospective tests and runtime checks remain separate.','',
        'The failed compile and process-identity attempts are preserved, with separately recorded '
        'repairs and unchanged model settings. Research policy files stay local and must not be '
        'loaded into the ordinary app.','',
        '[Detailed results](RESULTS.md) · [Experiment ledger](ledger.json) · '
        '[Accuracy/settling figure](accuracy-and-settling.png)','']
    (OUT/'SUMMARY.md').write_text('\n'.join(lines),encoding='utf-8',newline='\n')
    print(OUT/'SUMMARY.md')


if __name__=='__main__':main()
