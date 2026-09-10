from pathlib import Path
import subprocess, difflib, hashlib
root=Path(r'T:\Dev\GTOpen\target\autoresearch\preflop-20260910')
out=Path(__file__).parent
rel='crates/solver/src/preflop/multiway.rs'
def show(rev):
    return subprocess.check_output(['git','show',rev+':'+rel],cwd=root).decode('utf-8').replace('\r\n','\n')
original=show('9880326')
clean=show('423f58a')
current=(root/rel).read_text(encoding='utf-8')
signature='    pub fn equities(&self, opponents: &[Vec<f32>]) -> [f64; NUM_CLASSES] {\n'
start=original.index(signature)
end=original.index('\n    }\n}',start)+len('\n    }')
old_body=original[start:end]
assert old_body.count('assert!(opponents.len() <= 8);')==1
guard='''        // Keep the original five-point hot body in this public entry point.
        // Smaller rules return through helpers; eight opponents falls through.
        match opponents.len() {
            0..=1 => return self.equities_with_rule(opponents, QUAD_T1, QUAD_W1),
            2..=3 => return self.equities_with_rule(opponents, QUAD_T2, QUAD_W2),
            4..=5 => return self.equities_with_rule(opponents, QUAD_T3, QUAD_W3),
            6..=7 => return self.equities_with_rule(opponents, QUAD_T4, QUAD_W4),
            _ => {},
        }
'''
old_body=old_body.replace('        assert!(opponents.len() <= 8);\n','        assert!(opponents.len() <= 8);\n'+guard)
start=clean.index(signature)
end=clean.index('\n    fn equities_with_rule',start)
candidate=clean[:start]+old_body+'\n'+clean[end:]
def patch(a,b):
    return ''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
(out/'from-current.patch').write_text(patch(current,candidate),encoding='utf-8',newline='\n')
(out/'from-clean423.patch').write_text(patch(clean,candidate),encoding='utf-8',newline='\n')
(out/'multiway.rs').write_bytes(candidate.replace('\n','\r\n').encode('utf-8'))
(out/'base.txt').write_text(subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True)+hashlib.sha256((root/rel).read_bytes()).hexdigest()+' '+rel+'\n',encoding='utf-8')
print('Optional public-body Q5 proposal written; no source changes.')
