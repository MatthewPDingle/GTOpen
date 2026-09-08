# Additional data for preflop player models

Reviewed 8 September 2026. No purchase or vendor contact has been made. Prices and available dates require a current quote; software/converter prices are not hand-history prices.

## Recommended order

| Source | Cost/access | Useful for GTOpen | Important limit |
|---|---|---|---|
| [Ignition complete exports](https://www.ignitioncasino.eu/poker/features) | Account exports; additional voluntarily shared collections may need an arrangement | Highest priority for learning actual hand/action probabilities, including folds, across more dates and stakes | Anonymous pools; do not claim persistent-player identities |
| [HHDealer cash histories](https://www.hhdealer.com/buy.php) | Paid batches/subscriptions; quote by room, stakes and volume | Extend the existing CoinPoker NL10/25/50/100 sample, contextual frequencies, sizing and player clusters | Public listing does not establish complete folded-hole-card coverage |
| [KingsHands](https://kingshands.com/) | Paid histories; obtain sample/quote | Candidate alternative populations, including club networks advertised on its site | Confirm actual room/stake availability and known-card coverage before buying; different populations need separate labels |
| [PHH dataset](https://github.com/uoftcprg/phh-dataset) / [Zenodo archive](https://doi.org/10.5281/zenodo.10796885) | Public research download | Parser/regression testing and historical comparisons | Its 21.6M HandHQ human hands are from July 2009 and overlap the source family already used here; Pluribus is a benchmark, not a current recreational pool |

Ignition's official description explicitly says delayed exports reveal every player's hole cards, including hands not played, 24 hours after a session. That makes **more full-reveal exports** my first choice. I did not verify a currently purchasable catalog of full-reveal Ignition histories. A seller merely advertising Ignition compatibility or mucked showdown cards is insufficient.

HHDealer explicitly offers native CoinPoker and converted PokerStars formats. Prefer native samples so conversion artifacts can be checked. Its [terms](https://www.hhdealer.com/terms.php) describe derived statistical/model outputs as permitted and raw-history redistribution as restricted; confirm the chosen delivery's terms before use.

## Sample request before spending money

Ask for 1,000–5,000 representative hands plus:

- Exact dates, site, stakes, currency, cash/fast-fold format, seated and dealt-in player counts, ante/blind structure, and stack coverage.
- The proportion of **opponents' preflop folds with both hole cards known**, separately from showdown coverage. Ask for actual examples of a player folding preflop with their cards present.
- Whether identities persist across sessions, whether all hands or only selected wins/showdowns were collected, and how duplicates are removed.
- Native text format, complete action amounts, and permission to train models and distribute aggregate derived parameters with an open-source app.
- Price, minimum batch, and counts by desired site/stake/date. Prioritize new periods and rare situations rather than more duplicates of existing data.

## How new data would be used

Keep each site/stake/format distinct. Audit replay and cards; deduplicate against existing histories; split whole sessions chronologically. Reserve genuinely new dates for testing the recent Vs Limps refinement. Measure opportunity counts by position, table size, number of limpers, raise size and effective stack before adding finer conditioning.

Complete known-card data can train direct fold/call/raise probabilities. Ordinary observed histories improve contextual action rates and player-type definitions, but showdown-revealed hands are a selected sample: they cannot simply be treated as the full starting range. Any hand-composition inference must remain labeled and validated separately. Online stakes are not automatically interchangeable with a live $2/2 or $2/5 game.
