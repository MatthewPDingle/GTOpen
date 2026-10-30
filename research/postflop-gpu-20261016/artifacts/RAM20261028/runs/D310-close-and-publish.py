"""Preserve a passed transport control, decline prototype on observed copy cost, publish evidence."""
import json,shutil,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'))
import common as h
S=ROOT/'runs/D309-interleaved-learning-scout'
H=ROOT/'runs/D310-interleaved-copy-control'
O=H/'execution-v2'
h.custody();h.ar.refuse_active(h.ar.live_status())
assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists()
for name in ['protocol.json','protocol-v2.json','reader-protocol-v3.json','launch-continuation.json']:
    for path,digest in h.read(H/name)['input_sha256'].items():h.pin(path,digest)
N,R=h.read(H/'native-report.json'),h.read(H/'reader-report.json')
assert len(R['files'])==90 and len(R['cases'])==9 and len(R['negative_reader_fixtures_rejected'])==4
assert R['full_physical_and_output_words_checked']==3551107092
assert all(x['all_physical_before_after_and_logical_outputs_exact']for x in R['cases'])
markers=N['markers'];assert [len(markers[k])for k in ['D310_ABI','D310_COPY','D310_CASE_COMPLETE','D310_COMPLETE']]==[1,9,9,1]
end=markers['D310_COMPLETE'][0]
assert end['raw_words_including_guards']==R['full_physical_and_output_words_checked']
assert end['GPU_memory_before']==end['GPU_memory_after_owned_ranges_dropped']
assert end['all_owned_ranges_and_context_dropped']and end['cached_pinned_allocations']==end['cached_pinned_frees']==9
assert end['CUDA_application_kernels']==end['NVRTC_compiles']==end['CFR_iterations']==0
# Arithmetic summaries of one component round only, not a solver score or a prospective threshold.
copies=[]
for row in markers['D310_COPY']:
    up,down=row['upload_copy_and_sync_ns'],row['download_copy_and_sync_ns']
    record={'fixture':row['fixture'],'words':row['words'],'contiguous_upload_twofields_ms':sum(up[:2])/1e6,'interleaved_upload_twofields_ms':sum(up[2:])/1e6,'contiguous_download_twofields_ms':sum(down[:2])/1e6,'interleaved_download_twofields_ms':sum(down[2:])/1e6,
        'single_round_D2H_ratio':sum(down[2:])/sum(down[:2]),'copy_and_sync_only':True,'not_complete_cycle_or_statistical_speed_test':True}
    copies.append(record)
assert next(x for x in copies if x['fixture']=='rainbow')['single_round_D2H_ratio']>40
assert next(x for x in copies if x['fixture']=='two-tone')['single_round_D2H_ratio']>40
receipts=[]
for path in H.rglob('*.exit.json'):
    receipt=h.read(path);assert receipt['returncode']in[0,1,None]
    receipts.append({'path':str(path),'sha256':h.sha(path),'returncode':receipt['returncode'],'error':receipt['error'],'cleanup':receipt['cleanup']})
assert len(receipts)==6
assert sorted(x['returncode']for x in receipts if x['returncode']is not None)==[0,0,0,1,1]
assert h.read(H/'execution/rustc.exit.json')['returncode']==1
assert h.read(O/'rustc.exit.json')['returncode']==0
assert h.read(O/'native.exit.json')['returncode']is None and 'FileNotFoundError'in h.read(O/'native.exit.json')['error']
assert h.read(O/'native-v3.exit.json')['returncode']==0
assert h.read(O/'reader.exit.json')['returncode']==1
assert h.read(O/'reader-v3.exit.json')['returncode']==0
assert not(H/'execution/native.invocation.json').exists()
assert sum(x['bytes']for x in R['files'])==h.read(H/'protocol.json')['raw_reservation_bytes']==14204434128
h.save(H/'report.json',{'id':'D310','at':h.now(),'status':'EXACT_TRANSPORT_PASS_DECLINE_INTERLEAVED_SOLVER_PROTOTYPE_ON_OBSERVED_COPY_COST',
    'D309_report_sha256':h.sha(S/'report.json'),'source_protocol_sha256':h.sha(H/'protocol.json'),'effective_protocol_sha256':h.sha(H/'protocol-v2.json'),
    'native_report_sha256':h.sha(H/'native-report.json'),'reader_report_sha256':h.sha(H/'reader-report.json'),
    'native_transport_pass':True,'independent_complete_raw_pass':True,'raw_files':90,'raw_bytes':14204434128,'all_physical_and_output_words_checked':3551107092,
    'negative_corruption_controls_rejected':R['negative_reader_fixtures_rejected'],'single_component_round_diagnostics':copies,
    'decision':'Do not build E125 from thislead. Fixedwidth4/pitch8 interleavedR/S copyroute is bitexact at9sizes but observedlargearenaD2H cost exceeds40x contiguous inthisoneround. That isstrongnegativeengineeringevidence foraproposedlayoutrequiringthese fielddownloads. Conservativeprototypeadmissiondecision, notfailedprospectiveperformancegate, statisticalregression, completecyclespeedclaim orproofthatallinterleavingdesignsmustlose. No componentgainthreshold inventedaftertest.',
    'scope':'Rawtransportonly; noCFRmath/GPUapplicationkernel/solver/ordinary/convergence/primarytiming/fresh16/broad/material/capacity/holdout/cumulative/appvalidation performed. Originalacceptedsolver arithmetic/storage/CPUcodec untouched. Logicalperarm2LFP32payloadsame, small128wordpinneddiagnosticminimumanddifferentphysicalguards explicit; no productioncapacity/memoryneutrality claim.',
    'closed_form':'ClosefixedR/Sinterleaving withwidth4pitch8 host-devicecopyroute. No pitch/width/chunk/gather/helper/kernel/storage/guard/source/quality/round rescue; preserve negativecost andfullsuccessfulrawexactness evidence.',
    'mechanical_repairs':['Firstcompilerexit1:twohelpers&CudaStream receivers require&Arc<CudaStream>; only2signatureschanged inretainedv2. No nativehadstarted.','v2compilerexit0; wrapperattemptedobsoleteprobe.exeratherthanprobe-v2.exe, PopenfailedwithnoPID. Existingcompiledbinarylaunchedcorrectpathonce, nocompilerrepeat.','CopiedreaderROOTparents1 pointedrunsinstead ofepochroot; readerexit1 atcommonimportbeforeanyrawread. Additivev3parents2/protocolpathrepair, originalreader/receipt preserved; fullnativeoutputreused, no native/compilerrepeat.'],
    'owned_receipts':receipts,'all_launched_owned_processes_terminal':True,'launched_processes':5,'successful_processes':3,'failed_processes':2,'never_started_launches':1,
    'new_compiler_invocations':2,'actual_native_copy_processes':1,'successful_complete_raw_readers':1,'application_kernel_launches':0,'NVRTC_compiles':0,'CFR_or_solver_speed_runs':0,
    'GPU_free_bytes_before_after_equal_in_owned_control':True,'accepted_main_live_protected_PTX_D304_HTML_unchanged':True,
    'candidate_adopted':False,'next_unused_candidate':'E125','last_primary_baseline':'B377','next_unused_primary_baseline':'B378',
    'RAM20261028_reference_sum_medians_ms':10456.4109,'qualified_live_config':'E080/GPU/compressed/Rayon16/defaultaffinity',
    'all_new_bulk_X_S_readonly_no_T':True,'goal_active':True})
files=[S/'history.json',S/'report.json']
files += [H/name for name in ['protocol.json','protocol-v2.json','reader-protocol-v3.json','launch-continuation.json','probe.rs','probe-v2.rs','reader.py','reader-v2.py','reader-v3.py','native-report.json','reader-report.json','report.json']]
files += list((H/'execution').glob('*.*'))
files += [x for x in O.glob('*.*')if x.is_file()]
published=[]
for path in files:
    assert path.suffix.lower()not in['.bin','.exe']
    relative=path.relative_to(ROOT/'runs')
    destination=h.ar.DASHBOARD/'evidence'/relative;destination.parent.mkdir(parents=True,exist_ok=True)
    if destination.exists():assert destination.read_bytes()==path.read_bytes()
    else:shutil.copyfile(path,destination)
    with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+relative.as_posix(),timeout=20)as response:assert response.read()==path.read_bytes()
    published.append({'url':relative.as_posix(),'sha256':h.sha(path)})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS)
    for identity in ['D309','D310']:
        row=next(e for e in status['experiments']if e['id']==identity)
        row.update(at=h.now(),accepted=False,status='rejected'if identity=='D310'else'complete',
            stage='Transportexact; prototype declined on observed copycost'if identity=='D310'else'Source/history/address contract complete',
            correctness='all90whole_raw_transport_files_exact'if identity=='D310'else'CPU_address_contract_only',
            reason='9sizes bitexact,3.551billionrawphysical/outputwords+guards. Largearena stridedD2H >40x contiguous in1diagnosticround; declinefixedroute beforeCFRprototype. Notfullcycle/statisticalspeedtest. No newgain/E125source.',
            evidence=[{'label':'Scout and contract'if identity=='D309'else'Exactness, measured copycost and decision','url':f'evidence/{S.name if identity=="D309"else H.name}/report.json'}])
    status.update(updated_at=h.now(),state='running',goal_status='active',active_experiment='D310',stage='Interleaved learning route closed; distinct performance search continues',activity='All90rawcopyimages exact; observedstridedreadback>40xcontiguous inlargecases. No solverprototype/newgain. E080/GPU/compressed/16 qualified/live; RAMreference10.4564109s; nextE125/B378unused.')
    h.ar.atomic_json(h.ar.STATUS,status)
ledger=h.REPO/'research/postflop-gpu-20261016/experiments.md';old=ledger.read_bytes()
assert b'\n## D309-D310 interleaved learning transport control'not in old
assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=h.REPO,text=True).strip()
entry=f'''

## D309-D310 interleaved learning transport control - exact, prototype declined on copy cost

PriorD308nativearithmeticclosure/acceptedmainlive/PTX/D304HTML/idle/locks/currentledgerHEAD revalidated readonly; no create-onlyauditorrepeat. UserXonly/Sreadonly/noT/fullaccess maintained. LastB377/nextB378,E080/GPU/compressed/Rayon16/defaultaffinitylive. Distinctnewlead interleavesregretandstrategyFP32wordsperplayer,notE099adjacenthands/E046nodeAoS/E010pinnedpackets/E087window/E092quantization. No closedhunkcomposed. D309alllocalref43uniqueCUDA/Rustsourcehashrecords +retainedX/Srs/cu literal2D/interleavingsearch finds2vendoredcudarcAPIbindingsnapshots,norecognizedR/Simplementation; boundednotuniversalnoveltyclaim. Exhaustivesmalladdressbijection1..1025 pluscheckedlargegeometry,logical2Lwordsunchanged. No productionhost/kernel/storagecandidatecreated(E125unused).

ProspectiveD310protocol{h.sha(H/'protocol.json')}:1nativecopyround/9sizes1,2,17,1023,1024,1025,185172163rainbow,110745280two-tone,4480river. ActualcanonicalmaxarenageometryretainedD280fixturemanifestpinned. CachedcuMemHostAllocflags0singlemax(L,128diagnosticminimum)buffer,ordinarycontiguous2ownersvsoneinterleaved2Lowner; 64wordprefix/suffixeachactualdeviceowner(diagnosticguardoverheadexplicit). cuMemcpy2DAsync_v2width4heightLpitches4/8andfieldoffset0/4,actualWin64cudarc128bytealign8descriptorABI11offsetschecked,validHOST/DEVICEenumstructliteral,invalidgeometryrejectedbeforeCUDA,maxpitch/freeGPUchecked. Onecontext/streamexplicitdrainbeforeCPUreuse/free,enqueueerrorfirstdrains/syncerrorabortratherthanfreeinflight. NoGPUapplicationkernels/NVRTC/CFR; drivercopyworkreal. Singlecopy+syncclocksnotfullcycle/statisticalspeed/CPU/material/capacityqualifier; nocomponentgainthreshold.

Nativeall9casesexactu32fieldH2D/D2H/physicalbefore+after inclspecialIEEEpayloads,complementpoison,wholeguards. 90rawfiles{14204434128}bytes,{3551107092}physical/outputwords preservedX,independentcompleteNumPyreaderallheaders/lengths/wordsexact and4payload/leftguard/rightguard/swappedfieldcorruptioncontrolsreject. Native9cachedpinnedalloc/free+27deviceownerdrops,ownedGPUfreebefore/afterexact32496418816bytes; notproductioncapacityneutralityproof. Fullrawmanifest{h.sha(H/'reader-report.json')},source/native/reports/logsretained; {len(published)}nonbulkHTTPartifactsbyteverified.

Observed1roundrainbowtwocontiguousfieldD2H52.1745msvsinterleaved2212.2289ms; two-tone31.7055msvs1313.2483ms; river0.0734msvs0.1366ms. Largearena>40x coststrongnegativeengineeringevidence forlayoutrequiringfielddownloads; conservativeDECLINEprototypeadmissionbeforeE125CFRsource. Nofailedprospectiveperformancegateclaimed,nopairmedian/1%/statistical/fullcyclescore,notproofallinterleavingdesignsmustlose. ClosefixedR/Sinterleavedwidth4pitch8route; no pitch/width/chunk/gather/helper/kernel/storage/guard/source/quality/sample rescue. Noproductionaccuracy/gain/adoptionclaimed. Full1%/strictfixture/fresh16/rawengine/canonical/broad/material/capacity/holdout/freshoriginalcumulative/appgatesuntouched.

Mechanicaltoolchainrecordpreserved: originalcompilerexit1(twohelper&CudaStreamreceiversrequire&Arc),only2signatureschangedv2; v2compilerexit0wrapperattemptedobsoleteprobe.exe,nativePopenfailedwithnoPID,correctalreadybuiltprobe-v2.exe launchedonce/norecompile. CopiedreaderrelativeROOTparents1wrong,exit1atcommonimportbeforerawreads; additivev3parents2/protocolpathfixretainsallwords/controls/gates,reusescompletednativeoutputs. Sixreceipts:5actualprocessesterminal(3exit0/2exit1),1launchneverstarted; nohiddenallzeroassertion,nocompletednative/sample repeats. Report{h.sha(H/'report.json')}. Accepted/main/live/protectedPTX/D304HTMLexact,serveridle,locksabsent,allbulkX/Sreadonly/noT. CurrentRAMreference10456.4109msunchangedandseparatefromhistoricalgain. Nomaincommit/push/prune; appendprefixbyteexact,localledger-onlycommit. Goalactive,distinctsearchcontinues.
'''
ledger.write_bytes(old+entry.encode());assert ledger.read_bytes()[:len(old)]==old
h.custody()
subprocess.run(['git','add','--','research/postflop-gpu-20261016/experiments.md'],cwd=h.REPO,check=True)
assert subprocess.check_output(['git','diff','--cached','--name-only'],cwd=h.REPO,text=True).splitlines()==['research/postflop-gpu-20261016/experiments.md']
subprocess.run(['git','-c','gc.auto=0','commit','-m','research: preserve exact interleaved transfer controls and decline costly route'],cwd=h.REPO,check=True)
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=h.REPO,text=True).strip()
h.save(H/'publication.json',{'at':h.now(),'local_commit':head,'HTTP_artifacts':published,'report_sha256':h.sha(H/'report.json'),'goal_active':True})
h.custody();h.ar.refuse_active(h.ar.live_status())
assert not subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=h.REPO,text=True).strip()
assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=h.REPO,text=True).strip()
h.pin(h.ar.DASHBOARD/'index.html',h.read(ROOT/'runs/D304-tracker-display-metadata/layout-fix.json')['after_sha256'])
for path,url in [(h.ar.STATUS,'status.json'),(h.ar.DASHBOARD/'index.html','index.html'),(H/'report.json','evidence/'+H.name+'/report.json')]:
    with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/'+url,timeout=20)as response:assert response.read()==path.read_bytes()
process=json.loads(subprocess.check_output(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process -Filter 'ProcessId = 26528' | Select-Object ProcessId,ExecutablePath | ConvertTo-Json -Compress"],text=True))
assert process['ExecutablePath'].lower()==r'X:\Dev\GTOpen\target\desktop-runtime\release\gto-server.exe'.lower()
assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists()
h.save(H/'terminal-audit.json',{'at':h.now(),'status':'D309_D310_COMPLETE_ALL_OWNED_PROCESSES_TERMINAL',
    'local_ledger_commit':head,'launched_processes_terminal':5,'exit0':3,'exit1_preserved_mechanical_failures':2,'never_started_Popen_launch':1,
    'complete_native_copy_rounds':1,'full_raw_reader_pass':True,'raw_files':90,'raw_bytes':14204434128,
    'accepted_main_live_protected_PTX_D304_HTML_exact':True,'server_pid':26528,'server_idle':True,'locks_absent':True,'research_tracked_clean':True,
    'HTTP_status_index_report_exact':True,'new_solver_source_or_speed_trials':0,'new_adopted_gain':False,
    'next_unused_candidate':'E125','last_primary_baseline':'B377','next_unused_primary_baseline':'B378','X_free_bytes':shutil.disk_usage(ROOT).free,
    'all_new_bulk_X_S_readonly_no_T':True,'goal_active':True})
print(json.dumps(h.read(H/'terminal-audit.json')),flush=True)
