#[cfg(test)]
mod compatibility_batch_tests {
    use super::*;
    fn original_oracle(budget:u64,base:f64,fixed:usize,slots:usize,eq:usize,has_eq:bool)->Option<(usize,bool)> {
        let per_particle=slots*(NUM_CLASSES+1)*4;
        let remaining=(budget as f64*1e6-base*1e6-fixed as f64).max(0.0) as usize;
        let batch=(remaining/per_particle).min(32).min(super::super::multiway::SAMPLES);
        if batch==0{return None;}
        let need=base+(fixed+per_particle*batch) as f64/1e6;
        Some((batch,has_eq && need+eq as f64/1e6<=budget as f64))
    }
    #[test]
    fn compatibility_reference_matches_original_union_budget_arithmetic() {
        for slots in [1usize,1000,846156] {for budget in [1u64,19_000,21_000,23_000] {
            for (base,fixed,eq,has_eq) in [(0.,0,0,false),(64.,100_000,2_000_000,true),(5330.,171_096,302_708_744,true)] {
                let got=reference_multiway_plan(budget,base,fixed,slots,eq,has_eq).unwrap().map(|p|(p.batch,p.use_eq_cache));
                assert_eq!(got,original_oracle(budget,base,fixed,slots,eq,has_eq));
            }
        }}
    }
    #[test]
    fn compatibility_compaction_keeps_reference_batch_and_cache_at_19_21_23gb() {
        // Algebraically reduced fixed costs reproduce the observed modeled
        // six-seat planner totals; this is a pure planner test, not a GPU claim.
        for budget in [19_000,21_000,23_000] {
            let p=compatible_multiway_plan(budget,5330.,171_096,26_008_848,846156,432300,302_708_744,true).unwrap().unwrap();
            let r=original_oracle(budget,5330.,171_096,846156,302_708_744,true).unwrap();
            assert_eq!((p.storage.batch,p.reference.as_ref().unwrap().use_eq_cache),r);
            assert!(p.storage.normalized_bytes>0);
            let bytes=26_008_848+p.storage.normalized_bytes+p.storage.cache_len*4+if r.1{302_708_744}else{0};
            assert!(5330.+bytes as f64/1e6<=budget as f64);
            if budget==23_000 {assert_eq!(p.storage.batch,30);}
        }
    }
    #[test]
    fn compatibility_drops_normalization_to_keep_required_grouping() {
        // 2.5 MB available: original can fit 3 x 680,000-byte particles, but
        // adding a 676,000-byte normalized table would force a smaller batch.
        let p=compatible_multiway_plan(3,0.5,0,0,1000,1000,0,false).unwrap().unwrap();
        assert_eq!(p.storage.batch,3);assert_eq!(p.storage.normalized_bytes,0);
        // More room within the same original batch makes normalization safe
        // only if it actually fits; normalization is not a priority over B.
        let p=compatible_multiway_plan(4,0.1,0,0,1000,500,0,false).unwrap().unwrap();
        assert_eq!(p.storage.batch,5);assert!(p.storage.normalized_bytes>0);
    }
    #[test]
    fn compatibility_keeps_hu_cache_and_refuses_extra_metadata_regression() {
        let no_cache=compatible_multiway_plan(3,0.5,0,0,1000,500,500_000,true).unwrap().unwrap();
        assert!(!no_cache.reference.unwrap().use_eq_cache); // compaction's free room must not toggle it
        let cached=compatible_multiway_plan(3,0.5,0,0,1000,1000,400_000,true).unwrap().unwrap();
        assert!(cached.reference.unwrap().use_eq_cache);assert_eq!(cached.storage.batch,3);
        assert_eq!(cached.storage.normalized_bytes,0);
        assert!(compatible_multiway_plan(3,0.5,0,100_000,1000,1000,400_000,true).is_err());
        // Direct CDF itself cannot fit at reference B: do not silently choose B-1.
        assert!(compatible_multiway_plan(3,0.5,0,500_000,1000,1000,0,false).is_err());
    }
    #[test]
    fn compatibility_capacity_extension_has_no_fabricated_reference() {
        // Old union needs 680k/particle and has only 600k; compact fits.
        let p=compatible_multiway_plan(1,0.4,0,0,1000,500,0,false).unwrap().unwrap();
        assert!(p.reference.is_none());assert_eq!(p.storage.batch,1);assert_eq!(p.storage.normalized_bytes,0);
        assert!(compatible_multiway_plan(1,0.9,0,0,1000,500,0,false).unwrap().is_none());
        assert!(reference_multiway_plan(23_000,0.,0,usize::MAX,0,false).is_err());
        assert!(compatible_multiway_plan(23_000,0.,0,0,1000,usize::MAX,0,false).is_err());
        assert!(reference_multiway_plan(1,f64::NAN,0,1,0,false).is_err());
    }
}
