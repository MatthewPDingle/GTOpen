#[cfg(test)]
mod deployed_reference_tests {
    use super::*;
    #[test]
    fn deployed_reference_retains_literal_choices_with_accurate_compact_budget() {
        // Fixed terms are folded into base for this measured-cost host fixture.
        // HU cost includes 13,564,508 metadata bytes, not just equity entries.
        let accurate=5316.606588;let literal=4902.313904;let fixed_extra=25_837_752;
        let hu=316_273_252;let u=846156;let c=432300;
        for (budget,old_b,old_hu,corrected_b,corrected_hu,expected_bytes) in [
            (19000,24,false,23,true,12_689_815_140u64),
            (21000,27,true,27,false,13_887_980_392),
            (23000,31,false,30,true,14_747_563_140),
        ] {
            let old=reference_multiway_plan(budget,literal,0,u,hu,true).unwrap().unwrap();
            let corrected=reference_multiway_plan(budget,accurate,0,u,hu,true).unwrap().unwrap();
            assert_eq!((old.batch,old.use_eq_cache),(old_b,old_hu));
            assert_eq!((corrected.batch,corrected.use_eq_cache),(corrected_b,corrected_hu));
            let selected=deployed_compatible_multiway_plan(budget,accurate,literal,0,fixed_extra,u,c,hu,true,false).unwrap().unwrap();
            assert_eq!(selected.reference_source,"deployed_prepass");assert_eq!(selected.literal_reference,Some(old));
            assert_eq!(selected.plan.reference,Some(old));assert_eq!(selected.plan.storage.batch,old_b);
            assert!(!selected.plan.minimal_metadata && selected.plan.storage.normalized_bytes>0);
            let physical=accurate*1e6+(fixed_extra+selected.plan.storage.cache_len*4
                +selected.plan.storage.normalized_bytes+if old_hu {hu}else{0}) as f64;
            assert_eq!(physical.round() as u64,expected_bytes);
            assert!(physical<=budget as f64*1e6);
        }
    }
    #[test]
    fn deployed_reference_only_changes_when_exact_target_cannot_fit() {
        // Literal B4 fits compact storage despite corrected union choosing B3.
        let p=deployed_compatible_multiway_plan(3,0.5,0.,0,0,1000,500,400_000,true,false).unwrap().unwrap();
        assert_eq!(p.reference_source,"deployed_prepass");assert_eq!(p.plan.storage.batch,4);
        assert!(!p.plan.reference.unwrap().use_eq_cache);
        // No compaction: accurate B4 CDF itself exceeds budget even in minimal
        // metadata. Corrected B3/cache-on can fit via original-layout fallback.
        let p=deployed_compatible_multiway_plan(3,0.5,0.,0,100_000,1000,1000,400_000,true,false).unwrap().unwrap();
        assert_eq!(p.reference_source,"corrected_budget_fallback");
        assert_eq!(p.literal_reference.unwrap().batch,4);assert_eq!(p.plan.storage.batch,3);
        assert!(p.plan.minimal_metadata && p.plan.reference.unwrap().use_eq_cache);
        let physical=0.5e6+(p.plan.storage.cache_len*4+400_000) as f64;
        assert!(physical<=3e6);
        // Literal B5 wins over optional normalization at the required B.
        let p=deployed_compatible_multiway_plan(4,0.5,0.,0,0,1000,1000,0,false,false).unwrap().unwrap();
        assert_eq!(p.reference_source,"deployed_prepass");assert_eq!(p.plan.storage.batch,5);
        assert_eq!(p.plan.storage.normalized_bytes,0);
    }
    #[test]
    fn deployed_reference_keeps_no_forced_policy_four_byte_boundary() {
        // The pre-pass allocator omitted even the four-byte empty placeholder.
        // Compact storage can safely preserve B1 across that accounting edge.
        let corrected=reference_multiway_plan(1,0.320004,0,1000,0,false).unwrap();
        assert!(corrected.is_none());
        let p=deployed_compatible_multiway_plan(1,0.320004,0.32,0,0,1000,500,0,false,false).unwrap().unwrap();
        assert_eq!(p.reference_source,"deployed_prepass");assert_eq!(p.plan.storage.batch,1);
        let actual=0.320004e6+(p.plan.storage.cache_len*4+p.plan.storage.normalized_bytes) as f64;
        assert!(actual<=1e6);
    }
    #[test]
    fn deployed_reference_identifies_capacity_extension_and_total_no_fit() {
        let p=deployed_compatible_multiway_plan(3,2.5,0.,0,0,1000,500,0,false,false).unwrap().unwrap();
        assert_eq!(p.reference_source,"capacity_extension");assert!(p.plan.reference.is_none());
        assert_eq!(p.literal_reference.unwrap().batch,4);assert_eq!(p.plan.storage.batch,1);
        assert!(!p.plan.minimal_metadata && p.plan.storage.normalized_bytes==0);
        assert!(2.5e6+p.plan.storage.cache_len as f64*4.<=3e6);
        assert!(deployed_compatible_multiway_plan(3,2.9,0.,0,0,1000,500,0,false,false).unwrap().is_none());
        assert!(deployed_compatible_multiway_plan(3,0.4,0.5,0,0,1000,500,0,false,false).is_err());
        assert!(deployed_compatible_multiway_plan(3,f64::NAN,0.,0,0,1000,500,0,false,false).is_err());
    }
}
