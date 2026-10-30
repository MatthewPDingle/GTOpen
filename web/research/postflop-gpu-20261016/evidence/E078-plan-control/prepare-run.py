"""Freeze and execute compiled full host metadata controls for the exact fold marker."""
from pathlib import Path
import ast,json,shutil,subprocess,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3 and shutil.disk_usage('T:\\').free>=53687091200
S=R/'runs/E078-source';D=R/'runs/D128-fold-parent';assert old.read(R/'runs/D129-ABI-pointer-audit/report.json')['admit_frozen_E078_raw_controls']
H=R/'runs/E078-plan-control';M=R/'runs/E078-plan-control-manager';A=R/'runs/D092-action-arity-order';F=R/'runs/E077-plan-control';assert not H.exists()and not M.exists();H.mkdir()
for n in['game.rs','field-schema.json','fixture-0.json','fixture-1.json','fixture-2.json']:shutil.copyfile(F/n,H/n)
for n in['accepted-plan.rs','candidate-plan.rs']:shutil.copyfile(A/'accepted-plan.rs',H/n);old.pin(H/n,old.BASE['crates/solver/src/gpu/plan.rs'])
helper=(S/'mark-fold.rs').read_text(encoding='utf-8');mod=(S/'candidate-mod.rs').read_text(encoding='utf-8');assert helper in mod;(H/'mark-fold.rs').write_text(helper,encoding='utf-8',newline='\n')
probe=(F/'probe.rs').read_text(encoding='utf-8').replace('E077','E078');probe=probe.replace('use std::{fs::{File,OpenOptions},io::{BufWriter,Write}};','use std::{fs::{File,OpenOptions},io::{BufWriter,Write}};\nuse candidate::GpuPlan;\ninclude!("mark-fold.rs");')
oldline='assert_eq!(a.riv_sorted_idx,b.riv_sorted_idx,"public untagged plan indices");candidate::tag_prefix_reads(&mut b);';newline='assert_eq!(a.node_na,b.node_na,"public unmarked plan values");mark_fold_producers(&mut b);';assert probe.count(oldline)==1;probe=probe.replace(oldline,newline)
for index,name,allow in[(24,'node_na',True),(46,'riv_sorted_idx',False)]:
 before=f'count+=field(&mut f,{index},"{name}",&a.{name},&b.{name},{str(not allow).lower()});';after=f'count+=field(&mut f,{index},"{name}",&a.{name},&b.{name},{str(allow).lower()});';assert probe.count(before)==1;probe=probe.replace(before,after)
probe=probe.replace('all_non_tag_fields_bitwise_equal','all_non_marker_fields_bitwise_equal')
a=mod.index('    #[test]\n    fn fold_producer_markers_are_private_and_exact()');b=mod.index('    fn reach_reuse_solver(',a);unit=mod[a:b];probe+='\n#[cfg(test)]mod marker_controls {use super::*;use game::Spot;\n'+unit+'}\n';(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
replay=r'''"""Independently compare all actual53fields/caps and precise fold marker against accepted dumps."""
import array,json,struct,sys
from pathlib import Path
def replay(path,case,reference):
 checks=0;words=0;markers=0;folds=None
 def ck(v,label):
  nonlocal checks
  assert v,(case,label);checks+=1
 def vec(f):
  n,=struct.unpack('<Q',f.read(8));ck(n<100000000,'bounded vector');v=array.array('Q');v.fromfile(f,n);ck(len(v)==n,'complete vector');return v
 with Path(path).open('rb')as f,Path(reference).open('rb')as g:
  ck(f.read(16)==b'E078-PLAN-RAW1\0\0'and g.read(16)==b'D092-PLAN-RAW1\0\0','magic');ck(f.read(8)==g.read(8)==struct.pack('<II',case,53),'case and schema');sa,sb=struct.unpack('<QQ',f.read(16));ra,rb=struct.unpack('<QQ',g.read(16));ck(sa==sb==ra==rb,'allactualstruct sizes')
  for field in range(53):
   ck(f.read(4)==g.read(4)==struct.pack('<I',field),'fieldid');ca,cb,wa,wb=[vec(f)for _ in range(4)];rca,rcb,rwa,rwb=[vec(g)for _ in range(4)];ck(ca==cb==rca,'allactualfieldcapacities matchaccepted');ck(wa==rwa,'all53baselinefieldvalues matchaccepted');words+=len(wa)
   if field==13:ck(wa[0]==len(wa)-1,'fold vector');folds=wa[1:]
   if field==24:
    ck(folds is not None and wa[0]==len(wa)-1,'arity/fold framing');expected=wa[:]
    for node in folds:ck(node<wa[0]and wa[node+1]==0,'onlyoriginalzeroarityfold entry');expected[node+1]=(1<<64)-1;markers+=1
    ck(wb==expected,'allactualprivate marker bits onlyfolds')
   else:ck(wa==wb,'all52otherfullfieldvalues exact')
  ck(vec(f)==vec(g),'allnodekind words exact');ck(vec(f)==vec(g),'fullchildslot words exact');ck(f.read(1)==g.read(1)==b'','complete rawendpoints')
 native=[json.loads(x.split('E078 ',1)[1])for x in Path(path).with_suffix('.stdout.log').read_text(encoding='utf-8').splitlines()if x.startswith('E078 ')];ck(len(native)==1,'one nativecase');v=native[0];ck(v['id']==case and v['fields']==53 and v['baseline_words']==words and v['all_non_marker_fields_bitwise_equal']and v['all_vec_capacities_equal']and v['gpu_executions']==0,'nativeinventory')
 return {'case':case,'root_checks':checks,'accepted_baseline_words':words,'exact_private_fold_markers':markers,'all52otherfields_and53capacities_and_structs_exact':True,'all53baselinefields_match_retained_accepted':True,'native_summary':v}
''';(H/'replay.py').write_text(replay,encoding='utf-8',newline='\n')
execute=r'''from pathlib import Path
import json,shutil,sys
H=Path(__file__).resolve().parent;R=H.parent.parent;sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as old
from replay import replay
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json');B=H/'build';E=H/'execution'
def verify():
 for p,h in P['input_sha256'].items():old.pin(p,h)
 old.custody()
verify();assert not B.exists()and not E.exists()
with old.ar.exclusive_lock(R/'gpu-run.lock'):
 old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3;B.mkdir();E.mkdir()
 for label,cmd in P['compile_commands'].items():old.child(cmd,B,label,old.env(),600);verify()
 old.child([str(B/'tests.exe'),'--test-threads=1'],E,'unit',old.env(),300);verify();unit=(E/'unit.stdout.log').read_text(encoding='utf-8');assert 'test result: ok.'in unit and 'fold_producer_markers_are_private_and_exact ... ok'in unit
 results=[]
 for spec in P['cases']:
  case=spec['id'];label=f'case-{case:02d}';raw=E/(label+'.bin');old.pin(spec['reference'],spec['reference_sha256']);old.ar.refuse_active(old.ar.live_status());old.child([str(B/'probe.exe'),str(case),str(raw)],E,label,old.env(),240);verify();r=replay(raw,case,spec['reference']);r.update(raw_sha256=old.sha(raw),raw_bytes=raw.stat().st_size);old.save(E/(label+'.replay.json'),r);results.append(r);print(json.dumps({k:r[k]for k in['case','root_checks','accepted_baseline_words','exact_private_fold_markers']}),flush=True)
 report={'id':'E078-plan-control','at':old.now(),'status':'pass_compiled_private_fold_marker_full_metadata','protocol_sha256':sys.argv[1],'cases':results,'original_public_plan_values_unchanged':True,'all53baselinefields_match_retained_accepted':True,'all52otherfields_values_and_all53capacities_structs_exact':True,'exact_private_marker_count':sum(x['exact_private_fold_markers']for x in results),'baseline_encoded_words':sum(x['accepted_baseline_words']for x in results),'root_checks':sum(x['root_checks']for x in results),'raw_bytes':sum(x['raw_bytes']for x in results),'source_unit_and_both_plan_units_pass':True,'native_processes':13,'Rust_compilers':2,'all_owned_children_terminal':True,'GPU_or_solver_executions':0,'performance_measured':False,'source_activated':False,'candidate_accepted':False,'source_main_live_PTX_custody_pass':True,'limits':'Two exactaccepted source plan modules/customacceptedgame/retainedRLIB and exactcandidatehostmarker plus sourceunit compiled off-tree. Fullactual53field/capacity/struct/reference replay, not compiledintegratedGpuSolverconstructor/kernelcaller, GPUstate/numeric/speed ormaterialproof. AllGPUraw/broad/completecycle/material gates remain.'};old.save(H/'report.json',report);verify()
print('E078host controls terminal: all12fullmetadata maps and units pass',flush=True)
''';ast.parse(execute);ast.parse(replay);(H/'execute.py').write_text(execute,encoding='utf-8',newline='\n')
previous=old.read(F/'protocol.json');commands={k:[x.replace(str(F),str(H)).replace('e077_plan_probe','e078_plan_probe')for x in v]for k,v in previous['compile_commands'].items()};deps={p:h for p,h in previous['input_sha256'].items()if Path(p).suffix in['.rlib','.rmeta','.dll','.lib']}
for p,h in deps.items():old.pin(p,h)
AR=old.read(A/'report.json');cases=[{'id':i,'reference':str(A/'execution'/f'case-{i:02d}.bin'),'reference_sha256':AR['cases'][i]['raw_sha256']}for i in range(12)]
paths=[Path(__file__),*[p for p in H.iterdir()if p.is_file()],S/'manifest.json',S/'candidate-mod.rs',S/'mark-fold.rs',D/'report.json',R/'runs/D129-ABI-pointer-audit/report.json',A/'report.json',C/'common_e051_live.py',C/'protected-main.json'];P={'id':'E078-plan-control','at':old.now(),'status':'FROZEN_PRE_COMPILER_NATIVE','input_sha256':deps|{str(p):old.sha(p)for p in paths},'compile_commands':commands,'cases':cases,'scope':'TwoRustcompilers, oneunitprocess and12freshCPUmetadata processes, allcases retainedfixedorder0..11. Exactly samehostmarker/code fromE078source; acceptedpublicplan unchanged. All53baseline fields matchretainedD092; onlyfoldnode_na0to-1 differs, all52otherfields/53caps/struct/fullkind/children exact. No productionactivation/GPU/newtiming. Rawbulk~3.65GBphysicallyS reserved66GiB. No repeats/variants afteractual failure.','candidate_accepted':False};old.save(H/'protocol.json',P)
def publish(p,key):
 dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert dst.read_bytes()==p.read_bytes(),key
 else:shutil.copyfile(p,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
 return {'url':'evidence/'+key,'sha256':old.sha(p)}
pub=[publish(p,H.name+'/'+p.name)for p in H.iterdir()if p.is_file()];pub.append(publish(Path(__file__),H.name+'/prepare-run.py'));old.save(H/'pre-execution-publication.json',{'at':old.now(),'protocol_sha256':old.sha(H/'protocol.json'),'HTTP_byte_verified_artifacts':pub,'compiler_or_native_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E078');e.update(stage='Compiledhost53field/foldmarker controls',correctness='Resource/D129ABIpass;hostcompiledmapsrunning',updated_at=old.now());e['evidence'].append({'label':'Frozen fullhostmetadata protocol','url':'evidence/E078-plan-control/protocol.json'});s.update(updated_at=old.now(),active_experiment='E078',stage='E078compiledhostmetadata controls',activity='Compile exacthostmarker/units andcompare12fullactual53fieldplans against acceptedmetadata. No applicationGPUkernel/speed result;E051live/accepted12.44%unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
M.mkdir();print('E078host protocol',old.sha(H/'protocol.json'),flush=True);old.child([sys.executable,'-B',str(H/'execute.py'),old.sha(H/'protocol.json')],M,'host',old.env(),2400);q=old.read(H/'report.json');old.custody();assert not(R/'gpu-run.lock').exists()
for folder in[H,H/'build',H/'execution',M]:
 for p in folder.iterdir():
  if p.is_file()and p.suffix in['.py','.rs','.json','.log']:pub.append(publish(p,(H.name+'-'+folder.name if folder in[H/'build',H/'execution']else folder.name)+'/'+p.name))
old.save(M/'publication.json',{'at':old.now(),'HTTP_byte_verified_artifacts':pub,'bulk_raw_registered_physically_S':True,'all_owned_children_terminal':True,'source_main_live_PTX_custody_pass':True})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E078');e.update(stage='Preparing fullrawGPUfold/action controls',correctness='Resources/ABI/full12compiledhostmetadata+markercontrols pass;GPUrawpending',updated_at=old.now());e['evidence'].append({'label':'All12fullcompiledhostmaps andexactmarker replay','url':'evidence/E078-plan-control/report.json'});s.update(updated_at=old.now(),active_experiment='E078',stage='E078fullrawGPUcontrols next',activity='All12hostmaps matchaccepted;onlyintendedfoldmarkersdiffer. GPUfloat/statecontrolsnext,no solver/speedgain yet;E051accepted/live12.44%unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'### E078 compiled fold-marker metadata controls'not in raw
entry=f'''

### E078 compiled fold-marker metadata controls

D128ownership andD129same4PTXcompleteABIparserrepairpass;originalfailedobserverreport preserved. ExactE078CUDA/hostsource unchanged. Frozenprotocol{old.sha(H/'protocol.json')} before2Rustcompilers,originalsourcefoldmarkerunit+bothacceptedplanunitmodules,then12freshCPUmetadata processes fixed0..11. Exactconstructor-private markerfunction copiedfromfrozenmodsource; bothpublicplans acceptedbyte-exact beforemarking. No solver/GPUkernel/current-sourceactivation/newtiming.

All12actual53fieldplans dumpedcompletely,fullbaseline matchesretainedD092acceptedraw; onlyreachedfold node_na changes0to-1. All52otherfullfieldvalues,53capacities,structsizes,fullnodekind/childvectors exact. Sourceunit checksprivate/all-and-onlyfold/idempotence/publicfreshplan/length/capacity/actionpositive across3boardsxisooff/onxcompact/full. Fullreplay {q['root_checks']}checks,{q['baseline_encoded_words']}baselineencodedwords,{q['exact_private_marker_count']}exactmarkers,{q['raw_bytes']}rawbytesphysicallyS. Report{old.sha(H/'report.json')}. Theseareofftreehostsourcecontrols,not integratedGpuSolverconstructor/callerorGPUfloat/state/material/speedproof. All{len(pub)}code/protocol/report/logartifacts HTTPbyteverified;allownedchildren terminal,accepted162/main163/live/protected2PTXunchanged. SameE078source needsfullrawfold+actionGPUcontrols beforecomplete-cycle1%/strictfixture/fresh16/broadF32/state/menu/save/resume/continuation/actualmaterial/holdout/cumulative. E051accepted/deployed12.4372274192%,lastprimaryB246unchanged;goalactive.
''';nl=b'\r\n'if b'\r\n'in raw else b'\n';ledger.write_bytes(raw+entry.encode().replace(b'\n',nl));old.custody();subprocess.run(['git','commit','--only','-m','research: verify all private fold markers and complete host metadata','--','research/postflop-gpu-20261016/experiments.md'],cwd=old.REPO,check=True);old.custody();print(json.dumps({'status':q['status'],'cases':len(q['cases']),'markers':q['exact_private_marker_count'],'report_sha256':old.sha(H/'report.json')}),flush=True)
