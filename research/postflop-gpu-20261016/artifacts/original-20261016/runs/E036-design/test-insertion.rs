
    // Pinned accepted E020 up_show only; entry rename is the sole body change.
    const SHOW_ORIGINAL_REFERENCE: &str = r###"typedef unsigned int u32;
typedef unsigned long long u64;
#define SENTINEL 0xFFFFFFFFu

extern "C" __global__ void up_show_reference(
    const u32* __restrict__ nodes, int start, int count,
    const float* __restrict__ node_twin, const float* __restrict__ node_tlose,
    const float* __restrict__ node_ttie,
    const int* __restrict__ node_river_slot,
    const u32* __restrict__ rsrc_o,
    const float* __restrict__ reach_o_buf,
    const u32* __restrict__ p_off, const u32* __restrict__ p_cnt,
    const u32* __restrict__ p_idx,
    const u32* __restrict__ p_lower, const u32* __restrict__ p_upper,
    const u32* __restrict__ o_off, const u32* __restrict__ o_cnt,
    const u32* __restrict__ o_idx,
    const u32* __restrict__ o_card_off, const u32* __restrict__ o_card_pos,
    const u32* __restrict__ same_p,
    const u32* __restrict__ pc1, const u32* __restrict__ pc2,
    const u32* __restrict__ cfv_slot, float* cfv,
    int nh_p, int nh_o, int nh_max)
{
    extern __shared__ char shraw[];
    int b = blockIdx.x;
    if (b >= count) return;
    u32 n = nodes[start + b];
    int slot = node_river_slot[n];
    int m_o = o_cnt[slot];
    u32 ob = o_off[slot];
    float* ro_sh = (float*)shraw; // nh_o entries, original hand order
    float* reach_sh = (float*)(shraw + sizeof(float) * nh_o);
    float* prefix = (float*)(shraw + sizeof(float) * (nh_o + m_o));
    u32* card_pos_sh = (u32*)(prefix + m_o); // 2*m_o immutable position indices
    u32 card_base = o_card_off[(u64)slot * 53];
    const float* ro_g = reach_o_buf + (u64)rsrc_o[n] * nh_o;

    for (int j = threadIdx.x; j < nh_o; j += blockDim.x) ro_sh[j] = ro_g[j];
    for (int j = threadIdx.x; j < 2 * m_o; j += blockDim.x)
        card_pos_sh[j] = o_card_pos[card_base + j];
    __syncthreads();
    const float* ro = ro_sh;
    for (int k = threadIdx.x; k < m_o; k += blockDim.x) {
        reach_sh[k] = ro[o_idx[ob + k]];
    }
    // zero my full cfv span (hands missing from this river's sorted list stay 0)
    for (int i = threadIdx.x; i < nh_p; i += blockDim.x)
        cfv[(u64)cfv_slot[n] * nh_max + i] = 0.f;
    __syncthreads();
    // Blocked inclusive scan: per-thread chunk scan, thread-0 scans chunk
    // totals, then chunk offsets are added back.
    __shared__ float chunk_sum[257];
    {
        int chunk = (m_o + blockDim.x - 1) / blockDim.x;
        int lo_k = threadIdx.x * chunk;
        int hi_k = min(lo_k + chunk, m_o);
        float acc = 0.f;
        for (int k = lo_k; k < hi_k; k++) {
            acc += reach_sh[k];
            prefix[k] = acc;
        }
        chunk_sum[threadIdx.x + 1] = acc;
        __syncthreads();
        if (threadIdx.x == 0) {
            chunk_sum[0] = 0.f;
            for (int t = 1; t <= (int)blockDim.x; t++) chunk_sum[t] += chunk_sum[t - 1];
        }
        __syncthreads();
        float base = chunk_sum[threadIdx.x];
        for (int k = lo_k; k < hi_k; k++) prefix[k] += base;
    }
    __syncthreads();
    float total = m_o > 0 ? prefix[m_o - 1] : 0.f;
    float win = node_twin[n], lose = node_tlose[n], tie = node_ttie[n];

    int m_p = p_cnt[slot];
    u32 pb = p_off[slot];
    for (int k = threadIdx.x; k < m_p; k += blockDim.x) {
        u32 i = p_idx[pb + k];
        u32 lb = p_lower[pb + k], ub = p_upper[pb + k];
        float lower = lb > 0 ? prefix[lb - 1] : 0.f;
        float higher = total - (ub > 0 ? prefix[ub - 1] : 0.f);
        float tot_c = 0.f, lower_c = 0.f, higher_c = 0.f;
        u32 cc[2] = { pc1[i], pc2[i] };
        for (int x = 0; x < 2; x++) {
            u32 c0 = o_card_off[(u64)slot * 53 + cc[x]];
            u32 c1 = o_card_off[(u64)slot * 53 + cc[x] + 1];
            for (u32 t = c0; t < c1; t++) {
                u32 pos = card_pos_sh[t - card_base];
                float r = reach_sh[pos];
                tot_c += r;
                if (pos < lb) lower_c += r;
                else if (pos >= ub) higher_c += r;
            }
        }
        u32 sc = same_p[i];
        float same_r = sc != SENTINEL ? ro[sc] : 0.f;
        float valid = total - tot_c + same_r;
        lower -= lower_c;
        higher -= higher_c;
        float tied = valid - lower - higher;
        cfv[(u64)cfv_slot[n] * nh_max + i] = win * lower + lose * higher + tie * tied;
    }
}
"###;

    #[test]
    fn show_positive_zero_matches_original_kernel() {
        fn bits(values: &[f32]) -> Vec<u32> { values.iter().map(|v| v.to_bits()).collect() }
        fn sorted(hands: &[(u8,u8)], board: &[u8], mode: u32, own: bool) -> Vec<(u32,usize)> {
            let mut result = Vec::new();
            for (i, &(a,b)) in hands.iter().enumerate() {
                if mode == 2 || (mode == 0 && if own { i%5 == 0 } else { i%7 == 0 || i+1 == hands.len() }) { continue; }
                let mut cards = board.to_vec(); cards.extend([a,b]);
                result.push((crate::evaluator::evaluate7(&cards),i));
            }
            result.sort_unstable();
            result
        }
        const GUARD: u32 = 0x4f12_3456;
        const NH_MAX: usize = 272;
        let ctx = CudaContext::new(0).unwrap();
        let stream = ctx.default_stream();
        let (major,minor) = ctx.compute_capability().unwrap();
        let arch: &'static str = Box::leak(format!("compute_{major}{minor}").into_boxed_str());
        let compile = |source: &str, entry: &str| {
            let ptx = cudarc::nvrtc::compile_ptx_with_opts(source,cudarc::nvrtc::CompileOptions {
                arch: Some(arch), ..Default::default()
            }).unwrap();
            ctx.load_module(ptx).unwrap().load_function(entry).unwrap()
        };
        let reference = compile(SHOW_ORIGINAL_REFERENCE,"up_show_reference");
        let candidate = compile(include_str!("kernels.cu"),"up_show");
        let board = crate::cards::parse_cards("Ks7h2dQhTc").unwrap();
        let all_hands: Vec<(u8,u8)> = (0..52u8).flat_map(|a|((a+1)..52).map(move |b|(a,b)))
            .filter(|(a,b)|!board.contains(a) && !board.contains(b)).collect();
        let hands_a = all_hands[..257].to_vec();
        let hands_b: Vec<_> = (0..129).map(|i|if i%2==0 { hands_a[i] } else { all_hands[300+i] }).collect();
        let overflow = f64::MAX as f32;
        assert_eq!(overflow.to_bits(),0x7f80_0000);
        let mix = [0x4020_0000,0xc020_0000,0x3f40_0000];
        let neg = [0xc020_0000,0xbfc0_0000,0xbf40_0000];
        // name, reach profile, three actual f32 payoff bits, own/opponent list modes, eligibility.
        // list modes: 0 partial, 1 full, 2 empty. Partial opponent excludes the last logical word.
        let cases = [
            ("zero_mixed",0,mix,0,0,true), ("zero_all_negative",0,neg,0,0,true),
            ("zero_positive_zero",0,[0,0,0],0,0,true),
            ("zero_negative_zero",0,[0x8000_0000;3],0,0,true),
            ("zero_full",0,mix,1,1,true), ("zero_empty_own",0,neg,2,1,true),
            ("zero_empty_opponent",0,neg,1,2,true), ("zero_both_empty",0,neg,2,2,true),
            ("zero_win_overflow",0,[overflow.to_bits(),mix[1],mix[2]],0,0,false),
            ("zero_lose_overflow",0,[mix[0],(-overflow).to_bits(),mix[2]],0,0,false),
            ("zero_tie_nan",0,[mix[0],mix[1],0x7fc1_2345],0,0,false),
            ("negative_zero_excluded_tail",1,mix,0,0,false),
            ("positive_nonzero_excluded_tail",2,mix,0,0,false),
            ("signed_cancellation",3,mix,0,0,false),
            ("infinite_excluded_tail",4,mix,0,0,false),
            ("nan_excluded_tail",5,mix,0,0,false),
        ];
        let mut pairs = 0usize;
        let mut launches = 0usize;
        for &(name,profile,payout_bits,own_mode,opp_mode,eligible) in &cases { for orientation in 0..2 {
            let (own,opponent) = if orientation==0 { (&hands_b,&hands_a) } else { (&hands_a,&hands_b) };
            let (nh_p,nh_o) = (own.len(),opponent.len());
            let ps = sorted(own,&board,own_mode,true);
            let os = sorted(opponent,&board,opp_mode,false);
            if own_mode==0 {
                assert!(ps.iter().enumerate().any(|(k,&(_,i))|k%128!=i%128),"cross-lane witness {name}");
                assert!(ps.len()<nh_p && !ps.is_empty());
            }
            if opp_mode==0 { assert!(os.iter().all(|&(_,i)|i+1!=nh_o),"excluded tail {name}"); }
            let pc1: Vec<u32> = own.iter().map(|h|h.0 as u32).collect();
            let pc2: Vec<u32> = own.iter().map(|h|h.1 as u32).collect();
            let same: Vec<u32> = own.iter().map(|h|opponent.iter().position(|x|x==h).map_or(u32::MAX,|i|i as u32)).collect();
            assert!(same.contains(&u32::MAX) && same.iter().any(|&v|v!=u32::MAX));
            let mut row = vec![0.0f32;nh_o];
            match profile {
                0=>{}, 1=>row[nh_o-1]=f32::from_bits(0x8000_0000),
                2=>{row[os[0].1]=0.5;row[nh_o-1]=0.25;},
                3=>{row[os[0].1]=1.0;row[os[1].1]=-1.0;},
                4=>row[nh_o-1]=f32::INFINITY,
                5=>row[nh_o-1]=f32::from_bits(0x7fc1_2345), _=>unreachable!(),
            }
            let payout = payout_bits.map(f32::from_bits);
            assert_eq!(row.iter().all(|x|x.to_bits()==0) && payout.iter().all(|x|x.is_finite()),eligible,"{name}");
            let nodes = vec![u32::MAX,2,u32::MAX];
            let mut twin=vec![9.5f32;4];twin[2]=payout[0];
            let mut tlose=vec![9.5f32;4];tlose[2]=payout[1];
            let mut ttie=vec![9.5f32;4];ttie[2]=payout[2];
            let river_slot=vec![-1i32,-1,1,-1];
            let reach_slot=if orientation==0 {2usize} else {1usize};
            let rsrc=vec![0u32,0,reach_slot as u32,0];
            let mut reach=vec![3.5f32;4*nh_o];reach[reach_slot*nh_o..(reach_slot+1)*nh_o].copy_from_slice(&row);
            let p_off=vec![0u32,3];let p_cnt=vec![0u32,ps.len() as u32];
            let mut p_idx=vec![u32::MAX;3];p_idx.extend(ps.iter().map(|&(_,i)|i as u32));p_idx.push(u32::MAX);
            let mut lower=vec![u32::MAX;3];let mut upper=vec![u32::MAX;3];
            for &(strength,_) in &ps {
                lower.push(os.partition_point(|&(s,_)|s<strength) as u32);
                upper.push(os.partition_point(|&(s,_)|s<=strength) as u32);
            }
            lower.push(u32::MAX);upper.push(u32::MAX);
            let o_off=vec![0u32,5];let o_cnt=vec![0u32,os.len() as u32];
            let mut o_idx=vec![u32::MAX;5];o_idx.extend(os.iter().map(|&(_,i)|i as u32));o_idx.push(u32::MAX);
            let mut card_off=vec![0u32;53];let mut card_pos=vec![u32::MAX;3];
            for card in 0..52u8 {
                card_off.push(card_pos.len() as u32);
                for (pos,&(_,i)) in os.iter().enumerate() {
                    let (a,b)=opponent[i];if card==a || card==b {card_pos.push(pos as u32);}
                }
            }
            card_off.push(card_pos.len() as u32);assert_eq!(card_pos.len(),3+2*os.len());card_pos.push(u32::MAX);
            let slots=vec![u32::MAX,u32::MAX,2,u32::MAX];
            let d_nodes=stream.clone_htod(&nodes).unwrap();let d_twin=stream.clone_htod(&twin).unwrap();
            let d_tlose=stream.clone_htod(&tlose).unwrap();let d_ttie=stream.clone_htod(&ttie).unwrap();
            let d_river=stream.clone_htod(&river_slot).unwrap();let d_rsrc=stream.clone_htod(&rsrc).unwrap();
            let d_reach=stream.clone_htod(&reach).unwrap();
            let d_poff=stream.clone_htod(&p_off).unwrap();let d_pcnt=stream.clone_htod(&p_cnt).unwrap();
            let d_pidx=stream.clone_htod(&p_idx).unwrap();let d_lower=stream.clone_htod(&lower).unwrap();let d_upper=stream.clone_htod(&upper).unwrap();
            let d_ooff=stream.clone_htod(&o_off).unwrap();let d_ocnt=stream.clone_htod(&o_cnt).unwrap();let d_oidx=stream.clone_htod(&o_idx).unwrap();
            let d_coff=stream.clone_htod(&card_off).unwrap();let d_cpos=stream.clone_htod(&card_pos).unwrap();
            let d_same=stream.clone_htod(&same).unwrap();let d_pc1=stream.clone_htod(&pc1).unwrap();let d_pc2=stream.clone_htod(&pc2).unwrap();
            let d_slots=stream.clone_htod(&slots).unwrap();
            let counts: &[i32]=if name=="zero_mixed" {&[1,0]} else {&[1]};
            let mut present=vec![false;nh_p];for &(_,i) in &ps {present[i]=true;}
            for &count in counts {
                let initial=vec![f32::from_bits(GUARD);4*NH_MAX];let mut outputs=Vec::new();
                for function in [&reference,&candidate] {
                    let mut out=stream.clone_htod(&initial).unwrap();
                    let start=1i32;let hp=nh_p as i32;let ho=nh_o as i32;let hm=NH_MAX as i32;
                    unsafe {stream.launch_builder(function).arg(&d_nodes).arg(&start).arg(&count)
                        .arg(&d_twin).arg(&d_tlose).arg(&d_ttie).arg(&d_river).arg(&d_rsrc).arg(&d_reach)
                        .arg(&d_poff).arg(&d_pcnt).arg(&d_pidx).arg(&d_lower).arg(&d_upper)
                        .arg(&d_ooff).arg(&d_ocnt).arg(&d_oidx).arg(&d_coff).arg(&d_cpos)
                        .arg(&d_same).arg(&d_pc1).arg(&d_pc2).arg(&d_slots).arg(&mut out).arg(&hp).arg(&ho).arg(&hm)
                        .launch(LaunchConfig {grid_dim:(2,1,1),block_dim:(128,1,1),shared_mem_bytes:((nh_o+4*os.len())*4) as u32}).unwrap();}
                    launches+=1;
                    let actual=bits(&stream.clone_dtoh(&out).unwrap());
                    for (i,&word) in actual.iter().enumerate() {
                        if count==1 && (2*NH_MAX..2*NH_MAX+nh_p).contains(&i) {
                            let logical=i-2*NH_MAX;assert_ne!(word,GUARD,"active store {name}/{orientation}/{i}");
                            if !present[logical] {assert_eq!(word,0,"absent +0 {name}/{orientation}/{i}");}
                            else if eligible {
                                let negative=payout_bits.iter().all(|v|v&0x8000_0000!=0);
                                assert_eq!(word,if negative {0x8000_0000} else {0},"present signedzero {name}/{orientation}/{i}");
                            }
                        } else {assert_eq!(word,GUARD,"guard {name}/{orientation}/{i}");}
                    }
                    macro_rules! same_int {($h:expr,$d:expr)=>{assert_eq!(&stream.clone_dtoh($d).unwrap(),$h,"immutable {name}/{orientation}");};}
                    macro_rules! same_float {($h:expr,$d:expr)=>{assert_eq!(bits(&stream.clone_dtoh($d).unwrap()),bits($h),"immutable float {name}/{orientation}");};}
                    same_int!(&nodes,&d_nodes);same_float!(&twin,&d_twin);same_float!(&tlose,&d_tlose);same_float!(&ttie,&d_ttie);
                    same_int!(&river_slot,&d_river);same_int!(&rsrc,&d_rsrc);same_float!(&reach,&d_reach);
                    same_int!(&p_off,&d_poff);same_int!(&p_cnt,&d_pcnt);same_int!(&p_idx,&d_pidx);same_int!(&lower,&d_lower);same_int!(&upper,&d_upper);
                    same_int!(&o_off,&d_ooff);same_int!(&o_cnt,&d_ocnt);same_int!(&o_idx,&d_oidx);same_int!(&card_off,&d_coff);same_int!(&card_pos,&d_cpos);
                    same_int!(&same,&d_same);same_int!(&pc1,&d_pc1);same_int!(&pc2,&d_pc2);same_int!(&slots,&d_slots);
                    stream.synchronize().unwrap();outputs.push(actual);
                }
                assert_eq!(outputs[0],outputs[1],"full original GPU comparison {name}/{orientation}/count{count}");
                if count==1 && profile==2 {assert!(outputs[0][2*NH_MAX..2*NH_MAX+nh_p].iter().any(|&x|x&0x7fff_ffff!=0),"nonzero witness {name}/{orientation}");}
                pairs+=1;
            }
        }}
        stream.synchronize().unwrap();drop(reference);drop(candidate);ctx.check_err().unwrap();
        assert_eq!((pairs,launches),(34,68));
        println!("E036_SHOW_ZERO_TEST {{\"comparison_pairs\":34,\"kernel_launches\":68,\"threads\":128,\"exact\":true,\"performance_measurement\":false}}");
    }

