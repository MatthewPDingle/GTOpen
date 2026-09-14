"""Promote qualified C23 dispatch into normal builds, preserving its kernels."""
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[3]
GPU = LAB/'crates/solver/src/preflop/gpu'
ARCHIVE = HERE/'artifacts/r04-before'


def save(path, text):
    old = path.read_bytes()
    if b'\r\n' in old:
        text = text.replace('\n', '\r\n')
    path.write_bytes(text.encode('utf-8'))


def main():
    assert json.loads((HERE/'raw/c23-retention-verified.json').read_text())['retained']
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    paths = [GPU.parent/'gpu.rs', GPU/'static_cdf.rs', GPU/'adaptive_throughput.rs',
             GPU/'exact_reuse.rs', GPU/'cohort_reuse.rs']
    hashes = {}
    for path in paths:
        raw = path.read_bytes()
        archive = ARCHIVE/path.name
        if archive.exists():
            assert archive.read_bytes() == raw, path
        else:
            archive.write_bytes(raw)
        hashes[str(path.relative_to(LAB))] = hashlib.sha256(raw).hexdigest()
    (HERE/'artifacts/r04-before-source-map.json').write_text(json.dumps(hashes, indent=2)+'\n', encoding='utf-8')
    path = GPU.parent/'gpu.rs'; text = path.read_text(encoding='utf-8')
    text, n = re.subn(r'    #\[cfg\(all\(test, feature = "preflop-research"\)\)\]\n(    static_cdf:Option<static_cdf::Packed>,)', r'\1', text); assert n == 1
    text, n = re.subn(r'            #\[cfg\(all\(test, feature = "preflop-research"\)\)\]\n(            static_cdf:None,)', r'\1', text); assert n == 1
    text = text.replace('#[cfg(all(test, feature = "preflop-research"))]\nmod static_cdf;', 'mod static_cdf;')
    save(path, text)
    for name in ['exact_reuse.rs', 'cohort_reuse.rs']:
        path = GPU/name; text = path.read_text(encoding='utf-8')
        text, n = re.subn(r'#\[cfg\(all\(test, feature = "preflop-research"\)\)\]\n(\s*let static_done=)', r'\1', text); assert n == 2
        text, n = re.subn(r'\s*#\[cfg\(not\(all\(test, feature = "preflop-research"\)\)\)\]\n\s*let static_done=false;', '', text); assert n == 2
        save(path, text)
    path = GPU/'static_cdf.rs'; text = path.read_text(encoding='utf-8')
    text = text.replace('//! C23 static rank-boundary CDF prototype; no runtime selection.', '//! Exact static rank-boundary CDF storage for fresh retained GPU engines.')
    text = text.replace('#[test]\n#[ignore=', '#[cfg(feature = "preflop-research")]\n#[test]\n#[ignore=')
    text = text.replace('\nfn table(kind:', '\n#[cfg(all(test, feature = "preflop-research"))]\nfn table(kind:')
    text = text.replace('\nthread_local! {pub(super) static FAIL_STAGE', '\n#[cfg(test)]\nthread_local! {pub(super) static FAIL_STAGE')
    text = text.replace('\nfn fault(g:', '\n#[cfg(test)]\nfn fault(g:')
    old = 'pub(super) fn new(s:&PreflopSolver,budget:u64)->Result<PreflopGpu,String>{\n    let mut g=PreflopGpu::new_research_narrow_cohorts(s,budget)?;'
    new = '''#[cfg(all(test, feature = "preflop-research"))]
pub(super) fn new(s:&PreflopSolver,budget:u64)->Result<PreflopGpu,String>{
    promote(PreflopGpu::new_research_narrow_cohorts(s,budget)?,s,budget)
}
pub(super) fn promote(mut g:PreflopGpu,s:&PreflopSolver,budget:u64)->Result<PreflopGpu,String>{
    if g.warmed || g.eval_warmed || g.static_cdf.is_some() || !g.throughput_narrow {
        return Err("static CDF requires a fresh retained engine with narrow offsets".into());
    }'''
    assert old in text; text = text.replace(old, new)
    for stage in [1, 2, 3]:
        text = text.replace(f'    fault(&g,{stage})?;', f'    #[cfg(test)]\n    fault(&g,{stage})?;')
    text = text.replace('    if let Ok(path)=std::env::var("PREFLOP_GPU_STATIC_CDF_INTEGRATED_OUTPUT")', '    #[cfg(all(test, feature = "preflop-research"))]\n    if let Ok(path)=std::env::var("PREFLOP_GPU_STATIC_CDF_INTEGRATED_OUTPUT")')
    save(path, text)


if __name__ == '__main__':
    main()
