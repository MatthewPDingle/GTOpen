
#[cfg(test)]
mod e041_inactive_controls {
    use super::*;

    fn seeded(len: usize, signed: bool) -> Store {
        let mut s = if signed { Store::i16(len as u64, 9) } else { Store::u16(len as u64, 9) };
        match &mut s {
            Store::I16 {q,scale} => {
                for (i,v) in q.as_mut_slice().iter_mut().enumerate() {
                    *v = (i as u16).wrapping_mul(997).wrapping_add(123) as i16;
                }
                for (i,v) in scale.as_mut_slice().iter_mut().enumerate() {
                    *v = f32::from_bits(0x7fc0_0100 + i as u32);
                }
            }
            Store::U16 {q,scale} => {
                for (i,v) in q.as_mut_slice().iter_mut().enumerate() {
                    *v = (i as u16).wrapping_mul(991).wrapping_add(117);
                }
                for (i,v) in scale.as_mut_slice().iter_mut().enumerate() {
                    *v = f32::from_bits(0x7fc0_0200 + i as u32);
                }
            }
            Store::F32(_) => unreachable!(),
        }
        s
    }
    fn raw_equal(a: &Store, b: &Store) {
        match (a,b) {
            (Store::I16 {q:lq,scale:ls},Store::I16 {q:rq,scale:rs}) => {
                assert_eq!(lq.as_slice(),rq.as_slice());
                assert_eq!(ls.as_slice().iter().map(|v|v.to_bits()).collect::<Vec<_>>(),
                    rs.as_slice().iter().map(|v|v.to_bits()).collect::<Vec<_>>());
            }
            (Store::U16 {q:lq,scale:ls},Store::U16 {q:rq,scale:rs}) => {
                assert_eq!(lq.as_slice(),rq.as_slice());
                assert_eq!(ls.as_slice().iter().map(|v|v.to_bits()).collect::<Vec<_>>(),
                    rs.as_slice().iter().map(|v|v.to_bits()).collect::<Vec<_>>());
            }
            _ => panic!("matching compressed stores required"),
        }
    }
    fn metadata(len: usize, values: &[f32]) -> ArenaLayout {
        let mut initial = [vec![f32::from_bits(0x7fc0_1234);3],vec![-0.0;7]];
        initial[0].extend_from_slice(values);initial[1].extend_from_slice(values);
        ArenaLayout { compact:true,len:0,active:vec![],copies:vec![],inactive:vec![],
            initial,zeros:vec![0.0;len] }
    }

    #[test]
    fn exact_inactive_zero_restore_matches_original_encoder_and_guards() {
        let mut cases = 0;
        for signed in [true,false] {
            for len in [0,1,2,7,8,15,16,17,31,32,33,1024,7777] {
                for which in 0..2 {
                    let values=vec![0.0;len];
                    let layout=metadata(len,&values);
                    let block=InactiveBlock {node:4,host:13,len,initial:[usize::MAX;2]};
                    let reference=seeded(len+30,signed);let candidate=seeded(len+30,signed);
                    unsafe {reference.write_f32(block.node,block.host,len,&values);}
                    layout.write_compressed_inactive(&candidate,&block,which);
                    raw_equal(&reference,&candidate);
                    // Dirty the owned target again; the sentinel must restore it repeatedly.
                    let dirty=vec![3.25;len];
                    unsafe {candidate.write_f32(block.node,block.host,len,&dirty);}
                    layout.write_compressed_inactive(&candidate,&block,which);
                    raw_equal(&reference,&candidate);
                    cases+=1;
                }
            }
        }
        assert_eq!(cases,52);
        println!("E041_CPU_ZERO_RESTORE cases={cases}");
    }

    #[test]
    fn explicit_inactive_snapshots_keep_original_encoding() {
        let mut cases=0;
        for signed in [true,false] {
            for len in [0,1,2,7,8,15,16,17,31,32,33,1024,7777] {
                for which in 0..2 {
                    for kind in 0..3 {
                        let values:Vec<f32>=(0..len).map(|i|match kind {
                            0 => ((i*73%1009) as f32-504.0)/32.0,
                            1 => if i%2==0 {-0.0} else {0.0},
                            _ => [f32::from_bits(0x7fc0_4567),f32::INFINITY,f32::NEG_INFINITY,
                                f32::from_bits(1),-f32::from_bits(1),1.0,-1.0][i%7],
                        }).collect();
                        let layout=metadata(len,&values);
                        let block=InactiveBlock {node:4,host:13,len,initial:[3,7]};
                        let reference=seeded(len+30,signed);let candidate=seeded(len+30,signed);
                        unsafe {reference.write_f32(block.node,block.host,len,&values);}
                        layout.write_compressed_inactive(&candidate,&block,which);
                        raw_equal(&reference,&candidate);cases+=1;
                    }
                }
            }
        }
        assert_eq!(cases,156);
        println!("E041_CPU_SNAPSHOT_RESTORE cases={cases}");
    }
}
