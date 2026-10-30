"""Prepare one immutable, off-tree untouched-default provenance candidate."""
import difflib,json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;old.custody();ar.refuse_active(ar.live_status())
assert not (ROOT/'gpu-run.lock').exists()
D=ROOT/'runs/E049-final-source';D.mkdir()
owned={}
store=(old.REPO/'crates/solver/src/store.rs').read_text(encoding='utf-8')
store=store.replace('use serde::{Deserialize, Serialize};','use serde::{Deserialize, Serialize};\n#[cfg(feature = "gpu")]\nuse std::sync::atomic::{AtomicBool, Ordering};',1)
store=store.replace('    ptr: *mut T,\n}', '''    ptr: *mut T,
    // A borrowed view invalidates this proof before it can escape. Only
    // concrete i16/u16 callers may infer zero from an untouched default.
    #[cfg(feature = "gpu")]
    unexposed_default: AtomicBool,
}''',1)
store=store.replace('        ArenaBuf { buf, ptr }','''        ArenaBuf {
            buf, ptr,
            #[cfg(feature = "gpu")]
            unexposed_default: AtomicBool::new(true),
        }''',1)
marker='    #[inline(always)]\n    #[allow(clippy::mut_from_ref)]'
store=store.replace(marker,'''    /// Ownership/access-history proof, not a generic zero-value predicate.
    /// GPU entry already requires exclusive solver access, as for the scan.
    #[cfg(feature = "gpu")]
    #[inline(always)]
    pub(crate) fn is_unexposed_default(&self) -> bool {
        std::mem::size_of::<T>() == 2
            && self.unexposed_default.load(Ordering::Relaxed)
    }

    #[inline(always)]
    fn expose(&self) {
        // Constant-folded away for F32 and for builds without GPU support.
        // Avoid repeated writes to the shared cache line after the first
        // exposure. Existing disjoint-access contracts still govern data.
        #[cfg(feature = "gpu")]
        if self.is_unexposed_default() {
            self.unexposed_default.store(false, Ordering::Relaxed);
        }
    }

'''+marker,1)
for signature in ['pub unsafe fn slice(&self, offset: u64, len: usize) -> &mut [T] {',
                  'pub unsafe fn write_at(&self, idx: usize, v: T) {',
                  'pub fn as_slice(&self) -> &[T] {',
                  'pub fn as_mut_slice(&mut self) -> &mut [T] {']:
 assert store.count(signature)==1
 store=store.replace(signature,signature+'\n        self.expose();',1)
store+='''
#[cfg(all(test, feature = "gpu"))]
mod provenance_tests {
    use super::*;

    #[test]
    fn untouched_default_proof_covers_all_access_paths() {
        fn check<T: Copy + Default + PartialEq + Send + Sync>(one: T) {
            for len in [0, 1, 3, 64, 4097] {
                let b = ArenaBuf::<T>::new(len);
                assert!(b.is_unexposed_default());
                assert_eq!(b.len(), len);
                assert_eq!(b.is_empty(), len == 0);
                if len > 0 { assert!(unsafe { b.read_at(len - 1) } == T::default()); }
                assert!(b.is_unexposed_default());
                let b = b; // move owner without dropping the proof
                assert!(b.is_unexposed_default());
                let _escaped_pointer = b.as_slice().as_ptr();
                assert!(!b.is_unexposed_default());
                if len > 0 { unsafe { b.write_at(0, T::default()); } }
                assert!(!b.is_unexposed_default());

                let mut b = ArenaBuf::<T>::new(len);
                b.as_mut_slice().fill(T::default());
                assert!(!b.is_unexposed_default());
                let b = ArenaBuf::<T>::new(len);
                unsafe { b.slice(0, len).fill(T::default()); }
                assert!(!b.is_unexposed_default());
            }
            let b = ArenaBuf::<T>::new(16);
            std::thread::scope(|scope| {
                for i in 0..16 {
                    let b = &b;
                    scope.spawn(move || unsafe { b.write_at(i, one); });
                }
            });
            assert!(!b.is_unexposed_default());
            assert!(b.as_slice().iter().all(|&v| v == one));
            unsafe { b.slice(0, 16).fill(T::default()); }
            assert!(!b.is_unexposed_default());
        }
        check::<i16>(-7);
        check::<u16>(7);
        assert!(!ArenaBuf::<f32>::new(1).is_unexposed_default());
        println!("E049_METADATA arena_i16={} arena_f32={} store={}",
            std::mem::size_of::<ArenaBuf<i16>>(),
            std::mem::size_of::<ArenaBuf<f32>>(),std::mem::size_of::<Store>());
    }
}
'''
arena=(old.REPO/'crates/solver/src/gpu/arena.rs').read_text(encoding='utf-8')
for term in ['bits | v as u16','bits | v']:
 expression='q.as_slice().iter().fold(0u16, |bits, &v| '+term+') == 0'
 assert arena.count(expression)==1
 arena=arena.replace(expression,'(q.is_unexposed_default() || '+expression+')',1)
arena+='''
#[cfg(test)]
mod provenance_predicate_tests {
    use super::*;

    fn original(layout: &ArenaLayout, store: &Store, which: usize) -> bool {
        let zero = match store {
            Store::I16 { q, scale } => scale.as_slice().iter().all(|v| v.to_bits() == 0)
                && q.as_slice().iter().fold(0u16, |bits, &v| bits | v as u16) == 0,
            Store::U16 { q, scale } => scale.as_slice().iter().all(|v| v.to_bits() == 0)
                && q.as_slice().iter().fold(0u16, |bits, &v| bits | v) == 0,
            Store::F32(_) => false,
        };
        zero && layout.initial[which].is_empty()
            && layout.inactive.iter().all(|b| b.initial[which] == usize::MAX)
    }

    #[test]
    fn untouched_and_exposed_predicates_match_original_scan() {
        let scales = [0, 0x80000000, 1, 0x80000001, 0x3f800000, 0xbf800000,
            0x7f800000, 0xff800000, 0x7fc00123, 0xffc00123];
        let mut cases = 0;
        let mut no_scan_witnesses = 0;
        for len in [0u64, 1, 3, 64, 4097] {
            for signed in [false, true] {
                for access in 0..7 {
                    for &scale_bits in &scales {
                        for snapshot in 0..4 {
                            let mut store = if signed { Store::i16(len, 2) } else { Store::u16(len, 2) };
                            macro_rules! prepare {
                                ($q:expr, $s:expr) => {{
                                    $s.as_mut_slice()[1] = f32::from_bits(scale_bits);
                                    match access {
                                        0 => {},
                                        1 => { let _ = $q.as_slice().as_ptr(); },
                                        2 => { $q.as_mut_slice().fill(0); },
                                        3 => { unsafe { $q.slice(0, len as usize).fill(0); } },
                                        4 if len > 0 => { unsafe { $q.write_at(len as usize - 1, 1); } },
                                        5 if len > 0 => { unsafe { $q.write_at(0, 1); $q.write_at(0, 0); } },
                                        6 if len > 0 => { unsafe { let _ = $q.read_at(0); } },
                                        _ => {},
                                    }
                                }};
                            }
                            match &mut store {
                                Store::I16 { q, scale } => prepare!(q, scale),
                                Store::U16 { q, scale } => prepare!(q, scale),
                                _ => unreachable!(),
                            }
                            let mut layout = ArenaLayout {
                                compact: true, len: len as usize, active: Vec::new(), copies: Vec::new(),
                                inactive: vec![InactiveBlock { node: 0, host: 0, len: 0, initial: [usize::MAX; 2] }],
                                initial: [Vec::new(), Vec::new()], zeros: Vec::new(),
                            };
                            if snapshot & 1 != 0 { layout.initial[0].push(-0.0); }
                            if snapshot & 2 != 0 { layout.inactive[0].initial[0] = 0; }
                            // Candidate must run first: the reference scan exposes q.
                            let pristine = match &store {
                                Store::I16 { q, .. } => q.is_unexposed_default(),
                                Store::U16 { q, .. } => q.is_unexposed_default(), _ => false,
                            };
                            for which in 0..2 {
                                let got = layout.can_upload_zeros(&store, which);
                                let still_pristine = match &store {
                                    Store::I16 { q, .. } => q.is_unexposed_default(),
                                    Store::U16 { q, .. } => q.is_unexposed_default(), _ => false,
                                };
                                if which == 0 && pristine && scale_bits == 0 {
                                    assert!(still_pristine, "fast-path must not expose q");
                                    no_scan_witnesses += 1;
                                }
                                assert_eq!(got, original(&layout, &store, which));
                                cases += 1;
                            }
                        }
                    }
                }
            }
        }
        assert_eq!(cases, 5600);
        assert!(no_scan_witnesses > 0);
        println!("E049_PREDICATE cases={cases} no_scan_witnesses={no_scan_witnesses}");
    }
}
'''
for rel,candidate in [('crates/solver/src/store.rs',store),('crates/solver/src/gpu/arena.rs',arena)]:
 base=old.REPO/rel;name=Path(rel).name;b=D/('base-'+name);c=D/('candidate-'+name)
 b.write_bytes(base.read_bytes());c.write_bytes(candidate.replace('\n','\r\n').encode('utf-8'))
 owned[rel]={'base':str(b),'base_sha256':old.sha(b),'candidate':str(c),'candidate_sha256':old.sha(c)}
 patch=''.join(difflib.unified_diff(base.read_text(encoding='utf-8').splitlines(True),candidate.splitlines(True),fromfile=rel,tofile=rel))
 (D/(name+'.patch')).write_text(patch,encoding='utf-8')
old.save(D/'manifest.json',{'id':'E049','at':old.now(),'owned':owned,'hypothesis':'Skip exact q scan only for unexposed default-filled i16/u16 ownership. Retain original scale and snapshot guards and fallback. No changed GPU code/math.','new_tests':2,'ordinary_gpu_expected':{'passed':86,'ignored':4},'predicate_comparisons':5600,'cpu_only_tracking':False,'candidate_accepted':False})
old.save(D/'source-review.json',{'at':old.now(),'root_review_only':True,'invalidation_before':['slice','write_at','as_slice','as_mut_slice'],'by_value_and_metadata_only':['read_at','len','is_empty'],'concurrency':'Sticky relaxed atomic. Existing exclusive upload / disjoint mutation contracts govern data. First exposure may redundantly store false; never reset true.','generic_limit':'No inference from arbitrary T default. can_upload_zeros concretely matches i16/u16; f32 is false. size gate eliminates F32 expose work.','extra_costs_pending':['GPU-feature ArenaBuf metadata size','Compressed CPU accessor loads/branches','warm constructor/full-process/page first-touch'],'controls':'candidate before original on same owner; witness remains pristine after fast predicate, nonzero q forces fallback false; 5600 full predicate comparisons plus access/move/concurrency tests','acceptance':'1% full cycle, strict fixture guard; fresh16 and broader/resource/CPU/whole-process qualification before adoption','source_sha256':{n:v['candidate_sha256'] for n,v in owned.items()}})
B=ROOT/'runs/E049-build-plan';B.mkdir();prior=ROOT/'runs/E048-build-plan'
s=(prior/'build.py').read_text(encoding='utf-8').replace('E048','E049')
s=s.replace("cmd=['cargo','test','--release','--locked','--offline','-p','solver','--features',phase['features'],'--lib']","cmd=['cargo','test','--release','--locked','--offline','-p','solver','--lib']\n  if phase['features']:cmd+=['--features',phase['features']]")
s=s.replace("assert (REPO/'crates/solver/src/gpu/kernels.cu').read_bytes() in Path(x['executable']).read_bytes()","if phase['features']:assert (REPO/'crates/solver/src/gpu/kernels.cu').read_bytes() in Path(x['executable']).read_bytes()")
(B/'build.py').write_text(s,encoding='utf-8')
p=old.read(prior/'build-protocol.json');p.update(id='E049-final-build',at=old.now(),owned=owned)
p['phases']=[{'id':'cpu','features':'','expected_features':[],'integration':False,'target':str(ROOT/'build-e049-final-cpu'),'outputs':{'solver':'E049-cpu-solver'}}]+[{**x,'target':x['target'].replace('e048','e049'),'outputs':{n:v.replace('E048','E049') for n,v in x['outputs'].items()}} for x in p['phases']]
paths=[B/'build.py',D/'manifest.json',D/'source-review.json',ROOT/'runs/D079-initial-zero-provenance/report.json',Path(p['protected_main']),ROOT/'runs/small-gain-confirmation-plan/common.py',ar.REPO/'tools/postflop_autoresearch.py']
for v in owned.values():paths.extend([Path(v['base']),Path(v['candidate'])])
p['input_sha256']={str(x):old.sha(x) for x in paths};old.save(B/'build-protocol.json',p)
published={}
for directory in [D,B]:
 for src in directory.rglob('*'):
  if not src.is_file():continue
  key=directory.name+'/'+src.relative_to(directory).as_posix();dst=ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
  assert not dst.exists();dst.write_bytes(src.read_bytes())
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==src.read_bytes()
  published[key]=old.sha(src)
old.save(B/'publication.json',{'at':old.now(),'http_verified_files':len(published),'sha256':published})
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(ar.STATUS);assert not any(x['id']=='E049' for x in st['experiments'])
 st['experiments'].append({'id':'E049','title':'Untouched-default quantized ownership proof','kind':'candidate','status':'running','stage':'Frozen candidate; fresh CPU/feature/GPU builds next','reason':'Exact conservative provenance may skip initial q reads. Every borrowed or mutable access invalidates; full fallback and scale/snapshot guards retained. CPU/resource costs pending.','evidence':[{'label':'E049 source review','url':'evidence/E049-final-source/source-review.json'},{'label':'E049 build protocol','url':'evidence/E049-build-plan/build-protocol.json'}]})
 st.update(state='running',stage='E049 builds and provenance controls',activity='One fixed provenance design, two new access/predicate tests. No performance or adoption claim.',updated_at=ar.now());ar.atomic_json(ar.STATUS,st)
old.custody();print(json.dumps({'source_sha256':{n:v['candidate_sha256'] for n,v in owned.items()},'build_protocol_sha256':old.sha(B/'build-protocol.json'),'published':len(published)}),flush=True)
