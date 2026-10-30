"""Freeze one source form; no production activation or compiler is run."""
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists()
C=ROOT/'runs/D276-single-positive-census';r=h.read(C/'report.json');assert r['status']=='pass_scoped_retained_endpoint_census'and len(r['frames'])==12
assert h.read(C/'execution/reader.exit.json')['returncode']==0
S=ROOT/'runs/D275-single-positive-scout';h.read(S/'hit-classification.json');H=ROOT/'runs/E116-source';H.mkdir(exist_ok=False)
path=h.REPO/'crates/solver/src/gpu/kernels.cu';original=path.read_bytes();assert b'\r\n'in original and original.count(b'\n')==original.count(b'\r\n');text=original.decode('utf-8');candidate=text;edits=[]
for name,end in[('down_action_impl','extern "C" __global__ void down_action('),('up_action_impl','extern "C" __global__ void up_action(')]:
    start=candidate.index('__device__ __forceinline__ void '+name+'(');stop=candidate.index(end,start);body=candidate[start:stop];oldbody=body
    def change(before,after):
        global body
        assert body.count(before)==1,(name,before,body.count(before));at=body.index(before);body=body[:at]+after+body[at+len(before):];edits.append({'helper':name,'before':before,'after':after})
    indent='        'if name=='down_action_impl'else'            '
    change('\r\n'+indent+'float sum = 0.f;', '\r\n'+indent+'u32 positive_count = 0;\r\n'+indent+'float sum = 0.f;')
    change('\r\n'+indent+'    sum += r > 0.f ? r : 0.f;', '\r\n'+indent+'    sum += r > 0.f ? r : 0.f;\r\n'+indent+'    positive_count += r > 0.f;')
    flag='        // Used only inside the original sum > 1e-12f branch.\r\n        bool one_positive = positive_count == 1 && __float_as_uint(sum) < 0x7f800000u;\r\n'
    if name=='down_action_impl':
        change('\r\n        float pr = parent_reach[i];','\r\n'+flag+'        float pr = parent_reach[i];')
        change('v = pr * ((r > 0.f ? r : 0.f) / sum);','v = pr * (one_positive ? (r > 0.f ? 1.f : 0.f) : ((r > 0.f ? r : 0.f) / sum));')
    else:
        change('\r\n            float uni = 1.f / (float)na;','\r\n'+flag.replace('        ','            ')+'            float uni = 1.f / (float)na;')
        change('float sig = sum > 1e-12f ? (r > 0.f ? r : 0.f) / sum : uni;','float sig = sum > 1e-12f ? (one_positive ? (r > 0.f ? 1.f : 0.f) : (r > 0.f ? r : 0.f) / sum) : uni;')
    reverse=body
    for edit in reversed([e for e in edits if e['helper']==name]):assert reverse.count(edit['after'])==1;reverse=reverse.replace(edit['after'],edit['before'])
    assert reverse==oldbody;candidate=candidate[:start]+body+candidate[stop:]
assert len(edits)==8
(H/'baseline.cu').write_bytes(original);(H/'candidate.cu').write_bytes(candidate.encode('utf-8'));back=candidate
for e in reversed(edits):assert back.count(e['after'])==1,(e['helper'],e['after']);back=back.replace(e['after'],e['before'])
assert back.encode()==original
counts=[]
for f in r['frames']:
    rows=[g for g in f['groups']if g['actions']>=2];total=sum(g['unlocked_node_hands']for g in rows);one=sum(g['categories']['finite_above_threshold_one_positive']for g in rows);counts.append({'fixture':f['fixture'],'stage':f['stage'],'all_unlocked_endpoint_fraction':f['eligible_endpoint_node_hand_fraction'],'actions_ge2_node_hands':total,'actions_ge2_eligible_endpoint_fraction':one/total if total else 0})
h.save(H/'manifest.json',{'id':'E116','at':h.now(),'status':'FROZEN_OFF_TREE_SOURCE_ONLY','input_sha256':{str(p):h.sha(p)for p in[Path(__file__),S/'report.json',S/'hit-classification.json',C/'protocol.json',C/'report.json',C/'execution/reader.exit.json',ROOT/'epoch/common.py']},'owned_path':'crates/solver/src/gpu/kernels.cu','baseline_sha256':h.sha(H/'baseline.cu'),'candidate_sha256':h.sha(H/'candidate.cu'),'edits':edits,'inverse_entire_CRLF_source_byte_exact':True,'source_activated':False,'new_compilers_GPU_CFR_solver_or_speed_samples':0,'arithmetic_contract':'Count strictly positive regrets during unchanged ascending original f32 sum in unlocked down_action and training up_action. Only within original sum>1e-12 branch, exactly1positive and finite sum allow normalized sigma+1/+0, bypass division. Keep every original multiply, expectation reduction, strategy FMA/update, regret discount/update and output write, plus original fallback/locked/opponent/zero-sum/nonfinite paths. NaN/inf/overflow/signedzero/subnormal and payload behavior require actual raw CUDA equivalence; source reasoning alone does not qualify.',
 'scope':'One CUDA source only, no host/plan/ABI/entry/launch/block/menu/array/cache/allocation/precision/compiler-flag/cadence/quality/save change. Existing NA2/3/4/generic dispatch unchanged; E047 NA1 template binding is not composed. No zero-reach/zero-output shortcut, omitted multiplication, persistent sigma cache, clamp spelling or closed E091/E028/D199 form. No implementation/result-driven arity/selection/helper/threshold/source/flags/sample rescue.',
 'counterevidence':'Existing E047 changes template binding for na1 and failed its speed screen; current form binds no arity and depends on per-hand regret distribution across original menus. Extra count/predicate/branch/register/control cost is unqualified and may outweigh avoided divisions. Endpoint fractions are not per-iteration incidence or time/headroom. Source is not adopted.',
 'retained_endpoint_fractions':counts,'required_next':'Freeze compiler/resource/actual raw CUDA protocol before running any compiler. Require exact9entry ABI, untouched7entry bodies/resources, no local/shared/stack growth or supported-block/defaultoccupancy loss, changed target code with actual guarded division bypass and no FP contraction/reassociation/fast-math flags. Then full direct corpus including unusual floats/NaN payloads/overflow/near-threshold/locks/menus/hand+block tails/countzero/guards and immutable arrays. Require meaningful single-positive taken/fallback witnesses in both target helpers and exact original full engine/canonical raw physical state. Only afterward ordinary real-NVRTC/JIT builds/units and original fullcycle>=1%/strictfixture/fresh16/broad/material/capacity/holdout/freshoriginal/cumulative/application gates; actual failure closes form without rescue.'})
h.custody();print(json.dumps({'status':'off_tree_only','candidate_sha256':h.sha(H/'candidate.cu'),'manifest_sha256':h.sha(H/'manifest.json'),'new_compilers_GPU_or_speed_samples':0}),flush=True)
