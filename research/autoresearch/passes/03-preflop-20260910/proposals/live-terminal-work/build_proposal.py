from pathlib import Path
import subprocess,difflib,hashlib
root=Path(r'T:\Dev\GTOpen\target\autoresearch\preflop-20260910')
out=Path(__file__).parent
gpu_rel='crates/solver/src/preflop/gpu.rs'
cu_rel='crates/solver/src/preflop/kernels.cu'
base={r:(root/r).read_text(encoding='utf-8') for r in [gpu_rel,cu_rel]}
g=base[gpu_rel]; c=base[cu_rel]
def gr(old,new):
    global g
    assert g.count(old)==1,(old[:100],g.count(old))
    g=g.replace(old,new)
def cr(old,new):
    global c
    assert c.count(old)==1,(old[:100],c.count(old))
    c=c.replace(old,new)
gr('    d_mw_terms: CudaSlice<u32>,','''    d_mw_terms: CudaSlice<u32>,
    d_mw_terminal_work: CudaSlice<u32>,
    mw_terminal_spans: Vec<(u32, u32)>,
    use_mw_terminal_work: i32,''')
helpers=(out/'planner.rs').read_text(encoding='utf-8')
gr('/// Preferred VRAM including the exact-equity cache, in MB.',helpers+'\n/// Preferred VRAM including the exact-equity cache, in MB.')
gr('            + mw.blocks.len() * 4 + compact.capacity * NUM_CLASSES * 4\n','''            + mw.blocks.len() * 4 + compact.capacity * NUM_CLASSES * 4
            + s.nodes.iter().filter(|nd| nd.kind == KIND_POT_SHARE && nd.live.count_ones() >= 3)
                .map(|nd| nd.live.count_ones() as usize * 4).sum::<usize>()
''')
gr('        let use_multiway = !mw_terms.is_empty();','''        let use_multiway = !mw_terms.is_empty();
        let terminal_work = MultiwayTerminalPlan::build(s, &mw_terms)?;
        let mut use_mw_terminal_work = false;''')
gr('            mw_batch = plan.batch;','''            // This optional list must not consume the last particle's space,
            // reduce the CDF batch, or force a different normalization mode.
            use_mw_terminal_work = terminal_work_preserves_plan(remaining, compact.capacity,
                terminal_work.bytes(), &plan)?;
            let without_work = need + (fixed + plan.normalized_bytes + plan.cache_len * 4) as f64 / 1e6;
            if !eq_plan.blocks.is_empty() && without_work + eq_plan.bytes() as f64 / 1e6 <= budget_mb as f64
                && without_work + (eq_plan.bytes() + terminal_work.bytes()) as f64 / 1e6 > budget_mb as f64 {
                use_mw_terminal_work = false; // retain an otherwise-fitting HU cache
            }
            mw_batch = plan.batch;''')
gr('            need += (fixed + plan.normalized_bytes + mw_cache_len * 4) as f64 / 1e6;','''            need += (fixed + plan.normalized_bytes + mw_cache_len * 4
                + if use_mw_terminal_work { terminal_work.bytes() } else { 0 }) as f64 / 1e6;''')
gr('            if compact.enabled {','''            println!("preflop gpu: live terminal work enabled={}, global={}, per-seat={:?}, {:.3} MB indices",
                use_mw_terminal_work, mw_terms.len(), terminal_work.spans.iter().map(|x|x.1).collect::<Vec<_>>(),
                if use_mw_terminal_work { terminal_work.bytes() as f64 / 1e6 } else { 0.0 });
            if compact.enabled {''')
gr('            d_mw_terms: stream.clone_htod(if mw_terms.is_empty() { &[0u32][..] } else { mw_terms.as_slice() }).map_err(e)?,','''            d_mw_terms: stream.clone_htod(if mw_terms.is_empty() { &[0u32][..] } else { mw_terms.as_slice() }).map_err(e)?,
            d_mw_terminal_work: stream.clone_htod(if use_mw_terminal_work { terminal_work.work.as_slice() } else { &[0u32][..] }).map_err(e)?,
            mw_terminal_spans: terminal_work.spans,
            use_mw_terminal_work: use_mw_terminal_work as i32,''')
gr('        let tcount = self.nterms as i32;','''        let (terminal_start, terminal_count) = if self.use_mw_terminal_work != 0 {
            self.mw_terminal_spans[p as usize]
        } else { (0, self.mw_nterms) };
        let tcount = self.nterms as i32;''')
gr('''                        #[cfg(test)]
                        self.phase_mark("coupled_terminals", p)?;
                        self.stream.launch_builder(&self.f_multiway_terminal)
                            .arg(&self.d_mw_terms).arg(&p).arg(&self.np)''','''                        if terminal_count > 0 {
                        #[cfg(test)]
                        self.phase_mark("coupled_terminals", p)?;
                        self.stream.launch_builder(&self.f_multiway_terminal)
                            .arg(&self.d_mw_terms).arg(&self.d_mw_terminal_work)
                            .arg(&terminal_start).arg(&self.use_mw_terminal_work).arg(&p).arg(&self.np)''')
gr('''                            .launch(LaunchConfig { block_dim: (192, 1, 1), ..Self::cfg(self.mw_nterms) }).map_err(e)?;''','''                            .launch(LaunchConfig { block_dim: (192, 1, 1), ..Self::cfg(terminal_count) }).map_err(e)?;
                        }''')
cr('''extern "C" __global__ void pf_multiway_terminal(
    const u32* __restrict__ terms, int p, int np,''','''extern "C" __global__ void pf_multiway_terminal(
    const u32* __restrict__ terms, const u32* __restrict__ terminal_work,
    u32 terminal_start, int use_terminal_work, int p, int np,''')
cr('''    u32 nd = terms[blockIdx.x];
    int lv = live[nd];''','''    u32 terminal_index = use_terminal_work ? terminal_work[terminal_start + blockIdx.x] : blockIdx.x;
    u32 nd = terms[terminal_index];
    int lv = live[nd];''')
cr('        prob = terminal_prob[blockIdx.x];','        prob = terminal_prob[terminal_index];')
implementation=g
testhelper=(out/'test_helpers.rs').read_text(encoding='utf-8')
gr('// Diagnostic-only eager phase timing.',testhelper+'\n// Diagnostic-only eager phase timing.')
old='gpu.d_mw_terms = gpu.stream.clone_htod(&[target as u32]).unwrap();\n'
assert g.count(old)==3,g.count(old)
import re
g,n=re.subn(r'gpu\.d_mw_terms = gpu\.stream\.clone_htod\(&\[target as u32\]\)\.unwrap\(\);\n\s*gpu\.mw_nterms = 1;', 'gpu.test_set_multiway_terms(&s, &[target as u32]);',g)
assert n==3
tests=(out/'tests.rs').read_text(encoding='utf-8')
gr('    fn phase_test_equity() -> Arc<crate::preflop::equity::EquityTable> {',tests+'\n    fn phase_test_equity() -> Arc<crate::preflop::equity::EquityTable> {')
def patch(a,b,rel):return ''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
(out/'implementation.patch').write_text(patch(base[gpu_rel],implementation,gpu_rel)+patch(base[cu_rel],c,cu_rel),encoding='utf-8',newline='\n')
(out/'tests.patch').write_text(patch(implementation,g,gpu_rel),encoding='utf-8',newline='\n')
(out/'combined.patch').write_text(patch(base[gpu_rel],g,gpu_rel)+patch(base[cu_rel],c,cu_rel),encoding='utf-8',newline='\n')
for name,txt in [('gpu.rs',g),('kernels.cu',c)]: (out/name).write_bytes(txt.replace('\n','\r\n').encode('utf-8'))
(out/'base.txt').write_text(subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True)+''.join(hashlib.sha256((root/r).read_bytes()).hexdigest()+' '+r+'\n' for r in base),encoding='utf-8')
print('Live terminal work proposal written; source unchanged.')
