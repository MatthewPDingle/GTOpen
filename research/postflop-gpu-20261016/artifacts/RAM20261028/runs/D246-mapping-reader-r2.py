import json,re,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D246-cluster-resource'
def inspect(t):
 a=t.index('.visible .entry d246_cluster_transport(');t=t[a:];assert '.reqnctapercluster 2, 1, 1'in t
 assert t.count('barrier.cluster.arrive;')==t.count('barrier.cluster.wait;')==2
 m=re.search(r'mapa\.u64\s+(%rd\d+),\s*(%rd\d+),\s*(%r\d+);',t);assert m
 mapped,source,rank=m.groups();x=re.search(r'xor\.b32\s+'+re.escape(rank)+r',\s*(%r\d+),\s*1;',t[:m.start()]);assert x
 assert re.search(r'mov\.u32\s+'+re.escape(x[1])+r',\s*%cluster_ctarank;',t[:x.start()])
 cv=re.search(r'cvta\.shared\.u64\s+'+re.escape(source)+r',\s*(%rd\d+);',t[:m.start()]);assert cv
 assert re.search(r'mov\.u64\s+'+re.escape(cv[1])+r',\s*scratch;',t[:cv.start()])
 post=t[m.end():];ad=re.search(r'add\.s64\s+(%rd\d+),\s*'+re.escape(mapped)+r',\s*(%rd\d+);',post);assert ad
 ld=re.search(r'ld\.u32\s+(%r\d+),\s*\['+re.escape(ad[1])+r'\];',post[ad.end():]);assert ld
 assert re.search(r'st\.global\.u32\s+\[%rd\d+\],\s*'+re.escape(ld[1])+r';',post)
 mw=re.search(r'mul\.wide\.u32\s+'+re.escape(ad[2])+r',\s*(%r\d+),\s*4;',post[:ad.start()]);assert mw;j=mw[1]
 inc=re.search(r'add\.s32\s+'+re.escape(j)+r',\s*'+re.escape(j)+r',\s*(%r\d+);',post);assert inc
 assert re.search(r'mov\.u32\s+'+re.escape(inc[1])+r',\s*%ntid\.x;',t[:m.start()])
 bound=re.search(r'setp\.lt\.u32\s+(%p\d+),\s*'+re.escape(j)+r',\s*(%r\d+);',post);assert bound
 assert re.search(r'ld\.param\.u32\s+'+re.escape(bound[2])+r',\s*\[d246_cluster_transport_param_2\];',t)
 return {'mapping':m[0],'peer_rank_xor':x[0],'generic_shared_conversion':cv[0],'mapped_base_plus_hand_byte_offset':ad[0],'remote_load':ld[0],'remote_value_stored_unchanged':True,'thread_stride_increment':inc[0],'wordcount_parameter_bound':bound[0],'two_publication_lifetime_cluster_sync_pairs':True}
if len(sys.argv)==1:
 h.custody();p=h.read(H/'report.json');assert[k for k,v in p['gates'].items()if not v]==['PTX_cluster_mapping_present']
 h.save(H/'mapping-reader-plan-r2.json',{'at':h.now(),'status':'FROZEN_PRE_READ_ONLY_MAPPING_DECODER','input_sha256':{str(f):h.sha(f)for f in [Path(__file__),H/'protocol.json',H/'report.json',H/'primitive.cu',H/'execution/primitive-compute_120.ptx',H/'execution/rustc.exit.json',H/'execution/probe.exit.json',ROOT/'epoch/common.py']},'original_failure':'Literalmapa.shared::cluster recognizer rejects emitted documentedgenericaddress mapa.u64; all40resourcegates andbarrierspassed, no appkernels yet.','unchanged_intended_gate':'Actual peer-rank XOR1 maps sharedscratch pointer andresultaddresses actualgenericremoteu32load feedingunchangedglobalstore, boundedstridedwordcount. Both clusterpublication/lifetime barriersremain.','official_source':'https://docs.nvidia.com/cuda/archive/12.9.0/parallel-thread-execution/index.html#data-movement-and-conversion-instructions-mapa','correction_scope':'PTX8.8 documents optionalspace qualifier, genericshared-pointer mapa.u64 legal. Preserve originalfailedreport/protocol/source/binary/PTX. No compiler/module/native repetition orshader/flags/feature/resource/numericalgate change. Wrongrank/removedlifetimebarrier fixtures testactualreader.'});print(h.sha(H/'mapping-reader-plan-r2.json'),flush=True);sys.exit(0)
assert len(sys.argv)==2;P=h.read(H/'mapping-reader-plan-r2.json');h.pin(H/'mapping-reader-plan-r2.json',sys.argv[1]);h.custody()
for p,d in P['input_sha256'].items():h.pin(p,d)
t=(H/'execution/primitive-compute_120.ptx').read_text();w=inspect(t);bad,n=re.subn(r'(xor\.b32\s+%r\d+,\s*%r\d+,\s*)1;',r'\g<1>0;',t);assert n==1
for label,mutant in [('wrong_peer_rank',bad),('missing_exit_lifetime_barrier',t[:t.rfind('barrier.cluster.arrive;')]+t[t.rfind('barrier.cluster.wait;')+len('barrier.cluster.wait;'):])]:
 try:inspect(mutant)
 except AssertionError:pass
 else:raise AssertionError(label+' fixture not rejected')
old=h.read(H/'report.json');gates=old['gates']|{'PTX_cluster_mapping_present':True};assert all(gates.values())
h.save(H/'report-r2.json',{'id':'D246-resource-r2','at':h.now(),'status':'pass_original_cluster_primitive_resource_and_mapped_operand_gate','original_failed_report_sha256':h.sha(H/'report.json'),'mapping_reader_plan_sha256':sys.argv[1],'all_original_resource_criteria_unchanged':True,'gates':gates,'resources':old['resources'],'actual_generic_address_mapping_witness':w,'negative_fixtures':['wrongpeerXOR','missingexitlifetimebarrier'],'PTX_sha256':old['PTX_sha256'],'binary_sha256':old['binary_sha256'],'no_completed_compiler_module_or_native_cases_repeated':True,'appkernels_solves_speed_samples':0,'candidate_accepted':False,'limits':'Resource/structuraloperandwitness only; original132casepeertransport/lifetime/graph controls remainmandatory. No FPCFR/sharedscan/solveroptimization orspeedproof.'})
for name in ['mapping-reader-plan-r2.json','report-r2.json','header-replay.json']:
 p=H/name;dst=h.ar.DASHBOARD/'evidence'/H.name/name;assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/'+name,timeout=20)as z:assert z.read()==p.read_bytes()
print('Documented generic mapa.u64 peer-address chain and all original resource gates passed.',flush=True)
