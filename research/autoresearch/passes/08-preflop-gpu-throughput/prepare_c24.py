"""Add a four-sample GPU qualification; keep production's 32-sample map."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent;ROOT=P.parents[3]
f=ROOT/'crates/solver/src/preflop/gpu/static_cdf.rs'
old=f.read_bytes();text=old.decode('utf-8')
assert 'fn with_batch' not in text and 'c24_four_sample' not in text
archive=P/'artifacts/c24-before';archive.mkdir(exist_ok=False)
(archive/'static_cdf.rs').write_bytes(old)
newline='\r\n' if '\r\n' in text else '\n'
a='    fn new(d:&CoupledDeck)->Self {'
b=a+newline+'        Self::with_batch(d,32)'+newline+'    }'+newline+'    fn with_batch(d:&CoupledDeck,batch:usize)->Self {'+newline+'        assert!((1..=32).contains(&batch));'
assert text.count(a)==1;text=text.replace(a,b)
a='out.offsets[(s+32).min(1024)]';assert text.count(a)==1
text=text.replace(a,'out.offsets[(s+batch).min(1024)]')
start=text.index('#[cfg(feature = "preflop-research")]\n#[test]') if '#[cfg(feature = "preflop-research")]\n#[test]' in text else text.index('#[cfg(feature = "preflop-research")]\r\n#[test]')
end=text.index('#[cfg(all(test, feature = "preflop-research"))]',start)
test=text[start:end]
changes={
 'static_cdf_matches_required_prefixes_and_hands':'c24_four_sample_prefixes_and_hands',
 'manual guarded static CDF qualification':'manual guarded C24 four-sample qualification',
 'Maps::new(deck)':'Maps::with_batch(deck,4)',
 '[(1u32,1u32),(5,1),(5,5),(32,1),(32,7),(32,31),(32,32)]':'[(4u32,1u32),(4,2),(4,3),(4,4)]',
 '[0u32,17,237,992]':'[0u32,17,237,1020]',
 '6720':'3840','94080':'53760','C23_STATIC':'C24_STATIC'}
for a,b in changes.items():
    assert a in test,a
    test=test.replace(a,b)
text=text[:end]+test+text[end:]
f.write_bytes(text.encode('utf-8'))
out=P/'artifacts/c24-v1';out.mkdir(exist_ok=False)
(out/'static_cdf.rs').write_bytes(f.read_bytes())
(P/'artifacts/c24-source-map.json').write_text(json.dumps({str(f.relative_to(ROOT)):{'before':hashlib.sha256(old).hexdigest(),'after':hashlib.sha256(f.read_bytes()).hexdigest()}},indent=2)+'\n')
