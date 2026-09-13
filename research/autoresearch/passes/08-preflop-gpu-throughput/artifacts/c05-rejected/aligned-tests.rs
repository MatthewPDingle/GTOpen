use super::*;
#[test]
fn aligned_capacity_guards_include_transient_peak_and_tail(){
    let old=388082usize*32*170;let expected=388082usize*32*192+32;
    assert_eq!(allocation(old,expected*4).unwrap(),expected);
    assert_eq!((expected-old)*4,1_092_839_040);
    assert!(allocation(old,expected*4-1).is_err());
    assert!(allocation(0,usize::MAX).is_err());
    assert!(allocation(171,usize::MAX).is_err());
    assert!(allocation(usize::MAX/170*170,usize::MAX).is_err());
    for rows in [1usize,2,31,32,1000]{
        let words=allocation(rows*170,usize::MAX).unwrap();
        assert!(BIAS+(rows-1)*STRIDE+169<words);
        assert_eq!((BIAS+1)*4%128,0);assert_eq!(STRIDE*4%128,0);
    }
}
#[test]
fn aligned_prefixes_aliases_and_poison_match_original(){
    let s=super::super::tests::fixture(false);let mut g=PreflopGpu::new(&s,2000).unwrap();
    g.enable_research_exact_cdf_reuse().unwrap();let old=g.d_mw_cdf.len();
    assert!(g.enable_research_aligned_cdf(1).is_err());assert_eq!(g.d_mw_cdf.len(),old);
    assert!(!g.research_exact_reuse.as_ref().unwrap().aligned);
    g.enable_research_aligned_cdf(200_000_000).unwrap();
    assert!(g.enable_research_aligned_cdf(200_000_000).is_err());
    let f=&g.research_exact_reuse.as_ref().unwrap().cdf;
    let slots=6usize;let batch=32u32;let start=1u32;let count=4u32;
    let host_work=[4u32,3,0,5,2];let work=g.stream.clone_htod(&host_work).unwrap();
    let blocks=g.stream.clone_htod(&[0u32,1,2,3,4,5]).unwrap();
    let poison=f32::from_bits(0x7fc01234);
    let old_words=slots*batch as usize*170;let new_words=slots*batch as usize*192+32;
    let mut order=Vec::new();for sample in 0..40{for rank in 0..169{order.push(((rank*37+sample*13)%169) as u32);}}
    let d_order=g.stream.clone_htod(&order).unwrap();
    for compact in [0i32,1]{for alias in [false,true]{for pattern in 0..8usize{
        let physical=|k:usize|if compact!=0{k}else{host_work[start as usize+k] as usize};
        let host_alias=if alias{[0u32,0,2,2]}else{[0u32,1,2,3]};
        let aliases=g.stream.clone_htod(&host_alias).unwrap();
        let mut norm=vec![0f32;slots*169];let mut seed=17u32+pattern as u32;
        for (i,v) in norm.iter_mut().enumerate(){seed=seed.wrapping_mul(1664525).wrapping_add(1013904223);let h=i%169;
            *v=match pattern{0=>0.,1=>if h==63{1.}else{0.},2=>1./169.,3=>if h%11==0{(h%7+1) as f32/100.}else{0.},
                4=>if h%3==0{f32::from_bits((h%7+1) as u32)}else{0.},
                5=>if h%4==0{0.5}else if h%4==1{1e-8}else{0.},
                _=>if seed&3==0{0.}else{(seed%100+1) as f32*2f32.powi(-(((seed>>12)%28) as i32)-6)}};
        }
        for k in 0..4{let rep=host_alias[k] as usize;if k!=rep{let v=norm[physical(rep)*169..physical(rep)*169+169].to_vec();norm[physical(k)*169..physical(k)*169+169].copy_from_slice(&v);}}
        let d_norm=g.stream.clone_htod(&norm).unwrap();
        for (sample_start,sample_count,gate) in [(0u32,32u32,0i32),(3,1,1),(3,7,1),(3,23,1),(3,31,1)]{
            let inactive=!alias&&sample_count==7;
            let active=if inactive{[1u32,1,0,1,1,1]}else{[1u32;6]};
            let mass=if inactive{[1f32,1.,1.,1.,1.,0.]}else{[1f32;6]};
            let d_active=g.stream.clone_htod(&active).unwrap();let d_mass=g.stream.clone_htod(&mass).unwrap();
            let mut original=g.stream.clone_htod(&vec![poison;old_words+17]).unwrap();
            let mut aligned=g.stream.clone_htod(&vec![poison;new_words+17]).unwrap();
            let config=LaunchConfig{grid_dim:(count,sample_count.div_ceil(4),1),block_dim:(128,1,1),shared_mem_bytes:0};
            unsafe{
                g.stream.launch_builder(&g.f_multiway_cdf).arg(&work).arg(&start).arg(&blocks).arg(&d_order).arg(&d_norm)
                    .arg(&d_mass).arg(&d_active).arg(&gate).arg(&compact).arg(&mut original).arg(&sample_start).arg(&sample_count).arg(&batch).launch(config).unwrap();
                g.stream.launch_builder(f).arg(&work).arg(&start).arg(&blocks).arg(&d_order).arg(&d_norm)
                    .arg(&d_mass).arg(&d_active).arg(&gate).arg(&compact).arg(&mut aligned).arg(&sample_start).arg(&sample_count).arg(&batch).arg(&aliases).launch(config).unwrap();
            }
            let a=g.stream.clone_dtoh(&original).unwrap();let b=g.stream.clone_dtoh(&aligned).unwrap();let mut written=vec![false;new_words+17];
            for k in 0..4{
                let slot=host_work[start as usize+k] as usize;
                if (gate!=0&&active[slot]==0)||mass[slot]<=0.{continue;}
                let rep=host_alias[k] as usize;
                for local in 0..sample_count as usize{
                    let a_base=(physical(k)*32+local)*170;let b_base=BIAS+(physical(rep)*32+local)*STRIDE;
                    for logical in 0..170{assert_eq!(a[a_base+logical].to_bits(),b[b_base+logical].to_bits(),"compact={compact} alias={alias} pattern={pattern} k={k} local={local} logical={logical}");written[b_base+logical]=true;}
                }
            }
            assert!(b.iter().zip(written).all(|(v,w)|w||v.to_bits()==poison.to_bits()),"padding/unused capacity modified");
            assert!(a[old_words..].iter().all(|v|v.to_bits()==poison.to_bits()));
        }
    }}}
}
