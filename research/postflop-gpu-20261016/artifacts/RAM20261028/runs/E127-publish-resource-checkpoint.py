"""Publish successful finite ownership/resource prerequisites without a speed or adoption claim."""
import json,shutil,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'))
import common as h
D=ROOT/'runs/D313-action-star-ownership';S=ROOT/'runs/E127-source';R=ROOT/'runs/E127-resource';N=ROOT/'runs/E127-native'
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists()
for path in[D/'protocol.json',D/'root-protocol.json',R/'protocol.json',N/'protocol.json']:
    for name,digest in h.read(path)['input_sha256'].items():h.pin(name,digest)
model,root,resource,capture,source=[h.read(path)for path in[D/'report.json',D/'root-report.json',R/'report.json',N/'capture-report.json',S/'manifest.json']]
assert len(model['cases'])==len(root['cases'])==6 and all(resource['gates'].values())and not resource['resource_warnings']
assert len(root['negative_corruption_controls_rejected'])==4
for a,b in zip(model['cases'],root['cases']):
    assert a['fixture']==b['fixture']and a['constructor']==b['constructor']and a['selected_disjoint_stars']==b['all_selected_stars_replayed']
    assert b['all_physical_last_writers_unchanged']and b['same_phase_writes_disjoint']and b['all_learning_update_intervals_disjoint']
    h.pin(a['projection'],a['projection_sha256'])
original=(S/'baseline.cu').read_bytes();h.pin(S/'baseline.cu',source['baseline_sha256']);h.pin(S/'candidate.cu',source['candidate_sha256'])
assert(S/'candidate.cu').read_bytes()[:len(original)]==original==(h.REPO/'crates/solver/src/gpu/kernels.cu').read_bytes()
markers=[json.loads(line.split('E127_RESOURCE ',1)[1])for line in(R/'execution/probe.stdout.log').read_text(encoding='utf-8').splitlines()if'E127_RESOURCE 'in line]
assert len(markers)==20 and markers[:-1]==resource['resource_rows']and markers[-1]['application_kernels']==0
rows={(x['variant'],x['kernel']):x for x in markers[:-1]}
keys=['registers','local_bytes_per_thread','constant_bytes','static_shared_bytes','dynamic_shared_bytes','max_threads','occupancy_by_threads','context_stack_after']
assert all(rows['baseline','up_action'][k]==rows['candidate','up_action_star'][k]for k in keys)
assert capture['status']=='native_code_captured_dataflow_proof_pending'and capture['application_kernel_launches']==capture['solver_or_speed_samples']==0
h.pin(capture['SASS_section_path'],capture['SASS_section_sha256'])
receipts=[]
for folder in[D/'execution',R/'execution',N/'execution']:
    for path in folder.glob('*.exit.json'):
        receipt=h.read(path);assert receipt['returncode']==0 and receipt['error']is receipt['cleanup']is None
        receipts.append({'path':str(path),'sha256':h.sha(path),'returncode':0})
assert len(receipts)==6
H=ROOT/'runs/E127-resource-checkpoint';H.mkdir(exist_ok=False)
h.save(H/'report.json',{'id':'E127-resource-checkpoint','at':h.now(),'status':'OWNERSHIP_AND_SHADER_RESOURCE_PASS_NATIVE_AND_HOST_PROOFS_PENDING',
    'model_report_sha256':h.sha(D/'report.json'),'root_report_sha256':h.sha(D/'root-report.json'),'source_manifest_sha256':h.sha(S/'manifest.json'),
    'resource_report_sha256':h.sha(R/'report.json'),'native_capture_report_sha256':h.sha(N/'capture-report.json'),
    'finite_ownership':model['cases'],'all_selected_stars_replayed_and_all_writer_classes_checked':root['cases'],
    'structural_numbers_not_performance':'Modeled reduction in scheduled actionCTAs21.481740406%rainbow/21.440724255%two-tone/41.666666667%river. Alloriginalfloatingpointoperationsremain. Serialnodework,loadbalance/cache/CPUplanner/list/graph/JITcostscanerasebenefit. No speed/headroom/no-tradeoffclaim.',
    'actual_shader_resources':rows['candidate','up_action_star'],'all_original9resources_and_both_arch_PTxbodies_unchanged':True,
    'source_helper_and_dispatch_inverse_exact':True,'original9_source_prefix_byteexact':True,
    'reader_coverage_correction':'Firstmodelcheckedactionlastwriters. Separateadditiverootreaderincludesalloriginalaction/chance/fold/showwriters,eachmovedphasewritesdisjointandallphysicalslotlastwritersunchanged,alllearningrangesdisjoint. Originalmodel/selection/inputsunchangedandnotrerun.',
    'preparation_records':'Firstsourcepreparerhistoryscanincludedthisturnnewownedprobe; V2excludesonlythatpath. V2thenencounteredE065action_startvariableprefix. Complete19filepreflightclassifies16E099handpair2/2E065prefix/1ownnewdraft. V3retainsallhistoricalhitswithseparateclassifications. Originalpreparersand2repairrecordsretained; neitherassertcreatedsourcefolderorstartedcompiler/native. Oneactualshaderformcompiledonce.',
    'next_requirements':['Complete actualPTX/native child-loop/helper/barrier/parent/control-flow proof; capturedcodealone doesnotpass it.','Auditallhost worklist/metadata/CFVpointerlifecyclemutators,includingownedpostflop andborrowed/paged/storedcontinuation. Oneprospectiveownershipbasedeligibility/fallbackmustbefrozenbeforeanyapplicationkernel,notfixture/speedoutcomebased.','Freezeonefullhostsourceformandexplicitnewhostwrapper/heap/worklist/GPUbuffer/module/graph/capacity/constructorpeak/lifetimecostsbeforefirstappkernel. Preserveoriginalpublicplan,CFVmap/data/cadence/locks/precision/quality.','Fulloriginal+newdirectphysicalword/ownership/CPUplan/rawengine/canonical and ordinary correctness. Fixed3pairedcompletecycle>=1%unrounded+strictfixtureguard; separatelyfrozenfresh16,allbroadsupportedF32/menu/locks/save/resume/symmetric/paged/stored/fallback/material/capacity/holdout/freshoriginalRAMcumulative/actualtempappbeforeadoption.'],
    'closed_form_policy':'On genuinefailurecloseD313deepest-firstdisjointstars/originalCFVmap/oneCTA128threads/childthenparentbarrier/helper/scheduleform;no width/phase/arity/helper/group/guard/order/layout/source/quality/sample rescue.',
    'all_managed_scientific_children_terminal0':True,'managed_child_receipts':receipts,'preserved_preparation_assertions':2,
    'new_Rust_compilers':1,'new_NVRTC_compiles':2,'new_application_kernel_launches':0,'new_solver_or_speed_trials':0,
    'source_activated':False,'candidate_adopted':False,'qualified_live_config':'E080/GPU/compressed/Rayon16/defaultaffinity',
    'last_primary_baseline':'B380','next_unused_primary_baseline':'B381','active_candidate':'E127','next_unused_candidate':'E128',
    'RAM_reference_sum_threefixture_medians_ms':10456.4109,'accepted_main_live_protected_PTX_D304_HTML_unchanged':True,'all_new_bulk_X_S_readonly_no_T':True,'goal_active':True})
files=[]
for folder in[D,S,R,N,H]:
    files += [path for path in folder.rglob('*')if path.is_file()and path.suffix in['.json','.rs','.cu','.log','.txt']and '__pycache__'not in path.parts]
published=[]
for path in files:
    relative=path.relative_to(ROOT/'runs');dst=h.ar.DASHBOARD/'evidence'/relative;dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.exists():assert dst.read_bytes()==path.read_bytes()
    else:shutil.copyfile(path,dst)
    with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+relative.as_posix(),timeout=20)as response:assert response.read()==path.read_bytes()
    published.append({'url':relative.as_posix(),'sha256':h.sha(path)})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);row=next(x for x in status['experiments']if x['id']=='D313')
    row.update(at=h.now(),status='complete',stage='Finite scheduling and memory rules passed',correctness='pass_finite_ownership_model',
        reason='Six retained plans replayed. The model schedules about 21% fewer action blocks on each flop fixture and 42% fewer on river, while retaining every action and all arithmetic. Every selected group, foreign-reader rule, CFV writer and learning interval was checked. These are structural counts, not speed gains.',
        evidence=[{'label':'Frozen selection and safety rules','url':'evidence/D313-action-star-ownership/protocol.json'},{'label':'Complete model and projections','url':'evidence/D313-action-star-ownership/report.json'},{'label':'Independent replay and all writer classes','url':'evidence/D313-action-star-ownership/root-report.json'}])
    row=next(x for x in status['experiments']if x['id']=='E127')
    row.update(at=h.now(),status='running',accepted=False,stage='Shader resources passed; native proof and host integration pending',correctness='pass_source_resource_checks_only',
        reason='The new action-group kernel matches the original action kernel: 62 registers, 64 local bytes, 1024-thread limit and reported occupancy. All nine original kernels remain unchanged. Native code was captured for inspection. No application kernel, numerical test or complete-solve timing has run; no gain is adopted.',
        evidence=[{'label':'Original helper and dispatch preservation','url':'evidence/E127-source/manifest.json'},{'label':'Full shader resource checks','url':'evidence/E127-resource/report.json'},{'label':'Native code captured; proof pending','url':'evidence/E127-native/capture-report.json'},{'label':'Checkpoint, costs and remaining qualification','url':'evidence/E127-resource-checkpoint/report.json'}])
    status.update(updated_at=h.now(),state='running',goal_status='active',active_experiment='E127',stage='Action groups: native proof and host scheduling next',activity='Ownership and shader resource prerequisites passed. Structural block savings are not measured speed gains. E080 remains qualified and live; no new gain adopted.')
    h.ar.atomic_json(h.ar.STATUS,status)
ledger=h.REPO/'research/postflop-gpu-20261016/experiments.md';old=ledger.read_bytes()
assert b'\n## D313/E127 action-only two-level groups'not in old
assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=h.REPO,text=True).strip()
entry=f'''

## D313/E127 action-only two-level groups - ownership and shader resources pass; no speed claim

Previousgoalturnprogress:E126actualSM120vector-emissionfailed/closedwith2managedchildren terminal0,notnumericalorspeedfailure. Accepted/main/live/protected2PTX/D304HTML/idle/locks/HEAD52a1e67f01011fba43ec3453c8ee03812985f7f9 revalidatedreadonlywithoutcreate-onlyauditrerun. Newdistinctlead computesactionchildrenandparentinoneCTA,originalFPmathandCFVmapretained. E078foldproducerfusion/E104persistentgrid/E076CFVlayout/E099adjacenthandpairing notcomposed/reopened.

ProspectiveD313protocol{h.sha(D/'protocol.json')}beforeanyownershipoutcomes: sixoriginalacceptedD272CPUinitial/resumedplans/kindarrays+correspondingentireGPUframesSHAverified19014914354bytes. Parentstarrequiresoneormoreactionchildren/nochancechild/uniqueparent/nochanceorbitreference/nextlevel. OriginalparityCFVpoolcanaliasparentwritesandgrandchildinputs:rejectallforeignnextlevelactionreadersofparentoutputslot. Amongeligible,deepestparentlevelfirstthenascendingIDmaximaldisjointmatching,no threshold/shape/fixture/parity/order tuning. Selectedheadmovesonephaseearlier,originalactionchildrenexecuteinoriginalactionindexorder/oneCTAbarrier/thenparent. Alloriginalactionsupdateonce;ownstarreadscompletebeforeparentwrite. RawmodelprojectionsretainedX,no newGPU/CFR/model-source productionactivation.

Model343670checks; selectedrainbow106592stars/112464actionchildren, two-tone64844/68302, river5/5 ineachconstructor. ScheduledCTAreduction21.481740406%/21.440724255%/41.666666667%,not time/headroom/operation savings: everyFPoperationretained,serialnodes/loadbalance/cache/cpuworklist/graph/JITcostscanerasebenefit. Originalmodellast-writercheckonlyactions; separateadditiveroot686163checksreplayeveryselectedstar/wholeorderedchildren/uniqueownership/foreignreaders andALL originalaction/chance/fold/showwriters. Eachnewphasewritesdisjoint,allphysicalrowlastwriteridentitiesandalllearningintervalsunchanged;4foreignreader/phase/duplicateexecution/childidentitycorruptioncontrolsreject. No source/model/selection/native rerun. Reports{h.sha(D/'report.json')}/{h.sha(D/'root-report.json')}.

BoundedretainedX/Srs/cu star/twolevel/pairmarkers:16E099handpair2hits/2E065action_startprefixhits,allclassifiedandpreserved,notexhaustivesemantic/helper/remote noveltyproof. FirstprepareraccidentallysawownnewE127resourceprobedraft;V2excludesonlyexactownedpath,thenstoppedonaction_startprefix. Complete19filepreflightclassifiesallhits;V3distinctfalsepositiveclasses,nopattern/history/source/gatechange. Original2preparers/assertionnotesretained;nonecreatedsourcefolder/compiler/nativebeforeitsassert. One actualshaderform:CUDA{source['candidate_sha256']},original9sourcebyteexactprefix+explicit-nodecopyoforiginalactionhelperand2/3/4/genericdispatch,bothinverseexact. New20argup_action_staroneCTA128threadsloopsoriginalchildren,onlyactionchildnode_na>0(nochancecontract),bar.sync,thenparent. NoFPexpression/precision/algorithm/loop/discount/lock/opponent change; nohostcandidate/worklistintroducedyet. NVIDIA12.9CTAglobal/sharedvisibilityanduniformbarriercontractlinked;sourceproofisnotGPUfloatproof.

Resourceprotocol{h.sha(R/'protocol.json')}:oneRustcompiler/onemoduleprobe/2NVRTC12.9targets120+75,sealedbaselinePTXreused. Original9headers/bodiesalphaexactbotharches/original9actualresourcesexact. NewentryABI20sameoriginalactiontypes,onebarrierbotharches;actualnewresources EXACT originalup_action:62regs/64local/0constant/static/dynamic/stack1024/max1024/64,128,256occupancy16,8,4. Allhardgatespass/noresourcewarning;thisisnotactualCPU/GPU/material/capacityorperformancequalification. OneownedexistingCUPTIresourcecallbackcapture+one nvdisasm,10entrymodule/original9queries/oneCUBIN/zeroerrors/zerolaunches,actualnativecapturedSHA{capture['CUBIN_sha256']}/section{capture['SASS_section_sha256']}; nativechild-loop/return/barrier/parent/control-flowproofPENDING,notpassedbycaptureorcounts. No counters/injection/settings/extra shadercompiles orarrays/appkernels.

Checkpoint{h.sha(H/'report.json')}/{len(published)}nonbulkHTTPartifactsbyteverified. Nextcompleteactualnative/PTXcontrolandcallerproof, auditeveryowned/borrowed/paged/stored worklist/CFVpointermutator,thenfreezeonefullhostform/ownershipbasedfallback+allnewwrapper/heap/worklist/GPU/module/graph/peak/capacity/lifetimecostsBEFOREfirstappkernel. No fixture/outcome scopefallback. Fullraw/device/CPUplan/engine/canonical/ordinary/complete1%strictfixture/fresh16/broad/material/capacity/holdout/freshoriginalRAMcumulative/tempapp allremainmandatorybeforeadoption. No source/phase/helper/group/guard/order/layout/arity/width/flags/quality/sample rescueaftergenuinefailure. All6managedscientificchildren terminal0;2preparationassertionspreserved;locksabsent,accepted/main/live/protectedPTX/D304HTMLexact,E080/GPU/compressed/16/defaultaffinitylive. No newgainadopted;RAMreference10456.4109msseparate,lastB380/nextB381,E127active/nextunusedE128. AllnewbulkX/Sreadonly/noT;ledgerprefixbyteexact/localledger-onlycommit/nopush/noprune;goalactive.
'''
ledger.write_bytes(old+entry.encode());assert ledger.read_bytes()[:len(old)]==old
h.custody();subprocess.run(['git','add','--','research/postflop-gpu-20261016/experiments.md'],cwd=h.REPO,check=True)
assert subprocess.check_output(['git','diff','--cached','--name-only'],cwd=h.REPO,text=True).splitlines()==['research/postflop-gpu-20261016/experiments.md']
subprocess.run(['git','-c','gc.auto=0','commit','-m','research: qualify action-star ownership and shader resource prerequisites'],cwd=h.REPO,check=True)
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=h.REPO,text=True).strip()
h.save(H/'publication.json',{'at':h.now(),'local_commit':head,'HTTP_artifacts':published,'report_sha256':h.sha(H/'report.json'),'goal_active':True})
h.custody();h.ar.refuse_active(h.ar.live_status());h.pin(h.ar.DASHBOARD/'index.html',h.read(ROOT/'runs/D304-tracker-display-metadata/layout-fix.json')['after_sha256'])
for path,url in[(h.ar.STATUS,'status.json'),(h.ar.DASHBOARD/'index.html','index.html'),(H/'report.json','evidence/'+H.name+'/report.json')]:
    with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/'+url,timeout=20)as response:assert response.read()==path.read_bytes()
assert not subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=h.REPO,text=True).strip()
assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=h.REPO,text=True).strip()
assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists()
process=json.loads(subprocess.check_output(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process -Filter 'ProcessId = 26528' | Select-Object ProcessId,ExecutablePath | ConvertTo-Json -Compress"],text=True))
assert process['ExecutablePath'].lower()==r'X:\Dev\GTOpen\target\desktop-runtime\release\gto-server.exe'.lower()
h.save(H/'terminal-audit.json',{'at':h.now(),'status':'E127_RESOURCE_CHECKPOINT_ALL_MANAGED_WORK_TERMINAL','local_ledger_commit':head,'managed_scientific_child_receipts_terminal0':6,'preserved_preparation_assertions':2,
    'accepted_main_live_protected_PTX_D304_HTML_exact':True,'server_idle':True,'live_pid':26528,'locks_absent':True,'research_tracked_clean':True,'HTTP_status_index_report_exact':True,
    'native_control_flow_proof_pending':True,'host_source_candidate_pending':True,'application_kernel_numerical_solver_or_speed_trials':0,'candidate_adopted':False,
    'last_primary_baseline':'B380','next_unused_primary_baseline':'B381','active_candidate':'E127','next_unused_candidate':'E128','X_free_bytes':shutil.disk_usage(ROOT).free,'all_new_bulk_X_S_readonly_no_T':True,'goal_active':True})
print(json.dumps(h.read(H/'terminal-audit.json')),flush=True)
