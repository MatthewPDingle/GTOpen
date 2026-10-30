# D037 exact candidate source review

PASS_SOURCE_ONLY. The frozen two-file candidate implements the approved design without scope drift. No build, CUDA/solver execution or production-source edit was performed by this reviewer. Resource feasibility and native numerical/performance acceptance remain pending.

Candidate CUDA075651690d59ede225c17ff9674662e040d40460a5e2b5436fd6fa7d4f5d663b; host mod.rsce71fa3bfb797baade1efe50beba68e971b88c7da1c9547d306e0b6e9245ee8d; manifest0be733fa538bc03b97782f520b4eeb48a3dc10914882f977c90e1fc7ea2a7946. All sealed candidate artifacts verify.

Independent byte reversal of the two inserted integer-cache declarations/copy loop and the one inner lookup returns the exact accepted kernel file. Reversing exactly two host8→16 sizing substitutions returns the accepted mod.rs bytes. No other kernel, prefix operation, float expression, barrier, loop predicate, ABI, launch shape/order, host method, graph state or allocation changed.

The cache starts after prefix[m_o], uses2*m_o u32 entries, reads from the current slot's global card_base and indexes by t-card_base. Plan construction proves the span and consumed bounds. Existing uniform CTA early-out and first barrier preserve initialization-before-use; empty opponent lists cause no cache read. The existing layout alignment applies unchanged. Both training and evaluation reserve sufficient dynamic shared memory at the plan maximum; continuation users inherit those methods.

The prospective no-launch resource probe may use the two verified rainbow shapes and the conservative1326/1326 bound. That is sufficient bounded feasibility evidence, provided it does not label two-tone/river per-plan occupancy as measured. Actual shared/register/local/occupancy queries are still necessary; no persistent VRAM budget addition is warranted. Existing exact solver checks remain the first native numerical screen. A broad duplicate numerical or graph harness is unnecessary absent a specific gap.
