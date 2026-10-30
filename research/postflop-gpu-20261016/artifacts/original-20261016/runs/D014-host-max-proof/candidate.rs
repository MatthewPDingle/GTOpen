// Experimental max reduction only; the production quantizer remains the oracle's.
pub fn encode_i16(src: &[f32], dst: &mut [i16]) -> f32 {
    let mut m = [0f32; 4];
    let mut chunks = src.chunks_exact(4);
    for c in &mut chunks {
        m[0] = m[0].max(c[0].abs());
        m[1] = m[1].max(c[1].abs());
        m[2] = m[2].max(c[2].abs());
        m[3] = m[3].max(c[3].abs());
    }
    let mut max = m[0].max(m[1]).max(m[2]).max(m[3]);
    for &v in chunks.remainder() { max = max.max(v.abs()); }
    crate::baseline::quantize_i16(src, max, dst)
}

pub fn encode_u16(src: &[f32], dst: &mut [u16]) -> f32 {
    let mut m = [0f32; 4];
    let mut chunks = src.chunks_exact(4);
    for c in &mut chunks {
        m[0] = m[0].max(c[0]);
        m[1] = m[1].max(c[1]);
        m[2] = m[2].max(c[2]);
        m[3] = m[3].max(c[3]);
    }
    let mut max = m[0].max(m[1]).max(m[2]).max(m[3]);
    for &v in chunks.remainder() { max = max.max(v); }
    crate::baseline::quantize_u16(src, max, dst)
}
