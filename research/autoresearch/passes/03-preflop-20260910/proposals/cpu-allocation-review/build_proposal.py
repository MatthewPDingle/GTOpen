from pathlib import Path
import difflib,hashlib,subprocess
root=Path(r'T:\Dev\GTOpen\target\autoresearch\preflop-20260910')
out=Path(__file__).parent
rel='crates/solver/src/preflop/mod.rs'
base=(root/rel).read_text(encoding='utf-8')
def replace_once(text,a,b):
    assert text.count(a)==1,(a[:100],text.count(a))
    return text.replace(a,b)
def patch(a,b):return ''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
start=base.index('    fn traverse(\n')
end=base.index('    fn root_reaches(',start)
traverse=base[start:end]
old='''        let forced = self.forced_sigma(node);
        let frozen = self.seat_frozen[actor];
        let mut sigma = vec![0f32; na * NUM_CLASSES];
        match &forced {
            Some(f) => sigma.copy_from_slice(f),
            None if mode == 0 && !frozen => self.current_strategy(node, &mut sigma),
            _ => sigma.copy_from_slice(&self.average_strategy(node)),
        }
'''
new='''        let forced = self.forced_sigma(node);
        let has_forced = forced.is_some();
        let frozen = self.seat_frozen[actor];
        // Both policy and average-strategy helpers already return owned
        // vectors. Use that allocation instead of zeroing/copying another.
        let sigma = match forced {
            Some(f) => f,
            None if mode == 0 && !frozen => {
                let mut sigma = vec![0f32; na * NUM_CLASSES];
                self.current_strategy(node, &mut sigma);
                sigma
            }
            None => self.average_strategy(node),
        };
        assert_eq!(sigma.len(), na * NUM_CLASSES);
'''
traverse=replace_once(traverse,old,new)
assert traverse.count('forced.is_none()')==3,traverse.count('forced.is_none()')
traverse=traverse.replace('forced.is_none()','!has_forced')
sigma=base[:start]+traverse+base[end:]
def masses(text):
    old='''        let nd = &self.nodes[node];
        let mut prob = 1f64;
        for q in 0..self.n {
            if q != p {
                let s: f32 = reaches[q].iter().sum();
                prob *= s as f64;
            }
        }
'''
    new='''        let nd = &self.nodes[node];
        let mut prob = 1f64;
        // Config validation permits at most nine seats. Preserve the exact
        // f32 reduction and f64 product order, and reuse each opponent mass.
        let mut masses = [0f32; 9];
        for q in 0..self.n {
            if q != p {
                let s: f32 = reaches[q].iter().sum();
                masses[q] = s;
                prob *= s as f64;
            }
        }
'''
    text=replace_once(text,old,new)
    return replace_once(text,'''                    if q != p && nd.live & (1 << q) != 0 {
                        let s: f32 = reaches[q].iter().sum();''','''                    if q != p && nd.live & (1 << q) != 0 {
                        let s = masses[q];''')
mass=masses(base)
combined=masses(sigma)
for name,a,b in [('owned-sigma.patch',base,sigma),('reuse-masses.patch',base,mass),('combined.patch',base,combined)]:
    (out/name).write_text(patch(a,b),encoding='utf-8',newline='\n')
(out/'mod.rs').write_bytes(combined.replace('\n','\r\n').encode('utf-8'))
(out/'base.txt').write_text(subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True)+hashlib.sha256((root/rel).read_bytes()).hexdigest()+' '+rel+'\n',encoding='utf-8')
print('Independent optional CPU patches written; no source changes.')
