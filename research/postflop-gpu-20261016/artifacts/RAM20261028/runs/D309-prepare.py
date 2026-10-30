"""Freeze a transport prerequisite, not a solver optimization or timing trial."""
import hashlib, json, re, shutil, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'))
import common as h
H = ROOT/'runs/D309-interleaved-learning-scout'
D = ROOT/'runs/D310-interleaved-copy-control'
h.custody()
h.ar.refuse_active(h.ar.live_status())
assert not (ROOT/'gpu-run.lock').exists() and not (ROOT/'epoch-sequence.lock').exists()
H.mkdir(exist_ok=False)
D.mkdir(exist_ok=False)
names=['crates/solver/src/gpu/mod.rs','crates/solver/src/gpu/kernels.cu','crates/solver/src/gpu/arena.rs']
pattern=re.compile(r'CUDA_MEMCPY2D|cuMemcpy2D|memcpy_2d|interleav.{0,50}(regret|strat)|(regret|strat).{0,50}interleav',re.I)
history=[]
for name in names[:2]:
    revisions=subprocess.check_output(['git','log','--all','--format=%H','--',name],cwd=h.REPO,text=True).splitlines()
    seen=set()
    for commit in revisions:
        blob=subprocess.check_output(['git','show',f'{commit}:{name}'],cwd=h.REPO)
        digest=hashlib.sha256(blob).hexdigest()
        if digest in seen:continue
        seen.add(digest)
        lines=blob.decode('utf-8').splitlines()
        hits=[{'line':i+1,'text':line}for i,line in enumerate(lines)if pattern.search(line)]
        history.append({'commit':commit,'file':name,'sha256':digest,'literal_hits':hits})
roots=[ROOT/'runs',Path(r'S:\GTOpen-research\postflop-gpu-20261016\runs')]
cmd=['rg','-l','-i',pattern.pattern,*map(str,roots),'-g','*.rs','-g','*.cu']
run=subprocess.run(cmd,capture_output=True,text=True)
assert run.returncode in [0,1] and not run.stderr
hits=[]
for value in run.stdout.splitlines():
    path=Path(value)
    # Exclude this newly authored copy-control source; all historical hits remain.
    if path==ROOT/'runs/D310-copy-control.rs':continue
    lines=path.read_text(encoding='utf-8-sig').splitlines()
    hits.append({'path':str(path),'sha256':h.sha(path),'hits':[{'line':i+1,'text':line}for i,line in enumerate(lines)if pattern.search(line)]})
h.save(H/'history.json',{'at':h.now(),'local_allref_unique_source_records':history,'retained_literal_hits':hits,
    'scope':'All local-ref unique gpu/mod.rs and kernels.cu plus retained X/S rs/cu literal interleaving or2DAPI markers; bounded search, not exhaustive semantic or remote novelty proof.',
    'classification':'Retained historical 2DAPI hits are vendored cudarc binding snapshots; no recognized regret/strategy interleaving implementation. New D310 probe is excluded explicitly.',
    'distinct_from_closed':'E099 pairs adjacent hand memory, E046 interleaves immutable node metadata, E010/E087/E092 alter pinned or quantization packets. Proposed per-playerR/S interleaving keeps a single hand lane, FPmath, FP32payload, CPUcontiguousfields and existingcachedpinnedmaxL. No closed hunk composed.'})
assert not any(row['literal_hits']for row in history)
assert all('cudarc__src__driver__sys__mod.rs' in row['path']for row in hits)
checks=0
for n in range(1,1026):
    addresses=[8*i+4*f for i in range(n)for f in[0,1]]
    assert len(set(addresses))==2*n and sorted(addresses)==list(range(0,8*n,4))
    for f in[0,1]:
        assert [8*i+4*f for i in range(n)]==[4*(2*i+f)for i in range(n)]
    checks+=2*n
fixtures=h.read(ROOT/'runs/D280-pinned-registration-lifecycle/fixtures.json')
cases=[{'fixture':f'boundary-{n}','words':n}for n in[1,2,17,1023,1024,1025]]+[{'fixture':v['fixture'],'words':v['words']}for v in fixtures]
raw_bytes=sum((12*c['words']+768)*4+10*64 for c in cases)
assert raw_bytes<16*1024**3
h.save(H/'report.json',{'id':'D309','at':h.now(),'status':'source_history_and_CPU_address_contract_pass_transport_prerequisite_only',
    'history_sha256':h.sha(H/'history.json'),'CPU_unique_address_checks':checks,
    'address_contract':'For any n>0,fieldf in{0,1}, rowi address=8*i+4*f, exactly original logical fieldi at physicalu32[2*i+f]; twofieldimages biject2*n words withsamepayloadbytes. Checkedallsmalln1..1025; checkedusize arithmetic required before descriptor construction.',
    'copy_route':'cuMemcpy2DAsync_v2 width4/heightL/pitcheshost4,device8/deviceXfield*4, sameownedstream, cachedcuMemHostAlloc flags0 max(L,128diagnosticminimum)u32words. Onecachedpinnedallocation perfixture, explicit drainbeforeCPUreuse/free. No extra pinnedbuffer/gather/scratch/kernel/FPprocessing.',
    'descriptor_ABI':'ActualcudarcCUDA_MEMCPY2D_v2 usesusize fields. Structliteral populatesvalidHOST/DEVICEenums; nozeroedRustenum. Native128byte/align8/11offset assertions before copies. Documentation inline legacyunsignedint example is not used asABI.',
    'API_url':'https://docs.nvidia.com/cuda/archive/12.9.0/cuda-driver-api/group__CUDA__MEM.html',
    'fixtures_source_sha256':h.sha(ROOT/'runs/D280-pinned-registration-lifecycle/fixtures.json'),
    'cases':cases,'raw_reserved_bytes':raw_bytes,'all_new_bulk_X_S_readonly_no_T':True,
    'new_native_or_GPU_or_solver_samples':0,'full_solver_candidate_admitted':False,'next_unused_candidate':'E125',
    'open_costs':'Copyengine rowcost, kernelcoalescing/readonlyfieldtransactionfootprint, resource/ABI/driverallocation/capacity/hostwrapper/JIT/module effects unproven. Layout could regress. No speed/headroom/adoption claim.',
    'later_requirements':'Full sourceownership/ABI/physicalrawallwords/CPUstoragecodec/F32/locks/query/save/resume/symmetric/paged/stored/fallback audit, ordinaryunits then3pairfullcycle/fresh16/broad/material/capacity/holdout/freshoriginalcumulative/realtempapp. No closedform rescue.'})
for file in ['D310-copy-control.rs','D310-read-copy-control.py']:
    shutil.copyfile(ROOT/'runs'/file,D/('probe.rs'if file.endswith('.rs')else'reader.py'))
old=h.read(ROOT/'runs/D280-pinned-registration-lifecycle/protocol.json')
command=old['rustc_command'].copy()
command[1]=str(D/'probe.rs');command[-1]=str(D/'probe.exe')
inputs={k:v for k,v in old['input_sha256'].items()if str(ROOT/'reference/accepted-e080-deps') in k}
paths=[Path(__file__),ROOT/'runs/D310-copy-control.rs',ROOT/'runs/D310-read-copy-control.py',ROOT/'runs/D310-execute.py',ROOT/'epoch/common.py',D/'probe.rs',D/'reader.py',H/'history.json',H/'report.json',ROOT/'runs/D280-pinned-registration-lifecycle/fixtures.json',ROOT/'runs/D280-pinned-registration-lifecycle/protocol.json',Path(r'C:\Users\there\.cargo\registry\src\index.crates.io-1949cf8c6b5b557f\cudarc-0.19.7\src\driver\sys\mod.rs'),Path(r'C:\Users\there\.cargo\registry\src\index.crates.io-1949cf8c6b5b557f\cudarc-0.19.7\src\driver\safe\core.rs')]
for name in names:paths.append(h.REPO/name)
inputs.update({str(p):h.sha(p)for p in paths})
for p,v in inputs.items():h.pin(p,v)
h.save(D/'protocol.json',{'id':'D310','at':h.now(),'status':'frozen_before_any_new_compiler_or_native_trial',
    'input_sha256':inputs,'rustc_command':command,'cases':cases,'native_rounds':1,
    'controls':'Oneprocess/onecontext/oneserializedstream, onecachedcuMemHostAllocflags0max(L,128)buffer percase; original twocontiguous owners vs one2L interleaved owner. Sameu32patternsource, all13specialIEEEwordpayloads included, no FPmath. Guardsbaseline2*(L+128),interleaved2L+128; differingdiagnosticguardoverheadexplicit. H2Dfielduploads/directvs2D and poisonedD2Hfieldoutputs. Wholephysicalbefore+after and everylogicaloutput retained/independentlychecked.',
    'raw_header':'64bytes littleendian <8sQ6I3Q: magicD310RAW1,wordcount,kind(0hostout/1basephysical/2interleavedphysical),field,fixtureindex,seed,stage(0before/1out/2after),reserved0,payloadbytes,guardwords64physicalor0host,logicalL; thenallrawu32.',
    'raw_reservation_bytes':raw_bytes,'raw_cap_bytes':16*1024**3,'peak_reservation_bytes':32*1024**3,'required_free_bytes':96*1024**3,
    'minimum_available_RAM_bytes':16*1024**3,'minimum_free_GPU_over_explicit_payload_bytes':1024**3,
    'maximum_native_seconds':1200,'maximum_reader_seconds':1200,
    'pre_native_gates':'Sourcepins/custody/liveidle/GPUUUID+drivercurrentbaseline/Xfree/RAMfree, descriptoractualABI/bounds/invalidgeometryguard tests, maxpitch>=8, freedevice>=4L+384words+1GiB.',
    'numeric_gate':'All90headers/exactlengths/allphysicalbeforeafterwords+guards/allpoisonedlogicaloutputs exact expectedpattern; independentcomplete reader with4corruptionfixtures. No sampledwordorfloat-equality shortcuts.',
    'timing_interpretation':'Individual copy+explicitstreamwait times only, one diagnosticround not pairedsolver speed orcapacity/CPU/materialqualification. Physicalobserver/read/poison/verify/dump nottimed. Do notaccept1%gain ordiscardcorrectnessbasedon these clocks. No component speed threshold; complete solvercycle decides later.',
    'failure_policy':'API/descriptor/word/guardfailure closesfixed width4pitch8 host-device route; preserve original evidence, no width/pitch/chunk/helper/kernel/source/quality/sample rescue. Enqueueerror drainsbeforepanic; syncerror abortsownedprocess ratherthanfreepossiblyinflightpinnedmemory. Fixedtimeout preservepartial/unqualified, no restart.',
    'scope':'Drivercopywork real; no applicationCUDAkernels/NVRTC/CFR/numericalsolver/primarybaseline/acceptedsourceactivation, noTaccess/Swrite/hardwarecounters/settings.'})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS)
    assert not any(e['id']in['D309','D310']for e in status['experiments'])
    for identity,stage,reason in [('D309','Source/history/address contract passed','Boundedhistoryno recognizedR/Sinterleavingform; CPUaddressbijection checked. NotGPUaccuracy/speed.'),('D310','Frozen transport control; native pending','Checkcachedpinned2Dstridedtransfer at9sizes incl3actualbenchmarkarenaextents. No fullsolvercandidate orspeedclaim.')]:
        status['experiments'].append({'id':identity,'at':h.now(),'status':'running','accepted':False,'stage':stage,'reason':reason,'correctness':'pending_transport_control','evidence':[]})
    status.update(updated_at=h.now(),state='running',goal_status='active',active_experiment='D310',stage='Interleaved learning layout: exact transport prerequisite',activity='E080remainsqualified/live. Copygeometryandallrawbitsexactness first; noE125solvercandidate/primarytiming yet. CurrentRAMreference10456.4109ms remains separate.')
    h.ar.atomic_json(h.ar.STATUS,status)
print(json.dumps({'protocol_sha256':h.sha(D/'protocol.json'),'history_records':len(history),'retained_hits':len(hits),'raw_bytes':raw_bytes,'cases':len(cases)}),flush=True)
