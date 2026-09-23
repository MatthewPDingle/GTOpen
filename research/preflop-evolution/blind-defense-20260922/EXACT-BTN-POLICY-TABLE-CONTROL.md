# Exact response state can be mapped into a separate policy table

23 September 2026. A CPU-only integration control passed while the fixed wider
evaluation continued. Neither its candidate nor the active trainer changed.

The new runtime table has a separate format and explicit exact-accumulator,
population-matrix, context and native-catalog identities. It does not pretend
that cumulative exact regrets are retained sampled means and creates no fake
observation counts. A composed probability lookup gives exact rows precedence
over sampled rows only at BTN's first fold/call response to BB's initial shove.
Unreached classes preserve the supplied base policy. Other nodes retain their
existing probabilities.

Four accumulator states using old played generations 0, 25, 51 and 77 were
checked. All 96 incoming BTN classes matched the separately derived accumulator
probabilities. In a real 7,276-row native mixed-street query batch, the 14
matching initial-response rows took the exact policy and the remaining 7,262
rows stayed identical to the base policy. JSON round trips preserved all four
states, and zero accumulated reach preserved every base probability.

The existing CUDA table-preparation arrays agreed exactly with direct CPU
application. This tested their CPU-side preparation only: no CUDA execution,
network fitting or new trained policy was tested. Old sampled-table and model
readers rejected the new document rather than silently stripping its meaning.
Changed matrix/population, impossible own history and invented sampled counts
were also rejected, for six rejection cases in total.

Next integration work remains: a distinct full model/checkpoint reader and
writer, played-bank ordering and restart checks, the BB shove target correction,
and a small end-to-end CPU/CUDA control before fresh training. Exact response
state must receive one deterministic update per played generation, never the
sampled records as additional updates. If those original records remain in the
network reservoir, the declared runtime override must take precedence. The
current wider evaluation retains priority; this control is not an accuracy or
deployment result.

Evidence: `exact-btn-policy-table-control-v1-{registration,result}.json`.
