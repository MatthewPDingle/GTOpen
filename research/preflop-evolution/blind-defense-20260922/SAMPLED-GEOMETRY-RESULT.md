# On-demand postflop transitions match the actual BB study

The research transition engine generates legal actions and successor states
when needed, without constructing a public-tree arena or allocating strategy
arrays. Its first qualification compared it against the native tree builder
over **every legal public history** for all 112 fixed flops and all three
postflop continuation branches of the registered BB-defense context.

## Full-panel result

| Check | Count / result |
|---|---:|
| Flop/continuation games | 336 |
| Reachable public nodes compared | 231,143,136 |
| Action nodes / complete legal menus compared | 91,618,688 |
| Terminal nodes / payout triples compared | 139,133,120 |
| Maximum path depth | 14 edges |
| Maximum legal actions at a node | 3 |
| Transition mismatches | 0 |

The nine-game texture probe passed first. The full-panel check then took about
15 seconds and retained at least 102.3 GB free system RAM. This is CPU correctness
work, not a CPU performance optimization or a solve-time benchmark. No CUDA
device or strategy arena was allocated.

Each comparison checks node kind, player, street, contributions, the ordered
legal action menu and exact successor traversal. At fold/showdown terminals it
also compares winner/loser/tie payout values and checks the configured rake.
All legal turn/river branches are visited. Repeated public cards are excluded;
the native builder's unused repeated-turn padding is deliberately not treated
as a reachable game history. No river suit-isomorphism shortcut is used here.

The target remains BB versus BTN with full supported ranges and all three
continuations (pot/remaining stack 4.5/198, 12.5/194, 36.5/182), 5% rake capped
at 2 bb, 50% bets/donks and pot-sized raises, one raise per street. The reference
builder receives hand counts `[1,1]` solely for unused data-offset fields:
its public actions do not depend on those counts, and neither implementation
creates or solves private-hand strategy arrays in this test. This is not a
one-hand substitute for the intended 169-class/96-class training experiment.

## State and identity

The on-demand transition state occupies 48 bytes in this native build. A
depth-first traversal needs at most 15 such frames in the tested geometry,
or 720 bytes for these state records alone. That excludes action scratch,
private cards, public-history keys, GPU batches and all stored policies/regrets.
It must not be reported as the total memory requirement of the algorithm.

The information-set key prototype retains the continuation branch, player,
exact private cards, visible ordered board and entire public action history.
Tests distinguish different histories, branches, private suits and turn/river
order; reversing the order of the same two private cards preserves identity.
Neither opponent private cards nor future public cards are accepted by that key
interface. Keys are scoped to a fixed registered game configuration; a trainer
must not reuse the table across different games or model generations.

The state generator is only a betting transition engine. It intentionally
does not merge policies merely because pot, stack and action menus coincide.
Full public history remains part of the information identity.

## Remaining gates

The equivalent transitions currently run in the CPU reference. The next step
is to use and verify them inside a GPU sampled traversal, together with the
qualified batch-update rules. Actual private-card sampling, public chance
probabilities, suit relabeling, showdown evaluation, sparse key allocation and
preflop/postflop utility offsets must also be verified together.

After that, measure policy-table growth and time to independently evaluated
convergence. Lazy transitions remove one reason to retain an entire public
tree; they do not prove the persistent strategy table will fit or converge
quickly enough. No new BB policy or broader preflop model has been trained.

## Evidence

`research_sampled/state.rs` contains the isolated reference;
`hu_sampled_geometry_probe.rs` performs the native-tree comparison.
`hu_sampled_geometry_run_20260922.py` registered all inputs before executing the
probe and panel with a five-minute limit and 20 GiB free-RAM reserve per run.
The ten frozen input hashes were verified afterward. Results and logs use the
`sampled-geometry-v1-*` prefix. Production code, sessions and ranges were unchanged.
