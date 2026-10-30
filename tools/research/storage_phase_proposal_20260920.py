"""Prepare example-only phase timing without changing an active native build or run."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/ssd-storage-20260920'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    source=ROOT/'crates/solver/examples/integrated_continuation_stored.rs';candidate=source.read_text()
    edits=[('''let mut game=Game::new(&data,&manifest);let mut records=vec![];''','''let mut game=Game::new(&data,&manifest);let mut records=vec![];
    let setup_seconds=start.elapsed().as_secs_f64();let mut training_seconds=0.;let mut evaluation_seconds=0.;
    println!("STUDY_PHASE {}",json!({"phase":"construction_complete","elapsed_seconds":setup_seconds}));'''),
        ('''    for t in 1..=target {
        for p in 0..2 {let w=game.weights.clone();game.walk(p,0,&w[p],&w[1-p],t,false);}
        if [1,20,100,500,2000,5000,10000].contains(&t)||t==target {
            let evaluation=game.evaluate();println!''','''    for t in 1..=target {
        let phase_start=std::time::Instant::now();
        for p in 0..2 {let w=game.weights.clone();game.walk(p,0,&w[p],&w[1-p],t,false);}
        let iteration_seconds=phase_start.elapsed().as_secs_f64();training_seconds+=iteration_seconds;
        println!("STUDY_PHASE {}",json!({"phase":"iteration_complete","iteration":t,"iteration_seconds":iteration_seconds,
            "training_seconds":training_seconds,"elapsed_seconds":start.elapsed().as_secs_f64()}));
        if [1,20,100,500,2000,5000,10000].contains(&t)||t==target {
            println!("STUDY_PHASE {}",json!({"phase":"evaluation_start","iteration":t,"elapsed_seconds":start.elapsed().as_secs_f64()}));
            let evaluation_start=std::time::Instant::now();let evaluation=game.evaluate();
            evaluation_seconds+=evaluation_start.elapsed().as_secs_f64();
            println!("STUDY_PHASE {}",json!({"phase":"evaluation_complete","iteration":t,"evaluation_seconds":evaluation_seconds,
                "elapsed_seconds":start.elapsed().as_secs_f64()}));
            println!'''),
        ('''"root_normalizer":game.z,"entry_cutoff":0.00001,"records":records,''','''"root_normalizer":game.z,"entry_cutoff":0.00001,"records":records,
                "phase_timing":{"setup_seconds":setup_seconds,"training_seconds":training_seconds,"evaluation_seconds":evaluation_seconds},''')]
    for old,new in edits:
        assert candidate.count(old)==1,old
        candidate=candidate.replace(old,new)
    dest=OUT/'phase-timing-v1-proposal.rs';assert not dest.exists();dest.write_text(candidate)
    result=dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),candidate=str(dest.relative_to(ROOT)),
        candidate_sha256=sha(dest),native_source_changed=False,compiled=False,tested=False,replacements=len(edits))
    with (OUT/'phase-timing-v1-proposal.json').open('x') as f:json.dump(result,f,indent=2)
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
