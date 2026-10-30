const SEED: u64 = 0x5eed_2026_1016_f00d;
const GUARD: u16 = 0xa55a;
const GUARD_WORDS: usize = 3;
const LENGTHS: &[usize] = &[
    0, 1, 2, 3, 7, 15, 16, 17, 31, 32, 33, 63, 64, 65, 127, 128, 129,
    255, 256, 257, 511, 512, 513, 1023, 1024, 1025, 4095, 4096, 4097,
];

