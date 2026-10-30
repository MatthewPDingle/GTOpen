# D037 independent resource/provenance audit

PASS for the bounded no-launch compiler/resource diagnostic. The sealed manifest783bce1a…eadf63, candidate/base sources, dependency rlibs, binary, NVRTC DLLs and before/after input hashes match. One rustc invocation and one native probe returned zero; all16 raw markers (device,14 resource rows,complete) match the report. The probe source contains no kernel-launch or resource-mutation API. All five protected accepted E015 source hashes were unchanged at audit time.

The seven shapes use the exact baseline formula4*nh_o+8*m_max and candidate formula4*nh_o+16*m_max. Rainbow counts/allocations match the closed D033 raw graph descriptors; river counts233/280 match immutable original/E015 anchors and the final-board empty-extra-mask invariant. The1326 row is a conservative capacity bound, while empty/single rows are synthetic. Two-tone-specific occupancy was not queried.

| Shape | Dynamic shared bytes, base→candidate | Theoretical128-thread blocks/SM |
|---|---:|---:|
| Rainbow P0 |3788→6300|12→12|
| Rainbow P1 |3044→5060|12→12|
| Derived river P0 |3360→5600|12→12|
| Derived river P1 |2796→4660|12→12|
| Conservative1326 |15912→26520|5→3|
| Empty sorted opponent |1276→1276|12→12|
| Single sorted opponent |1284→1292|12→12|

Registers fall40→38; both variants report zero local bytes,1040 static shared bytes and1024 maximum threads. Every queried total is below the49152-byte default per-block shared-memory limit, with positive theoretical occupancy. All eight other PTX entrypoints are byte-identical.

The conservative wide shape loses40% of theoretical block residency (5→3). Preserve this as a material wide-range risk; it is not an observed runtime slowdown. Passing resource limits does not establish an actual successful launch, numerical equivalence or performance benefit. E020 may proceed only as a separately reviewed native candidate under its frozen qualification protocol. No GPU/build or production/status action was performed by this audit.

validation.json records220 assertions and47 hashed inputs. Compiler/probe process durations1.797/1.844seconds are operational metadata, not solver timing.
