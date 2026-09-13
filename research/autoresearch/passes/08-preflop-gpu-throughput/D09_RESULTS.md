# D09: narrower CDF writer indices rejected before timing

The writer is exact but fails the registered compiler admission gate. Direct
loaded registers increase from 26 to 30. The integer address-operation PTX
proxy increases from 69 to 84. Both use zero local/shared bytes. No full-work
C15 writer prototype is admitted and no speed claim is made.

252 paired device cases preserve every CDF float bit, guard value, inactive or
aliased row and unused sample position. Cases cover compact/noncompact indices,
gating, zero/recovery inputs, batch capacities 1/5/32, partial counts and sample
offsets 0/17/992. All 48 address witnesses pass, including byte offsets above
4 GiB (maximum 17,179,868,836). Oversized buffers remain refused.

Control PTX matches retained C14 byte-for-byte. The candidate changes only the
writer entry; all other 19 entry bodies are identical. The rewrite changes only
the writer element base and store indices, retaining final 64-bit byte pointer
conversion. Normalized loads and all scan additions remain unchanged.

The PTX proxy counts integer add/sub/multiply/mad/shift/conversion/bitwise
instructions in the writer entry. It is a static comparison, not hardware
counters or dynamic traffic. More instructions are sufficient to reject this
registered screen; they do not establish a measured runtime regression.

`check_d09.py` verifies source archives, immutable inputs, executable hash,
address cases, device case coverage, source rewrites, PTX entry differences,
resource records and the rejection. Output: `raw/d09-verified.json`.
`artifacts/d09-v1` preserves the exact tested source. The final test is marked
ignored because it is a manual compiler diagnostic requiring an output path;
that annotation is the only change from its archived tested body.

No runtime dispatch was added or changed; all new code is test-only. The
qualified server executable and 56708 remain untouched. The next proposal,
C16, is a different mechanism: fuse local CDF construction into terminal
consumption to avoid global scratch traffic, accepting extra prefix work.
