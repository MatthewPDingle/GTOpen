# R02: recovery after partial optimized GPU construction

Planned readiness qualification, not a speed experiment or deployment.
Keep 56708 read-only. Finish C14 and freeze its decision before editing runtime
source. Use the retained constructor, with the ordinary GPU path as fallback.

R01 verified plan rejection and an injected constructor error. It did not prove
cleanup after real device buffers were allocated. Add a test-only one-shot hook
inside cohort allocation after work/maps and at least one extra values buffer
exist. At that point request more device memory than the device total using the
same CUDA allocation API. Require an actual out-of-memory driver error; do not
fill the GPU with a pressure workload or change driver settings. Record that
real partial state existed and that the hook ran once. The hook must compile
out of the server/runtime build and remain disarmed in all other tests.

Exercise the actual adaptive constructor. Its failed optimized attempt must drop
partial owned state before ordinary GPU construction, then return the normal
engine with the allocation failure in its selection report. Preserve configured
budget, particle batch, HU-cache decisions, original solver age and arenas.
Run iterations and accuracy checks and compare full regret/strategy/root arrays
bit for bit with ordinary construction. Include frozen players and a point lock.
Verify captured execution, stop and CPU synchronization still work. Drop the
fallback, synchronize and construct the optimized path again to establish recovery.
Record memory before/at failure/after cleanup with stream synchronization; account
for asynchronous allocator pooling rather than assuming every cached byte is a leak.
Do not use a timing improvement or successful process exit as proof of cleanup.

Guard all build/test/GPU work with run07; build cap300s and numerical cap240s.
Archive exact sources, inputs, driver-error evidence and raw outputs; independently
verify the failure stage, returned mode, numerical equality and successful retry.
Retained code remains opt-in until unrelated research modules are separated and
an isolated server build/session qualification passes. Full native GPU and default
solver regression checks are required before promoting runtime changes.
