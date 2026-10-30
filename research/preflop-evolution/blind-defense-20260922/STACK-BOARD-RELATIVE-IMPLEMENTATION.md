# Implementation details frozen before the paired learning comparison

The387-input first layer computes the original362-column linear operation and
adds a25-column linear operation initialized to zero. This preserves the exact
original computation at initialization and avoids changing its rounding simply
by widening a matrix multiplication. Both parts are trained jointly with the
unchanged Adam settings and loss. The candidate still has3200 additional weights
across its two player networks. Report candidate timing separately; this change
does not promise faster inference.

CPU controls must establish identical initial scores and original parameters,
nonzero gradients through the additional features, exact checkpoint round trips,
rejection of changed hashes/wrong dimensions, and absence of CUDA use. GPU admission
will additionally check exact initial outputs on the same CUDA inputs and paired
batch draws before fitting. Both fits record first-batch hashes and generator
states at each checkpoint. Validation selection and final-test timing remain as
in the original prospective plan.

The trial may prepare CPU inputs first while the GPU is occupied. Freeze the full
learning registration before preparation. Retain a hashed complete preparation
manifest before releasing its lock; a later GPU invocation must verify it and
all registered sources. Report both stage costs and enforce the3600-second total
work cap across preparation and fitting/evaluation. Waiting for admission before
either stage starts does not count as scientific execution. Fresh storage
accounting is required at each stage admission. Both stages share the256MB new
evidence cap plus128MB reserve. Test-board labels are prepared only after all four
model identities are frozen. A started interrupted scientific attempt is retained;
it must not be silently restarted under a new name or with changed inputs.

Keep512 original fitting board/count files unchanged; retain only their25-column
extensions. New32 validation boards use the original factor/count generator plus
the same qualified extension. Public vectors receive25 zeros. Check original
columns/counts, legal hand ordering and context/actor/price correspondence before
fitting. Nothing here is a production checkpoint or deployment.
