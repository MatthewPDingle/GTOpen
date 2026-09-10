from pathlib import Path
import difflib, hashlib, subprocess
out=Path(__file__).resolve().parent
root=Path(r'T:\Dev\GTOpen\target\autoresearch\preflop-20260910')
rel='crates/solver/src/preflop/mod.rs'
old=(root/rel).read_text(encoding='utf-8')
impl=(out/'implementation.rs').read_text(encoding='utf-8').replace('pub fn try_gaps_and_evs(', 'fn checkpoint_gaps_and_evs(')
(out/'implementation.rs').write_text(impl,encoding='utf-8')
start=old.index('    /// Best-response gaps AND average-strategy EVs in one pass per player')
end=old.index('    /// EV per player (bb) under the average strategy profile.',start)
replacement='''    /// Best-response gaps and average-strategy EVs. The paired traversal shares
    /// terminal evaluation but preserves each output's own pruning/reduction.
    pub fn gaps_and_evs(&self) -> (Vec<f64>, Vec<f64>) {
        // Preserve the public signature and pre-set-stop zero result. Callers
        // with a stop flag must discard canceled values, as the preflop worker
        // already does before publishing a checkpoint or declaring convergence.
        self.checkpoint_gaps_and_evs()
            .unwrap_or_else(|| (vec![0.0; self.n], vec![0.0; self.n]))
    }

'''
production=old[:start]+replacement+old[end:]+'\n'+impl
new=production.replace('    fn terminal_value(&self, node: usize, p: usize, reaches: &[Vec<f32>], out: &mut [f32]) {',
'''    fn terminal_value(&self, node: usize, p: usize, reaches: &[Vec<f32>], out: &mut [f32]) {
        #[cfg(test)]
        checkpoint_tests::observe_terminal();''')+'\n#[cfg(test)]\nmod checkpoint_tests;\n'
assert new.count('checkpoint_tests::observe_terminal();')==1
# implementation hook also cfg(test), so it must be accompanied by tests module.
tests=(out/'checkpoint_tests.rs').read_text(encoding='utf-8-sig')
(out/'mod.rs').write_bytes(new.replace('\n','\r\n').encode())
(out/'checkpoint_tests.rs').write_text(tests,encoding='utf-8')
patch=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
patch+=''.join(difflib.unified_diff([],tests.splitlines(True),fromfile='/dev/null',tofile='b/crates/solver/src/preflop/checkpoint_tests.rs'))
(out/'combined.patch').write_text(patch,encoding='utf-8',newline='\n')
(out/'base.txt').write_text(subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()+'\n'+rel+' sha256 '+hashlib.sha256((root/rel).read_bytes()).hexdigest()+'\n',encoding='utf-8')
print('Proposal generated:',len(patch),'patch bytes;',len(tests.splitlines()),'test lines')
