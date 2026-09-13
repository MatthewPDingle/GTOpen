"""Prepare fresh-only C21 integration using the validated C19 test scaffold."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
EXTRAS=r"""
    p=root/'exact_reuse.rs';s=p.read_text()
    old='    pub(super) table:CudaSlice<u32>, pub(super) aliases:CudaSlice<u32>,'
    assert s.count(old)==1
    s=s.replace(old,old+'\n    #[cfg(all(test, feature = "preflop-research"))]\n    pub(super) cdf_learning:Option<CudaFunction>,')
    old='            terminal:module.load_function("pf_exact_reuse_terminal").map_err(e)?,'
    assert s.count(old)==1
    s=s.replace(old,old+'\n            #[cfg(all(test, feature = "preflop-research"))]\n            cdf_learning:if super::cdf_zero_predicate::constructor_active(){Some(module.load_function("pf_exact_reuse_cdf_sparse_predicate").map_err(e)?)}else{None},')
    old='self.stream.launch_builder(&r.cdf)';assert s.count(old)==1
    s=s.replace(old,'self.stream.launch_builder(r.cdf_for_gate(gate))')
    s+='''
impl ExactReuse {
    pub(super) fn cdf_for_gate(&self,gate:i32)->&CudaFunction {
        let _=gate;
        #[cfg(all(test, feature = "preflop-research"))]
        if gate!=0 {if let Some(f)=self.cdf_learning.as_ref(){return f;}}
        &self.cdf
    }
}
'''
    save(p,s)
    p=root/'cohort_reuse/tests.rs';s=p.read_text()
    old='    let initial=bits(&g);let _=g.gaps_and_evs().unwrap();let before=bits(&g);'
    assert s.count(old)==1
    s=s.replace(old,'''    let selected=g.research_exact_reuse.as_ref().unwrap();
    assert!(std::ptr::eq(selected.cdf_for_gate(0),&selected.cdf));
    assert!(std::ptr::eq(selected.cdf_for_gate(1),selected.cdf_learning.as_ref().unwrap()));
'''+old)
    old='    assert!(initial==bits(&normal));assert!(!super::super::cdf_zero_predicate::constructor_active());'
    assert s.count(old)==1
    s=s.replace(old,old+'''
    let retained=normal.research_exact_reuse.as_ref().unwrap();
    assert!(retained.cdf_learning.is_none());
    assert!(std::ptr::eq(retained.cdf_for_gate(0),&retained.cdf));
    assert!(std::ptr::eq(retained.cdf_for_gate(1),&retained.cdf));
''')
    save(p,s)
"""
def main():
    s=(HERE/'prepare_c19_integration.py').read_text(encoding='utf-8')
    s=s.replace('C19','C21').replace('c19','c21').replace('cdf_interleave','cdf_zero_predicate')
    s=s.replace('PREFLOP_GPU_CDF_INTERLEAVE','PREFLOP_GPU_CDF_ZERO_PREDICATE').replace('interleaved','sparse_scan')
    old='''    let before=bits(&g);let _=g.gaps_and_evs().unwrap();assert_eq!(before,bits(&g));
    drop(g);let normal=PreflopGpu::new_research_narrow_cohorts(&s,2000).unwrap();
    assert_eq!(before,bits(&normal));assert!(!super::super::cdf_zero_predicate::constructor_active());'''
    new='''    let initial=bits(&g);let _=g.gaps_and_evs().unwrap();let before=bits(&g);
    // First evaluation populates roots/value buffers; it must not learn.
    assert!(initial.0==before.0 && initial.1==before.1);
    let _=g.gaps_and_evs().unwrap();assert!(before==bits(&g));
    drop(g);let normal=PreflopGpu::new_research_narrow_cohorts(&s,2000).unwrap();
    assert!(initial==bits(&normal));assert!(!super::super::cdf_zero_predicate::constructor_active());'''
    assert s.count(old)==1;s=s.replace(old,new)
    assert s.count('    mapping={}')==1;s=s.replace('    mapping={}',EXTRAS+'\n    mapping={}')
    p=HERE/'prepare_c21_integration.py';assert not p.exists();p.write_text(s,encoding='utf-8',newline='\n')
    s=(HERE/'run_c19.py').read_text(encoding='utf-8')
    s=s.replace('C19','C21').replace('c19','c21').replace('PREFLOP_GPU_CDF_INTERLEAVE','PREFLOP_GPU_CDF_ZERO_PREDICATE').replace('interleaved','sparse_scan')
    s=s.replace('c21-v3-source-map','c21-v2-source-map').replace('c21-numerical-v2','c21-numerical-v1')
    p=HERE/'run_c21.py';assert not p.exists();p.write_text(s,encoding='utf-8',newline='\n')
if __name__=='__main__':main()
