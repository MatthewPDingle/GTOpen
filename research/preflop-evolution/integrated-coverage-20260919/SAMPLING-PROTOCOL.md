# Chance-only board-sampling audit

This is an independent combinatorial diagnostic. It reads no strategy results,
action values or Wizard outcomes, and does not solve reserved boards. It does
not change the already registered solve panels.

Enumerate the retained two-player entry support from the frozen subtree and
aggregate compatible physical hole-card pairs into hand-class pairs. For every
one of the 1,755 canonical flops, enumerate legal retained hole-card pairs and
weight by its suit-isomorphism count. Summing all boards must reproduce the
full-deck private-class prior, and its unnormalized mass must equal the
hole-card mass times C(48,3). Verify this before sampling.

Repeat 1,000 independently seeded panel draws per design. Sample canonical
boards uniformly without replacement inside each stratum, then weight each
by stratum size / sample size times its isomorphism count. Compare the original
five strata with six strata that distinguish trips from other paired rainbow
boards. This distinction is known from cards alone: their physical board
multiplicities differ. Seed 9026191940 + 1000*stratum-design + boards-per-stratum.
Use 1, 2, 4, 8, 16 and 32 boards per stratum, capped at each stratum's size.

Report median and 5th/95th percentiles of total variation in the joint
hand-class prior and both marginal priors. These are distribution diagnostics
over repeated samples, not uncertainty intervals on equilibrium ranges.
Report actual panel A/B/AB diagnostics separately. No design is selected on
the basis of producing a preferred AA mix. Larger samples may reduce prior
distortion without guaranteeing accurate continuation values or strategies.
