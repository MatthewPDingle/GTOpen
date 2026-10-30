# Real payoff resources for seven stack depths

Preparation passed for the retained 20, 40, 60, 100, 150, 200 and 400bb native
geometry fixtures. Each now has its own physical-pair population, exact all-in
payoff matrices, full physical preflop catalog and initial class catalog. These
replace synthetic routing matrices in the upcoming implementation controls.

The fixtures declare broad, unsolved incoming ranges: all 169 classes for both
players. These are not learned opening ranges and are not a matched GTO Wizard
scenario. No scientific training population has been selected by this work.

Three implementation tests passed in 6.122 seconds before preparation. They
reconstructed the original, narrower 776,650-pair context and its retained
matrices/catalogs; rejected missing coverage and altered catalog identities;
and rejected deliberately corrupted showdown and fold payoffs.

Preparation then completed once in 31.187 seconds after resource admission.
Canonical population weights were checked against direct physical-pair mass.
The existing matrix constructor was compared with separate vectorized payoff
arithmetic using each context's pot, contributions and rake. The largest
discrepancy across all depths was 8.674e-18. Every native preflop decision catalog
contains all 1,326 physical holdings, with source identity and class checks.

The original native catalog outputs are retained. A subsequent saved-file
readback passed for all seven contexts and 87 input/artifact identities. It
checked population coverage, normalized mass and context-specific cashflow
conservation. It reuses the separate exhaustive-count verification; it does not
independently rerun enumeration or establish learned strategy accuracy.

The 29 retained files use 82.8 MB logical and 22.44 MB allocated, all compressed,
in `S:\GTOpen-research\stack-context-resources-v1`. Evidence uses prefix
`stack-context-resources-v1` in this directory. Preparation session 64533 exited
0; PID 93520, creation 1790697774.207835, is historical rather than a live handle.
Do not rerun or overwrite the completed preparation or readback.

Remaining integration work: qualify cached CUDA scoring, complete the board and
posterior64 workers, exercise a complete joint training cycle, verify interruption
and restart, and show that downstream values affect upstream preflop decisions.
Only then register the matched learning comparison with explicit range
assumptions and acceptance criteria. No long scientific training, production
change or GitHub push occurred in this preparation.
