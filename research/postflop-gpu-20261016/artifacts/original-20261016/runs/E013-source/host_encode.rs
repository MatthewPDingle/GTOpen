//! Host encoding for GPU readback; shared Store/CPU CFR encoding stays unchanged.
use crate::store::Store;

/// Same safety contract as Store::write_f32: valid lengths/offsets, disjoint
/// writable node ranges and scale slots, with no concurrent reads of them.
pub(super) type Writer = unsafe fn(&Store, u32, u64, usize, &[f32]);

pub(super) fn writer() -> Writer {
    select_writer(true)
}

fn select_writer(allow_sse41: bool) -> Writer {
    #[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
    if allow_sse41 && std::is_x86_feature_detected!("sse4.1") {
        return write_sse41;
    }
    #[cfg(not(any(target_arch = "x86", target_arch = "x86_64")))]
    let _ = allow_sse41;
    Store::write_f32
}

// Select once per readback, outside the parallel node loops. Keep typed slice
// boundaries below so the compiler can see the source/destination alias contract.
#[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
#[target_feature(enable = "sse4.1")]
unsafe fn write_sse41(store: &Store, node: u32, offset: u64, len: usize, src: &[f32]) {
    match store {
        Store::I16 { q, scale } => {
            let dst = q.slice(offset, len);
            let max = encode_i16_sse41(src, dst);
            scale.write_at(node as usize, max);
        }
        Store::U16 { q, scale } => {
            let dst = q.slice(offset, len);
            let max = encode_u16_sse41(src, dst);
            scale.write_at(node as usize, max);
        }
        Store::F32(_) => store.write_f32(node, offset, len, src),
    }
}

#[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
#[target_feature(enable = "sse4.1")]
#[inline(never)]
unsafe fn encode_i16_sse41(src: &[f32], dst: &mut [i16]) -> f32 {
    crate::store::encode_i16(src, dst)
}

#[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
#[target_feature(enable = "sse4.1")]
#[inline(never)]
unsafe fn encode_u16_sse41(src: &[f32], dst: &mut [u16]) -> f32 {
    crate::store::encode_u16(src, dst)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn seeded(signed: bool, len: usize) -> Store {
        let mut store = if signed { Store::i16(len as u64, 6) }
            else { Store::u16(len as u64, 6) };
        match &mut store {
            Store::I16 { q, .. } => {
                for (i, v) in q.as_mut_slice().iter_mut().enumerate() {
                    *v = (0xa55au16.wrapping_add(i as u16)) as i16;
                }
            }
            Store::U16 { q, .. } => {
                for (i, v) in q.as_mut_slice().iter_mut().enumerate() {
                    *v = 0xa55au16.wrapping_add(i as u16);
                }
            }
            Store::F32(_) => unreachable!(),
        }
        match &mut store {
            Store::I16 { scale, .. } | Store::U16 { scale, .. } => {
                for (v, bits) in scale.as_mut_slice().iter_mut().zip([
                    0x8000_0000, 0x7fc0_1234, 0x3f80_0000, 0x7f80_0001, 1, 0xff80_0000,
                ]) { *v = f32::from_bits(bits); }
            }
            Store::F32(_) => unreachable!(),
        }
        store
    }

    fn image(store: &Store) -> (Vec<u16>, Vec<u32>) {
        match store {
            Store::I16 { q, scale } => (q.as_slice().iter().map(|&v| v as u16).collect(),
                scale.as_slice().iter().map(|v| v.to_bits()).collect()),
            Store::U16 { q, scale } => (q.as_slice().to_vec(),
                scale.as_slice().iter().map(|v| v.to_bits()).collect()),
            Store::F32(_) => unreachable!(),
        }
    }

    fn check(src: &[f32]) {
        let before: Vec<_> = src.iter().map(|v| v.to_bits()).collect();
        let zeros = vec![0.0; src.len()];
        for signed in [true, false] {
            // Both the actual runtime selection and forced portable fallback.
            for write in [writer(), select_writer(false)] {
                let expected = seeded(signed, src.len() + 7);
                let actual = seeded(signed, src.len() + 7);
                let guards = image(&actual);
                // A second write clears previously encoded state, not just new buffers.
                for values in [src, &zeros[..]] {
                    unsafe {
                        expected.write_f32(2, 3, src.len(), values);
                        write(&actual, 2, 3, src.len(), values);
                    }
                    let got = image(&actual);
                    assert_eq!(got, image(&expected), "signed={signed}, len={}", src.len());
                    assert_eq!(&got.0[..3], &guards.0[..3]);
                    assert_eq!(&got.0[3 + src.len()..], &guards.0[3 + src.len()..]);
                    for node in [0, 1, 3, 4, 5] {
                        assert_eq!(got.1[node], guards.1[node], "unowned scale {node}");
                    }
                }
            }
        }
        assert_eq!(before, src.iter().map(|v| v.to_bits()).collect::<Vec<_>>());
    }

    #[test]
    fn host_encode_matches_store_with_guards_specials_and_tails() {
        let specials = [
            0, 0x8000_0000, 1, 0x8000_0001, 0x007f_ffff, 0x0080_0000,
            0x7f7f_ffff, 0xff7f_ffff, 0x7f80_0000, 0xff80_0000,
            0x7fc0_1234, 0xffc0_5678, 0x7f80_0001, 0xff80_0001,
        ];
        for bits in specials {
            check(&[f32::from_bits(bits)]);
            check(&[1.0, f32::from_bits(bits), -1.0, -0.0]);
        }
        for len in [0, 1, 2, 3, 4, 7, 15, 16, 17, 257, 514, 638, 771, 957, 1025] {
            check(&vec![0.0; len]);
            check(&vec![-0.0; len]);
            check(&vec![f32::from_bits(0x7fc0_1234); len]);
            check(&(0..len).map(|i| f32::from_bits(specials[i % specials.len()])).collect::<Vec<_>>());
            check(&(0..len).map(|i| (i as f32 - len as f32 / 2.0) / 3.0).collect::<Vec<_>>());
            check(&(0..len).map(|i| f32::from_bits(1 + i as u32 % 7)).collect::<Vec<_>>());
        }
        for max in [32767u32, 65535] {
            let mut values = vec![max as f32];
            for n in [0u32, 1, 2, 127, 1023, 16383] {
                let bits = (n as f32 + 0.5).to_bits();
                for adjacent in [bits - 1, bits, bits + 1] {
                    values.push(f32::from_bits(adjacent));
                    values.push(-f32::from_bits(adjacent));
                }
            }
            check(&values);
        }
        let mut bits = 0x5eed_1016u32;
        for len in 0..128 {
            let values = (0..len).map(|_| {
                bits ^= bits << 13; bits ^= bits >> 17; bits ^= bits << 5;
                f32::from_bits(bits)
            }).collect::<Vec<_>>();
            check(&values);
        }
    }

    #[test]
    fn host_encode_dispatch_keeps_portable_fallback() {
        assert!(std::ptr::fn_addr_eq(select_writer(false), Store::write_f32 as Writer));
        #[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
        if std::is_x86_feature_detected!("sse4.1") {
            assert!(std::ptr::fn_addr_eq(writer(), write_sse41 as Writer));
        } else {
            assert!(std::ptr::fn_addr_eq(writer(), Store::write_f32 as Writer));
        }
        #[cfg(not(any(target_arch = "x86", target_arch = "x86_64")))]
        assert!(std::ptr::fn_addr_eq(writer(), Store::write_f32 as Writer));
    }
}
