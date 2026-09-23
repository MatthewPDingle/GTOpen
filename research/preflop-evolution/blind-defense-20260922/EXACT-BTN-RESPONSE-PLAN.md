# Remove sampling noise from the all-in response check

The present fixed BB-versus-BTN game has a useful special case: after BB jams,
BTN can only fold or call. No postflop strategy remains. Its value depends on
the two private hands, their all-in equity, contributions, dead money and rake.
This part can be evaluated over the complete entry population rather than
estimated from a random sample. That is a stronger next measurement option;
it does not replace the running trial's registered sampled evaluations.

## Feasibility evidence

`allin-private-population-plan-v1-result.json` enumerates all **776,650**
positive-probability, compatible physical private-hand pairs in the frozen
context. Keeping player roles fixed, global suit relabelling reduces them to
**47,478** distinct equity cases. The original independently reviewed cache
already contains **23,891**; **23,587** additional equity cases are required.
Existing cases cover 66.68% of the entry probability mass, but the missing
cases must all be supplied for an exhaustive claim.

The grouped population preserves every class-pair probability. The largest
class-pair mass discrepancy against direct physical enumeration was 8.9e-19;
the largest BB class-mass discrepancy against the previously checked full
prior was 1.6e-17. Both representatives and original physical pairs were also
checked with the separate scalar suit-canonicalization implementation.

The earlier complete-population diagnostic took 501.14 native seconds to
calculate 4,547 missing exact equity cases. At that measured rate, the new
23,587 cases would take about **43 minutes of native enumeration**, plus cache
assembly and checks. This is an estimate, not a benchmark of this new workload.
Some separately reviewed caches may reduce the missing count further. No new
equity cases were calculated by this planning step.

`preflop-catalog-control-v1-result.json` establishes a small policy lookup path:
169 BB root observations and 96 supported BTN response observations. All
1,326 physical hole combinations and all 24 global suit permutations map to
the expected native preflop keys. The catalog has no earlier own actions, so
the existing bank average retains its correct own-reach treatment. Using the
completed four-model control bank, its probabilities exactly matched 1,017
saved native-query reference rows; catalog inference took 0.203 seconds.
This control does not yet qualify the full 78-model candidate.

## Planned calculation and admission

1. Finish the unchanged current trial and both existing evaluation audits.
2. Register a separate exhaustive calculation: freeze the full population,
   candidate checkpoint(s), complete played banks, exact equity sources,
   endpoint, controller, resource caps and independent reviewer. Do not select
   an intermediate model based on its performance.
3. Complete the equity cache and audit full coverage, integer wins/ties/losses,
   player roles, all 1,712,304 boards per distinct private pair and provenance.
   The equity labels remain outside all policy inputs.
4. Check each admitted full bank's compact preflop catalog against its native
   evaluation observations, including the initial model, learned tables and
   neural fallback. No unobserved BTN classes are invented.
5. For every private pair, multiply its original entry probability by BB's jam
   probability. Calculate BTN's fold and call values, using BTN wins (BB losses)
   and half the ties. Sum these values separately for each BTN hand class.
6. Choose call or fold from those complete class totals. Compare that response,
   always-fold and always-call with the frozen BTN policy. Report gains per
   original spot entry, jam reach, conditional call frequencies and all class
   contributions. Independently rebuild the totals and cashflow formulas.

Because this would cover the complete finite entry population and every board
for the all-in branch, there is no held-out sampling interval for that endpoint.
It is an exhaustive calculation within the specified model, subject to numerical
and implementation checks. An independently reconstructed gain can be checked
directly, without hoping a noisy fitted responder is strong enough.

## Limits

This is a best response only at BTN's specified fold/call decision, with BB's
policy and both incoming ranges fixed. It is not a full-game best response,
joint equilibrium, postflop quality test or proof that the preflop ranges match
GTO Wizard. Earlier folded players' cards remain omitted by this fixed context.
BB's non-all-in choices still involve learned postflop behavior and require
separate evaluation; the improved stratified training method remains relevant
there. Equity results can be reused at other stack depths, but policy quality
does not transfer automatically with them.
