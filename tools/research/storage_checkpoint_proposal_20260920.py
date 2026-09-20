"""Prepare resumable-state APIs outside active/frozen native sources; no build or run."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/ssd-storage-20260920'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

DISK_METHODS=r'''
    /// Checkpoint metadata; paths are always derived from the independently expected key.
    pub(super) fn descriptor(&self) -> [u64;8] {
        [self.key,self.generation,u64::from(self.iteration),self.lengths[0] as u64,
            self.lengths[1] as u64,self.lengths[2] as u64,self.lengths[3] as u64,self.hash]
    }
    pub(super) fn reopen(root:&Path, key:u64, iteration:u32, lengths:[usize;4], descriptor:[u64;8])
        -> io::Result<(Self,[Vec<f32>;4])> {
        // Check against rebuilt shapes BEFORE allocating payload arrays. Snapshot records
        // are immutable generation zero; a live parked generation is not a checkpoint.
        if descriptor[0]!=key || descriptor[1]!=0 || descriptor[2]!=u64::from(iteration)
            || descriptor[3..7]!=lengths.map(|n|n as u64) {
            return Err(invalid("Checkpoint key, generation, iteration or rebuilt shape mismatch"));
        }
        let state=Self{root:root.to_path_buf(),key,generation:0,iteration,lengths,hash:descriptor[7]};
        let arrays=state.load()?;
        Ok((state,arrays))
    }
'''

STORAGE_METHODS=r'''
    /// Research snapshot of one canonical RAM entry. Whole-study completion is external.
    pub fn checkpoint_export(&self, root:&Path, key:u64, completed:u32) -> Result<[u64;8],String> {
        if self.poisoned || self.iteration!=completed || completed==0 {
            return Err("Checkpoint requires a healthy completed iteration".into());
        }
        // Broad training is currently all-RAM. Do not silently add disk-to-disk copying,
        // extra temporary arrays or unbudgeted writes to the separately tested SSD path.
        let State::Memory(arrays)=&self.state else {return Err("Checkpoint export currently requires RAM-backed state".into());};
        let snapshot=DiskState::create(root,key,arrays,completed).map_err(|e|e.to_string())?;
        Ok(snapshot.descriptor())
    }
    /// Import into a freshly constructed entry; next sweep uploads the canonical state.
    pub fn checkpoint_import(&mut self, root:&Path, key:u64, completed:u32, descriptor:[u64;8]) -> Result<(),String> {
        if self.poisoned || self.iteration!=0 || self.transferred_bytes!=0 || completed==0 {
            return Err("Checkpoint import requires fresh healthy state".into());
        }
        let State::Memory(current)=&self.state else {return Err("Checkpoint import currently requires RAM-backed state".into());};
        let lengths=std::array::from_fn(|k|current[k].len());
        let (_,arrays)=DiskState::reopen(root,key,completed,lengths,descriptor).map_err(|e|e.to_string())?;
        self.state=State::Memory(arrays);self.iteration=completed;
        Ok(())
    }
'''

def main():
    targets=[('disk','crates/solver/src/gpu/continuation_disk_state_tests.rs','impl DiskState {',DISK_METHODS),
        ('storage','crates/solver/src/gpu/continuation_storage.rs','    pub fn materialize(&self)',STORAGE_METHODS)]
    result={}
    for name,relative,marker,methods in targets:
        source=ROOT/relative;text=source.read_text();assert text.count(marker)==1
        if name=='disk':candidate=text.replace(marker,marker+'\n'+methods)
        else:candidate=text.replace(marker,methods+'\n'+marker)
        dest=OUT/f'checkpoint-v1-{name}-proposal.rs';assert not dest.exists();dest.write_text(candidate)
        result[name]=dict(source=relative,source_sha256=sha(source),candidate=str(dest.relative_to(ROOT)),candidate_sha256=sha(dest))
    phase=OUT/'phase-timing-v1-proposal.rs';candidate=phase.read_text()
    edits=[('impl Game {','#[path="support/stored_checkpoint.rs"]\nmod checkpoint;\nimpl Game {'),
        ('let mut game=Game::new(&data,&manifest);let mut records=vec![];',r'''let mut game=Game::new(&data,&manifest);let mut records=vec![];
    let checkpoint_identity=checkpoint::identity(std::path::Path::new(&a[0]),std::path::Path::new(&a[1])).unwrap();
    let resumed=match std::env::var("GTO_RESUME_CHECKPOINT") {
        Ok(path)=>game.checkpoint_load(std::path::Path::new(&path),&checkpoint_identity).expect("Restore failed; discard entire game"),
        Err(_)=>0,
    };
    assert!(target>0 && target>=resumed,"target precedes checkpoint");
    if let Ok(path)=std::env::var("GTO_RESTORED_COPY") {
        assert!(resumed>0);game.checkpoint_save(std::path::Path::new(&path),resumed,&checkpoint_identity).unwrap();
    }'''),
        ('for t in 1..=target {','for t in resumed.max(1)..=target {'),
        ('for p in 0..2 {let w=game.weights.clone();game.walk(p,0,&w[p],&w[1-p],t,false);}',
         'if t>resumed {for p in 0..2 {let w=game.weights.clone();game.walk(p,0,&w[p],&w[1-p],t,false);}}'),
        ('if [1,20,100,500,2000,5000,10000].contains(&t)||t==target {',
         'if [1,20,100,500,2000,5000,10000].contains(&t)||t==target||t==resumed {'),
        ('"root_normalizer":game.z,"entry_cutoff":0.00001,"records":records,',
         '"root_normalizer":game.z,"entry_cutoff":0.00001,"records":records,"resumed_iteration":resumed,')]
    for old,new in edits:
        assert candidate.count(old)==1,old
        candidate=candidate.replace(old,new)
    ending='    }\n}\n';assert candidate.endswith(ending)
    candidate=candidate[:-len(ending)]+'''    }
    if let Ok(path)=std::env::var("GTO_SAVE_CHECKPOINT") {
        game.checkpoint_save(std::path::Path::new(&path),target,&checkpoint_identity).unwrap();
    }
}
'''
    dest=OUT/'checkpoint-v1-example-proposal.rs';assert not dest.exists();dest.write_text(candidate)
    result['example']=dict(source='crates/solver/examples/integrated_continuation_stored.rs',
        source_sha256=sha(phase),candidate=str(dest.relative_to(ROOT)),candidate_sha256=sha(dest))
    helper=OUT/'checkpoint-v1-helper-proposal.rs'
    result['helper']=dict(source='crates/solver/examples/support/stored_checkpoint.rs',
        candidate=str(helper.relative_to(ROOT)),candidate_sha256=sha(helper))
    result['scope']='Unapplied RAM-study checkpoint API proposal, not compiled or qualified. SSD parking remains unchanged.'
    with (OUT/'checkpoint-v1-proposal.json').open('x') as f:json.dump(result,f,indent=2)
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
