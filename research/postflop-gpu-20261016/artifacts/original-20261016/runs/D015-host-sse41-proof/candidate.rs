// Only target-feature specialization; the original encoder/quantizer is unchanged.
#[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
#[no_mangle]
#[target_feature(enable = "sse4.1")]
pub unsafe fn d015_sse41_i16(src: &[f32], dst: &mut [i16]) -> f32 {
    crate::baseline::encode_i16(src, dst)
}
#[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
#[no_mangle]
#[target_feature(enable = "sse4.1")]
pub unsafe fn d015_sse41_u16(src: &[f32], dst: &mut [u16]) -> f32 {
    crate::baseline::encode_u16(src, dst)
}

pub fn available() -> bool {
    #[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
    { std::is_x86_feature_detected!("sse4.1") }
    #[cfg(not(any(target_arch = "x86", target_arch = "x86_64")))]
    { false }
}

// Keep a portable fallback and guard every call across the unsafe feature boundary.
pub fn encode_i16(src: &[f32], dst: &mut [i16]) -> f32 {
    #[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
    if available() { return unsafe { d015_sse41_i16(src, dst) }; }
    crate::baseline::encode_i16(src, dst)
}
pub fn encode_u16(src: &[f32], dst: &mut [u16]) -> f32 {
    #[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
    if available() { return unsafe { d015_sse41_u16(src, dst) }; }
    crate::baseline::encode_u16(src, dst)
}
