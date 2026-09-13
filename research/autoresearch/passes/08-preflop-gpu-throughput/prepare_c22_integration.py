"""Explicit test-only pipeline construction and both real terminal dispatches."""
import hashlib,json
from pathlib import Path
from prepare_c19_integration import save
HERE=Path(__file__).resolve().parent;LAB=HERE.parents[3]
def replace(s,a,b,n=1):
    assert s.count(a)==n,(a,s.count(a));return s.replace(a,b)
def launch(s,object_name,cohort):
    g=object_name;marker=f'{g}.stream.launch_builder(&'+('c.terminal)' if cohort else 'r.terminal)')
    start=s.index(marker);end=s.index('.map_err(e)?;',start)+len('.map_err(e)?;')
    old=s[start:end];chain=old[:old.index('.launch(LaunchConfig')]
    chain=chain.replace(marker,f'{g}.stream.launch_builder(if producer{{&k.producer}}else{{&k.consumer}})')
    chain+=f'.arg(&tile_first).arg(&tile_count).arg(&k.groups).arg(&k.quadratures).arg(&{int(cohort)}i32).arg(&k.lower).arg(&k.upper).arg(&k.hand).arg(&k.count).arg(&mut k.scratch)\n'
    chain+=f'.launch(LaunchConfig{{grid_dim:(tile_count,1,1),block_dim:(if producer{{k.groups.div_ceil(32)*32}}else{{192}},1,1),shared_mem_bytes:0}}).map_err(e)?;'
    new=f'''#[cfg(all(test, feature = "preflop-research"))]
                let pipeline_done=if let Some(k)={g}.rank_pipeline.as_mut() {{
                    for tile_first in (0..{g}.mw_nterms).step_by(k.tile as usize) {{
                        let tile_count=k.tile.min({g}.mw_nterms-tile_first);
                        for producer in [true,false] {{ {chain} }}
                    }}true
                }}else{{false}};
                #[cfg(not(all(test, feature = "preflop-research")))]
                let pipeline_done=false;
                if !pipeline_done {{ {old} }}'''
    return s[:start]+new+s[end:]
def main():
    root=LAB/'crates/solver/src/preflop/gpu';modified=[]
    p=root/'rank_pipeline.rs';s=p.read_text(encoding='utf-8');assert 'struct Pipeline' not in s
    save(p,s+(HERE/'c22_integration.rs.txt').read_text(encoding='utf-8'));modified.append(p)
    p=root.parent/'gpu.rs';s=p.read_text(encoding='utf-8')
    s=replace(s,'    throughput_narrow: bool,','    throughput_narrow: bool,\n    #[cfg(all(test, feature = "preflop-research"))]\n    rank_pipeline:Option<rank_pipeline::Pipeline>,')
    s=replace(s,'            throughput_narrow: narrow,','            throughput_narrow: narrow,\n            #[cfg(all(test, feature = "preflop-research"))]\n            rank_pipeline:None,')
    save(p,s);modified.append(p)
    for name,object_name,cohort in [('exact_reuse.rs','self',False),('cohort_reuse.rs','g',True)]:
        p=root/name;save(p,launch(p.read_text(encoding='utf-8'),object_name,cohort));modified.append(p)
    p=root/'cohort_reuse/tests.rs';s=p.read_text(encoding='utf-8')
    s=replace(s,'for mode in 0..6 {','for mode in 0..7 {',2)
    s=replace(s,'let mut g=if mode==5{','let mut g=if mode==6{super::super::rank_pipeline::new(&s,2000).unwrap()}else if mode==5{',2)
    for label in ['terminals np={np} batch={batch}','np={np} fixed={fixed} batch={batch}']:
        old=f'assert_eq!(runs[3],runs[5],"C14 {label}");'
        s=replace(s,old,old+f'\n        assert_eq!(runs[5],runs[6],"C22 {label}");')
    s=replace(s,'let g=if narrow{','let pipeline=std::env::var("PREFLOP_GPU_RANK_PIPELINE").ok().as_deref()==Some("1");\n    let g=if pipeline{super::super::rank_pipeline::new(&s,23000).unwrap()}else if narrow{')
    s=replace(s,'    let buffers=super::super::cross_player_inventory::device_buffer_bytes(&g);','''    let mut buffers=super::super::cross_player_inventory::device_buffer_bytes(&g);
    let pipeline_report=g.rank_pipeline.as_ref().map(|k|k.report());
    let pipeline_bytes=g.rank_pipeline.as_ref().map_or(0,|k|k.bytes());
    if let Some(k)=g.rank_pipeline.as_ref(){
        buffers.insert("rank_lower",k.lower.len()*4);buffers.insert("rank_upper",k.upper.len()*4);
        buffers.insert("rank_hand",k.hand.len()*4);buffers.insert("rank_count",k.count.len()*4);
        buffers.insert("rank_products",k.scratch.len()*4);
    }''')
    s=replace(s,'assert_eq!(actual,c.plan.total_bytes);assert!(actual+256*1024*1024<=20_500_000_000);','assert_eq!(actual,c.plan.total_bytes+pipeline_bytes);assert!(actual+256*1024*1024<=23_000_000_000);')
    s=replace(s,'"arenas_unchanged":true,"narrow_offsets":narrow,','"arenas_unchanged":true,"narrow_offsets":narrow,"rank_pipeline":pipeline_report,')
    tracing=s[s.index('#[test]\nfn retained_phase_tracing_preserves_solver_bits()'):]
    tracing=tracing.replace('retained_phase_tracing_preserves_solver_bits','pipeline_phase_tracing_preserves_solver_bits').replace('PreflopGpu::new_research_narrow_cohorts(&s,2000)','super::super::rank_pipeline::new(&s,2000)').replace('tracing altered retained C14','tracing altered C22')
    s+='\n'+tracing
    s+='''
#[test]
fn pipeline_partial_allocation_and_tile_recovery() {
    let mut s=fixture(4,false);let mut g=PreflopGpu::new_research_narrow_cohorts(&s,2000).unwrap();
    let initial=bits(&g);let pointers=(g.d_val.device_ptr(&g.stream).0,g.d_mw_cdf.device_ptr(&g.stream).0);
    assert!(g.enable_rank_pipeline(&s,0).is_err());assert!(g.rank_pipeline.is_none());
    super::super::rank_pipeline::FAIL_PARTIAL.set(true);
    assert!(g.enable_rank_pipeline(&s,2000).unwrap_err().contains("after two allocated maps"));
    assert!(!super::super::rank_pipeline::FAIL_PARTIAL.get());assert!(g.rank_pipeline.is_none());
    assert!(initial==bits(&g));assert_eq!(pointers,(g.d_val.device_ptr(&g.stream).0,g.d_mw_cdf.device_ptr(&g.stream).0));
    let _=g.gaps_and_evs().unwrap();assert!(g.enable_rank_pipeline(&s,2000).is_err());
    drop(g);let mut g=super::super::rank_pipeline::new(&s,2000).unwrap();
    g.rank_pipeline.as_mut().unwrap().tile=3;g.mw_batch=5;
    assert!(g.enable_rank_pipeline(&s,2000).is_err());
    let mut observed=Vec::new();for _ in 0..3{g.iterate(&mut s).unwrap();let metrics=g.gaps_and_evs().unwrap();observed.push((bits(&g),metrics));}
    drop(g);let mut s=fixture(4,false);let mut normal=PreflopGpu::new_research_narrow_cohorts(&s,2000).unwrap();normal.mw_batch=5;
    let mut expected=Vec::new();for _ in 0..3{normal.iterate(&mut s).unwrap();let metrics=normal.gaps_and_evs().unwrap();expected.push((bits(&normal),metrics));}
    assert!(observed==expected);assert!(normal.rank_pipeline.is_none());
}
'''
    save(p,s);modified.append(p)
    p=root/'exact_reuse/tests.rs';s=p.read_text(encoding='utf-8')
    s=replace(s,'    let mut selection=None;','    let pipeline=std::env::var("PREFLOP_GPU_RANK_PIPELINE").ok().as_deref()==Some("1");\n    assert!(!pipeline || (narrow && !production));\n    let mut selection=None;')
    s=replace(s,'let mut g=if production{','let mut g=if pipeline{super::super::rank_pipeline::new(&s,23000).unwrap()}else if production{')
    s=replace(s,'"narrow_offsets":g.throughput_narrow,"production_selection":production,','"narrow_offsets":g.throughput_narrow,"rank_pipeline":g.rank_pipeline.as_ref().map(|k|k.report()),"production_selection":production,')
    save(p,s);modified.append(p)
    mapping={}
    # Include unchanged qualified helper in the integration source manifest.
    modified.append(root/'rank_pipeline.cu')
    for p in modified:
        dest=HERE/'artifacts/c22-v2'/p.relative_to(LAB/'crates/solver');assert not dest.exists()
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
        mapping[p.relative_to(LAB).as_posix()]=dict(archive=dest.relative_to(HERE).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    (HERE/'artifacts/c22-v2-source-map.json').write_text(json.dumps(mapping,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
