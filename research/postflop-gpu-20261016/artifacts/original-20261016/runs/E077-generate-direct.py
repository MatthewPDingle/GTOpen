"""Prepare fixed full raw showdown controls; does not compile or run kernels."""
from pathlib import Path
import shutil,sys
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as old
H=R/'runs/E077-kernel-control';A=R/'runs/E073-kernel-control-r3';S=R/'runs/E077-source';old.custody();assert not H.exists();H.mkdir()
for n in ['baseline.cu','candidate.cu']:shutil.copyfile(S/n,H/n)
for arm in ['baseline','candidate']:
 p=R/'runs/E077-resource/execution'/(arm+'-compute_120.ptx');old.pin(p,old.read(R/'runs/E077-resource/report.json')['ptx_sha256'][arm+'-compute_120']);shutil.copyfile(p,H/(arm+'.ptx'))
for n in ['corpus.json','accepted-evaluator.rs']:shutil.copyfile(A/n,H/n)
old.pin(H/'accepted-evaluator.rs',old.BASE['crates/solver/src/evaluator.rs'])
probe=(A/'probe.rs').read_text(encoding='utf-8').replace('E073','E077')
def edit(a,b):
 global probe
 assert probe.count(a)==1,a;probe=probe.replace(a,b)
a=probe.index('enum Bounds {');b=probe.index('fn upload_u32',a);probe=probe[:a]+probe[b:]
tagger='''fn tag_indices(g:&Value,a:&mut Value) {
 const FLAG:u32=0x8000_0000;
 let mut pi=words(&a["p_idx"]);let mut oi=words(&a["o_idx"]);
 let pb=words(&a["p_off"])[1] as usize;let ob=words(&a["o_off"])[1] as usize;
 let mp=n(g,"m_p");let mo=n(g,"m_o");let lower=words(&a["p_lower"]);let upper=words(&a["p_upper"]);
 let ps=words(&g["strengths_p"]);let os=words(&g["strengths_o"]);
 let sorted_p:Vec<u32>=pi[pb..pb+mp].iter().map(|&i|ps[i as usize]).collect();
 let mut needed_p=std::collections::BTreeSet::new();let mut needed_o=std::collections::BTreeSet::new();
 if mp>0 {needed_p.insert(mp-1);}if mo>0 {needed_o.insert(mo-1);}
 for i in pb..pb+mp {for &v in [&lower[i],&upper[i]] {if v>0 {needed_o.insert(v as usize-1);}}}
 for &i in &oi[ob..ob+mo] {
  let strength=os[i as usize];let lb=sorted_p.partition_point(|&s|s<strength);let ub=sorted_p.partition_point(|&s|s<=strength);
  if lb>0 {needed_p.insert(lb-1);}if ub>0 {needed_p.insert(ub-1);}
 }
 for k in needed_p {pi[pb+k]|=FLAG;}for k in needed_o {oi[ob+k]|=FLAG;}
 a["p_idx"]=json!(pi);a["o_idx"]=json!(oi);
}
'''
needle='fn run_variant(';assert probe.count(needle)==1;probe=probe.replace(needle,tagger+needle)
edit('active:&[bool],narrow:bool)','active:&[bool],tagged:bool)')
edit(' let a=&g["arrays"];\n let (nodes,d_nodes)', ' let mut arrays=g["arrays"].clone();if tagged {tag_indices(g,&mut arrays);}\n let a=&arrays;\n let (nodes,d_nodes)')
edit('upload_bounds(s,a,"p_lower",narrow)','upload_u32(s,a,"p_lower")');edit('upload_bounds(s,a,"p_upper",narrow)','upload_u32(s,a,"p_upper")')
edit(' match &d_pl {Bounds::Wide(d)=>{launch.arg(d);},Bounds::Narrow(d)=>{launch.arg(d);}}',' launch.arg(&d_pl);')
edit(' match &d_pu {Bounds::Wide(d)=>{launch.arg(d);},Bounds::Narrow(d)=>{launch.arg(d);}}',' launch.arg(&d_pu);')
a=probe.index(' macro_rules! check_bounds');b=probe.index(' check_u!(nodes,d_nodes);',a);probe=probe[:a]+probe[b:]
probe=probe.replace('check_bounds!(pl,d_pl)','check_u!(pl,d_pl)').replace('check_bounds!(pu,d_pu)','check_u!(pu,d_pu)')
edit('"comparison_pairs":364,"accepted_rank_oracle"','"comparison_pairs":1820,"tested_block_widths":[1,32,64,128,256],"accepted_rank_oracle"')
edit(' for (f,width) in [(&bf,128),(&cf,128)]',' for (f,width) in [(&bf,256),(&cf,256)]')
edit('"baseline_physical_threads":128,"candidate_physical_threads":128,"logical_scan_threads":128','"tested_block_widths":[1,32,64,128,256]')
edit(' for c in cs {\n  let g=gs.iter()', ' for width in [1u32,32,64,128,256] {for c in cs {\n  let g=gs.iter()')
edit('run_variant(&s,&bf,g,c,128,&active,false)','run_variant(&s,&bf,g,c,width,&active,false)');edit('run_variant(&s,&cf,g,c,128,&active,true)','run_variant(&s,&cf,g,c,width,&active,true)')
edit('  if count>0&&g["board_text"]=="AsKsQsJsTs"','  if width==128&&count>0&&g["board_text"]=="AsKsQsJsTs"')
edit('"stage":"full_show_exact","case_id":c["id"]','"stage":"full_show_exact","case_id":c["id"],"threads":width')
edit(' }\n assert_eq!(launches,728);',' }}\n assert_eq!(launches,3640);')
edit('assert_eq!(active_words,197240)','assert_eq!(active_words,986200)');edit('assert_eq!(guard_checks,1292824)','assert_eq!(guard_checks,6464120)');edit('assert_eq!(input_checks,15288)','assert_eq!(input_checks,76440)')
edit('"comparison_pairs":364,"kernel_launches":launches','"comparison_pairs":1820,"kernel_launches":launches,"tested_block_widths":[1,32,64,128,256]')
assert 'Bounds'not in probe and 'narrow'not in probe
(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
print('E077 direct harness prepared only:1820 pairs,5 widths, no compiler/GPU execution.',flush=True)
