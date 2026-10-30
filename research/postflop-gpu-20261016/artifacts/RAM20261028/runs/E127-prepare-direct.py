"""Freeze original819parent controls plus two complete action-star derivatives before kernels."""
import ast,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'))
import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists()
host=h.read(ROOT/'runs/E127-host-control/report.json');assert host['status']=='pass_real_compiled_CPU_builder_all6_original_plans_and_types'
assert h.read(ROOT/'runs/E127-host-control/execution/control.exit.json')['returncode']==0
R=ROOT/'runs/E127-resource';assert all(h.read(R/'report.json')['gates'].values())
H=ROOT/'runs/E127-direct';H.mkdir(exist_ok=False);A=ROOT/'runs/D233-stride-up-action'
for name in['corpus.json','discounts.rs']:shutil.copyfile(A/name,H/('original-'+name if name.endswith('.json')else name))
original=h.read(H/'original-corpus.json');assert len(original['cases'])==819
cases=[];raw_bytes=42;launches=0
for variant in[0,1,2]:
    for case in original['cases']:
        row=dict(case);row['id']=len(cases);row['original_case_id']=case['id'];row['variant']=variant
        nh,na=case['hands'],case['actions'];nn=na+8;stride=nh+5;k=min(2,na)if variant else 0
        reg=30+na*nh+k*(33+na*nh)
        cfv=((nn+7+k*na)*stride+17)if variant else((nn+3)*stride+17)
        sigma=22+na*nh+k*(na*nh+17)
        imm=3+k+9*(nn+k*na)+(na+4+k*na)+(6*max(nh,1)+7)+sigma+3
        mut=2*reg+cfv
        row.update(selected_action_children=k,expected_mutable_words=mut,expected_immutable_words=imm,expected_kernel_launches=k+2)
        raw_bytes+=444+12*(imm+mut);launches+=k+2;cases.append(row)
assert len(cases)==2457 and raw_bytes<4*1024**3
h.save(H/'corpus.json',{'id':'E127-direct','at':h.now(),'original_case_count':819,'case_count':2457,'kernel_launches':launches,'estimated_raw_bytes':raw_bytes,'cases':cases,
    'original819_literal_prefix_preserved':cases[:819]==[dict(c,id=c['id'],original_case_id=c['id'],variant=0,selected_action_children=0,expected_mutable_words=cases[c['id']]['expected_mutable_words'],expected_immutable_words=cases[c['id']]['expected_immutable_words'],expected_kernel_launches=2)for c in original['cases']],
    'variants':'0entireoriginalparentcorpus,allchildnode_na=-7sofirststage skips,originalparentmathmustmatch.1addsfirst/lastactionchildren(unlocked)andfreshterminalinputs.2samechildrenwithfixedlocksandfirstgrandchildCFVrowaliasedtoparentoutput,initializedinputthenchildreadsbeforeparentoverwrite. Everyoriginalgeometry/discount/role/NaN/signedzero/subnormal/threadtail/count0retained inallvariants.'})
source=(A/'probe.rs').read_text(encoding='utf-8').replace('D233','E127')
def edit(old,new):
    global source
    assert source.count(old)==1,(old,source.count(old));source=source.replace(old,new,1)
edit('role:u32,algo:u32,t:u32,mode:u32,count:i32}','role:u32,algo:u32,t:u32,mode:u32,count:i32,variant:u32}')
source=source.replace('count:1});','count:1,variant:0});').replace('count:0});','count:0,variant:0});')
edit('assert_eq!(cases.len(),819);','assert_eq!(cases.len(),819);let original=cases.clone();for variant in[1,2]{cases.extend(original.iter().map(|c|Case{variant,..*c}));}assert_eq!(cases.len(),2457);')
edit('let Case{nh,na,block,p,role,algo,t,mode,count}=*c;','let Case{nh,na,block,p,role,algo,t,mode,count,variant}=*c;')
edit('let nn=na+8;','let mut nn=na+8;')
edit('let nodes=vec![0xdead_beefu32,parent as u32,0xdead_beef];','let mut nodes=vec![0xdead_beefu32,parent as u32,0xdead_beef];')
edit('let cf=cm.load_function("up_action").unwrap();','let cf=cm.load_function("up_action_star").unwrap();')
edit('fn disjoint_regions(s:&Arc<CudaStream>,buffers:[&CudaSlice<f32>;3])->Vec<[u64;2]> {\n let mut regions=Vec::new();\n for buffer in buffers {let (ptr,_guard)=buffer.device_ptr(s);regions.push([ptr,buffer.len() as u64*4]);}', 'fn region<T>(s:&Arc<CudaStream>,buffer:&CudaSlice<T>)->[u64;2]{let(ptr,_guard)=buffer.device_ptr(s);[ptr,buffer.len()as u64*std::mem::size_of::<T>()as u64]}\nfn disjoint_regions(regions:Vec<[u64;2]>)->Vec<[u64;2]> {')
edit('disjoint_regions(&stream,[&dr,&ds,&dv])','disjoint_regions(vec![region(&stream,&dn),region(&stream,&dp),region(&stream,&da),region(&stream,&doff),region(&stream,&dcs),region(&stream,&dc),region(&stream,&drs),region(&stream,&drp),region(&stream,&dl),region(&stream,&dls),region(&stream,&dslot),region(&stream,&dd),region(&stream,&dr),region(&stream,&ds),region(&stream,&dv)])')
extra='''  let mut child_ids=Vec::new();
  let mut owned_reg:Vec<(usize,usize)>=if role==0{vec![(off,off+na*nh)]}else{vec![]};
  let mut owned_cfv=vec![(parent*max,parent*max+nh)];
  if variant>0 {
   let old_nn=nn;let positions=if na==1{vec![0]}else{vec![0,na-1]};
   nn+=positions.len()*na;player.resize(nn,-7);arity.resize(nn,-7);offset.resize(nn,0);childstart.resize(nn,0);rsrc.resize(nn,0);lock.resize(nn,-1);slots.resize(nn,0);
   for (j,&a)in positions.iter().enumerate(){
    let child=4+a;child_ids.push(child);nodes.push(child as u32);player[child]=1-player[parent];arity[child]=na as i32;
    childstart[child]=children.len()as u32;for x in 0..na{children.push((old_nn+j*na+x)as u32);slots[old_nn+j*na+x]=(old_nn+4+j*na+x)as u32;}
    rsrc[child]=(1+j)as u32;let child_off=regret.len()+16;offset[child]=child_off as u64;
    regret.resize(child_off+na*nh+17,f32::from_bits(0x7fc0_aa55));strategy.resize(regret.len(),f32::from_bits(0x7fc0_aa55));
    for i in 0..na*nh{regret[child_off+i]=value(i+index+29+j*11,mode);strategy[child_off+i]=value(i+index+31+j*13,mode).abs();}
    let child_lock=sigma.len();sigma.resize(child_lock+na*nh+17,f32::from_bits(0x7fc0_cafe));
    for a in 0..na{for i in 0..nh{sigma[child_lock+a*nh+i]=(a+1)as f32/((na*(na+1)/2)as f32);}}
    if variant==2{lock[child]=child_lock as i64;}
    if player[child]==p&&lock[child]<0{owned_reg.push((child_off,child_off+na*nh));}
    owned_cfv.push((slots[child]as usize*max,slots[child]as usize*max+nh));
   }
   let end=(old_nn+7+positions.len()*na)*max+17;let begin=cfv.len();cfv.extend((begin..end).map(|i|value(i+index*7,mode)));
   if variant==2{slots[old_nn]=slots[parent];for i in 0..nh{cfv[parent*max+i]=value(i+index*7+101,mode);}}
  }
'''
edit('  let immutable=vec![',extra+'  let immutable=vec![')
edit('let mut output_words=0u64;let mut immutable_words=0u64;let mut guard_words=0u64;','let mut output_words=0u64;let mut immutable_words=0u64;let mut guard_words=0u64;let mut launches=0usize;')
call='''unsafe{stream.launch_builder(f).arg(&dn).arg(&start).arg(&count).arg(&p).arg(&dp).arg(&da).arg(&doff).arg(&dcs).arg(&dc).arg(&mut dr).arg(&mut ds).arg(&drs).arg(&drp).arg(&dl).arg(&dls).arg(&dslot).arg(&mut dv).arg(&dd).arg(&nharg).arg(&maxarg).launch(LaunchConfig{grid_dim:(3,1,1),block_dim:(block,1,1),shared_mem_bytes:0}).unwrap();}'''
child_call=call.replace('launch_builder(f)','launch_builder(&bf)').replace('.arg(&start)','.arg(&child_start)')
edit(call,'''if label=="baseline"{for j in 0..child_ids.len(){let child_start=3+j as i32;'''+child_call+'''launches+=1;}}
   '''+call+'''launches+=1;''')
edit('let owned=count!=0 && if kind<2 {role==0 && i>=off && i<off+na*nh}else{i>=parent*max && i<parent*max+nh};','let owned=count!=0 && if kind<2 {owned_reg.iter().any(|&(a,b)|i>=a&&i<b)}else{owned_cfv.iter().any(|&(a,b)|i>=a&&i<b)};')
edit('"stage":"case","id":index,','"stage":"case","id":index,"original_case_id":index%819,"variant":variant,"selected_action_children":child_ids.len(),')
edit('"kernel_launches":2*case_count','"kernel_launches":launches')
# Extra runtime ownership bounds cover every original and newly appended index before launch.
preflight='''  for &node in std::iter::once(&parent).chain(child_ids.iter()){
   assert!((offset[node]as usize)+na*nh<=regret.len());assert!((rsrc[node]as usize)*nh+nh<=reach.len());
   let cs=childstart[node]as usize;assert!(cs+na<=children.len());assert!((slots[node]as usize)*max+nh<=cfv.len());
   if lock[node]>=0{assert!((lock[node]as usize)+na*nh<=sigma.len());}
   for &child in &children[cs..cs+na]{assert!((child as usize)<nn);assert!((slots[child as usize]as usize)*max+nh<=cfv.len());assert_ne!(slots[node],slots[child as usize]);}
  }
'''
edit('  let dn=stream.clone_htod(&nodes).unwrap();',preflight+'  let dn=stream.clone_htod(&nodes).unwrap();')
(H/'probe.rs').write_bytes(source.encode());shutil.copyfile(A/'probe.rs',H/'original-probe.rs')
for arm in['baseline','candidate']:
    p=(R if arm=='baseline'else R/'execution')/(arm+'-compute_120.ptx');h.pin(p,h.read(R/'report.json')['PTX_sha256'][arm+'-compute_120']);shutil.copyfile(p,H/(arm+'.ptx'))
parent=h.read(R/'protocol.json');cmd=[x.replace('E127-resource','E127-direct')for x in parent['rustc_command']]
paths=[Path(__file__),ROOT/'runs/E127-run-direct.py',ROOT/'runs/E127-read-direct.py',ROOT/'epoch/common.py',ROOT/'runs/E127-host-source/manifest.json',ROOT/'runs/E127-host-source/design.json',ROOT/'runs/E127-host-control/report.json',ROOT/'runs/E127-native/control-report.json',R/'protocol.json',R/'report.json']+[p for p in H.iterdir()if p.is_file()]
inputs={k:v for k,v in parent['input_sha256'].items()if str(ROOT/'reference/accepted-e080-deps')in k};inputs.update({str(p):h.sha(p)for p in paths})
h.save(H/'protocol.json',{'id':'E127-direct','at':h.now(),'status':'FROZEN_BEFORE_FIRST_APPLICATION_KERNEL',
    'input_sha256':inputs,'rustc_command':cmd,'cases':2457,'expected_kernel_launches':launches,'expected_raw_bytes':raw_bytes,'raw_cap_bytes':4*1024**3,'required_free_bytes':68*1024**3,
    'scope':'Entireoriginal819unencodedparentcaseswithidenticalinputarrays/descriptorsandvaluegenerationprefix. Newkernelperformsnofirst-stageactionupdatestherebecauseoriginalchildarity=-7(initialized). Two819-casestarvariantsappendoneortwofirst/lastactionchildrenandtheirterminalinputs,allparentroles/arities/threads/hands/counts/specialvaluesretained. Variant2fixedchildlocksandown-grandchildCFVrowaliaswithreadbeforeparentoverwrite;no foreignreaders. Originalkernel(s)eachchildthenparentbaseline vsnewstaroneCTA. Fullphysicalregret/strategy/CFV plusall12actualimmutableinputs/guards retainedandcompared. No node/field/sample exclusions/extensions afteroutcomes.',
    'physical_contract':'Alloriginalandnewmutableoffsets/readrows/locks/reachesprecheckedbounded; parent/immediatechildrowsdistinct,onlyexplicitown-grandchildaliaspermitted. NewGPUprimitivehasnoextraallocation beyondoriginalmetadataextensions. Allnewhostworklist/types/capacitycostsdeclaredandCPUcompiledbeforefirstappkernel; actualintegratedruntime/driver/materialcostsnotyetqualified.',
    'interpretation':'DirectprimitiveGPUfloat equivalence only, notfullengine/canonical/accuracy/speed/capacity/material oradoption. No NVRTC here,sealedresourcePTXonly. Any real mismatch closesfixedsourceform,notrescuedbyfield/precision/width/loop/helper/schedule/quality/sample changes.',
    'later_gates':'Fullengine/canonicalnewimmutableworklistandalloldphysicalfields,ordinarychecks,freshordinaryintegrated3pairs1%strictfixture,thenfresh16/broad/material/capacity/holdout/freshoriginalcurrentRAMcumulative/tempappbeforeadoption.'})
print(json.dumps({'protocol_sha256':h.sha(H/'protocol.json'),'cases':2457,'launches':launches,'raw_bytes':raw_bytes}),flush=True)
