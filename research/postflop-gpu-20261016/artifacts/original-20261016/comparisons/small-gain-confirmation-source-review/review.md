# Four-arm current-E020 source review

PASS for the bounded source scope; material-cost qualification remains pending. All162 accepted inputs and the frozen package/reference pins match. E007/E008 reproduce only their original small hunks on E020. E032/E036 are byte-exact prior E020-based candidates, including their existing meaningful tests; none contains another candidate.

- E007: current up_action launches use128 threads, satisfying the new explicit maximum. The compiler hint can change registers, spills or code size; it does not prove9 resident blocks or compatibility with arbitrary larger launches. Inventory84/4.
- E008: the ascending scalar prefix retains+0 initialization, addition operands/order, loop bounds and all barriers. Compiler/native exactness and resource effects still require evidence. Inventory84/4.
- E032: there is no new terminal device storage. E020 already owns persistent terminal CFV rows and the allocation expression is unchanged. The added u32 field/query and stack scheduling are concrete costs; host padding, captured-graph allocation, locality and fallback/capability behavior are not proven cost-free. Its geometry/fallback unit and lifecycle controls are useful, but the fallback oracle shares dispatch code. Inventory85/4.
- E036: exact original E036 zero-row path, including the signed-zero-preserving present rewrite/barrier; E037 is absent. All rows pay the new predicate/collective work. The existing34-pair/68-launch original-GPU test is meaningful and must be freshly run; broader state/F32/lifecycle qualification remains. Inventory85/4.

No source correctness blocker found. None is certified free of material memory, compatibility or behavior costs by this source review, nor by a future timing pass alone. No code/build/native/GPU execution or production change was performed. Historical rejections remain intact.
