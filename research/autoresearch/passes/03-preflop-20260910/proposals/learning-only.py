from pathlib import Path
ROOT=Path('T:/Dev/GTOpen/target/autoresearch/preflop-20260910')
def edit(relative, replacements):
    p=ROOT/relative
    raw=p.read_bytes()
    crlf=b'\r\n' in raw
    text=raw.decode('utf-8').replace('\r\n','\n')
    for before, after in replacements:
        assert text.count(before)==1, (relative,before[:80],text.count(before))
        text=text.replace(before,after)
    p.write_bytes(text.replace('\n','\r\n').encode('utf-8') if crlf else text.encode('utf-8'))
edit('crates/solver/src/preflop/gpu.rs',[
('    fn terminals(&mut self, p: i32) -> Result<(), String> {\n',
 '    fn terminals(&mut self, p: i32) -> Result<(), String> {\n        self.terminals_masked(p, 1)\n    }\n\n    fn terminals_masked(&mut self, p: i32, gate: i32) -> Result<(), String> {\n'),
('                    self.stream.launch_builder(&self.f_multiway_clear_active)',
 '                    if gate != 0 {\n                    self.stream.launch_builder(&self.f_multiway_clear_active)'),
('                    self.stream.launch_builder(&self.f_multiway_prepare)',
 '                    }\n                    self.stream.launch_builder(&self.f_multiway_prepare)'),
('.arg(&self.d_mw_slots).arg(&mut self.d_mw_active).arg(&mut self.d_mw_prob)',
 '.arg(&self.d_mw_slots).arg(&mut self.d_mw_active).arg(&mut self.d_mw_prob).arg(&gate)'),
('.arg(&self.d_mw_order).arg(&self.d_reach).arg(&self.d_reach_mass).arg(&self.d_mw_active)',
 '.arg(&self.d_mw_order).arg(&self.d_reach).arg(&self.d_reach_mass).arg(&self.d_mw_active).arg(&gate)'),
('        self.down(1, -1)?;\n        for p in 0..self.np {\n            self.terminals(p)?;',
 '        self.down(1, -1)?;\n        for p in 0..self.np {\n            // Average reaches are typically dense: avoid mask atomics here.\n            self.terminals_masked(p, 0)?;')])
edit('crates/solver/src/preflop/kernels.cu',[
('    u32* active, float* terminal_prob)', '    u32* active, float* terminal_prob, int gate)'),
('    terminal_prob[index] = prob;\n    if (prob <= 0.f) return;',
 '    terminal_prob[index] = prob;\n    if (prob <= 0.f || !gate) return;'),
('    const u32* __restrict__ active,\n    float* cdf,',
 '    const u32* __restrict__ active, int gate,\n    float* cdf,'),
('    if (!active[slot]) return;', '    if (gate && !active[slot]) return;')])
