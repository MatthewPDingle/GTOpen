# Publication wording correction

Read this together with STACK-CONTEXT-COMPLETE-NATIVE-BOUNDS-20261003.md.
The original findings and publication receipt are preserved byte for byte.

The findings' phrase "four small Python wiring controls separately checked OS
command lines" is too broad. In the successful river-control suite, the two
bridge/trace children received independent OS command-line checks. The two
history/selected transport children checked argument/payload bindings without
independent OS command-line checks. The execution-v2 suite has one separate
OS-attestation control. Do not extend those checks to all 39 native receipts:
their observed_argv field records the owned Popen argument vector.

The independent publication review passed all technical byte/source/wiring
checks but intentionally saved overall passed=false for this prose issue.
This additive correction resolves the wording without rewriting that report or
rerunning any control. Its earlier audit-script helper argument-name failure is
also retained; it was not an implementation failure or a scientific attempt.
