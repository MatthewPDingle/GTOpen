"""Generate the public aggregate study and validation figure; no player IDs."""
import json, argparse
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--results',default='docs/coinpoker'); ap.add_argument('--document',default='docs/coinpoker_models.md')
    args=ap.parse_args(); root=Path(args.results)
    results=[json.loads((root/(s+'.json')).read_text()) for s in ['NL10','NL25','NL50','NL100']]
    lines=['# CoinPoker player models by stake','',
           'Measured 8 September 2026 from HHDealer CoinPoker hand histories recorded in 2025. No raw histories or individual player identifiers are included in this public study.','',
           '## Using the library','',
           'In Preflop Lab, open **Manage models** and search **CoinPoker**, or choose a **CoinPoker · NL… · measured** group in a seat menu. **Pool** is the opponent average; the other entries describe fitted behavior groups. Hover a library entry for its source and sample size, or Edit it to inspect/copy its stats. Refresh is enough: the existing server reads `cache/archetypes.json` on request. Existing profiles and seat assignments are unchanged.','',
           'These models describe **seven-max ante tables with five to seven players dealt in**. They are not measurements of live casino games or no-ante tables. Date windows differ across stakes, so differences between stakes are not necessarily caused by the stake itself.','',
           '## Coverage','',
           '| Stake | Validated hands | Player names | Pool VPIP / PFR / 3-bet | Fitted types | Dates |',
           '|---|---:|---:|---|---:|---|']
    for r in results:
        s=r['models'][0]['stats']
        lines.append(f"| {r['stake']} | {r['audit']['accepted']:,} | {r['players']:,} | {s['vpip']:.1f} / {s['pfr']:.1f} / {s['threebet']:.1f} | {len(r['models'])-1} | {r['date_from']} to {r['date_to']} |")
    lines+=['','Hand counts are distinct games; model sample sizes in the library are **player-hands**, not additional independent games. Names can overlap between stakes. Short-history players contribute to Pool even when they cannot be classified reliably.','',
            '## Validation and type selection','',
            'Each stake uses its last 14 calendar days as a temporal holdout. A stable hash additionally withholds 20% of player identities from both grouping and group-frequency estimation. Those players are assigned using only their earlier observations and scored on their later decisions. Types use 11 smoothed preflop/postflop features. We compare standardized k-means and a fitted decision hierarchy with 2–8 groups, plus the historical seven behavior bands remeasured on CoinPoker. Rare historical bands merge into the nearest supported group. All groups must contain at least 30 fitting players. Fixed seeds make fitting reproducible.','',
            'The decision hierarchy fits smoothed action distributions, emphasizing common situations and capping each player’s fitting weight at 3,000 hands. Its squared-error training criterion is only a proxy: every candidate is selected using the same later-action log-loss score. K-means fits players equally.','',
            'The score is opportunity-weighted multinomial log loss across entry/defense situations and street-specific betting/folding. Lower is better. A player-level bootstrap checks whether the gain over Pool is positive; it does not treat every action as independent. We select the smallest supported grouping within 0.1% of Pool log loss of the best candidate. This is model-selection validation, not an untouched final test set and not proof of natural, discrete player species.','',
            '| Stake | Method | Groups | Withheld players | Later opportunities | Gain over Pool | Old seven bins, refitted gain |',
            '|---|---|---:|---:|---:|---:|---:|']
    for r in results:
        v=r['validation']; selected=next(x for x in v['candidates'] if x['k']==v['selected_k'] and x['family']==v['selected_family'])
        old=100*(v['baseline']-v['legacy_seven_bins_refit_log_loss'])/v['baseline']
        lines.append(f"| {r['stake']} | {v['selected_family']} | {v['selected_k']} | {v['validation_players']} | {v['validation_opportunities']:,} | {selected['improvement_pct']:.2f}% | {old:.2f}% |")
    lines+=['','![Held-out action prediction by number of player groups](coinpoker/validation.png)','',
            'The old-bin comparison remeasures the historical seven VPIP/PFR categories on the same CoinPoker training players; it does not use 2009 parameter values. Its unmerged benchmark can include poorly supported bins, so it is a comparison rather than an automatically publishable library. Published names are descriptive labels assigned **after** fitting. Sticky/High-fold means at least seven percentage points below/above that stake pool’s fold-to-flop-bet rate, not a claim about profitability or skill. When two groups share a label, their VPIP/PFR appears as a disambiguator.','',
            '## Models','',
            '| Stake / type | Players | Player-hands | VPIP | PFR | 3-bet | Fold vs flop bet |',
            '|---|---:|---:|---:|---:|---:|---:|']
    for r in results:
        for m in r['models']:
            s=m['stats']; src=m['source']; label=m['name'].replace('Data · CoinPoker · ','')
            lines.append(f"| {label} | {src['players']:,} | {src['player_hands']:,} | {s['vpip']:.1f} | {s['pfr']:.1f} | {s['threebet']:.1f} | {m['postflop']['fold_to_bet'][0]:.1f} |")
    lines+=['','## What is measured and what is approximated','',
            '- Every rate pools its actual opportunities and outcomes, rather than averaging players’ percentages weighted by unrelated hand counts. Exported estimates use 100 prior opportunities from the stake pool. The aggregate JSON records denominators, sparse fields and any engine constraints.','- Players need 100 earlier hands to fit/validate types. At publication, players with 100 total eligible hands can be assigned with smoothed estimates; shorter histories remain in Pool. Final production groups refit on all eligible earlier players, then aggregate the complete sample.','- The 3-bet field follows GTOpen’s cold single-raise bucket with no caller ahead. Squeezes are measured separately; this is not necessarily a tracker’s combined 3-bet statistic. Fold-to-3-bet and 4-bet refer to the original raiser. Limp-then-face-raise is separate from cold defense.','- Postflop betting with initiative, betting without initiative and facing-bet decisions have separate denominators. The engine’s donk field pools no-initiative bets/stabs; raises facing bets are pooled across streets. All-in runouts do not generate fictitious checks or betting opportunities.','- Position, stack band, actual occupancy and size-band counters are retained in each public aggregate. Current GTOpen archetype inputs still pool position/stack frequencies and use the engine’s positional shaping.','- `flatten=0` deliberately uses GTO reference hand ordering. Hole-card composition was not fitted; zero is a modeling assumption, not measured intelligence or skill. Shove responses still follow GTOpen’s adaptive large-bet model.','- The current engine can choose only the smallest/largest configured size. The exporter maps the majority opening-size band (up to 2.5bb versus larger) and bet-size band (up to 60% pot versus larger) to those choices. These are approximations, not an exact sizing distribution. Defense bands are floored at the overall 3-bet percentage where the engine requires it; such adjustments are recorded.','- Site population samples are not random censuses. Dealer coverage, observation dates, selection into long histories and unusual-hand exclusions can affect the results. Prediction gains do not establish an exploit EV gain or exact hand ranges.','',
            '## Data checks and exclusions','',
            'The parser validates action order, street progression, calls including short all-ins, stack limits, blind/button order, and exact cent-level contributions against the recorded total pot after uncalled returns. Forced blinds/antes are not VPIP. Sitting-out/out-of-hand seats are not dealt players. Implicit all-in raises are reconstructed only when their amount equals the actor’s remaining stack.','',
            'Deduplication is by hand ID within each site/stake input. Timestamp shifts, trailing padding and showdown-only differences do not create extra action observations. One inspected NL10 duplicate disagreed about the showdown winner; these models do not use winners, revealed cards or win rates. A conflicting **action** duplicate stops fitting for review.','',
            'Four-max tables, hands dealt to fewer than five players, extra/missing blinds, dead-button cases, irregular antes, under-minimum raises and multiple runouts are excluded from this release. Excluding those hands can particularly affect short-stack and all-in behavior; they are not quietly treated as standard situations.','',
            '| Stake | Raw records | Repeated IDs | Accepted | Excluded distinct hands |',
            '|---|---:|---:|---:|---:|']
    for r in results:
        a=r['audit']; excluded=sum(v for k,v in a.items() if k.startswith('excluded/'))
        lines.append(f"| {r['stake']} | {a['raw']:,} | {a.get('duplicate',0):,} | {a['accepted']:,} | {excluded:,} |")
    lines+=['','Full exclusions, position/size counters, model-selection scores, opportunity counts and model parameters: '+', '.join(f"[{r['stake']}](coinpoker/{r['stake']}.json)" for r in results)+'.','',
            '## Reproduce','',
            'Python 3.12; NumPy 1.26.4; scikit-learn 1.5.2; Matplotlib for the figure. No solver session is built or changed by the data pipeline.','',
            '```powershell',
            'python -m unittest discover -s tools/coinpoker -v',
            'python tools/coinpoker/analyze.py --source "T:/Dev/Poker Data/hhdealer/CoinPoker" --out output/coinpoker --workers 4',
            'python tools/coinpoker/fit.py --input output/coinpoker --out docs/coinpoker --publish cache/archetypes.json',
            'python tools/coinpoker/report.py',
            '```','',
            'Per-player counters in `output/coinpoker` remain local. The fitting command without `--publish` creates reviewable aggregates without changing the library. Publishing replaces only the `Data · CoinPoker ·` collection and preserves other models. No raw data is uploaded.','']
    Path(args.document).write_text('\n'.join(lines),encoding='utf-8',newline='\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axs=plt.subplots(2,2,figsize=(10,6),constrained_layout=True)
    for ax,r in zip(axs.flat,results):
        v=r['validation']; cs=v['candidates']
        for family,color,title in [('kmeans','#5782af','K-means'),('tree','#438860','Decision hierarchy'),('behavior_bands','#955ea4','Merged behavior bands')]:
            sub=[c for c in cs if c['family']==family]
            ax.plot([c['k'] for c in sub],[c['improvement_pct'] for c in sub],marker='o',color=color,label=title)
        chosen=next(c for c in cs if c['k']==v['selected_k'] and c['family']==v['selected_family'])
        ax.scatter([chosen['k']],[chosen['improvement_pct']],s=90,color='#df9b35',zorder=3,label='Selected')
        ax.axhline(0,color='#888888',lw=.8)
        ax.set(title=r['stake'],xlabel='Number of groups',ylabel='Log-loss reduction vs pool (%)')
        ax.grid(alpha=.2); ax.legend(fontsize=8)
    fig.suptitle('CoinPoker: predicting later decisions of withheld players',fontsize=13)
    fig.savefig(root/'validation.png',dpi=150); plt.close(fig)

if __name__=='__main__': main()
