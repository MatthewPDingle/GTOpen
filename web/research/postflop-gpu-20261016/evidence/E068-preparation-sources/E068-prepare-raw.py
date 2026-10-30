"""Freeze complete first up_chance raw controls for exactE059source asE068."""
import ast,collections,json,re,struct,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();old.ar.refuse_active(old.ar.live_status());assert not (ROOT/'gpu-run.lock').exists()
RES=ROOT/'runs/E068-resource';S=ROOT/'runs/E068-source';RP=old.read(RES/'protocol.json');resource=old.read(RES/'report.json')
for p,h in RP['input_sha256'].items():old.pin(p,h)
assert resource['status']=='pass_resource_and_actual_mechanism_prerequisites' and all(resource['gates'].values())
for label in ['rustc','probe']:
 e=old.read(RES/'execution'/(label+'.exit.json'));assert e['returncode']==0 and e['error'] is e['cleanup'] is None
old.pin(RES/'blocker-branch-proof.json',resource['blocker_branch_proof_sha256']);branch=old.read(RES/'blocker-branch-proof.json');assert len(branch['baseline']['mask_dependent_branches'])==7 and not branch['candidate']['mask_dependent_branches'] and all(branch['gates'].values())
R=ROOT/'comparisons/E068-resource-root-check';assert not R.exists();R.mkdir();old.save(R/'report.json',{'id':R.name,'at':old.now(),'status':'pass_feasibility_abi_actual_blocker_branch_removal','resource_report_sha256':old.sha(RES/'report.json'),'blocker_branch_proof_sha256':old.sha(RES/'blocker-branch-proof.json'),'actual_mask_branch_sites':[7,0],'abi_parameters':15,'other8entries_exact_actual_and_sm75':True,'disclosed_resources':resource['details'],'source_and_address_binding_sha256':old.sha(S/'address-proof-binding.json'),'new_native_executions':0,'application_kernel_launches':0,'performance_measured':False,'candidate_accepted':False,'limits':'Root receipt/input/compiler replay only, not external independent review or dynamicSASS/latency/equivalence/materialcost proof. Actualtargetmaskbranchremoval passes; otherGPUsunqualified.'})
H=ROOT/'runs/E068-kernel-control';assert not H.exists();H.mkdir()
for v in ['baseline','candidate']:(H/(v+'.ptx')).write_bytes((RES/'execution'/(v+'-compute_120.ptx')).read_bytes())
probe=(ROOT/'runs/E068-raw-probe.rs').read_text();args=re.findall(r'\.arg\(&([^)]*)\)',probe);assert args==['nodes','start','count','cs','cc','card','child','perm','inv','mask','hp','slot','mut cfv','nh','stride'];(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
canon=struct.unpack('<I',struct.pack('<f',1/46))[0];cases=[]
def add(n,w,perm,group,threads=128,mode=0,pattern=0,active=1,pad=5,inv=canon,mask_style=0,salt=None):
 i=len(cases);salt=(i*29+7)%1326 if salt is None else salt;cases.append({'id':i,'descriptor':[1,n,pad,threads,active,mode,perm,w,pattern,salt],'inv_bits':inv,'mask_style':mask_style,'group':group})
widths=[0,1,2,3,7,8,9,16,17,31,32,33,51,52,53,64]
for ni,n in enumerate([0,1,31,32,33,63,64,65,127,128,129,255,256,257,511,512,513,1023,1024,1326]):
 for wi,w in enumerate(widths):
  for perm in [0,1]:add(n,w,perm,'boundary_dims_spans',pattern=(ni+wi)%3)
for card in range(52):add(1326,1,0,'each_card_full_canonical',pattern=3,salt=card)
for w in [1,2,3,4,7,8,9,16,17,31,32,33,51,52,53,64]:
 for perm in [0,1]:
  for mode in [1,2]:
   for pattern in [0,1,2,3]:add(257,w,perm,'value_stress',mode=mode,pattern=pattern)
for threads in [1,32,64,256]:
 for n in [7,129,513]:
  for w in [1,3,8,17,52,64]:
   for perm in [0,1]:add(n,w,perm,'supplementary_threads',threads=threads,pattern=2)
for w in [0,1,8,17,52,64]:
 for perm in [0,1]:add(129,w,perm,'zero_count',active=0,pattern=3)
for inv in [0,0x80000000,0x7f800000,0xff800000,0x7fc01234,0xffc05678,0x3f800000,0xbf800000]:
 for w in [0,1,17,52]:
  for perm in [0,1]:add(129,w,perm,'inverse_stress',mode=1,pattern=3,inv=inv)
for mask_style in [1,2]:
 for inv in [canon,canon^0x80000000,0,0x80000000,0x3f800000,0xbf800000,0x7f800000,0x7fc01234]:
  for w in [1,2,17,52,64]:
   for perm in [0,1]:
    for mode in [0,1,2]:add(257,w,perm,'all_blocked' if mask_style==1 else 'all_unblocked',mode=mode,pattern=4 if mask_style==1 else 5,inv=inv,mask_style=mask_style)
for n,pad in [(1,0),(1,1325),(129,0),(257,1069),(1326,0)]:
 for w in [0,1,3,52]:
  for perm in [0,1]:add(n,w,perm,'row_stride',pad=pad,pattern=1)
assert len(cases)==1788
assert dict(collections.Counter(c['group'] for c in cases))=={'boundary_dims_spans':640,'each_card_full_canonical':52,'value_stress':256,'supplementary_threads':144,'zero_count':12,'inverse_stress':64,'all_blocked':240,'all_unblocked':240,'row_stride':40}
assert len({tuple(c['descriptor'])+(c['inv_bits'],c['mask_style']) for c in cases})==1788
preflight=[];estimated=0
for c in cases:
 f,n,pad,threads,active,mode,perm,w,pattern,salt=c['descriptor'];stride=n+pad;nn=w+10;seed=(w+12)*stride+17
 assert f==1 and 0<=n<=1326 and 0<=w<=64 and 0<=pad<=1325 and stride>=n and threads in [1,32,64,128,256] and active in [0,1] and mode in [0,1,2] and perm in [0,1]
 assert 2*stride+n<=seed and (not n or not w or ((w+3)*stride+n<=seed and 4*stride>=2*stride+n))
 # Every four-table rotation maps each valid hand0..n-1 to another valid hand, including blocked hands.
 preflight.append({'id':c['id'],'all_child_row_addresses_bounded_disjoint_for_all_hands':True,'permutations_total_by_modulo_n_or_nohand':True,'full_seed_words_initialized':seed,'maximum_child_end_exclusive':(w+3)*stride+n if w and n else None})
 immutable=3+4*nn+3*(w+6)+4*(max(n,1)+3)+(4*n+7);estimated+=4*(3*immutable+3*seed)+1000
assert estimated<2*1024**3
old.save(H/'preflight-address-geometry.json',{'at':old.now(),'cases':preflight,'count':1788,'all_pass':True,'new_cuda_launches':0,'rule':'For everyhand/permutation including blockers, childslot>=4,parent2,stride>=nh,idx<nh,totalinitializedCFVrows. Zero-handcasesloadnone. Nativechecksactualeveryaddressagain beforeeachlaunch; rootreplaysactualrawarrays afterwards.'})
old.save(H/'corpus.json',{'id':'E068-up-chance-raw-corpus','at':old.now(),'status':'FROZEN_PRE_FIRST_NUMERICAL_LAUNCH','case_count':1788,'kernel_launches':3576,'cases':cases,'groups':dict(collections.Counter(c['group'] for c in cases)),'descriptor_schema':['family1','hands','row_stride_padding','threads','active_count','float_mode','permutations','chance_width','card_pattern','salt'],'binary_schema':'inputs:E068_IN1(8B),percaseu32id,descriptorvec(lengthu64thenwordsu32),immutableveclist(countu32then12vectors),seedveclist(countu32then1CFVvector). Eacharm:E068_OUT1(9B),percaseid,12actualpostinputvectors,1fullCFVoutputvector. u64masks arelow/highu32halves. AllLEfullwords; nofingerprints substitute.','immutable_vectors':['nodes','chance_start','chance_count','cards','children','permutations','inverse_bits','mask_halves','card_a','card_b','hand_permutation','cfv_slot'],'max_raw_bytes':2*1024**3,'max_case_array_words':1000000,'estimated_raw_bytes_with_record_overhead':estimated,'reference_corpus_sha256':old.sha(ROOT/'runs/E048-kernel-control/corpus.json'),'reference_source_only':'Reuses previous raw harness constructors/serialization, not old outcomes; both current kernels use same15parameter production ABI. Newfixedcasesinclude allblocked/unblocked/negativezeroinverse/stride and validignoredread preflights.','limits':'FiniteactualRTX5090matrix; oneparentperrawcase,fullintegratedgraphs later. Duplicatehands/allblocked masks andchancewidth53/64 are synthetic bounded raw stress, not supported gameplay/inputcapacity claims. Canonicaleachcardmatrix uses1326uniquehands; otherGPUand>2^32spans unqualified.'})
old.save(H/'source-review.json',{'at':old.now(),'id':'E068-raw-source-review','root_review_only':True,'production_abi_arguments':args,'current_resource_ptx_loaded_exact':True,'actual_read_contract':'AllhostCFVseeds initialized; every actual child/permutation index includingblocked precheckedbeforelaunch,childrowsdisjointparentwrites. Actualimmutablebuffers readback andexactcomparison separately perarm; fullrawCFV includingallguards retained.','floating_contract':'Alloriginalorderedusedadds/oldaccbits mustmatch includingNaNpayload/signedzero/overflow/subnormal; noepsilon/normonlytest. Extraignoredarithmetic not scored; no per-kernel timing.','case_count':1788,'kernel_launches':3576,'scope':'ActualGPUonly; unchangedfallbackABIcompile is not fallbacknumerical/performancequalification.'})
prior=ROOT/'runs/E048-kernel-control';runner=(prior/'execute.py').read_text().replace('E048','E068').replace("HERE.parent/'small-gain-confirmation-plan'","HERE.parent/'accepted-E051'").replace('import common as old','import common_e051 as old').replace('one-shot direct up_action comparison','one-shot direct up_chance comparison').replace("=='pass_resource_feasibility_only'","=='pass_resource_and_actual_mechanism_prerequisites'")
needle="m['guards_exact']";runner=runner.replace(needle,needle+" and m['inv_bits']==c['inv_bits'] and m['mask_style']==c['mask_style']")
ast.parse(runner);(H/'execute.py').write_text(runner,encoding='utf-8',newline='\n')
P=old.read(prior/'protocol.json');P.update(id='E068-kernel-control',at=old.now(),status='FROZEN_PRE_FIRST_APPLICATION_KERNEL',resource_report=str(RES/'report.json'),raw_output=str(H/'evidence'),expected_cases=1788,expected_launches=3576,max_raw_evidence_bytes=2*1024**3,source_manifest_sha256=old.sha(S/'manifest.json'),current_mechanism_resource_report_sha256=old.sha(RES/'report.json'),resource_root_sha256=old.sha(R/'report.json'),address_preflight_sha256=old.sha(H/'preflight-address-geometry.json'),failure_policy='Preserveallfailuresandraw; no source/guard/mask/shape/width/placement variants or extra cases/samples. Numericalfailure closesexactE059/E068form. No solver timing beforefullraw/rootpasses.',criterion='EveryfullrawCFVoutputbit/actualimmutableword/guardexact. Also everyextraignoredaddressvalidinitialized/disjointbeforesubmission. Allblocked/unblocked,signedzero/nonfinite/overflow/subnormal,all52cardfull1326matrix,zerohands/count,width/tail/thread/rowstride controls. No historical outcome/timing reuse.')
P['rustc_command']=[x.replace(str(prior),str(H)) for x in P['rustc_command']]
paths=[*H.iterdir(),*S.iterdir(),Path(__file__),ROOT/'runs/E068-make-probe.py',ROOT/'runs/E068-raw-probe.rs',RES/'protocol.json',RES/'report.json',RES/'blocker-branch-proof.json',R/'report.json',ROOT/'runs/D097-chance-selection/protocol.json',ROOT/'runs/D097-chance-selection/report.json',ROOT/'runs/D108-resource-feasibility-audit/docket.json',ROOT/'runs/D108-resource-feasibility-audit/commit.json',old.REPO/'research/postflop-gpu-20261016/resource-feasibility-policy-20261017.md',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',ROOT/'runs/accepted-E051/common_e051.py']
P['input_sha256']={str(p):old.sha(p) for p in paths if p.is_file()}|{p:h for p,h in RP['input_sha256'].items() if Path(p).suffix in ['.rlib','.lib']};old.save(H/'protocol.json',P)
published={}
for folder in [H,R,RES]:
 for p in folder.rglob('*'):
  if not p.is_file() or '__pycache__' in p.parts or p.suffix in ['.exe','.pdb','.bin']:continue
  key='evidence/'+folder.name+'/'+p.relative_to(folder).as_posix();dst=old.ar.DASHBOARD/key;dst.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists():assert dst.read_bytes()==p.read_bytes()
  else:dst.write_bytes(p.read_bytes())
  with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
  published[key]=old.sha(p)
old.save(H/'pre-execution-publication.json',{'at':old.now(),'published':published,'http_bytes_verified':True,'new_application_kernel_executions':0,'raw_reservation_bytes':2*1024**3})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);e=next(e for e in st['experiments'] if e['id']=='E068');e.update(stage='Fixed1788paired full raw up_chance controls',reason='Actual7blockerbranches to0;15parameterABI/8otherentries exact andfeasibility passes. Registers30to40roundedallocationwarning;occupancyunchanged. Everyrawreadbounded/initialized/disjointpreflight;1788fixedpairswithallblocked/unblocked andbitstress beforecomplete-solvespeed.');e['evidence'].extend([{'label':'Fresh root resources/mechanism','url':'evidence/'+R.name+'/report.json'},{'label':'First full numerical protocol','url':'evidence/'+H.name+'/protocol.json'},{'label':'Concrete extra-read geometry preflight','url':'evidence/'+H.name+'/preflight-address-geometry.json'}]);st.update(updated_at=old.now(),stage='E068 full raw numerical matrix',activity='1788pairedcases/3576launches,allfullCFV/input/guardbits. Extraignoredreadscheckedbeforeeachlaunch; actualno-material-cost/fullsolveperformance notyetproven.');old.ar.atomic_json(old.ar.STATUS,st)
old.custody();print(json.dumps({'protocol_sha256':old.sha(H/'protocol.json'),'cases':1788,'kernel_launches':3576,'estimated_raw_bytes':estimated,'actual_blocker_branches':[7,0]}),flush=True)