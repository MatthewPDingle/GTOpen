from pathlib import Path
import hashlib,json,re,subprocess,datetime
H=Path(__file__).resolve().parent
ROOT=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
B=H.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
def write(name,v):
    with (H/name).open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,indent=2,ensure_ascii=True);f.write('\n')
assert not (H/'manifest.json').exists()
pins=load(B/'binaries/E020-postflop_autoresearch.manifest.json')['source_sha256']
for r,h in pins.items():assert sha(ROOT/r)==h,r
owned=['crates/solver/src/gpu/kernels.cu','crates/solver/src/gpu/mod.rs','crates/solver/src/gpu/plan.rs','crates/solver/src/gpu/continuation_capacity.rs','crates/solver/src/game.rs']
base={r:(H/'base'/r).read_text(encoding='utf-8') for r in owned}
c={r:(H/'candidate'/r).read_text(encoding='utf-8') for r in owned}
for r in owned:assert sha(H/'base'/r)==pins[r] and base[r]!=c[r],r
parse=[]
for r in owned:
    if r.endswith('.rs'):
        cmd=['rustfmt','--edition','2021','--emit','stdout','--config','skip_children=true',str(H/'candidate'/r)]
        p=subprocess.run(cmd,capture_output=True,timeout=30)
        assert p.returncode==0,(r,p.stderr.decode('utf-8','replace'))
        parse.append({'path':r,'command':cmd,'exit_code':p.returncode,'scope':'syntax-only, no typecheck/build'})
cmd=['git','apply','--check',str(H/'candidate.patch')]
p=subprocess.run(cmd,cwd=ROOT,capture_output=True,timeout=30)
assert p.returncode==0,p.stderr.decode('utf-8','replace')
k=owned[0];m=owned[1];plan=owned[2]
start='extern "C" __global__ void up_show('
end='// Up sweep, chance nodes:'
def show(s):return s.split(start,1)[1].split(end,1)[0]
assert base[k].split(start)[0]==c[k].split(start)[0]
assert base[k].split(end,1)[1]==c[k].split(end,1)[1]
scan='    // Blocked inclusive scan:'
finish='    float win = node_twin[n], lose = node_tlose[n], tie = node_ttie[n];'
assert show(base[k]).split(scan)[1].split(finish)[0]==show(c[k]).split(scan)[1].split(finish)[0]
tail='    for (int k = threadIdx.x; k < m_p; k += blockDim.x) {'
assert show(base[k]).split(tail)[1]==show(c[k]).split(tail)[1]
assert show(base[k]).count('__syncthreads();')==show(c[k]).count('__syncthreads();')==5
assert c[m].count('.arg(&self.d_riv_missing_idx[p])')==2
assert c[m].count('launch_builder(&self.f_up_show)')==2
assert c[m].count('let show_shared')==base[m].count('let show_shared')
assert re.findall(r'.*let show_shared.*',c[m])==re.findall(r'.*let show_shared.*',base[m])
for r in owned:
    assert c[r].count('#[test]')==base[r].count('#[test]'),r
    # Preserve all unrelated non-ASCII source lines exactly.
    assert [l for l in c[r].splitlines() if not l.isascii()]==[l for l in base[r].splitlines() if not l.isascii()],r
checks={'id':'E029-source-checks','created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'accepted_source_count':len(pins),'accepted_current_sha256_exact':True,'owned_count':len(owned),
 'syntax_only':parse,'patch_applicability':{'command':cmd,'exit_code':p.returncode},
 'unchanged_cuda_outside_up_show':True,'unchanged_scan_text':True,'unchanged_present_hand_fp_tail':True,
 'barriers_per_up_show':5,'both_training_eval_missing_args':True,'unchanged_show_shared_reservation':True,
 'unchanged_test_declaration_inventory':True,'prospective_gpu_only_passed':84,'prospective_gpu_only_ignored':4,
 'constructor_partial_move_audit':'All whole-plan methods remain before struct field moves; new upload closures borrow unmoved individual list fields only.',
 'accounting':'Exact sum(max(len_p,1)*4) in admission/planned metadata; observed slice lengths; public estimate per-player all-slot bound; seven mutable buffers and11 capacity components unchanged.',
 'compile_native_gpu_execution':False,'numeric_tests_executed':False,'candidate_accepted':False}
write('source-checks.json',checks)
refs=[B/'binaries/E020-postflop_autoresearch.manifest.json',B/'runs/D054-next-hypothesis-scout/manifest.json',B/'runs/D054-next-hypothesis-scout/report.json',B/'comparisons/D054-independent-source-review/report.json',B/'comparisons/D054-independent-source-review/manifest.json',B/'runs/D051-show-physical256-exact/protocol.json',B/'runs/D051-show-physical256-exact/corpus.json',B/'runs/D051-show-physical256-exact/probe.rs']
artifacts={str(f.relative_to(H)).replace('\\','/'):sha(f) for f in sorted(H.rglob('*')) if f.is_file()}
write('manifest.json',{'id':'E029-design','status':'FROZEN_OFF_TREE_UNEXECUTED','created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'accepted_base':'E020','accepted_source_sha256':pins,'owned_sources':owned,
 'accepted_owned_sha256':{r:pins[r] for r in owned},'candidate_owned_sha256':{r:sha(H/'candidate'/r) for r in owned},
 'artifact_sha256':artifacts,'reference_sha256':{str(f):sha(f) for f in refs},
 'prospective_unit_inventory':{'passed':84,'ignored':4,'total':88},
 'direct_validation':{'status':'separate preparation; not executed','scope':'complete immutable E020 vs candidate up_show','comparison_pairs':152,'launches':304,'physical_threads':[128,128]},
 'compiler_or_native_execution':False,'checkout_changed':False,'candidate_accepted':False})
print(json.dumps({'manifest_sha256':sha(H/'manifest.json'),'patch_sha256':sha(H/'candidate.patch'),'source_checks_sha256':sha(H/'source-checks.json'),'candidate_owned_sha256':{r:sha(H/'candidate'/r) for r in owned}}))
