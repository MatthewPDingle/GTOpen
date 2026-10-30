"""Read-only byte accounting and unapplied candidate for future qualification."""
import difflib
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/preflop-evolution/representative-coverage-20260919'


def main():
    plan_path = OUT/'memory-plan.json'
    result_path = OUT/'report47-full-result.json'
    source_path = ROOT/'crates/solver/src/gpu/continuation_paging.rs'
    plan = json.loads(plan_path.read_text())
    result_raw = result_path.read_bytes()
    result = json.loads(result_raw)
    iteration = result['records'][-1]['iteration']
    arenas = sum(r['full_arena_bytes'] for r in plan['rows'] if not r['future_card_orbits'])
    assert result['manifest'] == plan['manifest']
    assert result['transferred_bytes'] == iteration*3*arenas
    original = source_path.read_text()
    old = '''                self.gpu.stream.memcpy_htod(s.as_slice(), &mut self.gpu.d_strat[q].slice_mut(0..self.lengths[q+2])).map_err(e)?;
                self.transferred_bytes += (self.lengths[q] + self.lengths[q+2]) as u64 * 4;'''
    new = '''                self.transferred_bytes += self.lengths[q] as u64 * 4;
                // Training reads both current regret policies, but only the
                // traverser's average sums. Evaluation uses synchronized host state.
                if q == p {
                    self.gpu.stream.memcpy_htod(s.as_slice(), &mut self.gpu.d_strat[q].slice_mut(0..self.lengths[q+2])).map_err(e)?;
                    self.transferred_bytes += self.lengths[q+2] as u64 * 4;
                }'''
    assert original.count(old) == 1
    candidate = original.replace(old,new)
    patch = ''.join(difflib.unified_diff(original.splitlines(keepends=True),candidate.splitlines(keepends=True),
                    fromfile='a/crates/solver/src/gpu/continuation_paging.rs',
                    tofile='b/crates/solver/src/gpu/continuation_paging.rs'))
    patch_path = OUT/'paging-own-average-candidate.patch'
    output = OUT/'paging-transfer-audit.json'
    assert not patch_path.exists() and not output.exists()
    patch_path.write_bytes(patch.encode('utf-8'))
    inputs = [Path(__file__),plan_path,source_path,ROOT/'crates/solver/src/gpu/mod.rs',
              ROOT/'crates/solver/src/gpu/kernels.cu',ROOT/'crates/solver/tests/continuation_paging.rs']
    summary = dict(checkpoint=iteration, actual_transferred_bytes=result['transferred_bytes'],
                   all_board_arena_bytes=arenas, baseline_bytes_per_iteration=3*arenas,
                   proposed_bytes_per_iteration=5*arenas//2, proposed_saved_bytes_per_iteration=arenas//2,
                   fractional_byte_reduction=1/6, patch_applied=False, candidate_executed=False,
                   result_at_checkpoint_sha256=hashlib.sha256(result_raw).hexdigest(),
                   candidate_patch_sha256=hashlib.sha256(patch_path.read_bytes()).hexdigest(),
                   inputs_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
                   interpretation='Counter exactly matches two uploads of all arenas plus one combined download per iteration. Candidate omits only opposing average-strategy uploads during training. Its dataflow rationale is not a parity test. Bytes are counted arena traffic, not a measured timing breakdown or proof of a speedup. No host-memory savings and no production/current-queue change.')
    output.write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='inputs_sha256'},indent=2))


if __name__=='__main__':
    main()
