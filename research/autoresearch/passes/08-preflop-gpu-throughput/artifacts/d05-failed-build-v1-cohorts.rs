//! D05: bounded cohort partitions, using exact membership-mask union counts.
use super::*;

fn histogram(sets: &[HashSet<u32>]) -> Vec<usize> {
    assert!(sets.len()<=9);
    let max=sets.iter().flatten().copied().max().map_or(0,|x|x as usize+1);
    let mut membership=vec![0usize;max];
    for (p,s) in sets.iter().enumerate() { for &id in s { membership[id as usize]|=1<<p; }}
    let mut hist=vec![0;1<<sets.len()];
    for mask in membership { if mask!=0 {hist[mask]+=1;} }
    hist
}
fn unions(hist: &[usize]) -> Vec<usize> {
    (0..hist.len()).map(|subset|hist.iter().enumerate().filter(|(mask,_)|mask&subset!=0).map(|(_,n)|n).sum()).collect()
}
fn partitions(mask: usize, max_group: u32) -> Vec<Vec<usize>> {
    if mask==0 {return vec![vec![]];}
    let first=1usize<<mask.trailing_zeros(); let rest=mask^first;
    let mut subset=rest; let mut out=Vec::new();
    loop {
        if subset.count_ones()<max_group {
            for mut tail in partitions(rest^subset,max_group) {tail.insert(0,subset|first);out.push(tail);}
        }
        if subset==0 {break;}
        subset=(subset-1)&rest;
    }
    out
}
#[test]
fn cohort_membership_and_partitions() {
    let sets=vec![[0,1,2].into_iter().collect(),[1,2,3].into_iter().collect(),[2,4].into_iter().collect()];
    let h=histogram(&sets);let u=unions(&h);
    assert_eq!(h.iter().sum::<usize>(),5);assert_eq!(h[7],1);assert_eq!(h[0],0);
    for mask in 0..8 {
        let players:Vec<_>=(0..3).filter(|p|mask&(1<<p)!=0).collect();
        assert_eq!(u[mask],super::union_len(&players,&sets));
    }
    let mut bell=[0usize;10];bell[0]=1;
    for n in 1..=9 {
        // Independent restricted Bell recurrence, blocks of size 1..4.
        let mut choose=1;
        for k in 1..=n.min(4) {bell[n]+=choose*bell[n-k];choose=choose*(n-k)/k;}
        let all=(1usize<<n)-1;let ps=partitions(all,4);
        assert_eq!(ps.len(),bell[n]);let mut seen=HashSet::new();
        for p in ps {let mut covered=0;for &group in &p {
            assert!((1..=4).contains(&group.count_ones()));assert_eq!(covered&group,0);covered|=group;
        }assert_eq!(covered,all);assert!(seen.insert(p));}
    }
    assert_eq!(bell[8],3795);
    assert_eq!(partitions(0b11111,1),vec![vec![1,2,4,8,16]]);
}

pub(super) fn inventory(static_sets:&[HashSet<u32>],unique_sets:&[HashSet<u32>],buffers:&std::collections::BTreeMap<&str,usize>)->serde_json::Value {
    let n=static_sets.len();let all=(1<<n)-1;
    let static_hist=histogram(static_sets);let unique_hist=histogram(unique_sets);
    let su=unions(&static_hist);let uu=unions(&unique_hist);
    for mask in 1..=all {
        if mask.count_ones()<=2 || mask==all {
            let p:Vec<_>=(0..n).filter(|p|mask&(1<<p)!=0).collect();
            assert_eq!(su[mask],super::union_len(&p,static_sets));
            assert_eq!(uu[mask],super::union_len(&p,unique_sets));
        }
    }
    let base:usize=buffers.values().sum();let old_capacity=buffers["d_mw_normalized"]/(169*4);
    let baseline:usize=unique_sets.iter().map(|s|s.len()).sum();
    let plan=|groups:&[usize]| {
        let largest=groups.iter().map(|m|m.count_ones() as usize).max().unwrap();
        let capacity=old_capacity.max(groups.iter().map(|&m|su[m]).max().unwrap());
        let cdf=capacity*32*170*4;let normalized=capacity*169*4;
        let classification=(capacity+(capacity*2).next_power_of_two())*4;
        let maps=groups.len()*su[all]*4;let work=groups.iter().map(|&m|su[m]*4).sum::<usize>();
        let value=(largest-1)*buffers["d_val"];let prob=(largest-1)*buffers["d_mw_prob"];
        let total=base-buffers["d_mw_cdf"]-buffers["d_mw_normalized"]+cdf+normalized+classification+maps+work+value+prob;
        let reserve=256usize*1024*1024;let rows=groups.iter().map(|&m|uu[m]).sum::<usize>();
        json!({"group_masks":groups,"groups":groups.iter().map(|&m|(0..n).filter(|p|m&(1<<p)!=0).collect::<Vec<_>>()).collect::<Vec<_>>(),
            "largest_group":largest,"static_capacity":capacity,"static_rows":groups.iter().map(|&m|su[m]).sum::<usize>(),
            "cdf_rows":rows,"saved_fraction":1.0-rows as f64/baseline as f64,"cdf_bytes":cdf,"normalized_bytes":normalized,
            "classification_bytes":classification,"maps_bytes":maps,"work_bytes":work,"extra_value_bytes":value,
            "extra_prob_bytes":prob,"total_bytes":total,"reserve_bytes":reserve,"planned_initial_peak_bytes":total+reserve,
            "replace_existing_peak_bytes":total+reserve+buffers["d_mw_cdf"]+buffers["d_mw_normalized"]+(old_capacity+(old_capacity*2).next_power_of_two())*4,
            "fits_preplanned_23gb":total+reserve<=23_000_000_000usize})
    };
    let mut plans:Vec<_>=partitions(all,4).iter().map(|g|plan(g)).collect();
    // Static topology chooses deployable groups; no learned-strategy download is needed.
    plans.sort_by_key(|p|(p["static_rows"].as_u64().unwrap(),p["total_bytes"].as_u64().unwrap(),p["group_masks"].to_string()));
    let selected=plans.iter().find(|p|p["fits_preplanned_23gb"]==true).unwrap().clone();
    let best_observed=plans.iter().filter(|p|p["fits_preplanned_23gb"]==true).min_by_key(|p|p["cdf_rows"].as_u64().unwrap()).unwrap().clone();
    let mut natural=Vec::new();
    for size in 2..=4 {
        let groups:Vec<_>=(0..n).collect::<Vec<_>>().chunks(size).map(|s|s.iter().fold(0,|m,p|m|(1<<p))).collect();
        natural.push(plan(&groups));
    }
    let mut ordered:Vec<_>=plans.iter().collect();
    ordered.sort_by_key(|p|(p["planned_initial_peak_bytes"].as_u64().unwrap(),p["cdf_rows"].as_u64().unwrap()));
    let mut best=u64::MAX;let mut frontier=Vec::new();
    for p in ordered {let rows=p["cdf_rows"].as_u64().unwrap();if rows<best {best=rows;frontier.push(p.clone());}}
    let compact:Vec<_>=plans.iter().map(|p|json!([p["group_masks"],p["cdf_rows"],p["static_rows"],p["planned_initial_peak_bytes"]])).collect();
    json!({"static_membership_histogram":static_hist,"unique_membership_histogram":unique_hist,"static_subset_unions":su,
        "unique_subset_unions":uu,"partitions_count":plans.len(),"all_partitions_columns":["group_masks","cdf_rows","static_rows","peak_bytes"],
        "all_partitions":compact,"selected_static_plan":selected,"best_observed_fitting_plan":best_observed,
        "natural_plans":natural,"pareto_frontier":frontier,"admitted":selected["saved_fraction"].as_f64().unwrap()>=0.25,
        "selection":"Minimum static topology union work among <=4-player partitions fitting 23GB; no observed strategy used for grouping"})
}
