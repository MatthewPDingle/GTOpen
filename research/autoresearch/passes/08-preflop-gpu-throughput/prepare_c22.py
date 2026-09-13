"""Create standalone rank-pipeline qualification, without runtime selection."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;LAB=HERE.parents[3]
def main():
    target=LAB/'crates/solver/src/preflop/gpu/rank_pipeline.rs';assert not target.exists()
    archived=(HERE/'artifacts/c18-v4/src/preflop/gpu/rank_compact.rs').read_text()
    header=archived[:archived.index('#[test]')].replace('C18 standalone','C22 standalone')
    target.write_text(header+(HERE/'c22_test.rs.txt').read_text(),encoding='utf-8',newline='\n')
    parent=LAB/'crates/solver/src/preflop/gpu.rs';raw=parent.read_bytes();assert b'mod rank_pipeline;' not in raw
    parent.write_bytes(raw+b'\n#[cfg(all(test, feature = "preflop-research"))]\nmod rank_pipeline;\n')
    mapping={}
    for p in [target,parent,target.with_suffix('.cu')]:
        dest=HERE/'artifacts/c22-v1'/p.relative_to(LAB/'crates/solver');assert not dest.exists()
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
        mapping[p.relative_to(LAB).as_posix()]=dict(archive=dest.relative_to(HERE).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    (HERE/'artifacts/c22-v1-source-map.json').write_text(json.dumps(mapping,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
