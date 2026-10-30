# D036 additive preparation revision 3

R2's build failed before CUDA execution:62 E0277 errors because the frozen cudarc rlib was built without its optional std::error::Error implementations. Its complete failed attempt remains immutable at `../D036-fold-shuffle-probe-r2`. R2 manifest SHA256: `c23945d7afbf1364931047f58b41dc2b5460d854d39225fb3cbd86d4e298be18`.

Only error conversion is repaired. `ProbeError(String)` implements Display and explicit From conversions for cudarc DriverError and CompileError (using their unconditional Debug implementations), std::io::Error, serde_json::Error, String and &str. There is no blanket From implementation. Every statement beginning with the first constant, including all numerical functions, CUDA calls, resource queries, scheduling, guard checks, outputs and failure exit behavior, is byte-identical to R2. CUDA/corpus/protocol/runner/rlib inputs are unchanged. No feature or dependency rebuild is requested.

After root owns the serialized slot and independent review passes, execute only this new attempt:

```powershell
& 'C:\Program Files\Python312\python.exe' -B 'S:\GTOpen-research\postflop-gpu-20261016\runs\D036-fold-shuffle-probe-r3\run.py' --execute
```

Copied older README/revision commands are historical; this command selects R3. Preparation and seal scripts are retained historical reproducibility inputs and must not be rerun over sealed files. `failed-r2-evidence.json` preserves the full R2 file inventory/hashes; original logs are not overwritten or treated as a numerical failure. No build or GPU call was performed during R3 preparation.
