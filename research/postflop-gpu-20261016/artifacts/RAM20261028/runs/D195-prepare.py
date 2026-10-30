import ast, itertools, json, shutil, subprocess, sys, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not any((ROOT/x).exists() for x in ['gpu-run.lock','epoch-sequence.lock'])
E=ROOT/'runs/E102-resource';q=h.read(E/'report.json');assert all(q['gates'].values())
assert h.read(ROOT/'comparisons/E102-parent-load-mechanism/report.json')['status']=='pass_actual_NVRTC_parent_load_hoisting_and_copy_prerequisites'
old=ROOT/'runs/D177-chance';ref=h.read(old/'execution/complete.json')
for p,digest in ref['raw_file_sha256'].items():h.pin(p,digest)
assert h.sha(E/'execution/baseline-compute_120.ptx')==h.sha(old/'baseline.ptx')
H=ROOT/'runs/D195-parent-chance-controls';H.mkdir(exist_ok=False)
folders={'original':ROOT/'runs/D195-original-chance','fanout':ROOT/'runs/D195-parent-fanout'}
for folder in folders.values():folder.mkdir(exist_ok=False)
text=(old/'probe.rs').read_text(encoding='utf-8');a=text.index('impl Down{');b=text.index('struct Up{');before=text[a:b];section=before
helper='''
 fn parent_meta(&self)->Vec<Vec<u32>> {
  let width=self.parents.len()-4;let mut start=vec![0u32;self.r0.len()];let mut count=start.clone();
  start[2]=1;count[2]=width as u32;
  vec![vec![0xdeadbeef,2,0xdeadbeef],start,count,self.cards.clone(),self.childs.clone(),vec![0u32;self.cards.len()]]
 }
'''
section=section.replace('impl Down{','impl Down{'+helper,1)
old_inputs='fn inputs(&self)->Vec<Vec<u32>>{vec![self.parents.clone(),self.childs.clone(),self.cards.clone(),self.r0.clone(),self.r1.clone(),split(&self.m0),split(&self.m1),self.a0.clone(),self.b0.clone(),self.a1.clone(),self.b1.clone()]}'
new_inputs=old_inputs.replace('{vec![','{let mut fields=vec![').replace(']}','];fields.extend(self.parent_meta());fields}')
assert section.count(old_inputs)==1;section=section.replace(old_inputs,new_inputs,1)
assert section.count('_new:bool')==1;section=section.replace('_new:bool','new:bool',1)
needle='  let mut reach0=s.clone_htod(&self.seed0).unwrap();'
assert section.count(needle)==1
section=section.replace(needle,'  let meta=self.parent_meta();let extra:Vec<_>=meta.iter().map(|x|s.clone_htod(x).unwrap()).collect();\n'+needle,1)
launch='unsafe{s.launch_builder(f).arg(&parents).arg(&childs).arg(&cards).arg(&start).arg(&count).arg(&r0).arg(&r1).arg(&m0).arg(&m1).arg(&mut reach0).arg(&mut reach1).arg(&nh0).arg(&nh1).launch(cfg).unwrap();}'
new_launch='''unsafe{if new {
   let parent_count=if c.active(){1i32}else{0};
   s.launch_builder(f).arg(&extra[0]).arg(&start).arg(&parent_count)
    .arg(&extra[1]).arg(&extra[2]).arg(&extra[3]).arg(&extra[4]).arg(&extra[5])
    .arg(&r0).arg(&r1).arg(&m0).arg(&m1).arg(&mut reach0).arg(&mut reach1).arg(&nh0).arg(&nh1)
    .launch(LaunchConfig{grid_dim:(3,1,1),block_dim:(c.threads(),1,1),shared_mem_bytes:0}).unwrap();
  }else{'''+launch[len('unsafe{'):-1]+'''}}
'''
assert section.count(launch)==1;section=section.replace(launch,new_launch,1)
assert section.count('let post=vec![')==1;section=section.replace('let post=vec![','let mut post=vec![',1)
needle=';let out=vec![df32(s,&reach0),df32(s,&reach1)]'
assert section.count(needle)==1;section=section.replace(needle,';post.extend(extra.iter().map(|x|du32(s,x)))'+needle,1)
original=text[:a]+section+text[b:]
assert original.count('cm.load_function("down_chance").unwrap()')==1
original=original.replace('cm.load_function("down_chance").unwrap()','cm.load_function("down_chance_parent").unwrap()',1)
original=original.replace('E086_CONTROL ','E102_ORIGINAL_CONTROL ')
bind='emit(json!({"stage":"binding","baseline_ptx_sha256":"'+q['ptx_sha256']['baseline-compute_120']+'","candidate_ptx_sha256":"'+q['ptx_sha256']['candidate-compute_120']+'","runtime_NVRTC_compiles":0}));'
assert original.count('fn main(){')==1;original=original.replace('fn main(){','fn main(){'+bind,1)
(folders['original']/'probe.rs').write_text(original,encoding='utf-8',newline='\n');shutil.copyfile(old/'corpus.json',folders['original']/'corpus.json')
assert h.read(folders['original']/'corpus.json')['case_count']==425
prefix=text[:text.index('struct Case')].replace('E086_CONTROL ','E102_FAN_CONTROL ')
body=(ROOT/'runs/E102-fanout-probe-body.rs').read_text(encoding='utf-8');assert body.count('fn main() {')==1
body=body.replace('fn main() {','fn main() {'+bind,1)
(folders['fanout']/'probe.rs').write_text(prefix+body,encoding='utf-8',newline='\n')
nh=[(0,0),(0,1),(1,0),(1,1),(31,33),(32,32),(63,65),(127,129),(257,319),(258,320),(1326,1326)]
cases=[]
for (n0,n1),threads,parents,active,mode,pattern in itertools.product(nh,[1,32,64,128,256],[0,1,3,9],[0,1],[0,1,2],range(6)):
    cid=len(cases);cases.append({'id':cid,'descriptor':[n0,n1,threads,parents,active,mode,pattern,(cid*17+73)%1326]})
assert len(cases)==7920
h.save(folders['fanout']/'corpus.json',{'schema':['nh0','nh1','threads','parents','active','float_mode','edge_pattern','salt'],'case_count':len(cases),'cases':cases,'max_case_array_words':2500000,'scope':'Fixed prospective Cartesian matrix; no timing score. Pattern0 empty/skipped-only parents;1/3/7/47-minus-parent-offset/52 representative edges, interspersed nonrepresentative tags1/2/23/u32MAX and poisoned unused card/child fields. Out-of-domain unconsumed tags are guard tests, not physical-deal correctness claims. All consumed card IDs canonical0..51; actual plans separately validated by D194 and future full-engine controls.'})
for folder in folders.values():
    for arm in ['baseline','candidate']:
        p=E/'execution'/(arm+'-compute_120.ptx');h.pin(p,q['ptx_sha256'][arm+'-compute_120']);shutil.copyfile(p,folder/(arm+'.ptx'))
deps=ROOT/'reference/accepted-e080-deps';commands={}
for category,folder in folders.items():
    cmd=['rustc',str(folder/'probe.rs'),'--edition=2021','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-L','dependency='+str(deps)]
    for name,filename in [('cudarc','libcudarc-ba3140064b5903a3.rlib'),('serde_json','libserde_json-83a0670a02a34a4d.rlib')]:cmd+=['--extern',name+'='+str(deps/filename)]
    commands[category]=cmd+['-o',str(folder/'probe.exe')]
h.save(H/'source-review.json',{'id':'D195','at':h.now(),'status':'fixed_unfiltered_original_plus_new_parent_matrix',
    'original':'All425 existing case descriptors, factory/seed/mask/output geometry and original kernel launch remain, including157down/268unchangedup. Only new Down cc adapter/input images and candidate16argument parent launch added; original Up reference path and old Down launch retained. Original425 input/seed/baseline actual output words must match historical retained raw files in full; no old timing sample used.',
    'new_matrix':'7920 prospective cases, all11handcountpairs x5legalwidths1/32/64/128/256 x4parentcounts0/1/3/9 xactive0/1 x3floatprofiles x6fanout/orbit patterns. Nonadjacent parent/child IDs, reversed/scattered slots and original edge orders, heterogeneous cc sizes, empty/skipped-only groups,52canonicalcards/all1326hands, actual nh1=0 reuse, positive/negativezero/subnormal/inf/qNaN/sNaN/maxfinite bits. Consumed metadata bounded; poisoned unused nonrepresentative fields intentionally must not be read.',
    'proof':'Both arms exact sealed resource PTX, zero NVRTC repeat; baseline original down_chance vs candidate down_chance_parent. Entire actual immutable arrays, full physical outputs, parent-source/unique-output/disjointness, native and independent whole-bit copy/mask oracle and complete guards retained. Float arithmetic is absent for the changed path, not presumed equivalent without actual data.',
    'scope':'Finite direct raw matrix only, not full constructor/multi-level engine/lifecycle/quality/save/resume/physicalcanonical/speed/material/capacity qualification. Any true mismatch closes exact E102 form without grouping/tile/width/predicate/source/flags/sample rescue.'})
runner=ROOT/'runs/D195-execute.py';audit=ROOT/'runs/D195-audit.py'
for path in [runner,audit]:ast.parse(path.read_text(encoding='utf-8'))
files=[Path(__file__),runner,audit,ROOT/'runs/E102-fanout-probe-body.rs',ROOT/'epoch/common.py',old/'probe.rs',old/'corpus.json',old/'protocol.json',old/'execution/complete.json',E/'protocol.json',E/'report.json',ROOT/'runs/E102-source/manifest.json',ROOT/'comparisons/E102-parent-load-mechanism/report.json',ROOT/'runs/E102-prerequisite-checkpoint/report.json']+[p for p in ref['raw_file_sha256']]+[p for folder in [H,*folders.values()] for p in folder.iterdir() if p.is_file()]+[p for p in deps.iterdir() if p.is_file()]
files=[Path(p) for p in files]
h.save(H/'protocol.json',{'id':'D195','at':h.now(),'status':'FROZEN_PRE_COMPILERS_AND_APPLICATION_KERNELS','candidate':'E102','folders':{k:str(v) for k,v in folders.items()},'rustc_commands':commands,'input_sha256':{str(p):h.sha(p) for p in files},'original_reference':{'inputs':str(old/'output/inputs.bin'),'baseline':str(old/'output/baseline.bin')},'expected_cases':{'original':425,'fanout':7920},'markers':{'original':'E102_ORIGINAL_CONTROL ','fanout':'E102_FAN_CONTROL '},'required_free_bytes':96*1024**3,'conservative_peak_new_raw_bytes':32*1024**3,'reserved_headroom_bytes':64*1024**3,'max_case_array_words':2500000,'sequence':'Two serialized fresh Rustcompilers and raw GPU processes original425 then prospective7920, followed by one full streaming raw reader. Same sealed120PTX. Zero NVRTC repeat; no app/server change or solve/speed sample. All8345pairs/16690launches required; no filtering/exclusions/extensions or source/predicate/group/width/tile/helper/flags/sample rescue.'})
for filename in ['source-review.json','protocol.json']:
    p=H/filename;dst=h.ar.DASHBOARD/'evidence'/H.name/filename;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
    with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/'+filename,timeout=20) as response:assert response.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=h.read(h.ar.STATUS);item=next(x for x in s['experiments'] if x['id']=='E102');item.update(stage='Frozen full GPU copy/orbit equivalence matrix',correctness='pending_GPU_raw_controls',reason='425 unfiltered original chance cases plus7920prospective parent/orbit/zero/tail/nonfinite cases. All raw outputs, actual inputs, bit-copy oracles and guards must match. No speed sample or adoption.')
    item['evidence'].extend([{'label':name,'url':'evidence/'+H.name+'/'+name} for name in ['protocol.json','source-review.json']]);s.update(updated_at=h.now(),stage=item['stage'],activity='E102 now tests8345rawGPU pairs, including the complete original corpus and fixed multiple-parent/orbit/sNaN/zero-reuse cases. E080/16 remains live; no gain claimed.');h.ar.atomic_json(h.ar.STATUS,s)
ledger=h.REPO/'research/postflop-gpu-20261016/experiments.md'
with ledger.open('a',encoding='utf-8',newline='\n') as f:
    f.write('\n\n### D195 E102 original chance and parent-fanout raw controls frozen\n\nPrevious goal turn progressed by completing D194 all6integer edge/ownership cases and E102 actual/75 compiler plus static parent-load hoisting proof; no application kernels or speed result then. Current accepted/main/live/PTX/idle/locks revalidated. Protocol '+h.sha(H/'protocol.json')+' freezes2freshRustcompilers/2serializedGPUdirectprocesses and1fullstreamingreader. All425original chance cases157down/268up retained, exactdescriptors/factories/seeds/oldlaunches; onlycandidateDownparent adapter/6extra immutable arrays and new16arglaunch. Originalactual inputs/seeds/baselinefulloutputs must match all425retained D177records, no timing pooling.\n\nProspective7920matrix is11handcountpairs(0..1326)x5widths1/32/64/128/256x4parentcounts0/1/3/9xactive0/1x3floatprofilesx6edge/orbitpatterns. Heterogeneous0/1/3/7/47/52fanouts, scattered/reversed IDs/slots/order, empty/skippedonlyparent, cc tags1/2/23/u32MAXwithpoisonedUNCONSUMEDchild/cardfields, all52cards/full1326hands, actualnh1=0reuse, signedzero/subnormal/inf/qNaN/sNaN/extremebits. Poison cases are guardtests, not physicaldeal claims. Botharms exactsealedE102120PTX, noNVRTCrepeat. Completephysicaloutputs/allactualimmutablearrays/fullguards and independent exactbitcopy/maskoracle everyfloatprofile; perlevelcanonicalD194mapping remains separateproof. Newraw reservation32GiB+64GiBheadroom onX, oldreference onlyreadonly. No sourceactivation/solve/speed/adoption. Truefailure closesexactE102formwithoutgrouping/tile/width/guard/helper/source/flags/sample rescue. Fullengine/canonicalphysicalstate/ordinary/complete1%/strictfixture/fresh16/broad/material/capacity/holdout/cumulative/application gates remain. E080/16liveunchanged, lastprimaryB313, goalactive.\n')
h.custody();subprocess.run(['git','add','--','research/postflop-gpu-20261016/experiments.md'],cwd=h.REPO,check=True);subprocess.run(['git','commit','-m','research: freeze complete parent chance raw controls'],cwd=h.REPO,check=True)
print(json.dumps({'protocol_sha256':h.sha(H/'protocol.json'),'cases':{'original':425,'fanout':7920},'kernel_launches':16690,'NVRTC_repeats':0}),flush=True)
