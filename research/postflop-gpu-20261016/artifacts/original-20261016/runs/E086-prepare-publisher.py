"""Adapt common publication bookkeeping; write a new bit-field ledger entry."""
import ast
from pathlib import Path
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
source=(R/'runs/E085-publish-primary.py').read_text()
head=source[:source.index('ledger=old.REPO/')]
head=head.replace('E085','E086').replace('E086-resource-r2','E086-resource')
head=head.replace('D136-strategy-streaming-store','D137-bitfield-membership')
head=head.replace('E086-kernel-control-root-check','E086-kernel-control')
head=head.replace('819','425').replace('1638','850')
head=head.replace('strategy streaming-store form','unsigned64 length1 up_chance bit-field form')
head=head.replace('cache-operator, other-array, threshold, helper/clobber/source-scope/placement','other-kernel, packing, width, precision, helper, threshold, source-scope or placement')
head='\n'.join(line for line in head.split('\n')if 'precompiler_emission_observer_correction_sha256'not in line and 'precompiler_correction_original_compiler_native_observations'not in line)
head=head.replace('for folder in folders:\n','for folder in dict.fromkeys(folders):\n',1)
tail=r'''
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md'
raw=ledger.read_bytes()
assert b'### D137 and E086 chance bit-field extraction' not in raw
entry='''+"'''"+r'''

### D137 and E086 chance bit-field extraction

Previous goal turn progressed by closing E085 after0.5220789829%initial gain and strict two-tone guard failure. Current turn revalidates accepted source/main/live/protectedPTX custody and idle GPU. The accepted private up_chance PTX already lowers original left-onehot/AND to right-shift/AND, so an ordinary source-direction rewrite is declined without a candidate. New bounded current-ledger/retained-CU/all-local-ref audit found no explicit bfe.u64 form. E048canonical-card-comparison/removed-mask, E039sharedmetadata, E046packing and E085streaming-store forms stay closed; no hunk composed.

One CUDA-only candidate changes just up_chance's integer membership predicate to pure register unsigned64bit-field extraction, positioncc_card[t], length1. Typed64bit input/output and32bit position, no hidden memory or volatile/clobber needed. Original mask/card arrays, ABI, selected children, all ordered float additions/products, loop/permutation, other8kernels, host/launch/graph, allocation/quality/save retained. Source reversal exact. CPU85,336 canonical/basis/complement checks pass; actual GPU and performance not inferred. NVIDIA PTX bit-field semantics primary source recorded. Virtual instruction may lower to identical or slower native code; no SASS-speed claim.

One sealed resource compiler/process,4NVRTCcompiles120/75. Other8normalized entries and15argumentABI exact, bfe emitted onlycandidate. Actual30registers/local0/static0/dynamic0/maxthreads1024/stack1024 and64/128/256theoreticaloccupancy24/12/6 unchanged. Reuse original425canonical chance descriptors/order:157down unchanged controls plus268up cases,850launches. Delete only historical candidate card-ID ABI builder branches so both variants use original mask ABI; complete original card-ID/mask images still read back. Corpus metadata changes only ID/rawmagic labels. All18,950,844full output words,3,951,272actual immutable words,13,112,256guards and1,840,420independent finite down membership relations pass. Every canonical1326hand/dealt52card relation individually exercised; tails/count0/empty/permutation/nonfinite/subnormal/overflow/fivewidth controls retained. Separate raw reader2,508,695checks. All3full raw files stayS. Finite corpus/small offsets, no malformed-address/universal NaN proof.

Two fresh isolated feature/primary builds terminal0, E080 CUDA restored aftereach. Frozen primary '''+"'''"+r'''+old.sha(H/'protocol.json')+'''+"'''"+r''': V086unit86pass/4ignored; exactly B284/E086R1,E086R2/B285,B286/E086R3. All18complete non-timing records/138checkpoints exact unchangedE020C1, no exclusions/extensions/historical pooling. Sum fixture-median completecycle '''+"'''"+r'''+str(perf['baseline_full_cycle_ms'])+' -> '+str(perf['candidate_full_cycle_ms'])+'ms, unrounded gain '+str(perf['observed_gain_pct'])+'%. Guards '+json.dumps(perf['fixture_regression_guard'],separators=(',',':'))+'. '+reason+'\n\nRoot '+str(root['checks'])+'raw/arithmetic checks, assessmentSHA '+old.sha(qp)+'. '+str(len(pub))+'small artifacts HTTPbyte-verified. Primary full scientific records/whole-arena fingerprints exact; full raw primary arena bytes not independently compared. All owned children terminal, GPUlockabsent, accepted/main/live/protectedPTX custody passed. No adoption/livechange. Accepted E08014.7414188354%measured cumulative gain unchanged,lastprimaryB286,goalactive.\n'
nl=b'\r\n' if b'\r\n' in raw else b'\n'
ledger.write_bytes(raw+entry.encode().replace(b'\n',nl))
subprocess.run(['git','commit','--only','-m','research: screen chance bit-field extraction','--',
                'research/postflop-gpu-20261016/experiments.md'],cwd=old.REPO,check=True)
old.custody()
print(json.dumps({'decision':q['decision'],'gain_pct':perf['observed_gain_pct'],
    'guard_failures':[g['fixture_id']for g in perf['fixture_regression_guard']if g['failed']],
    'HTTP_files':len(pub)}),flush=True)
'''
# Raw tail deliberately preserves Python escape sequences in the generated file.
target=R/'runs/E086-publish-primary.py';assert not target.exists()
text=head+tail
ast.parse(text);target.write_text(text,encoding='utf-8',newline='\n')
print(target,flush=True)
