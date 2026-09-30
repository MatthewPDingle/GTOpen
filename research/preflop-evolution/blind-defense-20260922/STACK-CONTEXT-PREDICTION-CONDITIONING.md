# Fixed-teacher conditional history and future cards

The prediction diagnostic needs action values for the situation the player
actually sees. Knowing our own cards and the public actions does not reveal
the opponent's cards or an unplayed turn and river. This building block supplies
that conditional distribution without putting hidden information into the model.

For every compatible opponent hand, start with its inherited entry-range
weight and multiply the fixed teacher's probabilities of that opponent's
earlier actions. Normalize once. Our earlier actions establish the information
state; their probabilities are checked separately and do not reweight hidden
hands. The complete compatible domains contain 1,225 hands preflop, 1,081 on
the flop, 1,035 on the turn and 990 on the river. No population-wide floor or
arbitrary premium-hand rule is added. The existing PhysicalDeals entry rule,
including its 1e-5 cutoff, is preserved exactly.

Draw an opponent hand from that posterior, then deal unknown public cards
uniformly without replacement, excluding both players' cards and the visible
board. The flop is an unordered physical set; turn and river remain chronological.
For each fixed private-hand pair, there are 34,246,080 preflop runouts, 1,980
flop runouts, 44 turn cards and one completed river board. These are conditional
chance draws for labels, not new scientific observations or network inputs.
Preflop labels must not be conditioned on a future flop's train/test partition.

Every legal action uses the same recorded chance plan. Average its resulting
payoffs arithmetically, retaining repeated draws, then subtract the original
teacher strategy's action-value baseline and divide by the original stack.
The sampling has already applied the posterior: multiplying those payoffs by
the posterior, entry weights or arrival probability again would distort labels.
The sampler records its own RNG state and authenticates exact replay across
restarts without touching the global NumPy or Torch RNG.

Query export reconstructs both players' chronological public history and
genuine own-history links using the qualified native card-key convention. Each
query contains only that player's cards and the board visible at its decision.
Hypotheses and full future deals remain separate label-generation data. A
counterfactual state with zero teacher own-history or own-entry mass is marked
unsupported; a future diagnostic must explicitly declare how it handles such
states, rather than silently treating them as observed play.

## Local qualification evidence

`stack_context_teacher_conditioning_check_v1.py` passed in 51.25 seconds on
CPU, with two inference threads and below-normal priority. It used retained
20bb/60bb fixtures and both 362/387 input representations, not a new training
run or the prospective complete 64-generation teacher.

- All 32 combinations of two depths, four streets, two players and two input
  widths passed the real registry/model-input path. Matching retained native
  policy rows agreed within 1.12e-16. The 60bb case checks held-out geometry;
  this fixture does not measure held-out accuracy.
- Both retained native river targets reproduced their posterior probabilities
  exactly, including opponent mass and own-history likelihood, across 1,980
  original two-player history paths.
- All 32 sampler restart checks reproduced the uninterrupted draws exactly.
  The qualification checked all 17,296 compatible physical preflop flops,
  the 1,980 ordered flop runouts, 44 turn choices and the river domain.
- Repeated draws retained multiplicity. A synthetic action-value control
  rejected applying posterior weights twice. All 27 corruption cases were
  rejected, including changed history, hidden-pair order, future cards in
  preflop inputs, altered RNG endpoints and invalid action values.

Sources: `stack_context_teacher_conditioning_v1.py`, its qualification check
and independent readback script. Attempt, result and readback receipts bind
their exact input identities. The action values in this check were synthetic;
no native payoff invocation, fit, CUDA work, scientific sample or production
change occurred. These helpers are not imported by the live comparison.

## Work still required

Connect the sampled conditional deals to the native fixed-teacher action-value
adapter and qualify the integrated outputs, including repeated-label noise.
Authenticate and qualify inference with the complete prospective A-baseline
played bank 0..63, excluding unplayed fit 64, after successful main training.
Declare actual public-flop splits, a separate preflop holdout, unsupported-state
handling, seeds, sample/fit/noise budgets and statistics before admitting the
separate diagnostic. No diagnostic has been admitted or completed by this check.

The live four-arm study's extra 25 relative-hand features remain river-only,
and its entry ranges remain inherited from the 200bb source at every depth.
Its registered inputs and gates are unchanged. After all 64 cycles per arm,
the actual complete-bank throughput gate, fresh 4096x7 evaluation, independent
readback and plain-English analysis remain required. Neither implementation
fixtures nor this restricted heads-up comparison establish full-position or
multiway preflop accuracy.
