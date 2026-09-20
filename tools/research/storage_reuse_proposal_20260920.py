"""Prepare RAM-allocation reuse separately from owner-only transfer reduction."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/ssd-storage-20260920'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    prior=json.loads((OUT/'owner-download-v1-proposal.json').read_text())
    source=ROOT/prior['candidate'];assert sha(source)==prior['candidate_sha256']
    candidate=source.read_text()
    changes=[('''let mut next: [Vec<f32>;2]=std::array::from_fn(|k|vec![0.;arrays[p+2*k].len()]);
        let downloaded_bytes=next.iter().map(|a|a.len() as u64*4).sum::<u64>();''','''let download_lengths=[arrays[p].len(),arrays[p+2].len()];
        let downloaded_bytes=download_lengths.iter().sum::<usize>() as u64*4;
        let mut next: [Vec<f32>;2]=std::array::from_fn(|k|if self.disk_backed {vec![0.;download_lengths[k]]} else {Vec::new()});'''),
        ('''                let g=&mut self.gpu.gpu;
                for k in 0..2 {g.stream.memcpy_dtoh(&compact[p+2*k].slice(0..next[k].len()),&mut next[k]).map_err(crate::gpu::e)?;}
            } else {
                let g=&mut self.gpu.gpu;
                g.stream.memcpy_dtoh(&g.d_regrets[p].slice(0..next[0].len()),&mut next[0]).map_err(crate::gpu::e)?;
                g.stream.memcpy_dtoh(&g.d_strat[p].slice(0..next[1].len()),&mut next[1]).map_err(crate::gpu::e)?;
            }''','''            }
            let g=&mut self.gpu.gpu;
            for k in 0..2 {
                let dst=match &mut self.state {State::Memory(a)=>&mut a[p+2*k],State::Disk(_)=>&mut next[k]};
                let src=if self.plan.iso_active {&workspace.compact.as_ref().unwrap()[p+2*k]}
                    else if k==0 {&g.d_regrets[p]} else {&g.d_strat[p]};
                g.stream.memcpy_dtoh(&src.slice(0..download_lengths[k]),dst).map_err(crate::gpu::e)?;
            }'''),
        ('''State::Memory(a)=> {
                a[p]=std::mem::take(&mut next[0]);
                a[p+2]=std::mem::take(&mut next[1]);
            },''','''// Successful synchronization above makes in-place RAM copies visible.
            State::Memory(_)=> {},''')]
    for old,new in changes:
        assert candidate.count(old)==1,old
        candidate=candidate.replace(old,new)
    dest=OUT/'reuse-download-v1-proposal.rs';assert not dest.exists();dest.write_text(candidate)
    result=dict(base_candidate=str(source.relative_to(ROOT)),base_sha256=sha(source),
        candidate=str(dest.relative_to(ROOT)),candidate_sha256=sha(dest),native_source_changed=False,
        compiled=False,tested=False,replacements=len(changes))
    with (OUT/'reuse-download-v1-proposal.json').open('x') as f:json.dump(result,f,indent=2)
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
