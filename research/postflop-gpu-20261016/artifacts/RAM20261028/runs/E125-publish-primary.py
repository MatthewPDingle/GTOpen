"""Publish complete retained primary observations; adoption remains separately gated."""
import json,shutil,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'))
import common as h
h.custody();h.ar.refuse_active(h.ar.live_status())
assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists()
Q=ROOT/'comparisons/E125-three-pair-comparison/report.json';A=ROOT/'comparisons/E125-root-crosscheck/report.json';P=ROOT/'runs/E125-primary-plan/protocol.json'
q,a,plan=h.read(Q),h.read(A),h.read(P);perf=q['performance'];passed=perf['primary_timing_pass']
assert a['aggregate_gain_pct']==perf['observed_gain_pct']and a['status']==('pass_initial_timing_only'if passed else'pass_rejected')
assert q['exactness']=={'fixture_results':18,'convergence_records':138,'all_exact':True}and q['ordinary_units_passed']==86 and q['ordinary_units_ignored']==4
assert not q['excluded_samples']and q['extension_runs']==q['historical_timing_samples_used']==q['RAM_baseline_samples_scored']==0
assert h.read(ROOT/'runs/E125-primary-wrapper/complete.json')['all_owned_children_terminal']
S=ROOT/'runs/E125-source';manifest=h.read(S/'manifest.json')
for value in manifest['owned'].values():h.pin(value['base'],value['base_sha256']);h.pin(value['candidate'],value['candidate_sha256'])
direct=ROOT/'runs/E125-kernel-control/reader-report.json';raw=h.read(direct)
assert raw['cases']==1688 and raw['application_kernel_launches']==3376 and len(raw['negative_reader_fixtures_rejected'])==4
assert raw['all_original_inputs_and_seeds_independently_regenerated']
resource=h.read(ROOT/'runs/E125-resource/report.json');emitted=h.read(ROOT/'runs/E125-resource/emitted-report.json')
assert all(emitted['gates'].values())and len(emitted['negative_reader_fixtures_rejected'])==6
receipts=[]
for folder in ['E125-resource/execution','E125-kernel-control/execution','E125-final-build','E125-primary-execution','E125-primary-wrapper']:
    for path in(ROOT/'runs'/folder).rglob('*.exit.json'):
        receipt=h.read(path);assert receipt['returncode']==0 and receipt['error']is receipt['cleanup']is None
        receipts.append({'path':str(path),'sha256':h.sha(path),'returncode':0})
assert len(receipts)==17
direction=f"{abs(perf['observed_gain_pct']):.6f}% {'faster'if perf['observed_gain_pct']>=0 else'slower'}"
reason=f"Sum of three fixture medians: {perf['baseline_full_cycle_ms']:.4f} to {perf['candidate_full_cycle_ms']:.4f} ms; {direction}. "+('Initial timing screen passed. Separate confirmation and full state, compatibility, memory, capacity, holdout and application checks remain before adoption.'if passed else'The candidate failed the 1% cutoff and fixture slowdown rules. The fixed 16-bit hand-permutation table form is closed; no extra samples or source variants.')+' All 1,688 direct cases, 86 ordinary tests, 18 scientific result records and 138 convergence checkpoints passed. The accepted E080 solver remains live.'
H=ROOT/'runs/E125-primary-checkpoint';H.mkdir(exist_ok=False)
h.save(H/'report.json',{'id':'E125-primary-checkpoint','at':h.now(),'status':'INITIAL_SPEED_PASS_FULL_QUALIFICATION_PENDING'if passed else'REJECTED_CLOSED_U16_HANDPERM_TABLE_FORM',
    'measurement_epoch':'RAM20261028','candidate_source_manifest_sha256':h.sha(S/'manifest.json'),'change':'KeeporiginalSpotu16handpermwidththroughCpuGpuPlan/privateCudaSlice/kerneltypedreadandcapacityobserver. Alloriginaltablevalues/order/index/identity/FPmath/branch/launch/qualityretained; onlythisreadonlytable payload4to2bytes/element. No public save/model change.',
    'compiled_scope':'Both120/75same9ABIheaders/8untargetedbodies/resources. Sevencompiler-unrolledtableloadsreplaceu32withu16andpositivezeroextend/2byteelementstride; full120byteinverseand75inversewithbijectivevirtualregisterrename restoreoriginalentireentry. 6negativecorruptioncontrolsreject. Typedvirtualinstructionproof+fullrawfinitecontrols,notuniversalcompilerGPUproof.',
    'resource_warning':'Actualup_chance registers30to40; local0/static0/dynamic0/constant0/stack1024/max1024/occupancy64,128,256=24,12,6unchanged. Warningnotreclassifiedaway;actualfullmaterial/capacity/broadqualificationpending.',
    'observer_repairs':'Originalresourceobserverassumedoneemittedloadforonesourceload,butNVRTCunrolled7. Originalfailedcountreport/source/protocol retained. Firstadditivereaderhandled120syntaxbutnot75base/shift/directu64extension; V2supportsactual75andbijectivevirtualregisterrenameunderexhaustiveoriginalu16domain,wholeentryinversemustmatch. Positivecapturedfiles/source/gates unchanged; no compiler/module/GPUquery/native repeats. Readerrepairsarenotnumericalorperformancefailures.',
    'direct_control':raw,'primary_performance':perf,'fixtures':q['fixtures'],'pairs':q['pairs'],
    'primary_exactness':q['exactness'],'ordinary_units_passed':86,'ordinary_units_ignored':4,
    'root_crosscheck_sha256':h.sha(A),'primary_protocol_sha256':h.sha(P),'direct_report_sha256':h.sha(direct),
    'decision':reason,'all_owned_children_terminal':True,'owned_child_receipts':receipts,
    'candidate_adopted':False,'qualified_live_config':'E080/GPU/compressed/Rayon16/defaultaffinity',
    'RAM_reference_sum_of_threefixture_medians_ms':10456.4109,'RAM_reference_not_scored_or_pooled':True,
    'all_adoption_gates_still_pending':plan['adoption_requirements'],'full_CPUplan_rawengine_canonical_broad_capacity_material_not_yet_qualified':True,
    'last_primary_baseline':'B380','next_unused_primary_baseline':'B381','next_unused_candidate':'E126',
    'accepted_main_live_protected_PTX_D304_HTML_unchanged':True,'all_new_bulk_X_S_readonly_no_T':True,'goal_active':True})
files=[ROOT/'runs/D311-permutation-width-scout'/name for name in['history.json','report.json']]
for folder in ['E125-source','E125-resource','E125-kernel-control','E125-build-plan','E125-final-build','E125-primary-plan','E125-primary-execution','E125-primary-wrapper','E125-primary-checkpoint']:
    parent=ROOT/'runs'/folder
    files += [p for p in parent.rglob('*')if p.is_file()and p.suffix.lower()in['.json','.rs','.cu','.log','.txt','.py']and '__pycache__'not in p.parts]
files += [Q,A]
published=[]
for path in files:
    relative=(path.relative_to(ROOT/'runs')if path.is_relative_to(ROOT/'runs')else path.relative_to(ROOT/'comparisons'))
    destination=h.ar.DASHBOARD/'evidence'/relative;destination.parent.mkdir(parents=True,exist_ok=True)
    if destination.exists():assert destination.read_bytes()==path.read_bytes()
    else:shutil.copyfile(path,destination)
    with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+relative.as_posix(),timeout=20)as response:assert response.read()==path.read_bytes()
    published.append({'url':relative.as_posix(),'sha256':h.sha(path)})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS)
    display={
        'D309':{'title':'Interleaved learning buffers: source and address audit','stage':'Source, history and address checks complete','correctness':'source_contract_pass','reason':'The regret/strategy layout has a valid address mapping and no recognized prior implementation in the bounded history search. This is a source check; it does not establish GPU accuracy or speed.'},
        'D310':{'title':'Interleaved learning buffers: full transfer control','stage':'Exact transfers; prototype declined on copy cost','correctness':'pass_transport_exactness','reason':'All nine sizes passed: 90 complete raw files and 3.551 billion physical/output words, including guards. Large-case strided downloads took over 40 times as long as contiguous downloads in one diagnostic round. The proposed route is closed before a solver prototype. This was not a full-solve timing test.'},
        'D311':{'stage':'Original 16-bit domain and history checks complete','correctness':'source_contract_pass','reason':'The original hand-permutation tables already use 16-bit values. All 65,536 representations preserve their values exactly. Bounded history checks found no recognized matching GPU layout. Numerical and timing results are recorded under E125.'}}
    for identity,fields in display.items():next(x for x in status['experiments']if x['id']==identity).update(fields)
    scout=next(x for x in status['experiments']if x['id']=='D311');scout['evidence']=[{'label':'Original u16 domain and boundedhistory','url':'evidence/D311-permutation-width-scout/report.json'}]
    row=next(x for x in status['experiments']if x['id']=='E125')
    row.update(at=h.now(),accepted=False,status='running'if passed else'rejected',stage='Initial timing screen passed; full qualification pending'if passed else'Closed: complete-solve timing screen failed',correctness='pass_scoped_correctness_checks',reason=reason,performance=perf,baseline_full_cycle_ms=perf['baseline_full_cycle_ms'],candidate_full_cycle_ms=perf['candidate_full_cycle_ms'],full_cycle_ms=perf['candidate_full_cycle_ms'],fixture='Three-fixture sum of medians (3 matched pairs)',gain_pct=perf['observed_gain_pct'])
    row['evidence']=[{'label':label,'url':'evidence/'+path}for label,path in[('All source changes','E125-source/manifest.json'),('All7 typed emitted loads and resource warning','E125-resource/emitted-report.json'),('Entire original directraw corpus','E125-kernel-control/reader-report.json'),('Frozen completecycle protocol','E125-primary-plan/protocol.json'),('Retained completecycle score','E125-three-pair-comparison/report.json'),('Root raw/science/arithmetic replay','E125-root-crosscheck/report.json'),('Checkpoint and limitations','E125-primary-checkpoint/report.json')]]
    status.update(updated_at=h.now(),state='running',goal_status='active',active_experiment='E125',stage='16-bit table confirmation pending'if passed else'16-bit table rejected; performance search continues',activity=reason+' No new gain adopted. Last baseline B380; next B381.')
    h.ar.atomic_json(h.ar.STATUS,status)
ledger=h.REPO/'research/postflop-gpu-20261016/experiments.md';old=ledger.read_bytes()
assert b'\n## D311/E125 original-width hand-permutation table'not in old
assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=h.REPO,text=True).strip()
entry=f'''

## D311/E125 original-width hand-permutation table - {'initial speed pass, adoption pending'if passed else'closed at initial complete-cycle screen'}

PreviousD309/D310interleavedR/Swidth4pitch8copyrouteexact90rawfiles14.204GBbut>40xlargearenaD2Hsingle-roundcost, conservativeprototype decline preserved; no closedform rescue. NewdistinctleadpreservesactualSpot.hand_perm[Vec<Vec<u16>>;2]sourcewidthinGpuPlan/privateCudaSlice/chancekernel insteadofu32widening. Bounded52uniquealllocalrefkernel/mod/planhashrecords+retainedX/Srs/cu typedmarkers findsnorecognizedform; all65536u16words exactdomainrepresentationchecks. Fixed4filesCUDA/mod/plan/continuation_capacity(accounting)inverseexact/originalCRLF-LF preserved,sourceCUDA{manifest['owned']['crates/solver/src/gpu/kernels.cu']['candidate_sha256']}. Tablevalues/order/identity/FPmath/index/schedule/launch/quality/CPUarenas/save/modelunchanged; tableexplicitpayload4to2bytes/element. No E070playerarity/E115/E121row/E099handmemoryformcomposed. Fullactualplan/capacity/raw/broad/material remain required, notinferredfromnarrowerpayload.

OneRustresourcecompiler+one module-onlyprocess with2NVRTCtargets120/75,9sameABIheaders/8untargetedbodiesandactualresourcesexact. Targetup_chance30to40registerwarning,local0/static0/dynamic0/constant0/max1024/occupancy24,12,6/stack1024unchanged. Originalobserverincorrectlyrequiredoneemittedloadforonesourceload; actual7compilerunrolledsites. Originalfailedcountreport/protocol/source retained;firstadditivereader120works/75unsupportedbase-shift-direct64extension;V2all7botharchitectureswholeentryinverseexact(120byteexact,75restoresoriginalpositiveu16u32intermediate/signedextendandbijectivevirtualregisterrename),allFP/branches/othermetadata preserved;6corruptioncontrolsreject. No source/compiler/module/queryrepeat or realresourcecosthidden.

EntireoriginalE0681688-caseunencodedcorpusbyteexact,actualacceptedE080/currentcandidatePTX,one3376applicationlaunchcontrol. All12actualimmutablebuffers/wholephysicalCFV/guards preserved; candidatehandpermactualu16ownercheckedtry_fromallsourceliteralwords/noreinterpretcastandfullactualtypedphysicaldump alongsideoriginalu32input/posts. Independentreaderregeneratesalloriginal12buffers/seedbitsfromcorpus,checksallheaders/lengths/EOF/wordpairs/guard/fulltypedtable,all10938464used-or-ignoredreadaddresses bounded/disjoint. Botharms35904112CFVwords/9083648immutablewords/34875264guardchecks;2075704actualcandidateu16words;4rawfiles274766706bytespreservedX;4corruptioncontrolsreject. Report{h.sha(direct)}. Onecompiler/native/reader each terminal0,noNVRTC/solver/speed inthatcontrol.

Twofreshordinaryoffline/lockedfeature/primaryCargo builds exact4ownedresearchfiles/restoredE080aftereach; no main/liveactivation. V125-unit86passed/4ignored thenfrozenB378/E125R1,E125R2/B379,B380/E125R3. All18scientificfixturepayloads and138convergencecheckpoints exact originalanchor. CurrentRAMactualcompletecycle medians{perf['baseline_full_cycle_ms']:.10f}to{perf['candidate_full_cycle_ms']:.10f}ms,unroundedgain{perf['observed_gain_pct']:.12f}%; fixtureguards{json.dumps(perf['fixture_regression_guard'],separators=(',',':'))}. Rootrawlog/science/arithmetic replay{h.sha(A)}. {reason} No exclusions/extensions/oldRAM/historicaltimingpooling/statisticalsignificanceclaim. No fresh16/rawCPUplan-engine-canonical/broad/F32/locks/save/resume/symmetric/paged/stored/capacity/material/holdout/currentRAMcumulative/tempappqualified;allremainmandatorybeforeadoption. Scientificdirect/primarypassesnotuniversalIEEE/device/fullstateproof. All17ownedchildren terminal0;all{len(published)}nonbulkHTTPartifactsbyteverified. Accepted/main/live/protected2PTX/D304HTMLexact,serveridle/locksabsent;E080/GPU/compressed/16/defaultaffinity qualified/live;RAMreference10456.4109mskeptseparate. No newadoptedgain;lastB380/nextB381,nextcandidateE126. Xbulk/Sreadonly/noT;ledgerprefixbyteexact/localledger-onlycommit/nopush/noprune. Goalactive.
'''
ledger.write_bytes(old+entry.encode());assert ledger.read_bytes()[:len(old)]==old
h.custody();subprocess.run(['git','add','--','research/postflop-gpu-20261016/experiments.md'],cwd=h.REPO,check=True)
assert subprocess.check_output(['git','diff','--cached','--name-only'],cwd=h.REPO,text=True).splitlines()==['research/postflop-gpu-20261016/experiments.md']
subprocess.run(['git','-c','gc.auto=0','commit','-m','research: qualify original-width permutation table initial solve screen'],cwd=h.REPO,check=True)
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=h.REPO,text=True).strip()
h.save(H/'publication.json',{'at':h.now(),'local_commit':head,'HTTP_artifacts':published,'report_sha256':h.sha(H/'report.json'),'goal_active':True})
h.custody();h.ar.refuse_active(h.ar.live_status())
h.pin(h.ar.DASHBOARD/'index.html',h.read(ROOT/'runs/D304-tracker-display-metadata/layout-fix.json')['after_sha256'])
for path,url in[(h.ar.STATUS,'status.json'),(h.ar.DASHBOARD/'index.html','index.html'),(H/'report.json','evidence/'+H.name+'/report.json')]:
    with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/'+url,timeout=20)as response:assert response.read()==path.read_bytes()
assert not subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=h.REPO,text=True).strip()
assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=h.REPO,text=True).strip()
assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists()
process=json.loads(subprocess.check_output(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process -Filter 'ProcessId = 26528' | Select-Object ProcessId,ExecutablePath | ConvertTo-Json -Compress"],text=True))
assert process['ExecutablePath'].lower()==r'X:\Dev\GTOpen\target\desktop-runtime\release\gto-server.exe'.lower()
h.save(H/'terminal-audit.json',{'at':h.now(),'status':'E125_INITIAL_SCREEN_COMPLETE_ALL_OWNED_WORK_TERMINAL','initial_speed_pass':passed,'candidate_adopted':False,
    'owned_child_receipts_terminal0':17,'local_ledger_commit':head,'accepted_main_live_protected_PTX_D304_HTML_exact':True,'server_idle':True,'live_pid':26528,
    'locks_absent':True,'research_tracked_clean':True,'HTTP_status_index_report_exact':True,'last_primary_baseline':'B380','next_unused_primary_baseline':'B381','next_unused_candidate':'E126',
    'X_free_bytes':shutil.disk_usage(ROOT).free,'all_new_bulk_X_S_readonly_no_T':True,'goal_active':True})
print(json.dumps(h.read(H/'terminal-audit.json')),flush=True)
