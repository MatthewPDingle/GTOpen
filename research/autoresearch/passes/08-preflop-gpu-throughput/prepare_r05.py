"""Expose the already-qualified C24 implementation in normal GPU selection."""
import hashlib,json
from pathlib import Path
from prepare_c19_integration import save
HERE=Path(__file__).resolve().parent;LAB=HERE.parents[3]
root=LAB/'crates/solver/src/preflop/gpu'
files=[root/'static_cdf/ordinary.rs',root/'static_cdf.rs',root.parent/'gpu.rs',root/'adaptive_throughput.rs',root/'cross_player_inventory.rs',LAB/'crates/server/src/main.rs',LAB/'crates/solver/tests/preflop_throughput.rs']
archive=HERE/'artifacts/r05-before';archive.mkdir()
manifest={}
for p in files:
    name=str(p.relative_to(LAB)).replace('/','__').replace('\\','__');(archive/name).write_bytes(p.read_bytes())
    manifest[str(p.relative_to(LAB))]=hashlib.sha256(p.read_bytes()).hexdigest()
(HERE/'artifacts/r05-before-source-map.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
def edit(p,old,new):
    s=p.read_text(encoding='utf-8');assert s.count(old)==1,(p,old);save(p,s.replace(old,new))
p=root/'cross_player_inventory.rs';s=p.read_text(encoding='utf-8')
start=s.index('pub(super) fn device_buffer_bytes(');end=s.index('\n}',start)+2
inventory=s[start:end].replace('pub(super) fn device_buffer_bytes','pub(crate) fn ordinary_buffer_bytes')
edit(p,s[start:end],'pub(super) fn device_buffer_bytes(g:&PreflopGpu)->std::collections::BTreeMap<&\'static str,usize>{ super::static_cdf::ordinary::ordinary_buffer_bytes(g) }')
p=root/'static_cdf/ordinary.rs'
edit(p,'//! C24 ordinary-path prototype. Only compiled in opt-in research tests.','//! Static rank-boundary CDFs for ordinary GPU batches (C24).')
edit(p,'thread_local!{static FAIL_STAGE','#[cfg(test)]\npub(crate) fn set_failure_stage(stage:u32){FAIL_STAGE.set(stage);}\n#[cfg(test)]\nthread_local!{static FAIL_STAGE')
edit(p,'fn fault(g:&PreflopGpu,stage:u32)->Result<(),String>{','#[cfg(test)]\nfn fault(g:&PreflopGpu,stage:u32)->Result<(),String>{')
edit(p,'pub(crate) fn promote(mut g:PreflopGpu,s:&PreflopSolver,budget:u64)->Result<PreflopGpu,String>{\n    if g.warmed || g.eval_warmed || g.static_cdf.is_some() || g.research_exact_reuse.is_some()\n        || g.research_cohorts.is_some() || !g.exact_reuse_compatible() || g.research_unit_probability\n        || g.research_samples!=SAMPLES as u32 || !(1..=32).contains(&g.mw_batch) {',
'''pub(crate) fn compatible(g:&PreflopGpu)->bool {
    #[cfg(feature="preflop-research")]
    if g.research_unit_probability || g.research_samples!=SAMPLES as u32 {return false;}
    !g.warmed && !g.eval_warmed && g.static_cdf.is_none() && g.research_exact_reuse.is_none()
        && g.research_cohorts.is_none() && g.exact_reuse_compatible() && (1..=32).contains(&g.mw_batch)
}

pub(crate) fn promote(mut g:PreflopGpu,s:&PreflopSolver,budget:u64)->Result<PreflopGpu,String>{
    if !compatible(&g) {''')
for stage in [1,2,3]:edit(p,f'    fault(&g,{stage})?;',f'    #[cfg(test)]\n    fault(&g,{stage})?;')
s=p.read_text(encoding='utf-8').replace('super::super::cross_player_inventory::device_buffer_bytes','ordinary_buffer_bytes')
start=s.index('    let folder=std::path::PathBuf::from(');end=s.index('    g.static_cdf=Some(',start)
block=s[start:end];block=block.replace('    let folder=std::path::PathBuf::from(std::env::var("PREFLOP_GPU_ORDINARY_STATIC_OUTPUT").map_err(e)?);','    let folder=std::path::PathBuf::from(folder);')
s=s[:start]+'    #[cfg(all(test, feature="preflop-research"))]\n    if let Ok(folder)=std::env::var("PREFLOP_GPU_ORDINARY_STATIC_OUTPUT") {\n'+block+'    }\n'+s[end:]
s=s.replace('        g.phase_mark(', '        #[cfg(test)]\n        g.phase_mark(').replace('#[cfg(test)]\nmod tests;','#[cfg(all(test, feature="preflop-research"))]\nmod tests;')
s+='\n'+inventory+'\n';save(p,s)
edit(root/'static_cdf.rs','#[cfg(all(test, feature = "preflop-research"))]\npub(super) mod ordinary;','pub(super) mod ordinary;')
edit(root.parent/'gpu.rs','                    #[cfg(all(test, feature = "preflop-research"))]\n                    if self.static_cdf.is_some() {','                    if self.static_cdf.is_some() {')
p=root/'adaptive_throughput.rs'
edit(p,'        let (g,mut report)=choose(budget_mb, free,','        let (mut g,mut report)=choose(budget_mb, free,')
edit(p,'        report.narrow_offsets=g.throughput_narrow;','''        if narrow && report.mode=="normal_gpu" && static_cdf::ordinary::compatible(&g) {
            g=match static_cdf::ordinary::promote(g,s,budget_mb) {
                Ok(g)=>g,
                Err(error)=>{static_error=Some(error);Self::new(s,budget_mb)?}
            };
        }
        report.narrow_offsets=g.throughput_narrow;''')
# Reuse the same exact arena and real OOM recovery proof for the ordinary selector.
s=p.read_text(encoding='utf-8');start=s.index('    #[test]\n    fn static_promotion_failure_rebuilds_retained_engine()');end=s.index('\n    #[test]',start+10)
t=s[start:end].replace('static_promotion_failure_rebuilds_retained_engine','ordinary_static_promotion_failure_rebuilds_reference_engine').replace('static_cdf::FAIL_STAGE.set(stage);','static_cdf::ordinary::set_failure_stage(stage);').replace('Ok(2_000_000_000),true','Err("forced ordinary selection".into()),true').replace('assert_eq!(report.mode,"retained_cohorts");assert!(report.narrow_offsets);','assert_eq!(report.mode,"normal_gpu");assert!(!report.narrow_offsets);').replace('assert_eq!(static_cdf::FAIL_STAGE.get(),0);','')
s=s[:end]+'\n'+t+s[end:];save(p,s)
edit(LAB/'crates/solver/tests/preflop_throughput.rs','assert!(report.static_cdf_fallback_reason.is_none());','assert_eq!(report.static_cdf_fallback_reason.is_some(),n==4 && budget==128);')
p=LAB/'crates/server/src/main.rs'
edit(p,'"Shared GPU evaluation".into()\n                    } else {','"Shared GPU evaluation".into()\n                    } else if selection.static_cdf {\n                        "Memory-efficient GPU evaluation".into()\n                    } else {')
