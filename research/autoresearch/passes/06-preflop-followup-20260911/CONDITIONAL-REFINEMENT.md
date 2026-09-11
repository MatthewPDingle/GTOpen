# Bounded conditional convergence experiment

Diagnostics show zero **current** counterfactual prefix mass at the troublesome
eight-player SB/BB cold-call branches, although the saved average still reaches
them. No material-hand uniform fallback was observed there. Full-sample native
and sampled runs share this issue. A global weighted stopping number does not
qualify those conditional decisions.

Test actual additional local DCFR, not a preview or a relabeled global solve.
Start with the 23,038-node six-player all-solver fixture. Re-solve two disjoint
subtrees beginning with BTN after UTG raises or limps and intervening folds.
Use the candidate's saved average incoming hand distributions, fixed for the
local solve. Normalize each seat by its positive prefix mass; this is a constant
payoff scaling per traverser. Reset only mutable local regrets and sums to avoid
mixing those scales. All action menus, payoff rules, fixed policies, positions,
stacks, rake and upstream strategies remain unchanged. Disable pruning locally.

First screen: 100 local iterations from `six-native-b`. Cap at 600 seconds.
If completed, independently run all six existing local gates plus a full CPU
global check. Record load, refinement, revalidation and save time. Do not declare
global convergence from local progress. A saved research copy with partial or
canceled work must not be published. Test the same treatment on a sampled
candidate only after inspecting the baseline screen. Production integration,
adaptive branch selection and larger-tree GPU implementation are separate work.

The synthetic terminal cache screen found 374,346 reusable conditional vectors
in the modeled fixture (20.1% of terminal/traverser pairs; about 241 MiB dense
values), none in the all-solver fixtures. This is an opportunity count, not a
measured speedup. Folded-player reach still changes for 261,267 of those pairs.
