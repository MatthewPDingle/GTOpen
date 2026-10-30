"""Prepare one fixed parallel integer proof candidate, off-tree only."""
import difflib,json,sys,statistics,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;old.custody();assert not (ROOT/'gpu-run.lock').exists()
D=ROOT/'runs/E045-design';D.mkdir()
rel='crates/solver/src/gpu/arena.rs';base=ar.REPO/rel;raw=base.read_bytes();s=raw.decode('utf-8')
assert old.sha(base)==old.BASE[rel]
assert 'use rayon::prelude::*;' in s
helper='''// Integer OR is exact across chunk/reduction order. Keep small inputs serial.
const ZERO_PROOF_CHUNK_WORDS: usize = 1 << 20;
fn zero_proof_i16_bits(q: &[i16]) -> u16 {
    if q.len() < 2 * ZERO_PROOF_CHUNK_WORDS {
        q.iter().fold(0u16, |bits, &v| bits | v as u16)
    } else {
        q.par_chunks(ZERO_PROOF_CHUNK_WORDS)
            .map(|chunk| chunk.iter().fold(0u16, |bits, &v| bits | v as u16))
            .reduce(|| 0, |a, b| a | b)
    }
}
fn zero_proof_u16_bits(q: &[u16]) -> u16 {
    if q.len() < 2 * ZERO_PROOF_CHUNK_WORDS {
        q.iter().fold(0u16, |bits, &v| bits | v)
    } else {
        q.par_chunks(ZERO_PROOF_CHUNK_WORDS)
            .map(|chunk| chunk.iter().fold(0u16, |bits, &v| bits | v))
            .reduce(|| 0, |a, b| a | b)
    }
}

'''
a='q.as_slice().iter().fold(0u16, |bits, &v| bits | v as u16) == 0'
b='q.as_slice().iter().fold(0u16, |bits, &v| bits | v) == 0'
assert s.count(a)==s.count(b)==1
original=s[s.index('    fn can_upload_zeros('):s.index('    pub(super) fn upload(')]
assert 'zero_proof_' not in original
production=s.replace(a,'zero_proof_i16_bits(q.as_slice()) == 0').replace(b,'zero_proof_u16_bits(q.as_slice()) == 0')
at=production.index('impl ArenaLayout {');production=production[:at]+helper+production[at:]
reference=original.replace('fn can_upload_zeros(','fn e045_original_can_upload_zeros(')
tests='''
#[cfg(test)]
mod e045_zero_proof_control {
    use super::*;
    impl ArenaLayout {
REFERENCE
    }
    #[test]
    fn parallel_integer_or_matches_serial_original() {
        let c=ZERO_PROOF_CHUNK_WORDS;
        let lengths=[0,1,7,127,128,129,c-1,c,c+1,2*c-1,2*c,2*c+1,3*c+17];
        let mut checks=0usize;
        for threads in [1,2,16] {
            let pool=rayon::ThreadPoolBuilder::new().num_threads(threads).build().unwrap();
            pool.install(|| {
                for n in lengths {
                    let mut u=vec![0u16;n];let mut i=vec![0i16;n];
                    let mut check=|u:&[u16],i:&[i16]| {
                        let ub=u.to_vec();let ib=i.to_vec();
                        assert_eq!(zero_proof_u16_bits(u),u.iter().fold(0u16,|a,&v|a|v));
                        assert_eq!(zero_proof_i16_bits(i),i.iter().fold(0u16,|a,&v|a|v as u16));
                        assert_eq!(u,ub);assert_eq!(i,ib);checks+=2;
                    };
                    check(&u,&i);
                    let mut positions=vec![0,n.saturating_sub(1),c-1,c,2*c-1,2*c];
                    positions.retain(|&p|p<n);positions.sort_unstable();positions.dedup();
                    for p in positions {for bit in 0..16 {
                        u[p]=1u16<<bit;i[p]=u[p] as i16;check(&u,&i);u[p]=0;i[p]=0;
                    }}
                    for p in 0..n {
                        u[p]=(p as u32).wrapping_mul(73).wrapping_add(997) as u16;i[p]=u[p] as i16;
                    }
                    check(&u,&i);
                }
            });
        }
        assert_eq!(checks,EXPECTED_CHECKS);
        println!("E045_INTEGER_OR_CONTROL {}",serde_json::json!({"checks":checks,"threads":[1,2,16],"lengths":lengths,"inputs_unchanged":true,"raw_integer_or_exact":true}));
    }
    fn layout(compact:bool)->ArenaLayout {
        ArenaLayout {compact,len:4,active:Vec::new(),copies:Vec::new(),initial:[Vec::new(),Vec::new()],zeros:vec![0.;2],
            inactive:if compact {vec![InactiveBlock{node:1,host:2,len:2,initial:[usize::MAX;2]}]}else{Vec::new()}}
    }
    #[test]
    fn full_zero_predicate_matches_accepted_original() {
        let c=ZERO_PROOF_CHUNK_WORDS;let mut checks=0usize;
        for n in [0,1,c-1,c,c+1,2*c-1,2*c,2*c+1,3*c+17] {
            for compact in [false,true] {for which in 0..2 {for kind in 0..2 {for state in 0..8 {
                let mut a=layout(compact);let mut store=if kind==0{Store::i16(n,2)}else{Store::u16(n,2)};
                match &mut store {
                    Store::I16{q,scale}=>{if state==1&&n>0{q.as_mut_slice()[n-1]=i16::MIN;}if (2..=4).contains(&state){scale.as_mut_slice()[1]=f32::from_bits([0x80000000,0x7fc00123,0x3f800000][state-2]);}},
                    Store::U16{q,scale}=>{if state==1&&n>0{q.as_mut_slice()[n-1]=u16::MAX;}if (2..=4).contains(&state){scale.as_mut_slice()[1]=f32::from_bits([0x80000000,0x7fc00123,0x3f800000][state-2]);}},
                    _=>unreachable!(),
                }
                if state==5{a.initial[which].push(-0.0);}
                if state==6&&compact{a.inactive[0].initial[which]=0;}
                if state==7{a.initial[1-which].push(f32::from_bits(0x7fc00123));}
                let snapshot=match &store {Store::I16{q,scale}=>(q.as_slice().iter().map(|&x|x as u16).collect::<Vec<_>>(),scale.as_slice().iter().map(|x|x.to_bits()).collect::<Vec<_>>()),Store::U16{q,scale}=>(q.as_slice().to_vec(),scale.as_slice().iter().map(|x|x.to_bits()).collect::<Vec<_>>()),_=>unreachable!()};
                assert_eq!(a.can_upload_zeros(&store,which),a.e045_original_can_upload_zeros(&store,which),"n={n} compact={compact} which={which} kind={kind} state={state}");
                let after=match &store {Store::I16{q,scale}=>(q.as_slice().iter().map(|&x|x as u16).collect::<Vec<_>>(),scale.as_slice().iter().map(|x|x.to_bits()).collect::<Vec<_>>()),Store::U16{q,scale}=>(q.as_slice().to_vec(),scale.as_slice().iter().map(|x|x.to_bits()).collect::<Vec<_>>()),_=>unreachable!()};
                assert_eq!(snapshot,after);checks+=1;
            }}}}
        }
        assert_eq!(checks,576);
        println!("E045_FULL_PREDICATE_CONTROL {}",serde_json::json!({"cases":checks,"inputs_unchanged":true,"accepted_original_exact":true}));
    }
}
'''
chunk=1<<20;lengths=[0,1,7,127,128,129,chunk-1,chunk,chunk+1,2*chunk-1,2*chunk,2*chunk+1,3*chunk+17]
count=3*sum(2*(2+16*len(set(p for p in [0,max(0,n-1),chunk-1,chunk,2*chunk-1,2*chunk] if p<n))) for n in lengths)
tests=tests.replace('REFERENCE',reference).replace('EXPECTED_CHECKS',str(count))
candidate=production+tests
for name,data in [('base-arena.rs',raw),('production-arena.rs',production.encode('utf-8')),('candidate-arena.rs',candidate.encode('utf-8')),('tests.rs',tests.encode('utf-8'))]:(D/name).write_bytes(data)
for name,text in [('production.patch',production),('candidate.patch',candidate)]:
 (D/name).write_text(''.join(difflib.unified_diff(s.splitlines(keepends=True),text.splitlines(keepends=True),fromfile='a/'+rel,tofile='b/'+rel)),encoding='utf-8')
owned={rel:{'base':str(D/'base-arena.rs'),'base_sha256':old.sha(D/'base-arena.rs'),'candidate':str(D/'candidate-arena.rs'),'candidate_sha256':old.sha(D/'candidate-arena.rs')}}
old.save(D/'manifest.json',{'id':'E045-source','at':old.now(),'accepted_source_sha256':old.BASE,'owned':owned,'original_reference_exact':True,'chunk_words':chunk,'parallel_min_words':2*chunk,'raw_integer_checks_expected':count,'full_predicate_cases_expected':576,'ordinary_expected_passed':86,'ordinary_expected_ignored':4,'native_executed':False})
Q=ROOT/'runs/D075-zero-proof-parallel-source';Q.mkdir()
report=old.read(ROOT/'comparisons/D042-zero-proof-diagnostic/report.json')
spans={stage:sum(statistics.median([sum(x['stage_us'][stage] for x in report['raw_profiles'] if x['run_id']==rid and x['fixture_id']==f)/1000 for rid in ['D042P1','D042P2','D042P3']]) for f in ['rainbow','two-tone','river']) for stage in ['predicate','alloc_zeros_host_call','existing_stream_wait']}
duplicate_paths=[ROOT/'runs/D049-down-action-pointer-resource/candidate.cu',ROOT/'runs/E043-resource-r2/candidate.cu'];assert old.sha(duplicate_paths[0])==old.sha(duplicate_paths[1])
old.save(Q/'report.json',{'id':'D075-zero-proof-parallel-source','at':old.now(),'status':'go_one_fixed_parallel_proof_candidate','root_review_only':True,'source_sha256':{str(ar.REPO/x):old.sha(ar.REPO/x) for x in ['crates/solver/src/gpu/arena.rs','crates/solver/src/store.rs','crates/solver/src/gpu/mod.rs']},'diagnostic_sha256':old.sha(ROOT/'comparisons/D042-zero-proof-diagnostic/report.json'),'historical_sum_fixture_medians_ms':spans,'timing_limits':'Historical nested host spans only. They do not establish current headroom, removable work or projected complete-cycle gain. No new timings have run.','novelty':'D041 suggested parallel integer OR but it was not implemented. E038 omitted only unsigned q scanning and failed; E045 retains both complete scans and changes integer reduction scheduling only. E044 changed discount transfer scheduling, not these scans.','fixed_mechanism':{'chunk_words':chunk,'parallel_min_words':2*chunk,'thread_policy':'existing Rayon pool; research16 threads','factor_or_threshold_sweep_after_outcome':False},'exactness':'Scale-first bits check, signed u16 cast, all q values, zero identity, existing snapshot/inactive/F32 guards and all GPU/upload/readback behavior retained. OR is associative and commutative on u16; full result bits independent of chunk order. Read-only slices, no concurrent mutation under existing Solver borrowing contract.','cost_gate':'If timing qualifies, separately freeze matched whole-process CPU-time/peak-memory and responsiveness measurements. Positive median CPU-time increase plus strict majority paired increases disqualifies; no adoption on wall time alone. Existing16-worker pool can create extra concurrent CPU demand. No claim of no tradeoffs yet.','required_before_timing':['fresh feature/primary compilation','ordinary86pass/4ignored incl fixed raw integer corpus and576 full accepted-reference predicates','frozen3pair initial screen with1%/strict fixture policy'],'candidate_accepted':False})
old.save(Q/'E043-duplicate-correction.json',{'at':old.now(),'status':'historical_duplicate_identified','identical_candidate_sha256':old.sha(duplicate_paths[0]),'paths':[str(x) for x in duplicate_paths],'finding':'E043 exactly repeats D049 candidate CUDA and resource rejection. Count as a repeat, not a new hypothesis. Original records preserved. No further execution or rescue.','new_native_runs':0})
old.save(D/'source-review.json',{'id':'E045-source-review','at':old.now(),'status':'pass_for_compile_and_fixed_controls','root_review_only':True,'owned_files':1,'no_gpu_or_float_arithmetic_changes':True,'no_new_device_pinned_event_stream_graph_allocation':True,'new_solver_fields':0,'scale_snapshot_guards_exact':True,'original_reference_exact':True,'integer_raw_checks_expected':count,'full_predicate_cases_expected':576,'new_cpu_cost_validation_pending':True,'source_manifest_sha256':old.sha(D/'manifest.json'),'source_audit_sha256':old.sha(Q/'report.json'),'limits':'Source reasoning is not compiled correctness or timing evidence.'})
B=ROOT/'runs/E045-build-plan';B.mkdir()
build=(ROOT/'runs/E044-build-plan/build.py').read_text(encoding='utf-8').replace('E044','E045');(B/'build.py').write_text(build,encoding='utf-8')
p=old.read(ROOT/'runs/E044-build-plan/build-protocol.json');p.update(id='E045-final-build',at=old.now(),owned=owned)
for phase in p['phases']:
 phase['target']=phase['target'].replace('e044','e045');phase['outputs']={k:v.replace('E044','E045') for k,v in phase['outputs'].items()}
inputs=[B/'build.py',D/'manifest.json',D/'source-review.json',Q/'report.json',Q/'E043-duplicate-correction.json',D/'base-arena.rs',D/'candidate-arena.rs',ROOT/'runs/small-gain-confirmation-plan/common.py',Path(p['protected_main']),ar.REPO/'tools/postflop_autoresearch.py']
p['input_sha256']={str(x):old.sha(x) for x in inputs};old.save(B/'build-protocol.json',p)
published={}
for directory in [D,Q,B]:
 for source in directory.rglob('*'):
  if not source.is_file():continue
  key=directory.name+'/'+source.relative_to(directory).as_posix();target=ar.DASHBOARD/'evidence'/key;target.parent.mkdir(parents=True,exist_ok=True);assert not target.exists();raw=source.read_bytes();target.write_bytes(raw)
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==raw
  published[key]=old.sha(source)
old.save(B/'publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published,'native_executions':0})
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 status=old.read(ar.STATUS);assert not any(e['id']=='E045' for e in status['experiments'])
 status['experiments'].append({'id':'E045','at':old.now(),'title':'Parallel exact integer zero-proof scans','kind':'candidate','status':'preparing','correctness':'pending','stage':'Source frozen; fresh compile next','reason':'Both complete scans and all guards retained; existing Rayon pool. Fixed1Miword chunks/2Miword parallel boundary, no outcome-driven sweep. Extra CPU demand requires separate qualification if full-cycle timing passes.','evidence':[{'label':'E045 source review','url':'evidence/E045-design/source-review.json'},{'label':'D075 source/history audit','url':'evidence/D075-zero-proof-parallel-source/report.json'}]})
 e=next(x for x in status['experiments'] if x['id']=='E043');e['reason']+=' History correction: exact repeat of earlier rejected D049; not a new hypothesis.';e['evidence'].append({'label':'E043/D049 exact duplicate correction','url':'evidence/D075-zero-proof-parallel-source/E043-duplicate-correction.json'})
 status.update(stage='E045 fresh feature/primary compile',activity='Parallel zero-proof candidate prepared; no speed or compiled correctness result yet.',updated_at=ar.now(),state='running');ar.atomic_json(ar.STATUS,status)
print(json.dumps({'manifest_sha256':old.sha(D/'manifest.json'),'build_protocol_sha256':old.sha(B/'build-protocol.json'),'candidate_sha256':old.sha(D/'candidate-arena.rs'),'integer_checks':count,'historical_spans_ms':spans}),flush=True)
