#[cfg(test)]
mod packet_memory_controls {
    use super::*;
    #[test]
    fn exact_prefix_initialization_preserves_all_surrounding_words_and_declines_invalid_views() {
        use std::mem::ManuallyDrop;
        let mut backing=vec![0xdeadbeefu32;PACKET_WORDS+16];
        let mut owner=ManuallyDrop::new(PinnedBuf{ptr:unsafe{backing.as_mut_ptr().add(8).cast::<f32>()},len:PACKET_WORDS});
        {let view=staging(&mut owner).unwrap();assert_eq!(view.len(),PACKET_WORDS);assert!(view.iter().all(|v|v.to_bits()==0));}
        assert!(backing[..8].iter().chain(&backing[8+PACKET_WORDS..]).all(|&v|v==0xdeadbeef));
        let image=backing.clone();owner.len=PACKET_WORDS-1;assert!(staging(&mut owner).is_none());assert_eq!(backing,image);
        owner.len=PACKET_WORDS;owner.ptr=unsafe{backing.as_mut_ptr().cast::<u8>().add(1).cast::<f32>()};assert!(staging(&mut owner).is_none());assert_eq!(backing,image);
        owner.ptr=std::ptr::null_mut();assert!(staging(&mut owner).is_none());assert_eq!(backing,image);
    }
    #[test]
    fn checked_layout_declines_overflows_aliases_wrong_owners_and_capacity_excess() {
        let base=Block{node:1,host:3,source:5,len:3};
        assert!(validate(&[base],20,(20,4)).is_some());
        let second=Block{node:2,host:9,source:13,len:2};assert!(validate(&[base,second],20,(20,4)).is_some());
        for bad in [Block{host:19,..base},Block{source:19,..base},Block{node:4,..base},Block{host:u64::MAX,..base},Block{source:usize::MAX,..base},Block{len:u32::MAX as usize,..base}] {assert!(validate(&[bad],20,(20,4)).is_none());}
        for bad in [Block{host:4,..second},Block{source:6,..second},Block{node:1,..second}] {assert!(validate(&[base,bad],20,(20,4)).is_none());}
        assert!(validate(&[base],usize::MAX,(20,4)).is_none());assert!(validate(&[base],20,(usize::MAX,4)).is_none());
        let large=Block{node:1,host:0,source:0,len:131079};assert!(validate(&[large],200000,(200000,4)).is_none());
        let edge=Block{len:131078,..large};assert!(validate(&[edge],200000,(200000,4)).is_some());
    }
    #[test]
    fn direct_scatter_keeps_all_q_scale_guards_signed_bits_and_odd_tail_poison_exact() {
        for signed in [false,true] {
            let store=if signed {Store::i16(17,8)} else {Store::u16(17,8)};
            match &store {
                Store::I16{q,scale}=>{unsafe{q.slice(0,17)}.fill(0xa55au16 as i16);unsafe{scale.slice(0,8)}.fill(f32::from_bits(0x7fc0cafe));},
                Store::U16{q,scale}=>{unsafe{q.slice(0,17)}.fill(0xa55a);unsafe{scale.slice(0,8)}.fill(f32::from_bits(0x7fc0cafe));},
                _=>unreachable!(),
            }
            let blocks=[Block{node:1,host:3,source:5,len:3},Block{node:3,host:9,source:11,len:2},Block{node:5,host:13,source:16,len:0}];
            assert!(validate(&blocks,20,(17,8)).is_some());
            let stage:Vec<f32>=[0x3f800001u32,0x00000000,0x00000000,0x8000ffff,0xd00d7fff,0x0001fffe].into_iter().map(f32::from_bits).collect();
            scatter(&store,&blocks,&stage,3);
            let (q,scales):(Vec<u32>,Vec<u32>)=match &store {
                Store::I16{q,scale}=>(q.as_slice().iter().map(|&v|v as u16 as u32).collect(),scale.as_slice().iter().map(|v|v.to_bits()).collect()),
                Store::U16{q,scale}=>(q.as_slice().iter().map(|&v|v as u32).collect(),scale.as_slice().iter().map(|v|v.to_bits()).collect()),
                _=>unreachable!(),
            };
            let mut expected=vec![0xa55a;17];expected[3..6].copy_from_slice(&[0xffff,0x8000,0x7fff]);expected[9..11].copy_from_slice(&[0xfffe,1]);assert_eq!(q,expected);
            let mut expected=vec![0x7fc0cafe;8];expected[1]=0x3f800001;expected[3]=0;expected[5]=0;assert_eq!(scales,expected);
        }
    }
}
