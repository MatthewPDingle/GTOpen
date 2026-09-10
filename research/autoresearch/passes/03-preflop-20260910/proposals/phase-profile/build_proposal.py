from pathlib import Path
import difflib, hashlib, subprocess

root = Path(r'T:\Dev\GTOpen\target\autoresearch\preflop-20260910')
out = Path(__file__).parent
rel = 'crates/solver/src/preflop/gpu.rs'
original = (root / rel).read_text(encoding='utf-8')
text = original
def replace(old, new):
    global text
    assert text.count(old) == 1, (old[:100], text.count(old))
    text = text.replace(old, new)
def mark(label, player='p', indent='        '):
    return f'{indent}#[cfg(test)]\n{indent}self.phase_mark("{label}", {player})?;\n'

replace('    h_snapshot: Mutex<Option<PinnedBuf>>,', '    h_snapshot: Mutex<Option<PinnedBuf>>,\n    #[cfg(test)]\n    phase_trace: Option<PhaseEventTrace>,')
replace('            h_snapshot: Mutex::new(None),', '            h_snapshot: Mutex::new(None),\n            #[cfg(test)]\n            phase_trace: None,')
replace('    fn down(&mut self, mode: i32, p: i32) -> Result<(), String> {\n', '    fn down(&mut self, mode: i32, p: i32) -> Result<(), String> {\n' + mark('down'))
replace('    fn terminals_masked(&mut self, p: i32, gate: i32) -> Result<(), String> {\n', '    fn terminals_masked(&mut self, p: i32, gate: i32) -> Result<(), String> {\n' + mark('ordinary_terminals'))
replace('                let slot_count = self.d_mw_active.len() as u32;\n', mark('prepare', indent='                ') + '                let slot_count = self.d_mw_active.len() as u32;\n')
replace('                    if self.use_mw_normalized {\n', '                    if self.use_mw_normalized {\n' + mark('normalize', indent='                        '))
replace('                        self.stream.launch_builder(&self.f_multiway_cdf)\n', mark('cdf', indent='                        ') + '                        self.stream.launch_builder(&self.f_multiway_cdf)\n')
replace('                        self.stream.launch_builder(&self.f_multiway_terminal)\n', mark('coupled_terminals', indent='                        ') + '                        self.stream.launch_builder(&self.f_multiway_terminal)\n')
replace('    fn up(&mut self, p: i32, mode: i32) -> Result<(), String> {\n', '    fn up(&mut self, p: i32, mode: i32) -> Result<(), String> {\n        #[cfg(test)]\n        self.phase_mark(match mode { 0 => "up_learn", 1 => "up_average", _ => "up_br" }, p)?;\n')
replace('        let n_act = self.n_act as i32;\n', mark('discount', '-1') + '        let n_act = self.n_act as i32;\n')
replace('        self.stream.synchronize().map_err(e)?;\n        self.warmed = true;', mark('end', '-1') + '        self.stream.synchronize().map_err(e)?;\n        self.warmed = true;')
replace('        let roots = self.stream.clone_dtoh(&self.d_eval_roots).map_err(e)?;\n', mark('end', '-1') + '        let roots = self.stream.clone_dtoh(&self.d_eval_roots).map_err(e)?;\n')
replace('                let off = (2 * p as usize + slot) * NUM_CLASSES;\n', mark('root_copy', indent='                ') + '                let off = (2 * p as usize + slot) * NUM_CLASSES;\n')
helpers = (out / 'helpers.rs').read_text(encoding='utf-8')
replace('#[cfg(test)]\nmod tests {', helpers + '\n#[cfg(test)]\nmod tests {')
implementation = text
tests = (out / 'tests.rs').read_text(encoding='utf-8')
replace('    #[test]\n    fn multiway_normalization_budget_preserves_minimum_particle_fit()', tests + '\n    #[test]\n    fn multiway_normalization_budget_preserves_minimum_particle_fit()')
def patch(a,b):
    return ''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
(out/'instrumentation.patch').write_text(patch(original,implementation),encoding='utf-8',newline='\n')
(out/'tests.patch').write_text(patch(implementation,text),encoding='utf-8',newline='\n')
(out/'combined.patch').write_text(patch(original,text),encoding='utf-8',newline='\n')
(out/'gpu.rs').write_bytes(text.replace('\n','\r\n').encode('utf-8'))
(out/'base.txt').write_text(subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True)+hashlib.sha256((root/rel).read_bytes()).hexdigest()+'  '+rel+'\n',encoding='utf-8')
print('Proposal generated; source checkout unchanged.')
