# D017 / D018 evidence-boundary addendum

The sealed D017 and D018 files are preserved unchanged. Their cargo rustc --lib assembly shows the library-stage output, while D015 used a standalone thin-LTO executable. Absence of packed rounding in the library output does not prove its absence after final executable link-time optimization. Accordingly, D017 scalar-codegen observations are confirmed only for that artifact stage, and D018 does not justify rejecting E013. No final-executable vectorization claim follows from either library artifact. D019 is the separately authorized actual benchmark-executable assembly check; it compiles but does not run the benchmark.

D019 completed: final benchmark ThinLTO assembly contains two roundps sites and one roundss tail per typed encoder, with no rintf. Complete normalized encoder bodies match D015. This confirms the stage distinction; E013 is not rejected by D018. See D019-E013-final-codegen/review.md.
