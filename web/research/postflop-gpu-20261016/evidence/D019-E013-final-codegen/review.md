# D019 E013 final ThinLTO code generation

PASS for the code-generation hypothesis, not a correctness or performance acceptance. The actual postflop_autoresearch executable was compiled with --emit=asm,link. It was not run. Compilation and preservation completed successfully in 62.782 seconds; all 109 recorded source/input hashes match before and after. Frozen E012 binaries/manifests were untouched.

| Final ThinLTO function | rintf call sites | roundps sites | roundss sites |
| --- | ---: | ---: | ---: |
| E013 SSE writer | 0 | 0 | 0 |
| Typed I16 encoder | 0 | 2 | 1 |
| Typed U16 encoder | 0 | 2 | 1 |
| Portable Store::write_f32 | 10 | 0 | 0 |

The writer calls the retained typed encoder functions. Each typed encoder now contains packed multiplies/rounding in its vector loop plus a scalar tail. More strongly, each complete encoder assembly body is identical to its corresponding D015 standalone body after renaming only the function symbol and compiler local-label identifiers. Instructions, registers, constants and branch layout match; assembly-review.json records normalized hashes and the source artifact hashes.

This demonstrates why D017/D018 library assembly was insufficient: final ThinLTO vectorized both helpers. Their sealed files remain unchanged, with the separate runs/D017-D018-evidence-boundary.md addendum documenting the restriction. D019 establishes E013 final code generation only; it does not establish the final E012 instruction sequence or prove why E012 readback barely improved.

Preserved final executable: generated/postflop_autoresearch-ba6a3e8216b3a7e5.exe, 2,063,360 bytes, SHA256 a02f6c3c36062277a5210dbfe76f9b319b9aa58e0bfd300c9bdc9de65dba3c1b. All 35 newly generated assembly modules plus that executable were copied and hash-verified. The solver post-LTO module is generated/postflop_autoresearch-ba6a3e8216b3a7e5.solver-e2d3113d740308c1.solver.d49c914e8c5c5922-cgu.0.rcgu.o.rcgu.s (7,759,923 bytes, SHA256 9b2126cfa5510d3791a00b94b691e72a85860e257ce98cd1a37d668d589711ae).

Source review remains PASS for the private typed boundary, feature gate, portable fallback and original encoder delegation. Root must still run exact state/lifecycle tests and the fixed complete-cycle evaluator. D015/D019 codegen similarity does not itself establish a full readback or solve speedup.
