"""Correct first-evaluation expectations; preserve the failed v2 experiment."""
import hashlib,json
from pathlib import Path
from prepare_c19_integration import save
HERE=Path(__file__).resolve().parent;LAB=HERE.parents[3]
def main():
    runner=HERE/'run_c19.py';archive=HERE/'artifacts/c19-v2/run_c19.py'
    assert not archive.exists();archive.write_bytes(runner.read_bytes())
    p=LAB/'crates/solver/src/preflop/gpu/cohort_reuse/tests.rs';s=p.read_text()
    old='''    let before=bits(&g);let _=g.gaps_and_evs().unwrap();assert_eq!(before,bits(&g));
    drop(g);let normal=PreflopGpu::new_research_narrow_cohorts(&s,2000).unwrap();
    assert_eq!(before,bits(&normal));assert!(!super::super::cdf_interleave::constructor_active());'''
    new='''    let initial=bits(&g);let _=g.gaps_and_evs().unwrap();let before=bits(&g);
    // First evaluation populates roots/value buffers; it must not learn.
    assert!(initial.0==before.0 && initial.1==before.1);
    let _=g.gaps_and_evs().unwrap();assert!(before==bits(&g));
    drop(g);let normal=PreflopGpu::new_research_narrow_cohorts(&s,2000).unwrap();
    assert!(initial==bits(&normal));assert!(!super::super::cdf_interleave::constructor_active());'''
    assert s.count(old)==1;save(p,s.replace(old,new))
    s=runner.read_text().replace('c19-numerical-v1','c19-numerical-v2').replace('artifacts/c19-v2-source-map.json','artifacts/c19-v3-source-map.json')
    runner.write_text(s,encoding='utf-8')
    mapping={}
    for relative in json.loads((HERE/'artifacts/c19-v2-source-map.json').read_text()):
        p=LAB/relative;dest=HERE/'artifacts/c19-v3'/p.relative_to(LAB/'crates/solver')
        assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
        mapping[relative]=dict(archive=dest.relative_to(HERE).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    (HERE/'artifacts/c19-v3-source-map.json').write_text(json.dumps(mapping,indent=2)+'\n',encoding='utf-8')
    print('Archived failed harness version; only guard expectation corrected')
if __name__=='__main__':main()
