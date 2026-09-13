use super::*;
#[test]
fn rle_all_logical_prefixes_match_original_scan_bits(){
    let s=super::super::tests::fixture(false);let mut g=PreflopGpu::new(&s,2000).unwrap();
    g.enable_research_exact_cdf_reuse().unwrap();assert!(g.enable_research_rle_cdf(1).is_err());
    g.enable_research_rle_cdf(512*1024*1024).unwrap();
    let codec=g.research_exact_reuse.as_ref().unwrap().rle.as_ref().unwrap();
    let slots=6usize;let batch=32u32;let start=1u32;let count=4u32;
    let host_work=[4u32,3,0,5,2];let host_blocks=[0u32,1,2,3,4,5];
    let work=g.stream.clone_htod(&host_work).unwrap();let blocks=g.stream.clone_htod(&host_blocks).unwrap();
    let aliases=g.stream.clone_htod(&[0u32,1,2,3]).unwrap();
    let poison=f32::from_bits(0x7fc01234);let words=slots*batch as usize*(NUM_CLASSES+1);
    let mask_words=slots*batch as usize*6;let mut saw_zero_rounding_change=false;
    for compact in [0i32,1] {for pattern in 0..16usize {
        let mut normalized=vec![0f32;slots*NUM_CLASSES];
        let mut seed=17u32+pattern as u32;
        for (i,v) in normalized.iter_mut().enumerate(){
            seed=seed.wrapping_mul(1664525).wrapping_add(1013904223);
            let h=i%NUM_CLASSES;
            *v=match pattern {
                0=>0.,1=>if h==63{1.}else{0.},2=>1./169.,
                3=>if h%11==0{(h%7+1) as f32/100.}else{0.},
                4=>if h%3==0{f32::from_bits((h%7+1) as u32)}else{0.},
                5=>if h%4==0{0.5}else if h%4==1{1e-8}else{0.},
                _=>if seed&3==0{0.}else{(seed%100+1) as f32*2f32.powi(-(((seed>>12)%28) as i32)-6)},
            };
        }
        let mut order=Vec::new();
        for sample in 0..40 {for rank in 0..NUM_CLASSES {order.push(((rank*37+sample*13)%NUM_CLASSES) as u32);}}
        let d_norm=g.stream.clone_htod(&normalized).unwrap();let d_order=g.stream.clone_htod(&order).unwrap();
        for (sample_start,sample_count,gate) in [(0u32,32u32,0i32),(3,7,1),(11,5,1)] {
            let host_active=if sample_start==11{[1u32,1,0,1,1,1]}else{[1u32;6]};
            let host_mass=if sample_start==11{[1f32,1.,1.,1.,1.,0.]}else{[1f32;6]};
            let active=g.stream.clone_htod(&host_active).unwrap();let mass=g.stream.clone_htod(&host_mass).unwrap();
            let mut original=g.stream.clone_htod(&vec![poison;words+17]).unwrap();
            let mut encoded=g.stream.clone_htod(&vec![poison;words+17]).unwrap();
            let mut decoded=g.stream.clone_htod(&vec![poison;words+17]).unwrap();
            let mut masks=g.stream.clone_htod(&vec![0xdeadbeefu32;mask_words+17]).unwrap();
            unsafe {
                g.stream.launch_builder(&g.f_multiway_cdf).arg(&work).arg(&start).arg(&blocks).arg(&d_order)
                    .arg(&d_norm).arg(&mass).arg(&active).arg(&gate).arg(&compact).arg(&mut original)
                    .arg(&sample_start).arg(&sample_count).arg(&batch)
                    .launch(LaunchConfig{grid_dim:(count,sample_count.div_ceil(4),1),block_dim:(128,1,1),shared_mem_bytes:0}).unwrap();
                g.stream.launch_builder(&codec.cdf).arg(&work).arg(&start).arg(&blocks).arg(&d_order)
                    .arg(&d_norm).arg(&mass).arg(&active).arg(&gate).arg(&compact).arg(&mut encoded)
                    .arg(&sample_start).arg(&sample_count).arg(&batch).arg(&aliases).arg(&mut masks)
                    .launch(LaunchConfig{grid_dim:(count,sample_count.div_ceil(4),1),block_dim:(128,1,1),shared_mem_bytes:0}).unwrap();
                g.stream.launch_builder(&codec.decode).arg(&work).arg(&start).arg(&blocks).arg(&mass).arg(&active)
                    .arg(&gate).arg(&compact).arg(&encoded).arg(&masks).arg(&mut decoded).arg(&sample_count).arg(&batch)
                    .launch(LaunchConfig{grid_dim:(count,sample_count,1),block_dim:(192,1,1),shared_mem_bytes:0}).unwrap();
            }
            let a=g.stream.clone_dtoh(&original).unwrap();let b=g.stream.clone_dtoh(&decoded).unwrap();
            assert!(a.iter().zip(&b).all(|(x,y)|x.to_bits()==y.to_bits()),"prefix mismatch compact={compact} pattern={pattern} offset={sample_start}");
            let packed=g.stream.clone_dtoh(&encoded).unwrap();let mask=g.stream.clone_dtoh(&masks).unwrap();
            assert!(packed[words..].iter().all(|x|x.to_bits()==poison.to_bits()));assert!(mask[mask_words..].iter().all(|x|*x==0xdeadbeef));
            for k in 0..count as usize {
                let slot=host_work[start as usize+k] as usize;
                if (gate!=0&&host_active[slot]==0)||host_mass[slot]<=0. {continue;}
                let physical=if compact!=0{k}else{slot};
                for local in 0..sample_count as usize {
                    let row=physical*batch as usize+local;let base=row*(NUM_CLASSES+1);
                    let emitted=mask[row*6..row*6+6].iter().map(|w|w.count_ones() as usize).sum::<usize>();
                    assert!(emitted<=NUM_CLASSES);assert!(packed[base+emitted..base+NUM_CLASSES+1].iter().all(|x|x.to_bits()==poison.to_bits()));
                    assert_eq!(mask[row*6+5]>>9,0);
                    for rank in 0..NUM_CLASSES {
                        let hand=order[(sample_start as usize+local)*NUM_CLASSES+rank] as usize;
                        if normalized[physical*NUM_CLASSES+hand]==0. && a[base+rank+1].to_bits()!=a[base+rank].to_bits(){saw_zero_rounding_change=true;}
                    }
                }
            }
        }
    }}
    assert!(saw_zero_rounding_change,"fixture must cover prefix rounding changes across zero inputs");
}
