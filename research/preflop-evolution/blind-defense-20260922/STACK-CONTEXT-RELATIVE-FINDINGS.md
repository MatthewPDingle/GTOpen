# Native relative-input adapter passed CPU integration checks

The separate 387-input registry/model-object path can now consume actual native
observations without changing the existing 362-input implementation. A neutral
extension reproduced its source policy exactly across 5,028 retained native
observations at 20, 40, 60, 100, 150, 200 and 400 bb, covering both players and
all four betting streets. This is an interface result, not a learned strategy.

The first 362 input columns were identical. The additional 25 relative-hand
features were present on 3,696 river observations and zero on the 1,332 earlier
street observations. Fourteen selected native Fold/Call observations matched
the independent diagnostic feature assembler exactly.

Both existing synthetic model objects, including context-specific preflop
table overrides, retained exact predictions after explicit zero-weight
extension. Their played-model average and own-history reach were also exactly
equal. A synthetic nonzero extension changed river predictions at every depth
while leaving earlier-street predictions unchanged. The model objects survived
content-hashed write/read roundtrips in their new format.

Nine negative controls rejected old/new format mismatches, the wrong registry,
fitting on either held-out context, incorrect network width, nonfinite weights,
a nonuniform initializer, and changed context fitting roles. Hidden batch labels
and unobserved runout metadata did not affect inputs. The old sources and all
inputs registered by the pending GPU learning trial remain unchanged.

The control took 59.859 seconds including storage accounting, with four CPU
workers and one BLAS thread each. Retained evidence is 2.21 MB allocated and
3.25 MB logical across eleven compressed files. A post-completion readback
checked 84 source/artifact hashes and exact equality in the saved comparison
arrays. This was not a new model-inference implementation or a GPU readback.

Evidence:
- `stack-context-relative-control-v1-registration.json`
- `stack-context-relative-control-v1-result.json`
- `S:/GTOpen-research/stack-context-relative-control-v1`

Registration SHA256:
`6e623a0aa0dee9e9af7513f648a27645632667697f78b042b95f206c08876d16`.
Executed sources and registered inputs are immutable.

This extends the existing research inference/model-object contract. It is not
a resumable full-training checkpoint, a conversion of the 302-input played
models, or a promotion of the 387-input diagnostic. CUDA parity for the new
context policy still needs its own check when resources permit.

Do not copy the pending diagnostic's learned weights into unrestricted play:
that experiment trains terminal river Fold/Call values, not the other legal
actions or earlier streets. Its outcome decides whether these new features
justify a matched broader learning comparison. A full trainer must preserve
context-local sampler/reservoir/accumulator state, complete played-bank cycles,
source-deal weights, and all legal actions. It must be evaluated with realistic
history-conditioned opponent ranges and independent preflop evidence.

No new poker deals, strategic labels, GPU training, deployment or GitHub push
occurred. Production 56708 is unchanged. The primary next step is the already
queued relative-input learning trial and its registered readback, not more
repetition of these interface controls.
