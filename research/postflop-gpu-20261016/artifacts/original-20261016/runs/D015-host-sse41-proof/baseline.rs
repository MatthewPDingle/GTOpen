/// Quantize `src` into i16 against a caller-provided block max, returning the
/// scale actually stored (0 for a zero or non-finite max => all-zero block).
#[inline]
pub fn quantize_i16(src: &[f32], max: f32, dst: &mut [i16]) -> f32 {
    if !(max > 0.0 && max.is_finite()) {
        dst.fill(0);
        return 0.0;
    }
    let k = 32767.0 / max;
    for (d, &v) in dst.iter_mut().zip(src.iter()) {
        *d = (v * k).round_ties_even() as i16; // `as` saturates
    }
    max
}

/// Quantize non-negative `src` into u16 against a caller-provided block max.
#[inline]
pub fn quantize_u16(src: &[f32], max: f32, dst: &mut [u16]) -> f32 {
    if !(max > 0.0 && max.is_finite()) {
        dst.fill(0);
        return 0.0;
    }
    let k = 65535.0 / max;
    for (d, &v) in dst.iter_mut().zip(src.iter()) {
        *d = (v.max(0.0) * k).round_ties_even() as u16;
    }
    max
}

/// Quantize `src` into i16, returning the scale (block max |v|).
#[inline]
pub fn encode_i16(src: &[f32], dst: &mut [i16]) -> f32 {
    let mut m = 0f32;
    for &v in src {
        m = m.max(v.abs());
    }
    quantize_i16(src, m, dst)
}

/// Quantize non-negative `src` into u16, returning the scale (block max).
#[inline]
pub fn encode_u16(src: &[f32], dst: &mut [u16]) -> f32 {
    let mut m = 0f32;
    for &v in src {
        m = m.max(v);
    }
    quantize_u16(src, m, dst)
}

