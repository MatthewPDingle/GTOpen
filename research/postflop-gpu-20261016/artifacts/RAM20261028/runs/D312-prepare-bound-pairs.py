"""Freeze aligned adjacent card-bound metadata loads with original scalar fallback."""
import hashlib,json,re,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'))
import common as h
h.custody();h.ar.refuse_active(h.ar.live_status())
assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists()
D=ROOT/'runs/D312-card-bound-pair-scout';D.mkdir(exist_ok=False)
def show_body(text):
    marker='void up_show('
    if marker not in text:return ''
    opening=text.index('{',text.index(marker));i=opening+1;depth=1
    while depth:depth+=(text[i]=='{')-(text[i]=='}');i+=1
    return text[opening:i]
pattern=re.compile(r'uint2|v2\.u32|reinterpret_cast[^\n]*card|(?:unsigned long long|u64)[^\n]*\*[^\n]*card_off',re.I)
history=[];seen=set();name='crates/solver/src/gpu/kernels.cu'
for commit in subprocess.check_output(['git','log','--all','--format=%H','--',name],cwd=h.REPO,text=True).splitlines():
    data=subprocess.check_output(['git','show',commit+':'+name],cwd=h.REPO);digest=hashlib.sha256(data).hexdigest()
    if digest in seen:continue
    seen.add(digest);body=show_body(data.decode())
    history.append({'identity':'git:'+commit,'sha256':digest,'target_markers':[line for line in body.splitlines()if pattern.search(line)]})
for parent in [ROOT/'runs',Path(r'S:\GTOpen-research\postflop-gpu-20261016\runs')]:
    for path in parent.rglob('*.cu'):
        if path.stat().st_size>4*1024**2:continue
        data=path.read_bytes();digest=hashlib.sha256(data).hexdigest()
        if digest in seen:continue
        seen.add(digest);body=show_body(data.decode('utf-8-sig'))
        if body:history.append({'identity':str(path),'sha256':digest,'target_markers':[line for line in body.splitlines()if pattern.search(line)]})
assert not any(x['target_markers']for x in history)
h.save(D/'history.json',{'at':h.now(),'source_records':history,'recognized_prior_form':False,
    'bounded_scope':'AlllocalrefCUDAplusretainedX/S*.cu<=4MiB,uniquehashes,markersinscopedup_showbody. Notexhaustivehelper/patch/remote semanticnoveltyproof.',
    'distinct_from_closed':'E031 copies53offsetsintosharedcache; E099 vectorizesadjacentHANDlearningfields; E121 packsperHANDterminalmetadata. Newformonlypairsadjacentc0/c1u32card-offsetmetadataWORDreads forONEoriginalhand/card, withoutcache/payload/ordering/handpairing. No closedhunkcomposed.',
    'other_lead_triage':'D276originalconvergedcanonicalarityinventoryonly1/2/3;generic5..8controlunswitchcannotaffectthoseexecutedaritycases. No newcache/aritydispatchsourceornativeworkadmitted. Worker8/32,compilelatency,prefixbank,andotherclosedformsnotreopened.'})
# Exact byte coverage and alignment for every valid53-word card row, including unaligned-to8 subview bases.
count=0
for base in [0,4,8,12,0x100000000,0x100000004]:
    for slot in range(4096):
        for card in range(52):
            p=base+4*(slot*53+card);scalar=list(range(p,p+8));vector=list(range(p,p+8))
            assert scalar==vector and(p%8==0 or p%8==4)
            assert(slot*53+card+1)<(slot+1)*53
            count+=1
S=ROOT/'runs/E126-source';S.mkdir(exist_ok=False)
original=(h.REPO/name).read_bytes();assert original.count(b'\n')==original.count(b'\r\n')
before='''            u32 c0 = o_card_off[(u64)slot * 53 + cc[x]];
            u32 c1 = o_card_off[(u64)slot * 53 + cc[x] + 1];'''.replace('\n','\r\n')
after='''            const u32* bounds = o_card_off + (u64)slot * 53 + cc[x];
            u32 c0, c1;
            if (((u64)bounds & 7ull) == 0ull) {
                const uint2 pair = *reinterpret_cast<const uint2*>(bounds);
                c0 = pair.x;
                c1 = pair.y;
            } else {
                c0 = bounds[0];
                c1 = bounds[1];
            }'''.replace('\n','\r\n')
text=original.decode();assert text.count(before)==1;candidate=text.replace(before,after,1);assert candidate.replace(after,before,1)==text
(S/'baseline.cu').write_bytes(original);(S/'candidate.cu').write_bytes(candidate.encode())
h.save(S/'manifest.json',{'id':'E126','at':h.now(),'status':'FROZEN_OFFTREE_BEFORE_COMPILER','baseline_sha256':h.sha(S/'baseline.cu'),'candidate_sha256':h.sha(S/'candidate.cu'),
    'whole_CRLF_source_inverse_exact':True,'before':before,'after':after,
    'target':'up_showonly adjacentcardoffsetc0/c1reads. Actualpointeralignment8 guard, notassumingbase/row/cardparity; unalignedto8pointerretainsoriginal2scalaru32reads.',
    'unchanged':'EveryoriginalFPexpression/operand/reduction/payout/order/rankcondition/cache/prefix/barrier/arrayword/ABI/host/allocation/launch/graph/quality/save remains. Existingboundssourcehasoriginaltwoinitializedu32wordreads, vectorreadsidentical8bytes no extraaddress. No cachehint/precision/typewidth/datapayload change.',
    'risks':'Mixedalignmentwarpsmayexecutevectorandfallbackinstructions, extraaddresspredicate/registers/code/JITcouldregress. Widerloadmaystillscalarize. No instructionthroughput/transaction/speed/no-tradeoff inferencefromvirtualvectorwidth.',
    'failure':'Closefixed8bytealignedcard-boundpairloadwithoriginalscalarfallback; no width/guard/layout/cacheoperator/array/helper/architecture/kernel-scope/flags/source/quality/sample rescue.'})
h.save(D/'report.json',{'id':'D312','at':h.now(),'status':'bounded_history_and_alignment_address_contract_pass',
    'history_sha256':h.sha(D/'history.json'),'alignment_and_same8bytecoverage_checks':count,
    'scope':'Integeraddress/alignmentproofonly; noC++compiler/nativeGPU/float/pointeraliasing/throughputproof. All53wordrows/cards0..51staywithinoriginalrow, originaltwoaddresses unchanged; actualpointerguardhandlesbase0or4mod8.',
    'source_manifest_sha256':h.sha(S/'manifest.json'),
    'API_sources':['https://docs.nvidia.com/cuda/archive/12.8.0/cuda-c-programming-guide/index.html','https://developer.nvidia.com/blog/cuda-pro-tip-increase-performance-with-vectorized-memory-access/'],
    'API_contract':'CUDAuint2size/alignment8. A naturallyaligned8byteloadrequires8bytealignment; alignedvectorcastsaredocumented. Misaligned8readsnotassumedvalid. Documentationisnotactualcompiler/native/speedproof.',
    'new_compilers_GPU_or_solver_samples':0,'all_new_bulk_X_S_readonly_no_T':True})
H=ROOT/'runs/E126-resource';H.mkdir(exist_ok=False)
parent=ROOT/'runs/E125-resource';old=h.read(parent/'protocol.json')
shutil.copyfile(S/'candidate.cu',H/'candidate.cu')
for arch in['compute_120','compute_75']:shutil.copyfile(parent/('baseline-'+arch+'.ptx'),H/('baseline-'+arch+'.ptx'))
(H/'probe.rs').write_bytes((parent/'probe.rs').read_bytes().replace(b'E125_RESOURCE',b'E126_RESOURCE'))
script=ROOT/'runs/E126-resource-execute.py';code=(ROOT/'runs/E125-resource-execute.py').read_text(encoding='utf-8').replace('E125','E126').replace('up_chance','up_show')
before_check="gates[arch+':one_u16_load_instead_of_u32']=narrow(a[name])==0 and narrow(b[name])==1 and wide(b[name])==wide(a[name])-1"
after_check="gates[arch+':aligned_vector_pair_emitted']=len(re.findall(r'\\bld\\.global(?:\\.\\w+)*\\.v2\\.u32\\b',b[name]))>0 and not re.search(r'\\bld\\.global(?:\\.\\w+)*\\.v2\\.u32\\b',a[name])"
assert code.count(before_check)==1;code=code.replace(before_check,after_check).replace('candidate_global_u16_load_sites=narrow(b[name])','candidate_global_vector_pair_load_sites=len(re.findall(r\"\\bld\\.global(?:\\.\\w+)*\\.v2\\.u32\\b\",b[name]))')
code=code.replace('pass_resource_and_emitted_u16_load_prerequisites','pass_resources_vector_guard_and_full_pair_proof_pending').replace('rejected_closed_resource_or_emitted_load_gate','rejected_closed_resource_or_vector_gate')
import ast
ast.parse(code);script.write_bytes(code.encode())
inputs={k:v for k,v in old['input_sha256'].items()if str(ROOT/'reference/accepted-e080-deps')in k}
files=[Path(__file__),script,ROOT/'runs/E125-resource-execute.py',ROOT/'epoch/common.py',D/'history.json',D/'report.json',S/'manifest.json',S/'baseline.cu',S/'candidate.cu']+[p for p in H.iterdir()if p.is_file()]
inputs.update({str(p):h.sha(p)for p in files})
h.save(H/'protocol.json',{'id':'E126-resource','at':h.now(),'status':'FROZEN_PRE_RESOURCE_COMPILER_NATIVE_MODULE_PROCESS','input_sha256':inputs,
    'rustc_command':[x.replace('E125-resource','E126-resource')for x in old['rustc_command']],'GPU_uuid':old['GPU_uuid'],'original_entries':old['original_entries'],'target_entries':['up_show'],'required_free_bytes':16*1024**3,
    'gates':'Both120/75all9headerssame/8untargetedPTXbodiesandactualresourcesexact; up_showemitsguardedv2u32loadwhereoriginalscalarloads. No newlocal/constant/dynamic/stackgrowth,maxthreadloss,positive64/128/256occupancy/defaultfit. Register/static/residencycostwarningsretainedforlatermaterialgates.',
    'hard_mechanism_before_numerical':'Verifyactualpairaddress8alignmentguard/valueprovenance/scalarfallbackandbothc0/c1consumers, entireFP/barrierwork unchanged. ActualtesteddriverCUBINmustemitone64bitreadperalignedpairversusoriginaltwo32bitreads, ratherthanscalarizing; mixedwarpcostnotignored. No cacheoperator/source/widthforcingrescue.',
    'prospective_order':'Resource+PTX/nativepairproof ->fulloriginalunencoded2636+24terminalcorpus2660casesx5widths/full21inputs/physicalCFV/guards ->86ordinaryunits ->fixed3matchedcompletecycles>=1%unrounded+strictfixtureguard. Fullrawengine/canonical/fresh16/broad/material/capacity/holdout/freshoriginalRAMcumulative/tempappbeforeadoption.',
    'failure':'Closefixed8bytealignmentguard/two-wordreadonlycardboundsuint2form,noguard/width/cache/layout/helper/architecture/kernel-subset/flags/source/quality/sample rescue. No productionactivation/allnewbulkX/Sreadonly/noT.'})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);assert not any(x['id']in['D312','E126']for x in status['experiments'])
    status['experiments'] += [{'id':'D312','at':h.now(),'title':'Adjacent card-bound metadata loads: source audit','kind':'diagnostic','status':'complete','accepted':False,'stage':'Alignment and address contract passed','correctness':'source_contract_pass','reason':'Guard the actual pointer for eight-byte alignment; vector and scalar paths read the same two original words. No numerical or speed result yet.','evidence':[]},{'id':'E126','at':h.now(),'title':'Aligned card-bound pair loads','kind':'candidate','status':'staged','accepted':False,'stage':'Frozen compiler, resource and native-load checks','correctness':'not_yet_device_tested','reason':'Pair two adjacent read-only card-bound indices when aligned; preserve scalar fallback and every floating-point expression. Mixed-alignment warps may cost more. Live E080 remains unchanged.','evidence':[]}]
    status.update(updated_at=h.now(),active_experiment='E126',stage='Aligned card-bound pairs: compiler and native-load checks',activity='New source is frozen off tree. Resource, alignment, actual load width and full numerical checks precede timing. No new gain adopted.')
    h.ar.atomic_json(h.ar.STATUS,status)
print(json.dumps({'history_sources':len(history),'source_sha256':h.sha(S/'candidate.cu'),'protocol_sha256':h.sha(H/'protocol.json'),'CPUchecks':count}),flush=True)
