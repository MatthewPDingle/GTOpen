fn terminal_hand_words(c1: &[u32], c2: &[u32], same: &[u32]) -> Vec<u32> {
    c1.iter().zip(c2).zip(same).map(|((&a, &b), &s)| {
        let index = if s == u32::MAX { 0x7ff } else { s };
        a | (b << 6) | (index << 12)
    }).collect()
}
