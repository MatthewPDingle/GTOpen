"""Host-only source/corpus audit and preparation seal; no compiler or CUDA calls."""
from pathlib import Path
import ast, hashlib, json, struct
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
REPO=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,v):
    with (HERE/name).open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,indent=2,allow_nan=False);f.write('\n')
for name in ['prepare.py','run.py','seal.py']:
    ast.parse((HERE/name).read_text(encoding='utf-8'),filename=name)
c=json.loads((HERE/'corpus.json').read_text(encoding='utf-8'))
assert len(c['raw_cases'])==224 and len(c['full_scenarios'])==17
assert c['lengths']==[0,1,31,32,33,63,64,65,127,128,129,255,256,257,319,1326]
assert c['blocks']==[128,16,32,64,256]
for case in c['raw_cases']:
    assert all((v&0x7f800000)!=0x7f800000 for v in case['bits'])
full_expected_words=0;finite_words=0;max_device_payload=0
for s in c['full_scenarios']:
    n=s['nh_o'];own=s['nh_p'];stride=s['nh_max'];meta=s['node_meta']
    assert len(meta)==56 and s['start']==2 and s['count']==56
    assert len(s['nodes'])==59 and s['nodes'][2:58]==list(reversed(range(56)))
    assert len(set(s['cfv_slot']))==56
    assert len(s['card_off'])==53 and s['card_off'][0]==0 and s['card_off'][-1]==2*n
    assert len(s['card_idx'])==2*n and len(s['opponent_hands'])==n and len(s['own_hands'])==own
    for card in range(52):
        assert s['card_idx'][s['card_off'][card]:s['card_off'][card+1]]==[i for i,h in enumerate(s['opponent_hands']) if card in h]
    lookup={tuple(h):i for i,h in enumerate(s['opponent_hands'])}
    for i,h in enumerate(s['own_hands']):
        assert h==[s['pc1'][i],s['pc2'][i]] and h[0]<h[1]
        assert s['same_p'][i]==lookup.get(tuple(h),0xffffffff)
    for key in ['reach0_bits','reach1_bits']:
        assert all((v&0x7f800000)!=0x7f800000 for v in s[key])
    for i in range(56):
        assert s['rsrc0'][i]*n+n<=len(s['reach0_bits'])
        assert s['rsrc1'][i]*n+n<=len(s['reach1_bits'])
        assert s['cfv_slot'][i]*stride+own<=s['cfv_words']
    full_expected_words+=56*own*10
    finite_words+=52*own*10
    # Conservative single-scenario device vector payload, two outputs plus metadata.
    payload=4*(len(s['reach0_bits'])+len(s['reach1_bits'])+2*s['cfv_words']+
        sum(len(s[k]) for k in ['nodes','rsrc0','rsrc1','cfv_slot','pc1','pc2','same_p','card_off','card_idx'])+3*56+16)
    max_device_payload=max(max_device_payload,payload)
checks={'python_ast_parse':'pass','rust_parse':'rustfmt --edition 2021 --emit stdout probe.rs passed; no compiler invocation',
    'input_words_all_finite':True,'card_order_and_same_maps_exact':True,'slot_bounds_and_output_ownership':True,
    'raw_cases':224,'finite_domain_raw_cases':208,'full_scenarios':17,
    'ordinary_full_pairs':17*2*5,'additional_zero_count_pairs':2*5,'full_case_pairs':180,'kernel_launches':370,
    'all_full_output_words_per_variant':full_expected_words,'finite_domain_full_output_words_per_variant':finite_words,
    'max_single_scenario_device_payload_estimate_bytes':max_device_payload,
    'builds_executed':0,'gpu_calls_executed':0,'production_edits':0}
save('preparation-checks.json',checks)
protocol={'id':'D036','status':'prospective_frozen_before_execution','source_scope':'standalone only; accepted checkout unchanged',
    'accepted_base':'E015','full_kernel_authority':'Complete accepted/candidate up_fold in separate modules, same context/options',
    'candidate_scope':'Only 128x1x1 fold reduction tail; every other kernel/source byte unchanged',
    'inputs':'corpus.json IEEE u32 bits, exact serialized mappings/seed/order; never generated during execution',
    'matrix':checks,'blocks':[128,16,32,64,256],'player_order':[0,1],
    'all_fixed_finite_input_cases_must_match_gpu_bits':True,'overflow_mismatch_is_failure':True,
    'nonfinite_output_bits_and_counts_reported':True,'nan_inf_input_guarantee':False,
    'finite_output_domain_additional_cpu_raw_total_oracle':True,
    'corpus_sha256':sha(HERE/'corpus.json'),'source_variants':json.loads((HERE/'source-variants.json').read_text(encoding='utf-8')),
    'compile_options':'architecture compute_120 only; all other NVRTC defaults, matching accepted production',
    'stage_timeout_seconds':600,'heartbeat_seconds':10,'s_free_reserve_gib':50,'s_output_reservation_gib':1,
    'no_gpu_telemetry_poll_during_execution':True,'one_shot_no_retry':True,
    'expected_stage_counts':{'harness_checks':1,'resource':8,'raw_total_exact':5,'full_fold_exact':180,'complete':1},
    'output_guards_and_all_inputs_checked_after_each_variant':True,
    'mismatch_self_tests_are_not_cuda_numerical_cases':True,
    'performance_measurement':False,'candidate_accepted':False,'root_only_execution_after_independent_review':True,
    'official_reference':'https://docs.nvidia.com/cuda/archive/12.4.1/cuda-c-programming-guide/index.html#warp-shuffle-functions'}
save('protocol.json',protocol)
old=json.loads((ROOT/'runs/D031-child-slot-probe/prepared-manifest.json').read_text(encoding='utf-8'))
deps=old['dependency_rlibs']
for name,info in deps.items():assert sha(info['path'])==info['sha256'],name
protected={
 'crates/solver/src/gpu/kernels.cu':'8fe86cb859124592f9df13821f4a300450045620e6947e99466e4228b78c20d0',
 'crates/solver/src/gpu/mod.rs':'7de2cd46ef93742c603042306cfe2ad08a83ff52a2be1123efd9d201aca15f1a',
 'crates/solver/src/gpu/plan.rs':'aca00f163db77af01960cd55cb5484226f25c7c58bae325d4c50ebc44672b680',
 'crates/solver/src/gpu/continuation_capacity.rs':'e8b38a1c828e56d84af55f562270327e59dbcbc68d7bb6f289a90ab93f795ed2',
 'crates/solver/tests/postflop_autoresearch.rs':'f13d79410a22f140c05cb9a822fe9685c2180e5baeda4b625d52ae03feebd327'}
for name,h in protected.items():assert sha(REPO/name)==h,name
manifest={'id':'D036','status':'prepared_not_executed','protocol_sha256':sha(HERE/'protocol.json'),
    'source_variants':protocol['source_variants'],'dependency_rlibs':deps,'protected_checkout_sha256':protected,
    'artifact_sha256':{p.name:sha(p) for p in sorted(HERE.iterdir()) if p.is_file()},
    'builds_executed':0,'gpu_calls_executed':0,'production_edits':0}
save('prepared-manifest.json',manifest)
print(json.dumps({'directory':str(HERE),'manifest_sha256':sha(HERE/'prepared-manifest.json'),'protocol_sha256':sha(HERE/'protocol.json'),
    'probe_sha256':sha(HERE/'probe.rs'),'runner_sha256':sha(HERE/'run.py'),'checks':checks},indent=2))
