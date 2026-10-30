"""Audit source/history and freeze one exact-width hand-permutation candidate off tree."""
import hashlib,json,re,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'))
import common as h
h.custody();h.ar.refuse_active(h.ar.live_status())
assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists()
D=ROOT/'runs/D311-permutation-width-scout';D.mkdir(exist_ok=False)
paths=['crates/solver/src/gpu/kernels.cu','crates/solver/src/gpu/mod.rs','crates/solver/src/gpu/plan.rs','crates/solver/src/gpu/continuation_capacity.rs']
pattern=re.compile(r'(?:d_hand_perm|hand_perm_flat)\s*:\s*[^\n;]*u16|(?:unsigned short|uint16_t|u16)[^\n,;]*\bhand_perm_p\b',re.I)
history=[]
for path in paths[:3]:
    commits=subprocess.check_output(['git','log','--all','--format=%H','--',path],cwd=h.REPO,text=True).splitlines();seen=set()
    for commit in commits:
        data=subprocess.check_output(['git','show',commit+':'+path],cwd=h.REPO)
        digest=hashlib.sha256(data).hexdigest()
        if digest in seen:continue
        seen.add(digest)
        history.append({'file':path,'commit':commit,'sha256':digest,'hits':[{'line':i+1,'text':line}for i,line in enumerate(data.decode().splitlines())if pattern.search(line)]})
scan=subprocess.run(['rg','-l','-i',pattern.pattern,str(ROOT/'runs'),r'S:\GTOpen-research\postflop-gpu-20261016\runs','-g','*.rs','-g','*.cu'],capture_output=True,text=True)
assert scan.returncode in[0,1]and not scan.stderr
assert not any(row['hits']for row in history)and not scan.stdout.strip(),scan.stdout
h.save(D/'history.json',{'at':h.now(),'alllocalref_unique_records':history,'retained_X_S_rs_cu_literal_matches':scan.stdout.splitlines(),
    'scope':'All localref unique GPUkernel/mod/plan revisions plusretainedX/Srs/cu16bit handpermtyped-declaration markers. Boundednotuniversalsemantic/remote noveltyproof.',
    'distinct_from_closed':'E070 narrows player/aritymetadata; E115/E121 packnode rows; E099 pairsadjacenthandmemory. ThisleadkeepsonlyexistingSpot.hand_perm nativeu16 tableelementwidththroughCPUflatten/upload/chancekernel. No node/hand/order/scope/storage/quality change orclosedhunk composed.'})
game=(h.REPO/'crates/solver/src/game.rs').read_text(encoding='utf-8')
assert 'pub hand_perm: [Vec<Vec<u16>>; 2],'in game
assert all(int.from_bytes(i.to_bytes(2,'little'),'little')==i for i in range(65536))
S=ROOT/'runs/E125-source';S.mkdir(exist_ok=False)
edits={
paths[0]:[('const u32* __restrict__ hand_perm_p,','const unsigned short* __restrict__ hand_perm_p,')],
paths[1]:[('d_hand_perm: [CudaSlice<u32>; 2],','d_hand_perm: [CudaSlice<u16>; 2],'),('let up32 = |v: &Vec<u32>| stream.clone_htod(v).map_err(e);','let up16 = |v: &Vec<u16>| stream.clone_htod(v).map_err(e);\n        let up32 = |v: &Vec<u32>| stream.clone_htod(v).map_err(e);'),('d_hand_perm: [up32(&plan.hand_perm_flat[0])?, up32(&plan.hand_perm_flat[1])?],','d_hand_perm: [up16(&plan.hand_perm_flat[0])?, up16(&plan.hand_perm_flat[1])?],')],
paths[2]:[('pub hand_perm_flat: [Vec<u32>; 2],','pub hand_perm_flat: [Vec<u16>; 2],'),('hand_perm_flat[p].extend(tbl.iter().map(|&i| i as u32));','hand_perm_flat[p].extend_from_slice(tbl);')],
paths[3]:[('arr!(d_hand_perm:u32,','arr!(d_hand_perm:u16,')],
}
owned={}
for path,pairs in edits.items():
    original=(h.REPO/path).read_bytes();nl='\r\n'if path.endswith('.cu')else'\n'
    assert original.count(b'\r\n')==(original.count(b'\n')if path.endswith('.cu')else 0)
    text=original.decode();changed=text
    for before,after in pairs:
        before,after=before.replace('\n',nl),after.replace('\n',nl)
        assert changed.count(before)==1,(path,before)
        changed=changed.replace(before,after,1)
    reverse=changed
    for before,after in reversed(pairs):reverse=reverse.replace(after.replace('\n',nl),before.replace('\n',nl),1)
    assert reverse==text
    tag=Path(path).name
    base=S/('baseline-'+tag);candidate=S/('candidate-'+tag)
    base.write_bytes(original);candidate.write_bytes(changed.encode())
    owned[path]={'base':str(base),'candidate':str(candidate),'base_sha256':h.sha(base),'candidate_sha256':h.sha(candidate)}
h.save(S/'manifest.json',{'id':'E125','at':h.now(),'status':'FROZEN_OFFTREE_BEFORE_COMPILER','owned':owned,
    'all4inverse_exact_original_line_endings_preserved':True,'target_entries':['up_chance'],
    'concept':'Retain originalSpot.hand_perm u16throughGpuPlanflatten,privateCudaSliceupload,and unsignedshortloadinup_chance. Samevalues/order/indexarithmetic/castint,onescalarload perexistingnonidentityhand; originalk0identity skipsload. No FPexpression/reduction/order/launch/graph/schedule/save/quality changes.',
    'capacity':'ExplicitplanandGPUhandpermelementbytes4to2; sameelementcounts. GPUactualpayloadaccounting d_hand_perm typeupdatedu16; genericplanbytesusesactualT. Allotherpayloadandconservativebudgetformulaunchanged. Actualdriver/hostpeak/capacityandgraph/broadqualification stillrequired.',
    'source_domain':'AuthoritativeSpot.hand_perm [Vec<Vec<u16>>;2]; oldflatten onlywidenedthesewords. All65536u16words exactwidening/rangecontract; no sourcevaluecanbetruncated. FullactualCPUplanandGPUrawcontrolsnotyetperformed.',
    'risks':'Existingtablesmayalreadyfitincache;16bitload/scaling maycostasmuch; CPUflatcapacities/driverallocation granularity/publicRustfieldtype/instrumentedobservertypesandstoredcapacityneedfullvalidation. No speed/adoption/headroom claim.',
    'failure':'Closefixedu16handpermtable sourceform after genuinegatefailure; no width/otherfield/packing/helper/layout/scope/architecture/flag/source/quality/sample rescue.'})
h.save(D/'report.json',{'id':'D311','at':h.now(),'status':'bounded_history_and_existing_u16_domain_contract_pass',
    'history_sha256':h.sha(D/'history.json'),'accepted_game_rs_sha256':h.sha(h.REPO/'crates/solver/src/game.rs'),
    'all65536_u16_representations_exact':True,'candidate_source_manifest_sha256':h.sha(S/'manifest.json'),
    'new_native_compiler_GPU_or_solver_samples':0,'all_new_bulk_X_S_readonly_no_T':True,'next_candidate':'E125'})
H=ROOT/'runs/E125-resource';H.mkdir(exist_ok=False)
shutil.copyfile(S/'candidate-kernels.cu',H/'candidate.cu')
parent=ROOT/'runs/E124-resource'
for arch in ['compute_120','compute_75']:shutil.copyfile(parent/('baseline-'+arch+'.ptx'),H/('baseline-'+arch+'.ptx'))
(H/'probe.rs').write_bytes((parent/'probe.rs').read_bytes().replace(b'E124_RESOURCE',b'E125_RESOURCE'))
old=h.read(parent/'protocol.json')
inputs={k:v for k,v in old['input_sha256'].items()if str(ROOT/'reference/accepted-e080-deps')in k}
files=[Path(__file__),ROOT/'runs/E125-resource-execute.py',ROOT/'epoch/common.py',D/'history.json',D/'report.json',S/'manifest.json',h.REPO/'crates/solver/src/game.rs']
files += [Path(v[k])for v in owned.values()for k in['base','candidate']]
files += [x for x in H.iterdir()if x.is_file()]
inputs.update({str(p):h.sha(p)for p in files})
h.save(H/'protocol.json',{'id':'E125-resource','at':h.now(),'status':'FROZEN_PRE_RESOURCE_COMPILER_NATIVE_PROCESS',
    'input_sha256':inputs,'rustc_command':[x.replace('E124-resource','E125-resource')for x in old['rustc_command']],
    'GPU_uuid':old['GPU_uuid'],'original_entries':old['original_entries'],'target_entries':['up_chance'],'required_free_bytes':16*1024**3,
    'gates':'2architectures120/75all9headerssame;onlyup_chanceemittedbodychanges,scalaru16handpermreadmustreplaceoriginalu32read;all8untargetedbodiesandactualresourcesexact. No newlocal/constant/dynamic/stackgrowth,maxthreadloss;64/128/256occupancypositive/defaultlimitsfit;reg/static/residencycostswarningsforlatermaterialgates.',
    'prospective_order':'Resource+emittedmechanism -> fulloriginalunencodedchancecorpus withtypedactualu16GPUinputandfullphysicalCFV/allinputs/guards ->86ordinaryunits ->3matchedpairsinitialcompletecycle>=1%unrounded+strictfixtureguard. Fullrawengine/canonical/fresh16/broad/F32/save/resume/locks/symmetric/paged/stored/capacity/material/holdout/freshoriginalRAMcumulative/actualtempapp beforeadoption. No omittedfields/timingpool/exclusions/extensions.',
    'source_activated':False,'performance_claim':False,'failure':'Closefixedu16handpermtablesourceform,nowidth/otherfield/packing/helper/layout/scope/architecture/flags/source/quality/sample rescue.'})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);assert not any(x['id']in['D311','E125']for x in status['experiments'])
    status['experiments'] += [{'id':'D311','at':h.now(),'title':'Preserve original 16-bit hand-permutation width','kind':'diagnostic','status':'complete','accepted':False,'stage':'Existingu16domain and boundedhistory passed','correctness':'source_contract_only','reason':'OriginalSpot tablesalreadyu16; eliminatewidening only. Full65536representation check, boundedallref/retainedhistory. No GPUaccuracy/speedclaim.','evidence':[]},{'id':'E125','at':h.now(),'title':'16-bit GPU hand-permutation table','kind':'candidate','status':'staged','accepted':False,'stage':'Frozen resource and emitted-load gate','correctness':'not_yet_device_tested','reason':'Onechancekernelreadonlytableelementu32tou16; originalu16sourcevalues/order/math/qualityretained. Offtreesourceonly, liveE080unchanged.','evidence':[]}]
    status.update(updated_at=h.now(),active_experiment='E125',stage='16-bit hand-permutation table: resource gate',activity='D310copyrouteclosed. E125distinctu16sourcepreservationcandidatefrozenofftree; no newgain. E080/GPU/compressed/16live; lastB377/nextB378.')
    h.ar.atomic_json(h.ar.STATUS,status)
print(json.dumps({'history_records':len(history),'source_sha256':h.sha(S/'candidate-kernels.cu'),'protocol_sha256':h.sha(H/'protocol.json')}),flush=True)
