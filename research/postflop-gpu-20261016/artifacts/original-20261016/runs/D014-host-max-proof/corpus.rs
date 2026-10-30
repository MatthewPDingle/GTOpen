struct Case { name: String, values: Vec<f32> }
fn add(cases: &mut Vec<Case>, name: impl Into<String>, values: Vec<f32>) {
    cases.push(Case { name: name.into(), values });
}
struct Rng(u64);
impl Rng {
    fn next(&mut self) -> u32 {
        self.0 = self.0.wrapping_add(0x9e37_79b9_7f4a_7c15);
        let mut z = self.0;
        z = (z ^ (z >> 30)).wrapping_mul(0xbf58_476d_1ce4_e5b9);
        z = (z ^ (z >> 27)).wrapping_mul(0x94d0_49bb_1331_11eb);
        ((z ^ (z >> 31)) >> 32) as u32
    }
}

fn cases() -> Vec<Case> {
    let mut cases = Vec::new();
    let specials = [
        0, 0x8000_0000, 1, 0x8000_0001, 0x007f_ffff, 0x807f_ffff,
        0x0080_0000, 0x8080_0000, 0x3f80_0000, 0xbf80_0000,
        0x7f7f_ffff, 0xff7f_ffff, 0x7f80_0000, 0xff80_0000,
        0x7fc0_0000, 0xffc0_0123, 0x7f80_0001, 0xff80_0001,
    ];
    add(&mut cases, "empty", vec![]);
    for &bits in &specials {
        add(&mut cases, format!("singleton_{bits:08x}"), vec![f32::from_bits(bits)]);
    }
    for &length in LENGTHS {
        add(&mut cases, format!("signed_zeros_{length}"),
            (0..length).map(|i| if i % 2 == 0 { 0.0 } else { -0.0 }).collect());
        add(&mut cases, format!("special_cycle_{length}"),
            (0..length).map(|i| f32::from_bits(specials[i % specials.len()])).collect());
        add(&mut cases, format!("all_nan_{length}"),
            (0..length).map(|i| f32::from_bits(specials[14 + i % 4])).collect());
        add(&mut cases, format!("negative_u16_{length}"),
            (0..length).map(|i| -((i % 65535 + 1) as f32)).collect());
    }
    // Every zero/NaN/negative U16 item is also exercised with a finite positive max.
    for &bits in &specials {
        add(&mut cases, format!("mixed_finite_{bits:08x}"),
            vec![1.0, f32::from_bits(bits), -1.0, 0.0]);
    }
    // With max == C, k == 1: half-integers and their adjacent f32s are exact ties.
    for limit in [32767u32, 65535u32] {
        let mut values = vec![limit as f32];
        for n in [0u32, 1, 2, 3, 126, 127, 128, 129, 1023, 16383, 32765, 65533] {
            if n >= limit { continue; }
            let bits = (n as f32 + 0.5).to_bits();
            for nearby in [bits - 1, bits, bits + 1] {
                values.push(f32::from_bits(nearby));
                values.push(-f32::from_bits(nearby));
            }
        }
        add(&mut cases, format!("ties_adjacent_max_{limit}"), values);
    }
    for bits in [1u32, 2, 0x007f_ffff, 0x0080_0000, 0x0200_0000, 0x0400_0000] {
        let tiny = f32::from_bits(bits);
        add(&mut cases, format!("tiny_scale_{bits:08x}"),
            vec![tiny, -tiny, 0.0, -0.0, tiny * 0.5, -tiny * 0.5,
                 f32::from_bits(0x7fc0_0123), f32::from_bits(0xff80_0001)]);
    }
    add(&mut cases, "max_finite_and_tiny", vec![
        f32::MAX, -f32::MAX, f32::MIN_POSITIVE, -f32::MIN_POSITIVE,
        f32::from_bits(1), -f32::from_bits(1), 1.0, -1.0, 0.0, -0.0,
    ]);
    // Large tails make each CTA process many strided items as well as partial lanes.
    for length in [65537usize, 131071] {
        add(&mut cases, format!("long_tail_{length}"),
            (0..length).map(|i| ((i % 4093) as i32 - 2046) as f32 / 32.0).collect());
    }

    let mut rng = Rng(SEED);
    for index in 0..2048 {
        let length = if index % 2 == 0 { LENGTHS[index % LENGTHS.len()] }
            else { (rng.next() % 2050) as usize };
        let mode = index % 8;
        let values = (0..length).map(|_| {
            let bits = rng.next();
            match mode {
                0 => f32::from_bits(bits), // Unrestricted bits, including exceptional values.
                1 => f32::from_bits((bits & 0x807f_ffff) | (((rng.next() % 254) + 1) << 23)),
                2 => f32::from_bits(bits & 0x803f_ffff), // Signed subnormals, k overflows.
                3 => f32::from_bits((bits & 0x807f_ffff) | 0x7f00_0000),
                4 => f32::from_bits(specials[bits as usize % specials.len()]),
                5 => (bits % 1_000_003) as f32 / 1024.0,
                6 => -((bits % 1_000_003) as f32 / 1024.0),
                _ => ((bits % 65535) as i32 - 32767) as f32 + 0.5,
            }
        }).collect();
        add(&mut cases, format!("random_{index:04}_mode_{mode}"), values);
    }
    cases
}

