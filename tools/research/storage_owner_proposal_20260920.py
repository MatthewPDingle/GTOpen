"""Prepare an isolated, reviewable owner-only download proposal; do not alter native source."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/ssd-storage-20260920'
SRC=ROOT/'crates/solver/src/gpu/continuation_storage.rs'
def main():
    source=SRC.read_text();candidate=source
    changes=[
        ('let disk_arrays=match &self.state', 'let mut disk_arrays=match &self.state'),
        ('let mut next: [Vec<f32>;4]=std::array::from_fn(|k|vec![0.;arrays[k].len()]);',
         'let mut next: [Vec<f32>;2]=std::array::from_fn(|k|vec![0.;arrays[p+2*k].len()]);\n        let downloaded_bytes=next.iter().map(|a|a.len() as u64*4).sum::<u64>();'),
        ('for q in 0..2 {self.copy_canonical(compact,q,true)?;}', 'self.copy_canonical(compact,p,true)?;'),
        ('for k in 0..4 {g.stream.memcpy_dtoh(&compact[k].slice(0..next[k].len()),&mut next[k]).map_err(crate::gpu::e)?;}',
         'for k in 0..2 {g.stream.memcpy_dtoh(&compact[p+2*k].slice(0..next[k].len()),&mut next[k]).map_err(crate::gpu::e)?;}'),
        ('''for q in 0..2 {
                    g.stream.memcpy_dtoh(&g.d_regrets[q].slice(0..next[q].len()),&mut next[q]).map_err(crate::gpu::e)?;
                    g.stream.memcpy_dtoh(&g.d_strat[q].slice(0..next[q+2].len()),&mut next[q+2]).map_err(crate::gpu::e)?;
                }''', '''g.stream.memcpy_dtoh(&g.d_regrets[p].slice(0..next[0].len()),&mut next[0]).map_err(crate::gpu::e)?;
                g.stream.memcpy_dtoh(&g.d_strat[p].slice(0..next[1].len()),&mut next[1]).map_err(crate::gpu::e)?;'''),
        ('State::Memory(a)=>*a=next,', '''State::Memory(a)=> {
                a[p]=std::mem::take(&mut next[0]);
                a[p+2]=std::mem::take(&mut next[1]);
            },'''),
        ('if let Err(error)=d.replace(&next,t)', '''let mut complete=disk_arrays.take().ok_or("missing loaded disk state")?;
                complete[p]=std::mem::take(&mut next[0]);
                complete[p+2]=std::mem::take(&mut next[1]);
                if let Err(error)=d.replace(&complete,t)'''),
        ('self.transferred_bytes+=self.storage_bytes*2;', 'self.transferred_bytes+=self.storage_bytes+downloaded_bytes;')]
    for old,new in changes:
        assert candidate.count(old)==1,old
        candidate=candidate.replace(old,new)
    dst=OUT/'owner-download-v1-proposal.rs';assert not dst.exists();dst.write_text(candidate)
    audit=dict(source=str(SRC.relative_to(ROOT)),source_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),
        candidate=str(dst.relative_to(ROOT)),candidate_sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),
        native_source_changed=False,compiled=False,tested=False,replacements=len(changes))
    with (OUT/'owner-download-v1-proposal.json').open('x') as f:json.dump(audit,f,indent=2)
    print(json.dumps(audit,indent=2))
if __name__=='__main__':main()
