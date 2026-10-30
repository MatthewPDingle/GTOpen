E033 remains failed at the unit gate: 86 passed, 1 failed, 4 ignored; native exit101. The sole failure is an incorrect unconditional eligibility assertion for a36-byte buffer whose intentional aligned window is0. All3newtests passed. Both builds and restoration were verified; no primary benchmarks ran.

The prior source review missed this assertion scope. A separately registered assertion-only successor is justified with all numerical assertions and fresh gates retained. This is no numerical or performance acceptance.
