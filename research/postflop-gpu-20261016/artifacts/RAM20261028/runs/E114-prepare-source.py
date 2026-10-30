import hashlib,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists();D=ROOT/'runs/D260-paired-chance-scout/report.json';d=h.read(D);assert d['status']=='pass_source_history_and_integer_ownership_only'and not d['matching_multiaccumulator_chance_forms'];cuda=h.REPO/'crates/solver/src/gpu/kernels.cu';h.pin(cuda,d['accepted_CUDA_sha256']);base=cuda.read_bytes();assert base.count(b'\n')==base.count(b'\r\n');start=base.index(b'extern "C" __global__ void up_chance(');a=base.index(b'{',start);i=a+1;depth=1
while depth:depth+=(base[i]==123)-(base[i]==125);i+=1
body=base[a:i];old=b'''    for (int i = threadIdx.x; i < nh_p; i += blockDim.x) {
        u64 hm = mask_p[i];
        float acc = 0.f;
        for (u32 t = t0; t < t1; t++) {
            u64 cm = 1ull << cc_card[t];
            if (hm & cm) continue;
            u32 k = cc_perm[t];
            int idx = k == 0 ? i : (int)hand_perm_p[(u64)k * nh_p + i];
            acc += cfv[(u64)cfv_slot[cc_child[t]] * nh_max + idx];
        }
        cfv[(u64)cfv_slot[n] * nh_max + i] = acc * inv;
    }'''.replace(b'\n',b'\r\n')
new=b'''    for (int i0 = threadIdx.x; i0 < nh_p; i0 += 2 * blockDim.x) {
        int i1 = i0 + blockDim.x;
        bool have1 = i1 < nh_p;
        u64 hm0 = mask_p[i0];
        u64 hm1 = have1 ? mask_p[i1] : 0ull;
        float acc0 = 0.f, acc1 = 0.f;
        for (u32 t = t0; t < t1; t++) {
            u64 cm = 1ull << cc_card[t];
            bool live0 = (hm0 & cm) == 0;
            bool live1 = have1 && (hm1 & cm) == 0;
            if (!live0 && !live1) continue;
            u32 k = cc_perm[t];
            u64 child_base = (u64)cfv_slot[cc_child[t]] * nh_max;
            if (live0) {
                int idx0 = k == 0 ? i0 : (int)hand_perm_p[(u64)k * nh_p + i0];
                acc0 += cfv[child_base + idx0];
            }
            if (live1) {
                int idx1 = k == 0 ? i1 : (int)hand_perm_p[(u64)k * nh_p + i1];
                acc1 += cfv[child_base + idx1];
            }
        }
        cfv[(u64)cfv_slot[n] * nh_max + i0] = acc0 * inv;
        if (have1) cfv[(u64)cfv_slot[n] * nh_max + i1] = acc1 * inv;
    }'''.replace(b'\n',b'\r\n');assert body.count(old)==1;changed=body.replace(old,new,1);candidate=base[:a]+changed+base[i:];assert candidate[a:a+len(changed)].replace(new,old,1)==body and candidate[:a]+body+candidate[a+len(changed):]==base;assert candidate.count(b'\n')==candidate.count(b'\r\n');O=ROOT/'runs/E114-source';O.mkdir(exist_ok=False);(O/'baseline-kernels.cu').write_bytes(base);(O/'candidate-kernels.cu').write_bytes(candidate);name='crates/solver/src/gpu/kernels.cu';h.save(O/'manifest.json',{'id':'E114','at':h.now(),'accepted_source':'E080','accepted_source_sha256':h.custody(),'candidate_owned_sha256':{name:h.sha(O/'candidate-kernels.cu')},'owned':{name:{'base':str(O/'baseline-kernels.cu'),'candidate':str(O/'candidate-kernels.cu'),'base_sha256':h.sha(O/'baseline-kernels.cu'),'candidate_sha256':h.sha(O/'candidate-kernels.cu')}},'source_activated':False,'candidate_accepted':False,'fixed_form':'Exactly two striped ordered accumulators only in original up_chance, no width/hand-count/predicate/helper/flags/entrysubset/source/sample rescue.'});h.save(O/'source-review.json',{'at':h.now(),'D260_report_sha256':h.sha(D),'generator_sha256':h.sha(__file__),'original_up_chance_body_sha256':hashlib.sha256(body).hexdigest(),'candidate_up_chance_body_sha256':hashlib.sha256(changed).hexdigest(),'all_other_CUDA_bytes_exact':True,'signature_and_15argument_ABI_exact':True,'original_per_hand_FP_recurrence_retained':'acc=+0; ascending t; skip blocked; identical hand_perm and child scalar f32 addition; final acc*inv. Two distinct variables never combine. Source design only, not compiled/numerical proof.','original_64bit_address_products_retained':True,'tail_has_no_second_hand_memory_access':True,'both_blocked_skips_original_guarded_metadata':True,'CUDA_CRLF_and_reverse_exact':True,'host_layout_payload_allocations_graphs_quality_unchanged':True,'kernel_or_solver_runs':0,'outstanding':['Compiled operand/loop mechanism and resource gate','Actual worklist CFV parent/child address independence','Original direct/full-state/canonical exactness','All ordinary/fixed complete-cycle and broader adoption gates']});h.custody();print(h.sha(O/'candidate-kernels.cu'),flush=True)
