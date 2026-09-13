"""Integrate qualified static tables into explicit test-only construction."""
import hashlib,json
from pathlib import Path
from prepare_c19_integration import save
HERE=Path(__file__).resolve().parent;LAB=HERE.parents[3]
def replace(s,a,b,n=1):
    assert s.count(a)==n,(a,s.count(a));return s.replace(a,b)
def launch(s,obj,kernel,cohort,writer):
    marker=f'{obj}.stream.launch_builder(&{kernel})';start=s.index(marker);end=s.index('.map_err(e)?;',start)+len('.map_err(e)?;')
    old=s[start:end];cut=old.index('.launch(LaunchConfig');new=old[:cut].replace(marker,f'{obj}.stream.launch_builder(&k.'+('writer)' if writer else 'terminal)'))
    if writer:new+=f'.arg(&k.stride).arg(&k.prefix).arg(&k.offsets)'
    else:
        new=new.replace(f'.arg(&{obj}.d_mw_lower)', '.arg(&k.hand)')
        new+=f'.arg(&k.stride).arg(&k.offsets).arg(&{int(cohort)}i32)'
    new+=old[cut:]
    wrapped=f'''#[cfg(all(test, feature = "preflop-research"))]
                let static_done=if let Some(k)={obj}.static_cdf.as_ref(){{{new}true}}else{{false}};
                #[cfg(not(all(test, feature = "preflop-research")))]
                let static_done=false;
                if !static_done{{{old}}}'''
    return s[:start]+wrapped+s[end:]
def main():
    root=LAB/'crates/solver/src/preflop/gpu';modified=[]
    p=root/'static_cdf.rs';s=p.read_text(encoding='utf-8');assert 'struct Packed' not in s
    save(p,s+(HERE/'c23_integration.rs.txt').read_text(encoding='utf-8'));modified.append(p)
    p=root.parent/'gpu.rs';s=p.read_text(encoding='utf-8')
    s=replace(s,'    throughput_narrow: bool,','    throughput_narrow: bool,\n    #[cfg(all(test, feature = "preflop-research"))]\n    static_cdf:Option<static_cdf::Packed>,')
    s=replace(s,'            throughput_narrow: narrow,','            throughput_narrow: narrow,\n            #[cfg(all(test, feature = "preflop-research"))]\n            static_cdf:None,')
    save(p,s);modified.append(p)
    p=root/'exact_reuse.rs';s=p.read_text(encoding='utf-8')
    s=launch(s,'self','r.cdf',False,True);s=launch(s,'self','r.terminal',False,False);save(p,s);modified.append(p)
    p=root/'cohort_reuse.rs';s=p.read_text(encoding='utf-8')
    s=launch(s,'self','r.cdf',True,True);s=launch(s,'g','c.terminal',True,False);save(p,s);modified.append(p)
    p=root/'cohort_reuse/tests.rs';s=p.read_text(encoding='utf-8')
    s=replace(s,'for mode in 0..6 {','for mode in 0..7 {',2)
    s=replace(s,'let mut g=if mode==5{','let mut g=if mode==6{super::super::static_cdf::new(&s,2000).unwrap()}else if mode==5{',2)
    for label in ['terminals np={np} batch={batch}','np={np} fixed={fixed} batch={batch}']:
        old=f'assert_eq!(runs[3],runs[5],"C14 {label}");';s=replace(s,old,old+f'\n        assert_eq!(runs[5],runs[6],"C23 {label}");')
    s=replace(s,'let mut expected=g.stream.alloc_zeros::<f32>(g.d_mw_cdf.len()).unwrap();','let mut expected=g.stream.alloc_zeros::<f32>(c.plan.capacity*g.mw_batch as usize*170).unwrap();')
    s=replace(s,'    for k in 0..count as usize {','''    let compact=g.static_cdf.as_ref().map(|k|(g.stream.clone_dtoh(&k.prefix).unwrap(),g.stream.clone_dtoh(&k.offsets).unwrap(),k.stride as usize));
    for k in 0..count as usize {''')
    s=replace(s,'assert!(actual[a..a+170].iter().zip(&reference[b..b+170]).all(|(a,b)|a.to_bits()==b.to_bits()));','''if let Some((prefix,offsets,stride))=&compact{
                let at=sample_start as usize+sample;let base=representative*stride+(offsets[at]-offsets[sample_start as usize]) as usize;
                for i in 0..170{let packed=prefix[at*170+i];if packed!=u32::MAX{assert_eq!(actual[base+packed as usize].to_bits(),reference[b+i].to_bits());}}
            }else{assert!(actual[a..a+170].iter().zip(&reference[b..b+170]).all(|(a,b)|a.to_bits()==b.to_bits()));}''')
    s=replace(s,'let g=if narrow{','let compact=std::env::var("PREFLOP_GPU_STATIC_CDF").ok().as_deref()==Some("1");\n    let g=if compact{super::super::static_cdf::new(&s,23000).unwrap()}else if narrow{')
    s=replace(s,'    let buffers=super::super::cross_player_inventory::device_buffer_bytes(&g);','''    let mut buffers=super::super::cross_player_inventory::device_buffer_bytes(&g);
    let compact_report=g.static_cdf.as_ref().map(|k|k.report());
    let reduction=g.static_cdf.as_ref().map_or(0,|k|k.original_bytes-g.d_mw_cdf.len()*4-k.bytes());
    if let Some(k)=g.static_cdf.as_ref(){buffers.insert("static_prefix",k.prefix.len()*4);buffers.insert("static_hand",k.hand.len()*4);buffers.insert("static_offsets",k.offsets.len()*4);}''')
    s=replace(s,'assert_eq!(actual,c.plan.total_bytes);','assert_eq!(actual,c.plan.total_bytes-reduction);')
    s=replace(s,'"arenas_unchanged":true,"narrow_offsets":narrow,','"arenas_unchanged":true,"narrow_offsets":narrow,"static_cdf":compact_report,')
    tracing=s[s.index('#[test]\nfn retained_phase_tracing_preserves_solver_bits()'):]
    tracing=tracing.replace('retained_phase_tracing_preserves_solver_bits','static_cdf_phase_tracing_preserves_solver_bits').replace('PreflopGpu::new_research_narrow_cohorts(&s,2000)','super::super::static_cdf::new(&s,2000)').replace('tracing altered retained C14','tracing altered C23')
    s+='\n'+tracing+(HERE/'c23_recovery_tests.rs.txt').read_text(encoding='utf-8')
    save(p,s);modified.append(p)
    p=root/'exact_reuse/tests.rs';s=p.read_text(encoding='utf-8')
    s=replace(s,'    let mut selection=None;','    let compact=std::env::var("PREFLOP_GPU_STATIC_CDF").ok().as_deref()==Some("1");\n    assert!(!compact || (narrow && !production));\n    let mut selection=None;')
    s=replace(s,'let mut g=if production{','let mut g=if compact{super::super::static_cdf::new(&s,23000).unwrap()}else if production{')
    s=replace(s,'"narrow_offsets":g.throughput_narrow,"production_selection":production,','"narrow_offsets":g.throughput_narrow,"static_cdf":g.static_cdf.as_ref().map(|k|k.report()),"production_selection":production,')
    save(p,s);modified.append(p)
    mapping={}
    for p in modified:
        dest=HERE/'artifacts/c23-v2'/p.relative_to(LAB/'crates/solver');assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
        mapping[p.relative_to(LAB).as_posix()]=dict(archive=dest.relative_to(HERE).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    (HERE/'artifacts/c23-v2-source-map.json').write_text(json.dumps(mapping,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
