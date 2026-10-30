import ast,json,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists();H=ROOT/'runs/E121-resource';S=ROOT/'runs/E121-source';D=ROOT/'runs/D295-hand-word-scout';assert not(H/'protocol.json').exists()
host=r'''
include!("host-encode.rs");
fn host_check(out: &std::path::Path) -> (u64,usize) {
    let mut file=std::io::BufWriter::new(OpenOptions::new().create_new(true).write(true).open(out.join("host-hand-words.bin")).unwrap());
    file.write_all(b"E121_HAND_WORDS_V1\n").unwrap();
    let expected=1_759_602u64+3*1326;
    file.write_all(&expected.to_le_bytes()).unwrap();
    let mut count=0u64;let mut maximum_capacity=0usize;
    let write=|file:&mut std::io::BufWriter<std::fs::File>,a:u32,b:u32,s:u32,w:u32| {
        assert!(a<b&&b<52&&w<0x800000);
        assert_eq!(w&63,a);assert_eq!((w>>6)&63,b);
        assert_eq!(if w>>12==2047 {u32::MAX}else{w>>12},s);
        for x in [a,b,s,w] {file.write_all(&x.to_le_bytes()).unwrap();}
    };
    let same:Vec<u32>=(0..1326).collect();
    for a in 0u32..52 {for b in a+1..52 {
        let c1=vec![a;1326];let c2=vec![b;1326];let words=terminal_hand_words(&c1,&c2,&same);assert_eq!(words.len(),1326);maximum_capacity=maximum_capacity.max(words.capacity());
        for i in 0..1326 {write(&mut file,a,b,same[i],words[i]);count+=1;}
        let sentinel=terminal_hand_words(&[a],&[b],&[u32::MAX]);write(&mut file,a,b,u32::MAX,sentinel[0]);count+=1;
    }}
    let mut c1=Vec::with_capacity(1326);let mut c2=Vec::with_capacity(1326);
    for a in 0u32..52 {for b in a+1..52 {c1.push(a);c2.push(b);}}
    for mode in 0..3 {
        let s:Vec<u32>=(0u32..1326).map(|i|match mode {0=>i,1=>1325-i,_=>if i%7==0{u32::MAX}else{i*73%1326}}).collect();
        let words=terminal_hand_words(&c1,&c2,&s);assert_eq!(words.len(),1326);maximum_capacity=maximum_capacity.max(words.capacity());
        for i in 0..1326 {write(&mut file,c1[i],c2[i],s[i],words[i]);count+=1;}
    }
    assert_eq!(count,expected);assert_eq!(maximum_capacity,1326);file.flush().unwrap();file.get_ref().sync_all().unwrap();(count,maximum_capacity)
}
'''.replace('b"E121_HAND_WORDS_V1\\n"','b"E121_HAND_WORDS_V1\n"')
probe=(ROOT/'runs/E118-resource/probe.rs').read_text().replace('E118_RESOURCE','E121_RESOURCE')
probe=probe.replace('fn main(){',host+'\nfn main(){',1).replace('let ctx=CudaContext::new(0).unwrap();','let (host_records,host_capacity)=host_check(&out);let ctx=CudaContext::new(0).unwrap();',1)
old='"solver_or_speed_runs":0}';new='"solver_or_speed_runs":0,"host_encode_records":host_records,"host_maximum_words_capacity":host_capacity}';assert old in probe;probe=probe.replace(old,new,1);(H/'probe.rs').write_bytes(probe.encode())
reader=r'''import hashlib,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=Path(__file__).resolve().parent;O=H/'execution';h.custody();P=h.read(H/'protocol.json')
for p,d in P['input_sha256'].items():h.pin(p,d)
path=O/'host-hand-words.bin';raw=path.read_bytes();magic=b'E121_HAND_WORDS_V1\n';assert raw.startswith(magic);offset=len(magic);count,=struct.unpack_from('<Q',raw,offset);offset+=8;assert count==1763580;assert len(raw)==offset+count*16;checks=0;records=0
def row(a,b,s):
 global checks,records,offset
 aa,bb,ss,w=struct.unpack_from('<IIII',raw,offset);offset+=16;records+=1
 assert(aa,bb,ss)==(a,b,s);assert 0<=w<0x800000;assert w&63==a;assert(w>>6)&63==b;assert(0xffffffff if w>>12==2047 else w>>12)==s;checks+=5
for a in range(52):
 for b in range(a+1,52):
  for same in range(1326):row(a,b,same)
  row(a,b,0xffffffff)
cards=[(a,b)for a in range(52)for b in range(a+1,52)]
for mode in range(3):
 for i,(a,b)in enumerate(cards):row(a,b,i if mode==0 else(1325-i if mode==1 else(0xffffffff if i%7==0 else i*73%1326)))
assert records==count and offset==len(raw);h.save(H/'host-encode-report.json',{'id':'E121-host-encoding','at':h.now(),'status':'pass_entire_compiled_legal_tuple_domain_and_three_mixed_vectors','records':records,'checks':checks,'legal_tuples':1759602,'mixed_records':3978,'raw_path':str(path),'raw_bytes':len(raw),'raw_sha256':hashlib.sha256(raw).hexdigest(),'host_function_sha256':h.sha(H/'host-encode.rs'),'complete_encoding_decoded_without_ignored_words':True,'GPU_or_FP_results':0,'scope':'Actual candidate pureRusthelper compiled in resourceprobe, whole52choose2cardpairs x1326matchingindices+sentinel,3heterogeneous1326handvectors andallrawwords. Sourcecallsitearguments/lifetimes and integratedGPUencoding/numerical behavior remainunproven. No performance/materialclaim.'});h.custody();print('Host hand-word full-domain raw decode pass:',records,'records',checks,'checks',flush=True)
'''.replace("b'E121_HAND_WORDS_V1\\n'","b'E121_HAND_WORDS_V1\n'")
ast.parse(reader);(H/'host-audit.py').write_bytes(reader.encode())
code=(ROOT/'runs/E118-resource-execute.py').read_text().replace('E118','E121')
needle="h.child([str(H/'probe.exe'),str(O)],O,'probe',600);verify()";assert needle in code;code=code.replace(needle,needle+";h.child([sys.executable,str(H/'host-audit.py')],O,'host-reader',600);verify()",1)
code=code.replace("gates={};tables={};warnings=[]","assert markers[-1]['host_encode_records']==1763580 and markers[-1]['host_maximum_words_capacity']==1326\ngates={'compiled_host_encoding_full_domain':h.read(H/'host-encode-report.json')['records']==1763580};tables={};warnings=[]",1)
old="gates[arch+':architecture_expected_body_change']=not tables[arch]['up_show']['body_alpha_exact']if arch=='compute_120'else all(row['body_alpha_exact']for row in tables[arch].values())"
new="gates[arch+':architecture_expected_body_change']=all(not tables[arch][entry]['body_alpha_exact']for entry in P['target_entries'])";assert old in code;code=code.replace(old,new,1)
code=code.replace('zero-tie fastpath and FP mechanism pending','packed terminal metadata mechanism pending').replace('Finite zero-tie output prefix; actual guarded absence of tot_c/same/valid/tied work and exact baseline-prefix FP provenance plus barrier/caller reviews remain','Lossless privatehandwords; actualonewordload/decode, unusedlegacycardpointees, fulloriginalfloatingrecurrences/callerABI and changedprivatephysicalmetadata proofs remain').replace("'resource_warnings':warnings,","'resource_warnings':warnings,'host_encoding_report_sha256':h.sha(H/'host-encode-report.json'),",1).replace('changed up_show entry','changed fold/show entries')
ast.parse(code);script=ROOT/'runs/E121-resource-execute.py';assert not script.exists();script.write_bytes(code.encode())
oldP=h.read(ROOT/'runs/E118-resource/protocol.json');cmd=[x.replace('E118-resource','E121-resource')for x in oldP['rustc_command']]
files=[Path(__file__),ROOT/'runs/E121-prepare-hand-words.py',ROOT/'runs/E121-prepare-hand-words-r2.py',script,ROOT/'runs/E118-resource-execute.py',ROOT/'runs/E118-resource/probe.rs',ROOT/'epoch/common.py',h.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',h.REPO/'research/postflop-gpu-20261016/resource-feasibility-policy-20261017.md']+[p for folder in [D,S,H]for p in folder.iterdir()if p.is_file()]+[p for p in(ROOT/'reference/accepted-e080-deps').iterdir()if p.is_file()]
h.save(H/'protocol.json',{'id':'E121-resource','at':h.now(),'status':'FROZEN_PRE_ONE_RUST_COMPILER_AND_INTEGER_HOST_DOMAIN_PLUS_MODULE_PROCESS','rustc_command':cmd,'GPU_uuid':oldP['GPU_uuid'],'original_entries':oldP['original_entries'],'target_entries':['up_fold','up_show'],'required_free_bytes':16*1024**3,'input_sha256':{str(p):h.sha(p)for p in files},'host_gate':'Actual byteexactcandidate terminal_hand_words pureRusthelper,1759602legal(singlehand)tuples+3978heterogeneousrecords,whole raw quadruples independent decode;wordVecmaximumcapacity1326. No GPUkernel orfloatmodel.','resource_gates':'Both120/75 fold/showbodieschange, all9ABIs/7untargetedbodiesandresourcesexact. No local/constant/dynamic/stackgrowth/maxthreadloss/defaultlimitloss,positive64/128/256occupancy;register/static/residency changesdisclosed underD108. Sameglobalpayloadcapacity.','mechanism_before_applicationkernels':'Both targetedkernels actualonehandwordglobalread drives card1low6/card2next6/matchupper11 with2047sentinel; legacycardpointer globaldependencies absent; originalFPexpressions/order/barriers/ABI retained. Hostsourceprivate2d_samebuffers packed;allotherphysicalmetadataexact; future rawreaders independentlydecode changedwords,neveromit arrays.','prospective_test_order':'Source/compiledhostintegerdomain/resources/emittedmechanism ->entireoriginalfold/showrawcorpora withonlydeclaredsame_pencodedperarm plusnewboundaries ->ordinary86units ->initialfixed3paircompletecycles exactscience/fingerprints/EV/stops/checkpoints. Fullrawengine/canonical/broad/material/fresh16/holdout/currentRAMcumulative/app mandatorybeforeadoption. No source/encoding/sentinel/mask/bound/width/helper/flags/quality/sample rescue aftergenuinefailure. AllnewbulkX,Sreadonly,noT,liveE080unchanged.','application_kernel_launches_solver_or_speed_samples':0,'candidate_adopted':False})
for p in [D/'preparation-repair-r2.json',H/'protocol.json']:
 key=p.parent.name+'/'+p.name;dst=h.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E121');e.update(stage='Frozen compiled host-domain and resource checks',reason='OneRustcompiler;actualencodinghelper all1,759,602legal tuples+3mixedvectors/complete rawwords, then2NVRTCtargets/module-onlyresources. No candidate GPU numerical or timing results yet.');e['evidence'].append({'label':'Frozen host/resource gates','url':'evidence/'+H.name+'/protocol.json'});s.update(updated_at=h.now(),stage=e['stage'],activity=e['reason']);h.ar.atomic_json(h.ar.STATUS,s)
h.custody();print(h.sha(H/'protocol.json'),flush=True)
