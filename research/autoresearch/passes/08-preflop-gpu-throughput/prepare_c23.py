"""Prepare test-only static boundary writer and reader with immutable archive."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;LAB=HERE.parents[3]
def main():
    root=LAB/'crates/solver/src/preflop/gpu';target=root/'static_cdf.rs';assert not target.exists()
    old=(root/'rank_pipeline.rs').read_text(encoding='utf-8');table=old[old.index('fn table('):old.index('#[test]')]
    source=(HERE/'c23_module.rs.txt').read_text(encoding='utf-8')+'\n'+table
    target.write_text(source,encoding='utf-8',newline='\n')
    parent=root.parent/'gpu.rs';raw=parent.read_bytes();assert b'mod static_cdf;' not in raw
    parent.write_bytes(raw+b'\n#[cfg(all(test, feature = "preflop-research"))]\nmod static_cdf;\n')
    mapping={}
    for p in [target,parent]:
        dest=HERE/'artifacts/c23-v1'/p.relative_to(LAB/'crates/solver');assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
        mapping[p.relative_to(LAB).as_posix()]=dict(archive=dest.relative_to(HERE).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    (HERE/'artifacts/c23-v1-source-map.json').write_text(json.dumps(mapping,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
