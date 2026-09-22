# Matched starting network for a possible hand-description experiment

The prepared visible encoder adds 33 descriptions of currently visible cards
to the original 269 inputs. Merely constructing a larger randomly initialized
network changes later random weights too. That would complicate attribution.

`sampled_visible_initialization_v1.py` instead constructs the original seeded
269-input network, copies all original weights/biases exactly, and adds zero
columns for the 33 new inputs. The initial mathematical function is unchanged.
It preserves the caller's random state. This helper does not fit models or
convert saved checkpoints, and no active trial imports it.

The CPU control passed on 7,278 existing numerical response-training
observations and four predetermined seeds. Original columns and later layers
match exactly. Float64 predictions matched exactly on those fixtures; float32
score differences were at most 4.47e-8 because matrix arithmetic geometry can
change rounding. New columns start at zero but have nonzero postflop gradients.
Their preflop gradients are zero because the new inputs are zero preflop.
No optimizer step or weight update occurred.

This does not freeze future preflop behavior: shared network weights can still
change through learning. It avoids assigning preflop hand actions manually.
Each player's network grows from 21,700 to 23,812 parameters, about 9.7%. Any
future comparison must still account for this extra capacity and compute.

The active all-in trial and both player tests must finish first. No new
representation training is launched. A future 302-input model still needs an
explicit new artifact/checkpoint format, encoder hash, fitting integration,
CPU/CUDA controls, complete-policy-bank evaluation and independently reserved
chance streams. The current 269-input format must not silently accept it.

Evidence: `sampled-visible-initialization-control-v1-registration.json` and
`sampled-visible-initialization-control-v1-result.json`. No production or
experimental range-preview changes.
