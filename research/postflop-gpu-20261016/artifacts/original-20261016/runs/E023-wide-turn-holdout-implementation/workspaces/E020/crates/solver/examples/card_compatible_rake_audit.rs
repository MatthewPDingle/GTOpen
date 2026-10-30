//! Research-only configured-rake HU tree export. Writes no game saves.
#[cfg(not(feature = "preflop-research"))]
fn main() { panic!("Build with --features preflop-research"); }

#[cfg(feature = "preflop-research")]
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use serde_json::{json, Value};
    use solver::preflop::{PreflopConfig, PreflopSolver, equity::EquityTable, gpu::PreflopGpu};
    use std::sync::Arc;
    let args: Vec<_> = std::env::args().skip(1).collect();
    assert_eq!(args.len(),3,"CONFIG KERNEL OUTPUT");
    assert!(!std::path::Path::new(&args[2]).exists(),"preserve evidence");
    rayon::ThreadPoolBuilder::new().num_threads(4).build_global()?;
    let eq=Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin",20000));
    let cfg:PreflopConfig=serde_json::from_slice(&std::fs::read(&args[0])?)?;
    let source=std::fs::read_to_string(&args[1])?;
    let mut s=PreflopSolver::new(cfg,eq.clone())?;
    s.prune=false;
    let mut g=PreflopGpu::new(&s,1024)?;
    if s.cfg.rake_pct!=0. {assert!(g.enable_learned_interface_research(&s,&source,false).is_err());}
    let plan=g.enable_card_compatible_hu_rake_research(&s,&source)?;
    assert!(g.enable_card_compatible_hu_rake_research(&s,&source).is_err());
    let optimization=g.skip_redundant_interface_work(&s)?;
    let mut records=Vec::new();
    for target in [1000,10000] {
        while s.iteration<target {g.iterate(&mut s)?;}
        let (gaps,evs)=g.gaps_and_evs()?;g.sync_to_cpu(&mut s)?;
        let nodes:Vec<Value>=s.nodes.iter().enumerate().map(|(i,n)| {
            let children:Vec<usize>=(0..n.actions.len()).map(|a|s.child(i,a)).collect();
            let strategy=if n.kind==0 {s.average_strategy(i)} else {vec![]};
            json!({"kind":n.kind,"actor":n.actor,"children":children,"strategy":strategy,
                "pot":n.pot,"invested":n.invested,"winner":n.winner,"r":n.r,
                "actions":n.actions.iter().map(|a|json!({"kind":a.kind,"to":a.to})).collect::<Vec<_>>()})
        }).collect();
        let mut paths=Vec::new();let mut pending=vec![(0usize,vec![])];
        while let Some((i,path))=pending.pop() {if s.nodes[i].kind==0 {
            paths.push(path.clone());
            for a in 0..s.nodes[i].actions.len() {let mut child=path.clone();child.push(a);pending.push((s.child(i,a),child));}
        }}
        let before=s.arena_snapshot();let mut probe=PreflopGpu::new(&s,1024)?;
        probe.enable_card_compatible_hu_rake_research(&s,&source)?;
        probe.skip_redundant_interface_work(&s)?;
        let frontier=probe.research_frontier_action_values(&s,&paths)?;
        probe.sync_to_cpu(&mut s)?;assert_eq!(before,s.arena_snapshot());drop(probe);
        records.push(json!({"iteration":target,"gaps":gaps,"evs":evs,"nodes":nodes,"frontier":frontier}));
        println!("{} nodes, iteration {target}, gaps {gaps:?}",s.nodes.len());
    }
    drop(g);
    let mut cfg3=s.cfg.clone();cfg3.positions=vec!["BTN".into(),"SB".into(),"BB".into()];cfg3.posts=vec![0.,0.5,1.];
    let s3=PreflopSolver::new(cfg3,eq)?;let mut g3=PreflopGpu::new(&s3,1024)?;
    assert!(g3.enable_card_compatible_hu_rake_research(&s3,&source).is_err());
    let result=json!({"config":s.cfg,"plan":plan,"optimization":optimization,
        "postflop_order":s.postflop_order(),"class_base":s.fit.as_ref().map(|f|f.class_base()),
        "guards_passed":true,"records":records,
        "scope":"Two-player research only. Fixed Balanced leaf values with configured rake. No saves or production access."});
    std::fs::write(&args[2],serde_json::to_vec_pretty(&result)?)?;
    Ok(())
}
