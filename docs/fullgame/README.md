# Heads-up preflop-to-river games

`solver::fullgame` solves an SB-vs-BB game from the preflop root to the river
as one game: the Preflop Lab's two-player tree, a weighted panel of flops, and
one GPU postflop continuation per (called preflop line, flop). Every CFR+
iteration updates the preflop strategy and every continuation together, so
preflop and postflop play always come from the same ranges. It needs the
`gpu` feature. Design and sizing: [Heads-up preflop-to-river solving: design](https://claude.ai/artifact/NMUajt25UbYmEVRe6epULC).

```sh
cargo build --release -p solver --features gpu --bin fullgame-cli
FULLGAME_PANEL=5 ./target/release/fullgame-cli docs/fullgame/sb-vs-bb-100.json 500 50 out.json
```

`docs/fullgame/sb-vs-bb-100.json` is the reference game: 100bb, limps allowed,
open to 3bb, 3-bets to 3x, 4-bets to 2.4x, jams at every raise, 5% rake capped
at 3bb (no flop, no drop). Postflop: flop 33% with a 3x raise, turn and river
75% with an all-in raise, one raise per street. An empty `flops` list takes
`FULLGAME_PANEL` canonical flops (default 5) by systematic sampling.

## The game

- **Seats.** Seat 0 is the SB: first to act preflop, out of position postflop.
  Blinds only; antes and straddles are refused.
- **Chance.** Both hands come from a full deck, then a flop is drawn from the
  panel. A hand pair and flop occur with probability proportional to the flop
  weight times card compatibility, normalized once at the root. Preflop folds,
  all-ins and check-downs use pair tables built from the same panel (full
  turn and river runouts), so every terminal sees the same deal distribution.
- **Strategies.** Preflop strategies are per hand class: the game is
  suit-symmetric, so a symmetric equilibrium exists, and each canonical flop
  stands for its suit orbit. Postflop strategies are per combo, with turn and
  river suit isomorphism.
- **Support.** With `support` set, a quick Preflop Lab solve of the same tree
  (balanced realization) picks the classes each pot holds: those it sends there
  at least `min_freq` of the time. A hand pair with either hand outside the
  support checks down at full-runout equity instead of playing the
  continuation, so no preflop action is forbidden.
  `Evaluation::outside_support` is the probability that a flop is settled that
  way.
- **Growing the support.** Check-down overvalues weak hands (they realize all
  their equity), so a narrow seed pulls the game toward them: on the 2-flop
  reference game a third of flops were settled outside the support and the
  SB's EV was 0.08 bb too high. `expand_at` lists iterations after which each
  pot's support grows to the classes the full game itself sends there at least
  `min_freq` of the time. Changed lines rebuild their continuations (postflop
  learning restarts there; preflop learning is kept).

## Results

`FullGame::evaluate` returns each seat's average-strategy EV, its best
response against the other seat's average strategy (deviating on every
street), the gaps between them, and the outside-support probability, all in
bb per hand. The gaps measure the panel game, not real poker: board sampling
is the larger error (see the design doc).

## Memory

Postflop learning state is 16 bits per entry on the GPU (i16 regrets, u16
strategy sums, one scale per node, as in the CPU's compressed storage); set
`f32_state` for full precision. On the 2-flop reference game the two agree
to 0.0001 bb, and the 16-bit game needs about 4.4 GB per flop once the support
has grown (seven flop lines with limps) instead of about 8.

Continuations stay on the GPU until it is nearly full. Later ones are parked
in pinned host memory and streamed through one shared GPU slot each sweep:
both players' regrets and the updating player's strategy sums go up, and the
updating player's arrays come back. Parked and resident continuations give
bit-identical results. `resident_flops` parks every flop from that panel
index on. Streaming costs PCIe time, so parked flops are slower than resident
ones.

## Limits in this version

- Preflop all-ins use panel equity, not exact full-deck equity.
- No saves, Browse integration or server endpoints yet.
