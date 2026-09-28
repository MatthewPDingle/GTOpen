# Coverage collection archive-root correction

The first archive fixture failed before any learned inference, collection,
fitting or scoring. The reused archive writer correctly rejected the new store
because its ownership guard was still bound to the old target-learning store.
No historical archive was changed or deleted. The incomplete synthetic fixture
and failure record remain preserved under control/ and the study failure JSON.

Version 2 of the coverage collector uses a separately versioned archive writer
bound to the new coverage store. Its exact-owned transient removal policy is
unchanged. The new control runs under control-v2/ and publishes a new control
identity. Original collector v1 and selection/plan bytes remain unchanged.
The not-yet-executed fit/readback scripts reference the new collector/writer.

This is an execution routing correction only. Physical deals, memberships,
targets, seeds, budgets, model design and evaluation gates are unchanged.
