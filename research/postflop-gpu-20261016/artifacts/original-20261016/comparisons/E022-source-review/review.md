# E022 independent source review

PASS_SOURCE_ONLY. The frozen candidate changes exactly one thread0 bound and its loop condition; reversing those bytes recovers accepted E020 CUDA. No actionable source defect remains.

For m>0, c=ceil(m/B)>0 and L=floor((m-1)/c). Exactly threads0..L have nonempty chunks. Their bases use only chunk_sum[0..L], so computing original recurrence entries1..L preserves every consumed value and addition order. The final total uses prefix[m-1], not the discarded chunk_sum[L+1]. Each inactive thread still reads an initialized slot but performs no prefix write. For m=0 the conditional avoids division by zero, all prefix loops are empty, and the existing total remains literal zero. The 339,712 integer shapes m0..1326/B1..256 satisfy bounds and chunk geometry. All existing barriers and shared257-slot initialization remain.

This is distinct from rejected E008: E008 rewrote the recurrence into a register carry while retaining every entry; E022 retains the expression and removes only unconsumed iterations. The m236 prose count was corrected additively to11; original judgment remains preserved.

Benefit is unproved. At B128, only3 additions disappear for m252 and8 for m1081/1326, versus24 for m314 and43 for m257. Extra integer division and changed code generation may cost more than the tail. Source reasoning does not establish native exceptional-value behavior or performance. Use the unchanged primary, exactness, broad-range holdout and cumulative gates; no new broad harness is warranted.

No production edit, build, GPU or native solver execution occurred in this review.
