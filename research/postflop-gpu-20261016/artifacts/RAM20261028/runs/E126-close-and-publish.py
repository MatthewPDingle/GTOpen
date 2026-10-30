"""Root replay of failed SM120 vector-emission gate; no numerical or speed continuation."""
import collections,json,re,shutil,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'))
import common as h
D=ROOT/'runs/D312-card-bound-pair-scout';S=ROOT/'runs/E126-source';H=ROOT/'runs/E126-resource';O=H/'execution'
h.custody();h.ar.refuse_active(h.ar.live_status())
assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists()
P=h.read(H/'protocol.json');R=h.read(H/'report.json');M=h.read(S/'manifest.json')
for path,digest in P['input_sha256'].items():h.pin(path,digest)
h.pin(S/'baseline.cu',M['baseline_sha256']);h.pin(S/'candidate.cu',M['candidate_sha256'])
assert(S/'baseline.cu').read_bytes()==(h.REPO/'crates/solver/src/gpu/kernels.cu').read_bytes()
assert(S/'candidate.cu').read_bytes().replace(M['after'].encode(),M['before'].encode(),1)==(S/'baseline.cu').read_bytes()
markers=[json.loads(line.split('E126_RESOURCE ',1)[1])for line in(O/'probe.stdout.log').read_text(encoding='utf-8').splitlines()if'E126_RESOURCE 'in line]
assert len(markers)==19 and markers[-1]['stage']=='complete'and markers[-1]['candidate_NVRTC_compiles']==2
assert markers[-1]['application_kernels']==markers[-1]['solver_or_speed_runs']==0
assert markers[:-1]==R['resource_rows']
failed=[key for key,value in R['gates'].items()if not value]
assert failed==['compute_120:aligned_vector_pair_emitted']
inventories={}
for arch in['compute_120','compute_75']:
    inventory={}
    for arm in['baseline','candidate']:
        path=O/(arm+'-'+arch+'-up_show.ptx.txt');text=path.read_text(encoding='utf-8')
        ops=collections.Counter(re.findall(r'\bld\.global[\w.]+',text))
        inventory[arm]={'global_load_opcode_sites':dict(ops),'target_section_sha256':h.sha(path),'barrier_sites':len(re.findall(r'\bbar\.sync\b',text))}
    inventories[arch]=inventory
a,b=inventories['compute_120']['baseline'],inventories['compute_120']['candidate']
assert a['global_load_opcode_sites']==b['global_load_opcode_sites']=={'ld.global.nc.u32':22,'ld.global.nc.f32':4}
assert a['barrier_sites']==b['barrier_sites']==5
assert inventories['compute_75']['candidate']['global_load_opcode_sites']['ld.global.nc.v2.u32']==2
assert 'ld.global.nc.v2.u32'not in inventories['compute_75']['baseline']['global_load_opcode_sites']
rows={(x['variant'],x['kernel']):x for x in markers[:-1]}
keys=['registers','local_bytes_per_thread','constant_bytes','static_shared_bytes','dynamic_shared_bytes','max_threads','occupancy_by_threads','context_stack_after']
for name in P['original_entries']:
    assert all(rows['baseline',name][k]==rows['candidate',name][k]for k in keys)
assert not R['resource_warnings']
assert rows['candidate','up_show']['registers']==38 and rows['candidate','up_show']['local_bytes_per_thread']==0
receipts=[]
for path in O.glob('*.exit.json'):
    receipt=h.read(path);assert receipt['returncode']==0 and receipt['error']is receipt['cleanup']is None
    receipts.append({'path':str(path),'sha256':h.sha(path),'returncode':0})
assert len(receipts)==2
C=ROOT/'runs/E126-compiler-closure';C.mkdir(exist_ok=False)
reason='The RTX 5090 target emitted 22 scalar u32 and four scalar f32 global-load sites in both versions, with no wider pair load. The older compute75 target emitted two vector pair loads. The fixed form fails its compute120 emission gate and is closed before application kernels, numerical tests or solve timing. This is a compiler result, not a measured speed regression.'
h.save(C/'report.json',{'id':'E126','at':h.now(),'status':'REJECTED_CLOSED_COMPUTE120_VECTOR_EMISSION_GATE',
    'source_manifest_sha256':h.sha(S/'manifest.json'),'resource_protocol_sha256':h.sha(H/'protocol.json'),'resource_report_sha256':h.sha(H/'report.json'),
    'root_recomputed_failed_gates':failed,'complete_target_load_inventory':inventories,
    'all9_actual_driver_resources_exact':True,'all9_ABI_headers_exact_both_architectures':True,'all8_untargeted_PTX_bodies_exact':True,
    'up_show_actual_resources':rows['candidate','up_show'],'decision':reason,
    'source_contract':'OneCRLFsourceedit:actualpointer8bytealignmentguard selectsuint2read oforiginaladjacentc0/c1u32words;original2scalarreadsotherwise. NoFP/addressset/payload/host/launch/qualitychangeintended.1277952CPUrow/card/baseaddresschecks,notC++/GPUfloatproof.',
    'distinct_from_closed':'E031sharedoffsetcache/E099adjacenthandmemory/E121packedhandwords/E125narrowpermutationtable notcomposed. Fixedpairmetadatareadformclosed,notatuningrescueofthose mechanisms.',
    'closed_form':'No width/guard/pointer/layout/cacheoperator/helper/architecture/kernel-subset/flags/source/quality/sample rescue or forcedinlinePTXretrial. Preservebotharchitectureoutcomes.',
    'reporter_wording_correction':'Adaptedresourcecheckerretainedu16load/handpermtextinthelimitsandautomaticstatusmessagefromE125template. Itsactualsource,emittedvectorpredicate,params,targetentryup_show,resourcechecks andfrozenE126protocolarecorrect. Thisadditiveclosurecorrectstheprosenames;originalreport/checkerretained, no source/compiler/native/gatechange orrepeat.',
    'scope':'Source/history/addresscontractandmodule/PTXresourcechecks only. Noactualapplicationkerneloutputs/numericalcorrectness/throughput/physicaltransaction/performancegain/universalvectorizationclaim.',
    'new_Rust_compilers':1,'new_NVRTC_compiles':2,'owned_module_probe_processes':1,'application_kernel_launches':0,'solver_or_speed_trials':0,
    'all_owned_children_terminal':True,'child_receipts':receipts,'candidate_adopted':False,
    'qualified_live_config':'E080/GPU/compressed/Rayon16/defaultaffinity','RAM_reference_sum_threefixture_medians_ms':10456.4109,
    'last_primary_baseline':'B380','next_unused_primary_baseline':'B381','next_unused_candidate':'E127',
    'accepted_main_live_protected_PTX_D304_HTML_unchanged':True,'all_new_bulk_X_S_readonly_no_T':True,'goal_active':True})
files=[D/'history.json',D/'report.json',S/'manifest.json',S/'baseline.cu',S/'candidate.cu',H/'protocol.json',H/'report.json',H/'probe.rs',C/'report.json']
files += [p for p in O.iterdir()if p.is_file()and p.suffix in['.json','.log','.txt']]
published=[]
for path in files:
    relative=path.relative_to(ROOT/'runs');dst=h.ar.DASHBOARD/'evidence'/relative;dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.exists():assert dst.read_bytes()==path.read_bytes()
    else:shutil.copyfile(path,dst)
    with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+relative.as_posix(),timeout=20)as response:assert response.read()==path.read_bytes()
    published.append({'url':relative.as_posix(),'sha256':h.sha(path)})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);row=next(x for x in status['experiments']if x['id']=='D312')
    row.update(at=h.now(),status='complete',stage='Source and alignment checks complete',correctness='source_contract_pass',evidence=[{'label':'Source, alignment and history audit','url':'evidence/D312-card-bound-pair-scout/report.json'}])
    row=next(x for x in status['experiments']if x['id']=='E126')
    row.update(at=h.now(),status='rejected',accepted=False,stage='Closed: pair loads scalarized on the tested target',correctness='no_device_numerical_trials',reason=reason,
        evidence=[{'label':'Exact source change','url':'evidence/E126-source/manifest.json'},{'label':'Compiled resource and load inventory','url':'evidence/E126-resource/report.json'},{'label':'Root replay and closure','url':'evidence/E126-compiler-closure/report.json'}])
    status.update(updated_at=h.now(),state='running',goal_status='active',active_experiment='E126',stage='Aligned card-bound load form closed; performance search continues',activity=reason+' E080 remains qualified and live. Last baseline B380; next B381.')
    h.ar.atomic_json(h.ar.STATUS,status)
ledger=h.REPO/'research/postflop-gpu-20261016/experiments.md';old=ledger.read_bytes()
assert b'\n## D312/E126 aligned adjacent card-bound metadata loads'not in old
assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=h.REPO,text=True).strip()
entry=f'''

## D312/E126 aligned adjacent card-bound metadata loads - closed at compute120 emission

Previousgoalturnprogress:D309/D310fulltransportexact/negativecopycostandD311/E125full1688direct/86ordinary/18science/138checkpointspassbutfixed3pair-0.856660874%/two-tone+riverguardsclosed,all17children terminal0. Thisturnread-onlyactualaccepted/main/live/protected2PTX/D304HTMLSHA/idle/locks/HEAD0e4b28b92ac2cfbc109351ead89a1ffc8f4c1ef7 revalidated,withoutcreate-onlyauditorrerun. CurrentacceptedE080/GPU/compressed/Rayon16/defaultaffinitylive. Closedworker8/32/newRAMD169,compilelatencyD227,prefixbankE057/E062,cache/arity/otherfamiliesnotreopened. RetainedD276allconvergedcanonicalactionaritiesonly1/2/3(sourceunswitch5..8leadnotadmitted),notaperformancebound.

DistinctnewD312sourceleadpairsadjacentc0/c1readonlyu32card-boundoffsetsinsideoneoriginalhand/card,notE031sharedoffsetcache/E099adjacenthandmemory/E121packedhandwords/E125tablewidth. Bounded100uniqueup_show-containingCUDAhashrecords(alllocalrefs+retainedX/S<=4MiB)nomatchingtargetuint2/vectorloadmarkers;notexhaustivehelper/patch/remoteproof. Original2addressescover8bytes and53wordrow/card0..51bounds;actual8bytepointeralignmentguardsvectorreadandoriginalscalarfallbackcovers4mod8subviews. 1277952CPUaddress/alignmentchecksacross6bases/4096rows/52cards,notGPU/C++numericalproof. NVIDIAprimaryCUDAalignment/vectorcastcontractlinked. FixedofftreeCUDA{M['candidate_sha256']}wholeCRLFinverseexact;allFPexpressions/loops/reductions/payout/barriers/host/ABI/payload/launch/qualityunchangedintended. Mixedwarpvector+fallbackcostproactivelyrecognized;notclaimedfasterfromwidthalone.

Freeze{h.sha(H/'protocol.json')}before1Rustcompiler/1module-onlyprobe,2NVRTC12.9targets120/75,sealedacceptedPTXreused. All9sameABIheaders/8untargetedPTXbodiesexact;all9actualdriverresourcesexact. up_show38regs/local0/static1040/dynamicworst26520/stack1024/max1024/worstoccupancy3,3,3unchanged. Hardcompute120vector-emissiongatefails: entiretargetglobal-loadinventorybotharms22ld.global.nc.u32+4ld.global.nc.f32,5barriers;no widerglobalread. Compute75candidatehas2ld.global.nc.v2.u32whilebaselinehas0;bothoutcomesretained. Targetbodydiffersbyaddressconversionhoisting/virtualregisterchanges,notan alphaexactno-opclaim. Rootindependentlyreplaysall19markers/resources/PTXloadinventories/gate/pins/2terminal0receipts. Notmeasuredperformance/noactualGPUfloatproof/universalvectorizationfailureclaim. No actualCUBINcapture/applicationkernels/directnumerical/ordinary/integratedbuild/primary/fresh16/broad/material/holdout/cumulative/apptrialadmittedafterthehardfailure;lastB380/nextB381unchanged.

Closefixedactual8bytealignmentguard/uint2adjacentcardboundformbeforekernels. No width/guard/pointer/layout/cacheoperator/helper/architecture/kernel-subset/flags/source/quality/sample/forcedinlinePTXrescue. AdaptedresourcecheckerretainedE125u16/handpermwordsinlimits/automaticstatusproseonly;source/actualvectorpredicate/targetup_show/params/resources/frozenE126protocolcorrect. Originalchecker/reportretained,thisclosureadditivelycorrectsprosewithoutgate/native/sourcechanges. Report{h.sha(C/'report.json')};{len(published)}nonbulkHTTPartifactsbyteverified. All2ownedchildren terminal0,accepted/main/live/protected2PTX/D304HTMLexact,serveridle/locksabsent;no newgainadopted. RAMreference10456.4109msseparate,nextcandidateE127. AllnewbulkX/Sreadonly/noT;appendprefixbyteexact/localledger-onlycommit/nopush/noprune;goalactive.
'''
ledger.write_bytes(old+entry.encode());assert ledger.read_bytes()[:len(old)]==old
h.custody();subprocess.run(['git','add','--','research/postflop-gpu-20261016/experiments.md'],cwd=h.REPO,check=True)
assert subprocess.check_output(['git','diff','--cached','--name-only'],cwd=h.REPO,text=True).splitlines()==['research/postflop-gpu-20261016/experiments.md']
subprocess.run(['git','-c','gc.auto=0','commit','-m','research: close aligned card-bound pair form at target compiler gate'],cwd=h.REPO,check=True)
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=h.REPO,text=True).strip()
h.save(C/'publication.json',{'at':h.now(),'local_commit':head,'HTTP_artifacts':published,'report_sha256':h.sha(C/'report.json'),'goal_active':True})
h.custody();h.ar.refuse_active(h.ar.live_status())
h.pin(h.ar.DASHBOARD/'index.html',h.read(ROOT/'runs/D304-tracker-display-metadata/layout-fix.json')['after_sha256'])
for path,url in[(h.ar.STATUS,'status.json'),(h.ar.DASHBOARD/'index.html','index.html'),(C/'report.json','evidence/'+C.name+'/report.json')]:
    with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/'+url,timeout=20)as response:assert response.read()==path.read_bytes()
assert not subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=h.REPO,text=True).strip()
assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=h.REPO,text=True).strip()
assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists()
process=json.loads(subprocess.check_output(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process -Filter 'ProcessId = 26528' | Select-Object ProcessId,ExecutablePath | ConvertTo-Json -Compress"],text=True))
assert process['ExecutablePath'].lower()==r'X:\Dev\GTOpen\target\desktop-runtime\release\gto-server.exe'.lower()
h.save(C/'terminal-audit.json',{'at':h.now(),'status':'E126_CLOSED_ALL_OWNED_WORK_TERMINAL','local_ledger_commit':head,'owned_child_receipts_terminal0':2,
    'accepted_main_live_protected_PTX_D304_HTML_exact':True,'server_idle':True,'live_pid':26528,'locks_absent':True,'research_tracked_clean':True,'HTTP_status_index_report_exact':True,
    'application_kernel_numerical_solver_or_speed_trials':0,'candidate_adopted':False,'last_primary_baseline':'B380','next_unused_primary_baseline':'B381','next_unused_candidate':'E127',
    'X_free_bytes':shutil.disk_usage(ROOT).free,'all_new_bulk_X_S_readonly_no_T':True,'goal_active':True})
print(json.dumps(h.read(C/'terminal-audit.json')),flush=True)
