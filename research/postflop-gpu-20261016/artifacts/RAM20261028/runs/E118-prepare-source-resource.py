import ast,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists();D=ROOT/'runs/D281-zero-tie-scout';h.read(D/'hit-classification.json');h.read(D/'static-payout-census.json');proof=h.read(D/'arithmetic-contract.json');assert proof['complete_prefix_bit_domain_partition']['nonzero_finite_accepted']==4278190078
S=ROOT/'runs/E118-source';S.mkdir(exist_ok=False);cuda=h.REPO/'crates/solver/src/gpu/kernels.cu';original=cuda.read_bytes();text=original.decode('utf-8');assert original.count(b'\n')==original.count(b'\r\n');a=text.index('extern "C" __global__ void up_show(');b=text.index('// Up sweep, chance nodes:',a);body=text[a:b];before=body;edits=[]
def change(old,new):
    global body
    assert body.count(old)==1,(old,body.count(old));body=body.replace(old,new);edits.append({'old':old,'new':new})
old='    for (int j = threadIdx.x; j < nh_o; j += blockDim.x) ro_sh[j] = ro_g[j];'
new='''#if __CUDA_ARCH__ == 1200
    int unsafe_tie_reach = 0;
    for (int j = threadIdx.x; j < nh_o; j += blockDim.x) {
        float r = ro_g[j];
        ro_sh[j] = r;
        unsafe_tie_reach |= __float_as_uint(r) > 0x67800000u;
    }
#else
    for (int j = threadIdx.x; j < nh_o; j += blockDim.x) ro_sh[j] = ro_g[j];
#endif'''.replace('\n','\r\n');change(old,new)
old='''        card_pos_sh[j] = o_card_pos[card_base + j];
    __syncthreads();
    const float* ro = ro_sh;'''.replace('\n','\r\n')
new='''        card_pos_sh[j] = o_card_pos[card_base + j];
#if __CUDA_ARCH__ == 1200
    int any_unsafe_tie_reach = __syncthreads_or(unsafe_tie_reach);
#else
    __syncthreads();
#endif
    const float* ro = ro_sh;'''.replace('\n','\r\n');change(old,new)
anchor='''    int m_p = p_cnt[slot];
    u32 pb = p_off[slot];'''.replace('\n','\r\n')
fast='''
#if __CUDA_ARCH__ == 1200
    // Bounded nonnegative reach keeps the omitted tie argument finite.
    bool finite_zero_tie = !any_unsafe_tie_reach && m_o > 0 && m_o <= 1326
        && total > 0.f
        && (__float_as_uint(tie) & 0x7fffffffu) == 0
        && (__float_as_uint(win) & 0x7fffffffu) < 0x7f800000u
        && (__float_as_uint(lose) & 0x7fffffffu) < 0x7f800000u;
    if (finite_zero_tie) {
        for (int k = threadIdx.x; k < m_p; k += blockDim.x) {
            u32 i = p_idx[pb + k];
            u32 lb = p_lower[pb + k], ub = p_upper[pb + k];
            float lower = lb > 0 ? prefix[lb - 1] : 0.f;
            float higher = total - (ub > 0 ? prefix[ub - 1] : 0.f);
            float lower_c = 0.f, higher_c = 0.f;
            u32 cc[2] = { pc1[i], pc2[i] };
            for (int x = 0; x < 2; x++) {
                u32 c0 = o_card_off[(u64)slot * 53 + cc[x]];
                u32 c1 = o_card_off[(u64)slot * 53 + cc[x] + 1];
                for (u32 t = c0; t < c1; t++) {
                    u32 pos = card_pos_sh[t - card_base];
                    float r = reach_sh[pos];
                    if (pos < lb) lower_c += r;
                    else if (pos >= ub) higher_c += r;
                }
            }
            lower -= lower_c;
            higher -= higher_c;
            // Exact prefix ordering of the sealed compute_120 baseline.
            float first_terms = __fmaf_rn(win, lower, __fmul_rn(lose, higher));
            u32 first_bits = __float_as_uint(first_terms) & 0x7fffffffu;
            if (first_bits > 0 && first_bits < 0x7f800000u) {
                cfv[(u64)cfv_slot[n] * nh_max + i] = first_terms;
                continue;
            }
            // Signed-zero/nonfinite prefix: reproduce the original total
            // card sum and final payout, preserving every input order.
            float tot_c = 0.f;
            for (int x = 0; x < 2; x++) {
                u32 c0 = o_card_off[(u64)slot * 53 + cc[x]];
                u32 c1 = o_card_off[(u64)slot * 53 + cc[x] + 1];
                for (u32 t = c0; t < c1; t++) {
                    u32 pos = card_pos_sh[t - card_base];
                    tot_c += reach_sh[pos];
                }
            }
            u32 sc = same_p[i];
            float same_r = sc != SENTINEL ? ro[sc] : 0.f;
            float valid = total - tot_c + same_r;
            float tied = valid - lower - higher;
            cfv[(u64)cfv_slot[n] * nh_max + i] = win * lower + lose * higher + tie * tied;
        }
        return;
    }
#endif
'''.replace('\n','\r\n');change(anchor,anchor+fast)
back=body
for edit in reversed(edits):assert back.count(edit['new'])==1;back=back.replace(edit['new'],edit['old'])
assert back==before and(text[:a]+back+text[b:]).encode()==original
(S/'baseline.cu').write_bytes(original);(S/'candidate.cu').write_bytes((text[:a]+body+text[b:]).encode());h.save(S/'manifest.json',{'id':'E118','at':h.now(),'status':'FROZEN_OFF_TREE_PRE_COMPILER','baseline_sha256':h.sha(S/'baseline.cu'),'candidate_sha256':h.sha(S/'candidate.cu'),'edits':edits,'entire_CRLF_source_inverse_exact':True,'original_full_noneligible_hand_loop_byte_exact':True,'active_architecture_macro':1200,'scope':'Oneup_show-onlyCUDAform. Existingfirstcopybarrierbecomesor-reductionvalidatingallro bits<=+2^80; otherbarriers/sharedregions unchanged. Positive-total,m_o1..1326,finitepayoffs,tie±0 permitorderedlower/higheronlyloop. NativebaselineFMAprefixorderexplicit;nonzerofiniteprefixskipstot_c/same_r/valid/tied/finalzeroFMA. Signedzero/nonfiniteprefixreplaysorderedtot_candoriginalpayout. IneligibleCTAandallotherarchitecturesretainsoriginalhandloop, absent-handzeroing/root/host/ABI/launch/payload/quality/cadence unchanged.','proof_input_sha256':{str(p):h.sha(p)for p in[D/'report.json',D/'hit-classification.json',D/'arithmetic-contract.json',D/'static-payout-census.json']},'risks':'ExtraCTAclassifier/uniformbranch, replayatzeroprefix, functionsize/registers/divergence/driverJITcost maylose. Sourceproofdoesnotqualifyemittedbypass,prefixFPprovenance,wholeIEEEequivalence,materialcostorspeed. NoE036zero-row/E069zero-output/E084firstcardcache/E107payoutloadhoisthunkcomposed. Genuinefailureclosesfixedbound/predicate/arch/loop/sourcewithoutrescue.','new_compilers_GPU_CFR_solver_or_speed_samples':0,'source_activated':False})
R=ROOT/'runs/E118-resource';R.mkdir(exist_ok=False);shutil.copyfile(S/'candidate.cu',R/'candidate.cu')
for arch,digest in{'compute_120':'4457a101f35369c5d1d9893409e4bc8a9dc027fc4234e325b72c621f73017c12','compute_75':'21f11fbb05bd51236ef5efaddc87fcd506ce61eeff6d9d8fa19406b5ef27eb70'}.items():
    p=ROOT/'runs/D207-resident-resource'/('baseline-'+arch+'.ptx');h.pin(p,digest);shutil.copyfile(p,R/p.name)
(R/'probe.rs').write_bytes((ROOT/'runs/E114-resource/probe.rs').read_bytes().replace(b'E114_RESOURCE',b'E118_RESOURCE'));old=h.read(ROOT/'runs/E114-resource/protocol.json');command=[x.replace('E114-resource','E118-resource')for x in old['rustc_command']]
code=(ROOT/'runs/E114-resource-execute.py').read_text(encoding='utf-8').replace('E114','E118');code=code.replace("b[name].count('bar.sync')==c[name].count('bar.sync')","len(re.findall(r'\\bbar\\.(?:sync|red)\\b',b[name]))==len(re.findall(r'\\bbar\\.(?:sync|red)\\b',c[name]))")
needle="gates[arch+':paired_chance_emitted_change']=not tables[arch]['up_chance']['body_alpha_exact']";assert code.count(needle)==1;code=code.replace(needle,"gates[arch+':architecture_expected_body_change']=not tables[arch]['up_show']['body_alpha_exact']if arch=='compute_120'else all(row['body_alpha_exact']for row in tables[arch].values())")
code=code.replace('Two ordered chance accumulators; emitted shared immutable metadata/two recurrence and caller/extent reviews remain','Finite zero-tie output prefix; actual guarded absence of tot_c/same/valid/tied work and exact baseline-prefix FP provenance plus barrier/caller reviews remain').replace('paired chance operand mechanism pending','zero-tie fastpath and FP mechanism pending').replace('All9ABIs/resources and changed fold entry','All9ABIs/resources and changed up_show entry');ast.parse(code);script=ROOT/'runs/E118-resource-execute.py';assert not script.exists();script.write_bytes(code.encode())
paths=[Path(__file__),script,ROOT/'epoch/common.py',ROOT/'runs/D281-zero-tie-scout.py',ROOT/'runs/D281-classify-and-census.py',ROOT/'runs/E114-resource/probe.rs',ROOT/'runs/E114-resource-execute.py',ROOT/'runs/E114-resource/protocol.json',h.REPO/'research/postflop-gpu-20261016/resource-feasibility-policy-20261017.md']+[p for p in D.iterdir()if p.is_file()]+[p for p in S.iterdir()if p.is_file()]+[p for p in R.iterdir()if p.is_file()]+[p for p in(ROOT/'reference/accepted-e080-deps').iterdir()if p.is_file()]
h.save(R/'protocol.json',{'id':'E118-resource','at':h.now(),'status':'FROZEN_PRE_ONE_RUST_COMPILER_AND_MODULE_ONLY_PROBE','rustc_command':command,'GPU_uuid':old['GPU_uuid'],'original_entries':old['original_entries'],'target_entries':['up_show'],'required_free_bytes':16*1024**3,'input_sha256':{str(p):h.sha(p)for p in paths},'scope':'OneRustcompiler/onemodule-onlyprocess,2candidateNVRTC12.9compute120/75;sealedacceptedbaselinePTXreused. All9ABIexact;compute120onlyup_showchanged;compute75all9entirebodiesexact. Firstbar.sync becomesbar.red.or; total5semanticCTAbarrierssame, actualfirstbarrierplacement/sharedorderingmustreview.8otherentries/actualresourcesexact. No local/constant/dynamic/stackgrowth/maxthreadloss/defaultlimitloss;positive64/128/256occupancy,warningsforregister/static/residencyunderD108. Thispassonlypermitsseparateactualfastpathbranch/bypass/FMA/callerproof; thenfulloriginaldirectshowIEEE/geometrycorpus+meaningfuledgewitnesses/wholeengine/canonical/ordinary/fullcycle1%strictfixture/fresh16/broad/material/holdout/cumulative/appgates. No applicationkernel/solver/speed/sourceactivation. Genuinefailureclosesexactbound/predicate/arch/loop/helper/source/flags/quality/sampleformwithoutrescue.'})
h.custody();print(json.dumps({'protocol_sha256':h.sha(R/'protocol.json'),'candidate_sha256':h.sha(S/'candidate.cu')}),flush=True)
