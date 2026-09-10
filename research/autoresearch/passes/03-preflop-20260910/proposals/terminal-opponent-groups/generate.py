from pathlib import Path
import subprocess,difflib
p=Path(__file__).parent
root=Path(r'T:\Dev\GTOpen\target\autoresearch\preflop-20260910')
rel='crates/solver/src/preflop/gpu.rs';kr='crates/solver/src/preflop/kernels.cu'
old=subprocess.check_output(['git','show','5f4f42c:'+rel],cwd=root).decode().replace('\r\n','\n')
kold=subprocess.check_output(['git','show','5f4f42c:'+kr],cwd=root).decode().replace('\r\n','\n')
s=old

def replace(a,b):
 global s
 assert s.count(a)==1,(a[:90],s.count(a))
 s=s.replace(a,b)
replace('    f_multiway_terminal: CudaFunction,','    f_multiway_terminal: CudaFunction,\n    f_multiway_by_opponents: [CudaFunction; 3],')
replace('    mw_nterms: u32,','    mw_nterms: u32,\n    mw_term_groups: [(u32,u32);4],\n    use_mw_groups: bool,')
helper='''// Reuse the existing term/probability index space: O2/O3/O4 specialize;
// O5..8 retain the generic kernel. No extra device worklist or map allocation.
fn group_multiway_terms(terms: &mut [u32], live: &[i32]) -> Result<[(u32,u32);4],String> {
    let mut counts=[0u32;4];
    for &nd in terms.iter() {
        let n=live.get(nd as usize).ok_or("multiway term index outside live table")?.count_ones();
        if !(3..=9).contains(&n) {return Err("multiway group requires3..9 live players".into());}
        let group=(n.min(6)-3) as usize;
        counts[group]=counts[group].checked_add(1).ok_or("multiway group count overflow")?;
    }
    // Stable sorting preserves original node order within each group.
    terms.sort_by_key(|&nd|live[nd as usize].count_ones().min(6));
    let mut start=0u32;let mut spans=[(0,0);4];
    for (i,&count) in counts.iter().enumerate() {spans[i]=(start,count);start=start.checked_add(count).ok_or("multiway span overflow")?;}
    Ok(spans)
}

'''
replace('// Compact only if its immutable map plus one CDF particle is no larger',helper+'// Compact only if its immutable map plus one CDF particle is no larger')
replace('''        let mw_terms: Vec<u32> = s.nodes.iter().enumerate()''','''        let mut mw_terms: Vec<u32> = s.nodes.iter().enumerate()''')
replace('''        let eq_cache_len = if use_eq_cache { eq_plan.blocks.len() * NUM_CLASSES } else { 1 };
''','''        let eq_cache_len = if use_eq_cache { eq_plan.blocks.len() * NUM_CLASSES } else { 1 };
        let mw_term_groups = if use_multiway && use_mw_prepared {
            group_multiway_terms(&mut mw_terms,&live)?
        } else {[(0,0);4]};
''')
replace('''            f_multiway_terminal: func(if use_mw_prepared { "pf_multiway_terminal" } else { "pf_multiway_terminal_minimal" })?,''','''            f_multiway_terminal: func(if use_mw_prepared { "pf_multiway_terminal" } else { "pf_multiway_terminal_minimal" })?,
            f_multiway_by_opponents: [func("pf_multiway_terminal_o2")?,func("pf_multiway_terminal_o3")?,func("pf_multiway_terminal_o4")?],''')
replace('''            mw_nterms: mw_terms.len() as u32,''','''            mw_nterms: mw_terms.len() as u32,
            mw_term_groups,
            use_mw_groups: true,''')
# Replace only the existing coupled launch block. Its old path remains intact
# for generic control and minimal fallback. Views supply matching offsets.
start=s.index('''                        self.stream.launch_builder(&self.f_multiway_terminal)
''')
end=s.index('''                            .launch(LaunchConfig { block_dim:''',start)
end=s.index('\n',end)+1
original=s[start:end]
view=original.replace('self.stream.launch_builder(&self.f_multiway_terminal)','self.stream.launch_builder(kernel)',1)
view=view.replace('.arg(&self.d_mw_terms)', '.arg(&group_terms)',1)
view=view.replace('.arg(if self.use_mw_prepared { &self.d_mw_prob } else { &self.d_reach_mass })','.arg(&group_prob)',1)
view=view.replace('Self::cfg(self.mw_nterms)','Self::cfg(count)',1)
replacement='''                        if self.use_mw_prepared && self.use_mw_groups {
                            for group in 0..4 {
                                let (start,count)=self.mw_term_groups[group];
                                if count==0 {continue;}
                                let range=start as usize..(start+count) as usize;
                                // The two views offset terms and prepared probabilities
                                // together. Graph replay retains stable underlying storage.
                                let group_terms=self.d_mw_terms.slice(range.clone());
                                let group_prob=self.d_mw_prob.slice(range);
                                let kernel=if group<3 {&self.f_multiway_by_opponents[group]} else {&self.f_multiway_terminal};
'''+view+'''                            }
                        } else {
'''+original+'''                        }
'''
s=s[:start]+replacement+s[end:]
# Every existing test replacement uses a single target; refresh grouped spans.
needle='''            gpu.mw_nterms = 1;'''
assert s.count(needle)==1
s=s.replace(needle,needle+'''
            gpu.mw_term_groups=[(0,0);4];
            gpu.mw_term_groups[(s.nodes[target].live.count_ones().min(6)-3) as usize]=(0,1);''')
needle='''        gpu.mw_nterms = 1;'''
# Two remaining unindented sites (substring would also match previous one).
lines=s.splitlines(True);out=[]
for line in lines:
 out.append(line)
 if line=='        gpu.mw_nterms = 1;\n':
  out.extend(['        gpu.mw_term_groups=[(0,0);4];\n','        gpu.mw_term_groups[(s.nodes[target].live.count_ones().min(6)-3) as usize]=(0,1);\n'])
s=''.join(out)
if (p/'tests.rs').exists():
 replace('    fn phase_test_equity()', (p/'tests.rs').read_text(encoding='utf-8-sig')+'\n    fn phase_test_equity()')
k=(p.parent/'terminal-opponent-probe/kernels.cu').read_text(encoding='utf-8')
patch=''
for rel,a,b,name in [(rel,old,s,'gpu.rs'),(kr,kold,k,'kernels.cu')]:
 (p/name).write_text(b,encoding='utf-8',newline='\n')
 patch+=''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
(p/'groups.patch').write_text(patch,encoding='utf-8',newline='\n')
print('generated grouped host',len(s)-len(old),'kernel',len(k)-len(kold),'added bytes')
