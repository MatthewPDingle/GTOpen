"""Install the research-only ordinary GPU integration and archive exact inputs."""
import hashlib,json
from pathlib import Path
from prepare_c19_integration import save
P=Path(__file__).resolve().parent;ROOT=P.parents[3];gpu=ROOT/'crates/solver/src/preflop/gpu'
archive=P/'artifacts/c24-integration-v1';archive.mkdir(exist_ok=True)
mapping={}
for f in [gpu.with_suffix('.rs'),gpu/'static_cdf.rs']:
    before=archive/(f.name+'.before')
    if before.exists():assert before.read_bytes()==f.read_bytes()
    else:before.write_bytes(f.read_bytes())
    mapping[str(f.relative_to(ROOT))]={'before':hashlib.sha256(f.read_bytes()).hexdigest()}
f=gpu/'static_cdf.rs';s=f.read_text(encoding='utf-8');assert 'mod ordinary' not in s
s+='\n#[cfg(all(test, feature = "preflop-research"))]\npub(super) mod ordinary;\n';save(f,s)
f=gpu.with_suffix('.rs');s=f.read_text(encoding='utf-8');start=s.index('    fn multiway_terminals(');end=s.index('    fn up(',start)
part=s[start:end]
old='                    let sample_count = self.mw_batch.min(samples - sample_start);\n'
assert part.count(old)==1
part=part.replace(old,old+'''                    #[cfg(all(test, feature = "preflop-research"))]
                    if self.static_cdf.is_some() {
                        static_cdf::ordinary::launch(self,p,gate,work_start,work_count,sample_start,sample_count,samples)?;
                        continue;
                    }
''')
save(f,s[:start]+part+s[end:])
for target,source in [(gpu/'static_cdf/ordinary.rs',P/'c24_ordinary.rs.txt'),(gpu/'static_cdf/ordinary/tests.rs',P/'c24_ordinary_tests.rs.txt')]:
    assert not target.exists();target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes());mapping[str(target.relative_to(ROOT))]={}
for name,entry in mapping.items():
    f=ROOT/name;entry['sha256']=hashlib.sha256(f.read_bytes()).hexdigest()
    dest=archive/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(f.read_bytes());entry['archive']=str(dest.relative_to(P))
(P/'artifacts/c24-integration-source-map.json').write_text(json.dumps(mapping,indent=2)+'\n')
