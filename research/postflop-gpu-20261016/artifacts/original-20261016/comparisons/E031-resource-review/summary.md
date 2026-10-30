# E031 resource review

The terminal audit confirms REJECTED_RESOURCE_SCREEN. All20 retained rows were checked. Rainbow p0 and two-tone p0 drop from12 to11 theoretical active blocks per SM, violating the predeclared no-decrease condition. Other registered shapes retain their counts. This is a resource-screen failure, not a measured runtime slowdown.

Registers rise38 to39, local bytes remain0, and static shared allocation rises1040 to1248 bytes. The extra53-u32 declaration is212 bytes; declared totals1028/1240 versus queried1040/1248 show effective padding12/8 and explain the observed208-byte allocation difference. The other eight PTX entries are byte-exact. The separate changed-entry review finds matching arithmetic/scan structure within its stated source/PTX scope; no numerical kernel execution occurred.

The single authorized compiler/resource query completed successfully with zero kernel or solver launches. All162 accepted E020 source hashes and the live desktop-runtime binary hash remain unchanged. No direct numerical test, primary cohort, rescue, performance acceptance or deployment follows this failed screen.
