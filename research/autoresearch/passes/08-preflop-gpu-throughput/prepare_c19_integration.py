"""Direct-construction, test-only C19 integration; preserve unchanged line endings."""
import difflib,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;LAB=HERE.parents[3]
def save(p,text):
    raw=p.read_bytes();lines=raw.splitlines(keepends=True);old=raw.decode().splitlines(keepends=True)
    normalized=[s.replace('\r\n','\n') for s in old];new=text.splitlines(keepends=True);out=[]
    for tag,a,b,c,d in difflib.SequenceMatcher(a=normalized,b=new,autojunk=False).get_opcodes():
        out.extend(lines[a:b] if tag=='equal' else [s.encode() for s in new[c:d]])
    p.write_bytes(b''.join(out))
def main():
    root=LAB/'crates/solver/src/preflop/gpu';modified=[]
    p=root/'cdf_interleave.rs';s=p.read_text();assert 'compile_if_active' not in s
    s+='''
thread_local! {
    static ACTIVE:std::cell::Cell<bool>=const {std::cell::Cell::new(false)};
    static SELECTED:std::cell::Cell<usize>=const {std::cell::Cell::new(0)};
}
struct Reset;
impl Drop for Reset {fn drop(&mut self){ACTIVE.set(false);}}

pub(super) fn new(s:&PreflopSolver,budget:u64)->Result<PreflopGpu,String> {
    if ACTIVE.replace(true){return Err("nested C19 constructor".into());}
    let _reset=Reset;let before=SELECTED.get();
    let result=PreflopGpu::new_research_narrow_cohorts(s,budget)?;
    if SELECTED.get()!=before+1{return Err("C19 writer was not selected exactly once".into());}
    Ok(result)
}

pub(super) fn compile_if_active(source:&str,arch:&'static str)->Option<Result<cudarc::nvrtc::Ptx,String>> {
    if !ACTIVE.get(){return None;}
    SELECTED.set(SELECTED.get()+1);
    static PTX:std::sync::OnceLock<Result<cudarc::nvrtc::Ptx,String>>=std::sync::OnceLock::new();
    Some(PTX.get_or_init(||cudarc::nvrtc::compile_ptx_with_opts(candidate(source),
        cudarc::nvrtc::CompileOptions{arch:Some(arch),..Default::default()}).map_err(e)).clone())
}

pub(super) fn constructor_active()->bool {ACTIVE.get()}
'''
    save(p,s);modified.append(p)
    p=root/'exact_reuse.rs';s=p.read_text()
    old='''        let ptx=PTX[2*unrolled as usize+narrow as usize].get_or_init(||cudarc::nvrtc::compile_ptx_with_opts(source,cudarc::nvrtc::CompileOptions{
            arch:Some(arch),..Default::default()}).map_err(e)).clone()?;'''
    new='''        #[cfg(all(test, feature = "preflop-research"))]
        let replacement=super::cdf_interleave::compile_if_active(&source,arch);
        #[cfg(not(all(test, feature = "preflop-research")))]
        let replacement:Option<Result<cudarc::nvrtc::Ptx,String>>=None;
        let ptx=if let Some(ptx)=replacement {ptx?}else{PTX[2*unrolled as usize+narrow as usize].get_or_init(||cudarc::nvrtc::compile_ptx_with_opts(source,cudarc::nvrtc::CompileOptions{
            arch:Some(arch),..Default::default()}).map_err(e)).clone()?};'''
    assert s.count(old)==1;s=s.replace(old,new);save(p,s);modified.append(p)
    p=root/'cohort_reuse/tests.rs';s=p.read_text()
    assert s.count('for mode in 0..6 {')==2;s=s.replace('for mode in 0..6 {','for mode in 0..7 {')
    old='let mut g=if mode==5{';assert s.count(old)==2
    s=s.replace(old,'let mut g=if mode==6{super::super::cdf_interleave::new(&s,2000).unwrap()}else if mode==5{')
    for label in ['terminals np={np} batch={batch}','np={np} fixed={fixed} batch={batch}']:
        old=f'assert_eq!(runs[3],runs[5],"C14 {label}");'
        assert s.count(old)==1;s=s.replace(old,old+f'\n        assert_eq!(runs[5],runs[6],"C19 {label}");')
    old='let g=if narrow{';assert s.count(old)==1
    s=s.replace(old,'let interleaved=std::env::var("PREFLOP_GPU_CDF_INTERLEAVE").ok().as_deref()==Some("1");\n    assert!(!interleaved || (narrow && unrolled));\n    let g=if interleaved{super::super::cdf_interleave::new(&s,23000).unwrap()}else if narrow{')
    s=s.replace('"arenas_unchanged":true,"narrow_offsets":narrow,','"arenas_unchanged":true,"narrow_offsets":narrow,"interleaved_cdf":interleaved,')
    tracing=s[s.index('#[test]\nfn retained_phase_tracing_preserves_solver_bits()'):]
    tracing=tracing.replace('retained_phase_tracing_preserves_solver_bits','interleaved_phase_tracing_preserves_solver_bits').replace('PreflopGpu::new_research_narrow_cohorts(&s,2000)','super::super::cdf_interleave::new(&s,2000)').replace('tracing altered retained C14','tracing altered C19')
    s+='\n'+tracing
    s+='''
#[test]
fn interleaved_constructor_resets_selection_after_error() {
    let s=fixture(4,false);assert!(!super::super::cdf_interleave::constructor_active());
    assert!(super::super::cdf_interleave::new(&s,0).is_err());
    assert!(!super::super::cdf_interleave::constructor_active());
    let mut g=super::super::cdf_interleave::new(&s,2000).unwrap();
    assert!(!super::super::cdf_interleave::constructor_active());
    let before=bits(&g);let _=g.gaps_and_evs().unwrap();assert_eq!(before,bits(&g));
    drop(g);let normal=PreflopGpu::new_research_narrow_cohorts(&s,2000).unwrap();
    assert_eq!(before,bits(&normal));assert!(!super::super::cdf_interleave::constructor_active());
}
'''
    save(p,s);modified.append(p)
    p=root/'exact_reuse/tests.rs';s=p.read_text()
    old='    let mut selection=None;';assert s.count(old)==1
    s=s.replace(old,'    let interleaved=std::env::var("PREFLOP_GPU_CDF_INTERLEAVE").ok().as_deref()==Some("1");\n    assert!(!interleaved || (narrow && !production));\n'+old)
    old='let mut g=if production{';assert s.count(old)==1
    s=s.replace(old,'let mut g=if interleaved{super::super::cdf_interleave::new(&s,23000).unwrap()}else if production{')
    s=s.replace('"narrow_offsets":g.throughput_narrow,"production_selection":production,','"narrow_offsets":g.throughput_narrow,"interleaved_cdf":interleaved,"production_selection":production,')
    save(p,s);modified.append(p)
    mapping={}
    for p in modified:
        dest=HERE/'artifacts/c19-v2'/p.relative_to(LAB/'crates/solver')
        assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
        mapping[p.relative_to(LAB).as_posix()]=dict(archive=dest.relative_to(HERE).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    dest=HERE/'artifacts/c19-v2-source-map.json';assert not dest.exists();dest.write_text(json.dumps(mapping,indent=2)+'\n',encoding='utf-8')
    print('Created direct C19 construction and expanded cohort tests')
if __name__=='__main__':main()
