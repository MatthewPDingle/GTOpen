import ast,json,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists();R=ROOT/'runs/E112-resource';S=ROOT/'runs/E112-source';assert all(h.read(R/'report-r2.json')['gates'].values());assert h.read(ROOT/'runs/D254-constant-host-operand/report-r2.json')['exact_same_frozen_candidate_sources']
A=ROOT/'runs/D233-stride-up-action';H=ROOT/'runs/D256-constant-action';H.mkdir(exist_ok=False)
for name in['corpus.json','discounts.rs']:shutil.copyfile(A/name,H/name)
for arm in['baseline','candidate']:
 p=R/('baseline-compute_120.ptx'if arm=='baseline'else'execution/candidate-compute_120.ptx');shutil.copyfile(p,H/(arm+'.ptx'))
source=(A/'probe.rs').read_bytes().decode().replace('D233','D256');edits=[]
def edit(old,new):
 global source
 assert source.count(old)==1,(old,source.count(old));at=source.index(old);source=source[:at]+new+source[at+len(old):];edits.append((at,old,new))
helper='''
fn region<T:cudarc::driver::DeviceRepr>(s:&Arc<CudaStream>,d:&CudaSlice<T>)->[u64;2]{let(p,_g)=d.device_ptr(s);[p,(d.len()*std::mem::size_of::<T>())as u64]}
fn disjoint(all:&[[u64;2]]){for(i,a)in all.iter().enumerate(){for b in &all[i+1..]{assert!(a[0]+a[1]<=b[0]||b[0]+b[1]<=a[0],"actual bound input/output/symbol overlap");}}}
fn symbol_words(m:&Arc<cudarc::driver::CudaModule>,s:&Arc<CudaStream>)->Vec<u32>{let d=m.get_global("gto_postflop_discounts",s).unwrap();assert_eq!(d.len(),12);let v=s.clone_dtoh(&d).unwrap();v.chunks_exact(4).map(|b|u32::from_le_bytes(b.try_into().unwrap())).collect()}
fn symbol_upload(m:&Arc<cudarc::driver::CudaModule>,s:&Arc<CudaStream>,v:&[f32]){assert_eq!(v.len(),3);let mut raw=m.get_global("gto_postflop_discounts",s).unwrap();assert_eq!(raw.len(),12);let mut typed=unsafe{raw.transmute_mut::<f32>(3).unwrap()};s.memcpy_htod(v,&mut typed).unwrap();}
'''
edit('type Out=BufWriter<File>;','type Out=BufWriter<File>;\n'+helper)
edit('let mut ci=file(dir.join("candidate-inputs.bin"),b"D256_IM1");','let mut ci=file(dir.join("candidate-inputs.bin"),b"D256_IM1");let mut symbols=file(dir.join("symbol-bindings.bin"),b"D256_CONST1");')
edit('let cf=cm.load_function("up_action").unwrap();','let cf=cm.load_function("up_action").unwrap();assert_eq!(symbol_words(&cm,&stream),[0,0,0]);')
anchor='  let mut expected:Option<Vec<Vec<u32>>>=None;'
edit(anchor,'''  let immutable_regions=vec![region(&stream,&dn),region(&stream,&dp),region(&stream,&da),region(&stream,&doff),region(&stream,&dcs),region(&stream,&dc),region(&stream,&drs),region(&stream,&drp),region(&stream,&dl),region(&stream,&dls),region(&stream,&dslot),region(&stream,&dd)];
'''+anchor)
anchor='   device_ranges.push(serde_json::json!({"arm":label,"regions":disjoint_regions(&stream,[&dr,&ds,&dv])}));'
edit(anchor,'''   let regions=disjoint_regions(&stream,[&dr,&ds,&dv]);let mut all_regions=immutable_regions.clone();all_regions.extend_from_slice(&regions);let mut discount_symbol=None;
   if label=="candidate"{let raw=cm.get_global("gto_postflop_discounts",&stream).unwrap();assert_eq!(raw.len(),12);let(ptr,guard)=raw.device_ptr(&stream);drop(guard);discount_symbol=Some([ptr,12]);all_regions.push([ptr,12]);id(&mut symbols,index);words(&mut symbols,&symbol_words(&cm,&stream));symbol_upload(&cm,&stream,&disc);let uploaded=symbol_words(&cm,&stream);assert_eq!(uploaded,fb(&disc),"actual symbol upload");words(&mut symbols,&uploaded);symbols.flush().unwrap();}
   disjoint(&all_regions);device_ranges.push(serde_json::json!({"arm":label,"regions":regions,"immutable_regions":immutable_regions,"discount_symbol":discount_symbol,"kernel_parameter_count":if label=="baseline"{20}else{19}}));''')
edit('unsafe{stream.launch_builder(f).arg(&dn)','unsafe{let mut launch=stream.launch_builder(f);launch.arg(&dn)')
edit('.arg(&mut dv).arg(&dd).arg(&nharg).arg(&maxarg).launch(','.arg(&mut dv);if label=="baseline"{launch.arg(&dd);}launch.arg(&nharg).arg(&maxarg).launch(')
edit('post.push(readf(&stream,&dd));stream.synchronize().unwrap();','if label=="baseline"{post.push(readf(&stream,&dd));}else{let actual=symbol_words(&cm,&stream);words(&mut symbols,&actual);let unchanged_global=readf(&stream,&dd);assert_eq!(unchanged_global,fb(&disc));words(&mut symbols,&unchanged_global);symbols.flush().unwrap();post.push(actual);}stream.synchronize().unwrap();')
edit('for f in [&mut input,&mut baseline,&mut candidate,&mut bi,&mut ci]','for f in [&mut input,&mut baseline,&mut candidate,&mut bi,&mut ci,&mut symbols]')
back=source
for at,old,new in reversed(edits):assert back[at:at+len(new)]==new;back=back[:at]+old+back[at+len(new):]
assert back==(A/'probe.rs').read_bytes().decode().replace('D233','D256');(H/'probe.rs').write_bytes(source.encode());h.save(H/'source-adapter.json',{'id':'D256-source-adapter','at':h.now(),'original_probe_sha256':h.sha(A/'probe.rs'),'adapted_probe_sha256':h.sha(H/'probe.rs'),'namespace_only_before_documented_changes':True,'all_exact_edit_positions_reverse_to_original':True,'changes':[{'position':a,'old':o,'new':n}for a,o,n in edits],'scope':'Same original819cases andall floatdata/ownership/oracle/guard operations. Only candidatefunction ABI removal andconstantupload/readback binding differ. New symbol rawframes andactualallinput/mutable/symbol region evidence additive; no productioncandidate/source/quality change.'})
audit=(A/'audit.py').read_bytes().decode().replace('D233','D256');extra='''
# Original entire819case raw state checks remain above. Bind the new constant explicitly.
sr=Reader(R/'symbol-bindings.bin',b'D256_CONST1');previous=[0,0,0];symbol_words=0;symbol_changes=0
for case,marker in zip(cases,markers[:-1]):
 req(sr.id()==case['id'],'symbol case order');before,uploaded,post,global_after=[list(sr.vec())for _ in range(4)];expected=case['discount_bits'];req(before==previous,'entire prior actual constant image');req(uploaded==post==global_after==expected,'actual symbol upload/postkernel and unused baseline global image exact');symbol_changes+=sum(a!=b for a,b in zip(before,uploaded));symbol_words+=sum(map(len,[before,uploaded,post,global_after]));previous=post
 lengths=[3,case['actions']+8,case['actions']+8,2*(case['actions']+8),case['actions']+8,case['actions']+4,case['actions']+8,6*max(case['hands'],1)+7,2*(case['actions']+8),5+case['actions']*case['hands']+17,case['actions']+8,3]
 for witness in marker['disjoint_device_ranges']:
  imm=witness['immutable_regions'];req(len(imm)==12 and[x[1]for x in imm]==[4*n for n in lengths],'all actual immutable regions complete extents');all_regions=imm+witness['regions'];sym=witness['discount_symbol'];candidate=witness['arm']=='candidate';req(witness['kernel_parameter_count']==(19 if candidate else20),'actual intended kernel ABI binding')
  if candidate:req(isinstance(sym,list)and len(sym)==2 and sym[1]==12,'actual entire module constant region');all_regions=all_regions+[sym]
  else:req(sym is None,'original global discount binding')
  req(all(isinstance(p,int)and p>0 and n>0 and p+n<2**64 for p,n in all_regions),'all actual regions valid');req(all(a+sz<=b or b+bs<=a for i,(a,sz)in enumerate(all_regions)for b,bs in all_regions[i+1:]),'all immutable/mutable/symbol extents disjoint')
sr.eof();req(symbol_words==819*12 and symbol_changes>0,'whole nonvacuous symbol-update corpus')
'''
needle='old.custody()\nreport=';assert audit.count(needle)==1;audit=audit.replace(needle,extra+'\nold.custody()\nreport=',1);audit=audit.replace("'pass_scoped_up_action_raw_equivalence'","'pass_scoped_constant_discount_action_raw_equivalence'").replace("'root_cross_check_only':True","'actual_symbol_words':symbol_words,'nonvacuous_symbol_word_changes':symbol_changes,'root_cross_check_only':True");ast.parse(audit);(H/'audit.py').write_bytes(audit.encode())
old=h.read(A/'protocol.json');cmd=[x.replace(str(A),str(H))for x in old['rustc_command']];files=[Path(__file__),ROOT/'runs/D256-execute-constant-action.py',A/'protocol.json',A/'probe.rs',A/'audit.py',A/'corpus.json',A/'discounts.rs',S/'manifest.json',S/'source-review.json',R/'report-r2.json',ROOT/'runs/D254-constant-host-operand/report-r2.json',ROOT/'runs/E112-host-build/complete.json',ROOT/'epoch/common.py']+[p for p in H.iterdir()if p.is_file()]+[p for p in(ROOT/'reference/accepted-e080-deps').iterdir()if p.is_file()]
h.save(H/'protocol.json',{'id':'D256-constant-action','candidate':'E112','at':h.now(),'status':'FROZEN_PRE_COMPILER_AND_FIRST_CONSTANT_POKER_APPLICATION_KERNELS','rustc_command':cmd,'raw_output':str(H/'output'),'cases':819,'kernel_launches':1638,'raw_file_count':6,'raw_reservation_bytes':12*1024**3,'required_free_bytes':66*1024**3,'input_sha256':{str(p):h.sha(p)for p in files},'scope':'Whole unchanged819actioncases/1638launches/12actualsemanticimmutableimages/full3mutablebuffers andguards,3roles/arity1..17/hand0..1326/blocktails/algorithms/discounts/specialvalues/count0. Candidateconstant3floatwords replace semanticdiscountinput; fullbefore/upload/postconstant andunusedbaselineglobalimages retained. Original20args vsfixedcandidate19(dropoldpointer17). Entireactualimmutable/mutable/symbol regions verifieddisjoint. No solver/speed/sourceactivation. First realE112CFRmath kernels; genuinefailure closesfixedform withoutsource/helper/width/flags/quality/sample rescue. Mechanicalobserver errors additive; completednativecases neverrepeat.'})
for name in['source-adapter.json','protocol.json']:
 p=H/name;dst=h.ar.DASHBOARD/'evidence'/H.name/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
 with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/'+name,timeout=20)as z:assert z.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);s['experiments'].append({'id':'D256','title':'Constant discount action raw numerical controls','kind':'diagnostic','status':'staged','accepted':False,'measurement_epoch':'RAM20261028','stage':'Original819cases plus explicit symbol bindings frozen','reason':'First actual poker arithmetic for E112. Full original raw/edge/guard corpus plus constant pre/upload/post images, original global unchanged, actual disjoint regions and20to19binding. No speed claim.','evidence':[{'label':n,'url':'evidence/'+H.name+'/'+n}for n in['source-adapter.json','protocol.json']]});e=next(x for x in s['experiments']if x['id']=='E112');e.update(stage='Original direct action accuracy matrix frozen',correctness='no_poker_numerical_results_yet');s.update(updated_at=h.now(),active_experiment='D256',stage='Constant discounts: direct action numerical validation',activity='Compile and compare all original819cases with explicit actual module-symbol data. E080 remains live.');h.ar.atomic_json(h.ar.STATUS,s)
print(h.sha(H/'protocol.json'),flush=True)
