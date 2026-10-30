"""Freeze one selective-prefix CUDA/host prototype and compiler-only resource test."""
from pathlib import Path
import ast,difflib,json,shutil,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert not (R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3
D=R/'runs/D124-prefix-liveness';q=old.read(D/'report.json');assert q['status']=='admit_one_selective_prefix_resource_prototype'and len(q['cases'])==12
S=R/'runs/E077-source';H=R/'runs/E077-resource';assert not S.exists()and not H.exists();S.mkdir();H.mkdir()
cu=(old.REPO/'crates/solver/src/gpu/kernels.cu').read_text(encoding='utf-8');candidate=cu
edits=[('reach_sh[k] = ro[o_idx[ob + k]];','reach_sh[k] = ro[o_idx[ob + k] & 0x7fffffffu];'),('            prefix[k] = acc;','            if (o_idx[ob + k] & 0x80000000u) prefix[k] = acc;'),('        for (int k = lo_k; k < hi_k; k++) prefix[k] += base;','        for (int k = lo_k; k < hi_k; k++) {\n            if (o_idx[ob + k] & 0x80000000u) prefix[k] += base;\n        }'),('u32 i = p_idx[pb + k];','u32 i = p_idx[pb + k] & 0x7fffffffu;')]
for a,b in edits:assert candidate.count(a)==1;candidate=candidate.replace(a,b)
reverse=candidate
for a,b in reversed(edits):assert reverse.count(b)==1;reverse=reverse.replace(b,a)
assert reverse==cu
helper='''/// Tag precisely the shared prefixes read by the opposite player's showdown
/// evaluation. This mutates only a constructor-owned plan after its public build;
/// GPU index loads mask bit31, leaving every physical hand index unchanged.
pub(crate) fn tag_prefix_reads(plan: &mut GpuPlan) {
    const NEEDED: u32 = 0x8000_0000;
    for opponent in 0..2 {
        let own = 1 - opponent;
        for slot in 0..plan.num_slots {
            let ob = plan.riv_off[opponent][slot] as usize;
            let count = plan.riv_cnt[opponent][slot] as usize;
            if count != 0 { plan.riv_sorted_idx[opponent][ob + count - 1] |= NEEDED; }
            let begin = plan.riv_off[own][slot] as usize;
            let end = begin + plan.riv_cnt[own][slot] as usize;
            for i in begin..end {
                let lower = plan.riv_lower[own][i] as usize;
                let upper = plan.riv_upper[own][i] as usize;
                if lower != 0 { plan.riv_sorted_idx[opponent][ob + lower - 1] |= NEEDED; }
                if upper != 0 { plan.riv_sorted_idx[opponent][ob + upper - 1] |= NEEDED; }
            }
        }
    }
}

'''
unit='''    #[test]
    fn index_tags_preserve_hands_and_exact_prefix_consumers() {
        for board in ["KsQs2d", "Qs7h2dKh", "AsKsQsJsTs"] {
            let spot = Spot::new(SpotConfig {
                board: board.into(),
                range_oop: "AA,KK,QQ,JJ,TT,99,AKs,AQs,JTs,87s,AKo".into(),
                range_ip: "AA,QQ,TT,77,55,AQs,KQs,QJs,98s,AQo".into(),
                tree: TreeConfig { starting_pot: 10.0, effective_stack: 20.0, ..Default::default() },
            }).unwrap();
            for iso in [false, true] {
                let mut plan = GpuPlan::build(&spot, iso);
                let before = plan.riv_sorted_idx.clone();
                tag_prefix_reads(&mut plan);
                for opponent in 0..2 {
                    assert_eq!(plan.riv_sorted_idx[opponent].len(), before[opponent].len());
                    for (&tagged, &original) in plan.riv_sorted_idx[opponent].iter().zip(&before[opponent]) {
                        assert_eq!(tagged & 0x7fff_ffff, original);
                    }
                    let own = 1 - opponent;
                    for slot in 0..plan.num_slots {
                        let ob = plan.riv_off[opponent][slot] as usize;
                        let count = plan.riv_cnt[opponent][slot] as usize;
                        let begin = plan.riv_off[own][slot] as usize;
                        let end = begin + plan.riv_cnt[own][slot] as usize;
                        let mut expected = std::collections::HashSet::new();
                        if count != 0 { expected.insert(count - 1); }
                        for &bound in plan.riv_lower[own][begin..end].iter().chain(&plan.riv_upper[own][begin..end]) {
                            if bound != 0 { expected.insert(bound as usize - 1); }
                        }
                        let actual: std::collections::HashSet<_> = plan.riv_sorted_idx[opponent][ob..ob + count]
                            .iter().enumerate().filter_map(|(i, &v)| (v & 0x8000_0000 != 0).then_some(i)).collect();
                        assert_eq!(actual, expected);
                    }
                }
                let once = plan.riv_sorted_idx.clone();
                tag_prefix_reads(&mut plan);
                assert_eq!(plan.riv_sorted_idx, once, "tagging must be idempotent");
            }
        }
    }

'''
plan=(old.REPO/'crates/solver/src/gpu/plan.rs').read_text(encoding='utf-8');assert plan.count('#[cfg(test)]')==1
candidate_plan=plan.replace('#[cfg(test)]',helper+'#[cfg(test)]')
needle='    #[test]\n    fn river_bounds_match_strength_comparisons()';assert candidate_plan.count(needle)==1;candidate_plan=candidate_plan.replace(needle,unit+needle)
mod=(old.REPO/'crates/solver/src/gpu/mod.rs').read_text(encoding='utf-8');needle='        let ctx = CudaContext::new(0).map_err(e)?;';assert mod.count(needle)==1
candidate_mod=mod.replace(needle,'        plan::tag_prefix_reads(&mut plan);\n'+needle)
names=['crates/solver/src/gpu/kernels.cu','crates/solver/src/gpu/plan.rs','crates/solver/src/gpu/mod.rs'];base_files=['baseline.cu','baseline-plan.rs','baseline-mod.rs'];candidate_files=['candidate.cu','candidate-plan.rs','candidate-mod.rs']
patch=''
for n,b,c,a,z in zip(names,base_files,candidate_files,[cu,plan,mod],[candidate,candidate_plan,candidate_mod]):
 (S/b).write_text(a,encoding='utf-8',newline='\n');old.pin(S/b,old.BASE[n]);(S/c).write_text(z,encoding='utf-8',newline='\n');patch+=''.join(difflib.unified_diff(a.splitlines(True),z.splitlines(True),fromfile=n,tofile=n))
(S/'candidate.patch').write_text(patch,encoding='utf-8',newline='\n');(S/'tag-prefix.rs').write_text(helper,encoding='utf-8',newline='\n')
old.save(S/'manifest.json',{'id':'E077','at':old.now(),'accepted_source_sha256':old.BASE,'candidate_owned_sha256':{n:old.sha(S/c)for n,c in zip(names,candidate_files)},'owned':{n:{'base':str(S/b),'candidate':str(S/c)}for n,b,c in zip(names,base_files,candidate_files)},'source_scope':'Selective materialization of demanded shared prefixes in up_show. Encode demand in bit31 of existing sorted hand-index vectors in place in constructor-owned CPU plan, mask low31 at original two CUDA hand dereferences. Suppress only unread per-chunk prefix stores and dead offset-adds; every live recurrence/barrier/float expression/ordered chunk sum/card correction/output remains. No extra allocation, persistent field/device buffer/byte, temporary array, synchronization, ABI27, launch/graph/sizing/save/quality change. CPU tagging loops remain inside constructor clock. One host exact-tag/idempotence unit test added. Public GpuPlan::build still produces original values.','D124_report_sha256':old.sha(D/'report.json'),'candidate_accepted':False})
old.save(S/'source-review.json',{'id':'E077','at':old.now(),'status':'source_and_retained_demand_review_only','CUDA_edits':edits,'four_edits_reverse_exactly_to_accepted_CUDA':True,'all8_other_source_entries_exact':True,'host_scope':'One internal pure-integer in-place tagging helper and one call after unchanged budget check/before context creation. Original sorted-index vector allocations/lifetimes/uploads and all buffer counts/bytes retained. No new arrays/fields; helper uses immutable offsets/counts/boundaries and mutates only high bits of its constructor-owned sorted indices. All training/evaluation up_show uses pass those same arrays.','float_scope':'Original per-thread acc += reach, all chunk_sum operations, all barriers, each consumed prefix offset addition, total/boundary/card-order corrections and payout expressions retained. Only unobserved shared writes and their unobserved per-element offset additions are omitted. Source reasoning is not compiled FP/NaN equivalence proof.','limits':'New mask/predicate arithmetic and CPU tagging can cost time or resources. Full compiled host integer and GPU raw controls, primary timing and all broader/material qualification required. No E022/E062/E059/E073/E076 form composed.'})
for n in ['baseline.cu','candidate.cu']:shutil.copyfile(S/n,H/n)
probe=(R/'runs/E073-resource/probe.rs').read_text(encoding='utf-8').replace('E073_RESOURCE','E077_RESOURCE');(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
execute=r'''"""One exact-source compiler/resource process; no application kernels or source activation."""
from pathlib import Path
import collections,hashlib,json,re,shutil,subprocess,sys
H=Path(__file__).resolve().parent;R=H.parent.parent
sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json');O=H/'execution'
def verify():
 for p,h in P['input_sha256'].items():old.pin(p,h)
 old.pin(P['allocation_proof']['path'],P['allocation_proof']['sha256']);old.custody()
def entries(path):
 t=path.read_text(encoding='utf-8');out={};i=0
 while True:
  i=t.find('.visible .entry ',i)
  if i<0:break
  n=t.index('(',i);name=t[i+len('.visible .entry '):n].strip();a=t.index('{',n);j=a+1;depth=1
  while depth:
   if t[j]=='{':depth+=1
   elif t[j]=='}':depth-=1
   j+=1
  assert name not in out;out[name]=t[i:j];i=j
 return out
def normalize(t):
 t=re.sub(r'\$L__BB\d+_(\d+)',r'$L__BB_FUNCTION_\1',t)
 t=re.sub(r'__local_depot\d+','__local_depot_FUNCTION',t)
 return re.sub(r'\$L__func_(begin|end)\d+',r'$L__func_\1_FUNCTION',t)
assert normalize('$L__BB7_2: __local_depot7[64]')==normalize('$L__BB8_2: __local_depot8[64]')
assert normalize('add.u32 %r1, %r2, 4;')!=normalize('add.u32 %r1, %r2, 8;')
def child(command,label,timeout):
 proc=None;error=None;cleanup=None;start=old.now()
 try:
  with (O/(label+'.stdout.log')).open('xb')as out,(O/(label+'.stderr.log')).open('xb')as err:
   old.save(O/(label+'.invocation.json'),{'at':start,'command':command,'cwd':str(O)});proc=subprocess.Popen(command,cwd=O,env=old.env(),stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW);proc.wait(timeout=timeout)
  assert proc.returncode==0,(label,(O/(label+'.stderr.log')).read_text(encoding='utf-8',errors='replace')[-3000:])
 except BaseException as exc:error=repr(exc);cleanup=old.ar.cleanup_child(proc);raise
 finally:old.save(O/(label+'.exit.json'),{'started_at':start,'finished_at':old.now(),'returncode':proc.returncode if proc else None,'error':error,'cleanup':cleanup})
verify()
with old.ar.exclusive_lock(R/'gpu-run.lock'):
 old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3;assert not O.exists()and not (H/'probe.exe').exists();O.mkdir()
 gpu=old.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total','--format=csv,noheader'],timeout=10);assert gpu['returncode']==0 and P['gpu_uuid']in gpu['stdout'];old.save(O/'before.json',{'at':old.now(),'GPU':gpu,'application_kernel_launches':0})
 child(P['rustc_command'],'rustc',180);verify();old.save(O/'build-complete.json',{'at':old.now(),'compiler_terminal':True,'binary_sha256':old.sha(H/'probe.exe'),'native_executions':0})
 child([str(H/'probe.exe')],'probe',180);verify()
 markers=[json.loads(x.split('E077_RESOURCE ',1)[1])for x in (O/'probe.stdout.log').read_text(encoding='utf-8').splitlines()if 'E077_RESOURCE 'in x];assert len(markers)==22 and markers[0]['stage']=='device'and markers[-1]['stage']=='complete'
 rows={(x['variant'],x['shape']):x for x in markers[1:-1]};assert len(rows)==20
 tables={(v,a):entries(O/f'{v}-{a}.ptx')for v in ['baseline','candidate']for a in ['compute_120','compute_75']};assert all(set(t)==set(P['expected_entries'])for t in tables.values())
 gates={};abi={};mechanism={}
 for arch in ['compute_120','compute_75']:
  b,c=tables['baseline',arch],tables['candidate',arch]
  comparisons={n:{'raw_exact':b[n]==c[n],'normalized_only_local_function_ordinals_exact':normalize(b[n])==normalize(c[n])}for n in b if n!='up_show'}
  gates[arch+':other8entries_exact_modulo_only_local_function_ordinals']=all(x['normalized_only_local_function_ordinals_exact']for x in comparisons.values())
  be,ce=b['up_show'],c['up_show'];bs=be.split('{',1)[0];cs=ce.split('{',1)[0];gates[arch+':ABI27_exact']=bs==cs and bs.count('.param ')==27
  masks=lambda t:re.findall(r'\band\.b32\s+[^;\n]*,\s*(?:2147483647|0x7[fF]{7})\s*;',t)
  bm,cm=masks(be),masks(ce);gates[arch+':low31bit_decode_masks_emitted']=len(cm)>=2 and len(cm)>len(bm);gates[arch+':show_entry_changed']=normalize(be)!=normalize(ce)
  abi[arch]={'parameters':bs.count('.param '),'baseline_header_sha256':hashlib.sha256(bs.encode()).hexdigest(),'candidate_header_sha256':hashlib.sha256(cs.encode()).hexdigest()}
  fp=lambda t:dict(collections.Counter(re.findall(r'\b(?:add|sub|mul|fma|div|rcp|sqrt|abs|max|min|setp)(?:\.[A-Za-z0-9_]+)*\.f(?:32|64)\b',t)))
  mechanism[arch]={'other_entries':comparisons,'baseline_low31_mask_sites':bm,'candidate_low31_mask_sites':cm,'FP_opcode_counts_diagnostic_only':{'baseline':fp(be),'candidate':fp(ce)},'limits':'Static masks and changed entry prove new index decode was compiled. This is not full dataflow, dynamic dead-store, SASS/traffic, numeric or speed proof. Source demand/control proof and direct raw cases remain mandatory.'}
 sys.path.insert(0,str(old.REPO/'tools'));from postflop_resource_feasibility import evaluate_feasibility
 feasibility={};warnings=[]
 for shape in P['shapes']:
  b,c=rows['baseline',shape],rows['candidate',shape];a=evaluate_feasibility(b,c,old.read(P['allocation_proof']['path']));feasibility[shape]=a
  gates.update({shape+':'+k:v for k,v in a['gates'].items()});gates[shape+':local_bytes_exact']=b['local_bytes_per_thread']==c['local_bytes_per_thread'];gates[shape+':static_shared_bytes_exact']=b['static_shared_bytes']==c['static_shared_bytes'];gates[shape+':dynamic_shared_bytes_exact']=b['dynamic_shared_bytes']==c['dynamic_shared_bytes'];warnings.extend(a['resource_warnings'])
 report={'id':'E077-resource','at':old.now(),'status':'pass_compiled_selective_prefix_prerequisites'if all(gates.values())else'rejected_compiled_prerequisite','protocol_sha256':sys.argv[1],'gates':gates,'rows':markers[1:-1],'feasibility':feasibility,'resource_warnings':warnings,'abi':abi,'emitted_mechanism':mechanism,'raw_markers':markers,'ptx_sha256':{v+'-'+a:old.sha(O/f'{v}-{a}.ptx')for v in ['baseline','candidate']for a in ['compute_120','compute_75']},'binary_sha256':old.sha(H/'probe.exe'),'all_owned_children_terminal':True,'application_kernel_launches':0,'solver_executions':0,'performance_measurements':0,'candidate_accepted':False,'source_activated':False,'accepted_main_live_PTX_unchanged':True,'limits':'Source-matched PTX decode masks/ABI/other8 entries and queried resources only. No SASS/dynamic memory, GPU numerical/state, compiled host tagging, actual material/CPU cost, integrated solver or speed proof.'};old.save(H/'report.json',report)
 old.save(O/'complete.json',{'at':old.now(),'report_sha256':old.sha(H/'report.json'),'all_owned_children_terminal':True,'application_kernel_launches':0})
 print(json.dumps({'status':report['status'],'failed_gates':[k for k,v in gates.items()if not v],'registers':[rows['baseline',P['shapes'][0]]['registers'],rows['candidate',P['shapes'][0]]['registers']],'resource_warnings':warnings,'report_sha256':old.sha(H/'report.json')}),flush=True)
'''
ast.parse(execute);(H/'execute.py').write_text(execute,encoding='utf-8',newline='\n')
prior=old.read(R/'runs/E073-resource/protocol.json');command=[str(x).replace('E073-resource','E077-resource')for x in prior['rustc_command']]
deps={p:h for p,h in prior['input_sha256'].items()if 'release\\deps'in p}
for p,h in deps.items():old.pin(p,h)
paths=[Path(__file__),D/'protocol.json',D/'report.json',D/'publication.json',*[p for p in S.iterdir()if p.is_file()],*[p for p in H.iterdir()if p.is_file()],C/'common_e051_live.py',C/'protected-main.json',old.REPO/'tools/postflop_resource_feasibility.py',old.REPO/'tools/postflop_resource_admission.py']
P={'id':'E077-resource','at':old.now(),'status':'FROZEN_PRE_COMPILE_RESOURCE','rustc_command':command,'gpu_uuid':prior['gpu_uuid'],'allocation_proof':prior['allocation_proof'],'expected_entries':prior['expected_entries'],'changed_entries':['up_show'],'shapes':prior['shapes'],'input_sha256':deps|{str(p):old.sha(p)for p in paths},'scope':'One Rust compiler, one no-application-kernel process,4 NVRTC compiles (both sources x compute120/75),2 driver resource sets x10 fixed shapes. No source activation/numerical/speed work.','gates':'Other8 entry bodies exact modulo only compiler-local ordinals, exact ABI27, changed show with >=2 newly emitted low31bit masks. D108 feasibility plus exact local/static/dynamic storage. Static FP counts diagnostic only. No malformed mask/flag or speed inference from counts.','planned_payload':'Same u32 sorted-index arrays, tagged in place in constructor-owned plan. No new array/field/argument/allocation/synchronization or width change; CPU tag loops inside score. Actual material and accuracy evidence remains required.','no_variants_or_rescue':True,'candidate_accepted':False};old.save(H/'protocol.json',P)
pub=[]
for folder in [S,H]:
 for p in folder.iterdir():
  if not p.is_file():continue
  key=folder.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
  with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
  pub.append({'url':'evidence/'+key,'sha256':old.sha(p)})
old.save(H/'pre-resource-publication.json',{'at':old.now(),'protocol_sha256':old.sha(H/'protocol.json'),'HTTP_byte_verified_artifacts':pub,'compiler_or_numerical_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);assert not any(x['id']=='E077'for x in s['experiments']);s['experiments'].append({'id':'E077','at':old.now(),'title':'Materialize only showdown prefixes that are read','kind':'experiment','status':'running','correctness':'Retained read-demand/tag model passes','fixture':'10 compiled resource shapes,2 CUDA architectures','stage':'Compiler/resource prerequisite','reason':'Original ordered scan remains; skip only unused shared prefix stores/offset adds. Bit31 tags reuse existing index arrays, with low31 decode at both hand loads. No new buffer or ABI argument. No GPU numeric or speed result.','accepted':False,'evidence':[{'label':'Frozen source manifest','url':'evidence/E077-source/manifest.json'},{'label':'Frozen CUDA resource prerequisite','url':'evidence/E077-resource/protocol.json'}]});s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E077',stage='E077 selective-prefix compiled-resource checks',activity='D124 found84–86% unused weighted prefix cells in canonical flops; exact original hand indices/demand retained. Compile one selective-materialization prototype before numerical or timing controls. E051 accepted/live gain12.44% unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
print(json.dumps({'protocol_sha256':old.sha(H/'protocol.json'),'CUDA_sha256':old.sha(S/'candidate.cu'),'compiler_or_numerical_executions':0}),flush=True)
