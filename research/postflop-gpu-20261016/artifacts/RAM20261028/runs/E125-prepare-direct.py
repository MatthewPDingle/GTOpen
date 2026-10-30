"""Retain the complete original1688-case chance corpus; adapt only typed immutable table upload."""
import json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'))
import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()
assert shutil.disk_usage(ROOT).free>=68*1024**3
R=ROOT/'runs/E125-resource';assert all(h.read(R/'emitted-report.json')['gates'].values())
A=Path(r'S:\GTOpen-research\postflop-gpu-20261016\runs\E068-kernel-control')
H=ROOT/'runs/E125-kernel-control';H.mkdir(exist_ok=False)
shutil.copyfile(A/'corpus.json',H/'corpus.json');corpus=h.read(H/'corpus.json');assert len(corpus['cases'])==1688
for arm in['baseline','candidate']:
    source=(R if arm=='baseline'else R/'execution')/(arm+'-compute_120.ptx')
    h.pin(source,h.read(R/'report.json')['PTX_sha256'][arm+'-compute_120']);shutil.copyfile(source,H/(arm+'.ptx'))
source=(A/'probe.rs').read_text(encoding='utf-8');text=source.replace('E068','E125').replace('exact original/new bit-selected','originalu32/candidateu16 typed-table')
edits=[
('f:&cudarc::driver::CudaFunction)->(Vec<Vec<u32>>,Vec<Vec<u32>>)','f:&cudarc::driver::CudaFunction,packed:bool,physical:&mut Out)->(Vec<Vec<u32>>,Vec<Vec<u32>>)'),
('let hp=s.clone_htod(&self.hp).unwrap();','let hp32=if packed{None}else{Some(s.clone_htod(&self.hp).unwrap())};let hp16=if packed{let narrow:Vec<u16>=self.hp.iter().map(|&v|u16::try_from(v).expect("sourceu16domain")).collect();Some(s.clone_htod(&narrow).unwrap())}else{None};'),
('unsafe{s.launch_builder(f).arg(&nodes).arg(&start).arg(&count).arg(&cs).arg(&cc).arg(&card).arg(&child).arg(&perm).arg(&inv).arg(&mask).arg(&hp).arg(&slot).arg(&mut cfv).arg(&nh).arg(&stride).launch(cfg).unwrap();}',
 'let mut launch=s.launch_builder(f);launch.arg(&nodes).arg(&start).arg(&count).arg(&cs).arg(&cc).arg(&card).arg(&child).arg(&perm).arg(&inv).arg(&mask);if packed{launch.arg(hp16.as_ref().unwrap());}else{launch.arg(hp32.as_ref().unwrap());}unsafe{launch.arg(&slot).arg(&mut cfv).arg(&nh).arg(&stride).launch(cfg).unwrap();}'),
('s.synchronize().unwrap();let post=vec![','s.synchronize().unwrap();let hp_post=if let Some(v)=hp16.as_ref(){let raw=s.clone_dtoh(v).unwrap();s.synchronize().unwrap();physical.write_all(&(raw.len()as u64).to_le_bytes()).unwrap();for x in &raw{physical.write_all(&x.to_le_bytes()).unwrap();}raw.into_iter().map(u32::from).collect()}else{du32(s,hp32.as_ref().unwrap())};let post=vec!['),
('du32(s,&hp),du32(s,&slot)','hp_post,du32(s,&slot)'),
('let mut candidate=file(dir.join("candidate.bin"),b"E125_OUT1");','let mut candidate=file(dir.join("candidate.bin"),b"E125_OUT1");let mut physical=file(dir.join("candidate-handperm-u16.bin"),b"E125_U16");'),
('for (f,outfile) in [(&bf,&mut baseline),(&cf,&mut candidate)]{','for (packed,f,outfile) in [(false,&bf,&mut baseline),(true,&cf,&mut candidate)]{'),
('let (post,out)=up.run(&c,&stream,f);','if packed{u32w(&mut physical,id as u32);}let (post,out)=up.run(&c,&stream,f,packed,&mut physical);'),
('for f in [&mut input,&mut baseline,&mut candidate]','for f in [&mut input,&mut baseline,&mut candidate,&mut physical]'),
]
for before,after in edits:
    assert text.count(before)==1,before;text=text.replace(before,after,1)
(H/'probe.rs').write_bytes(text.encode())
(H/'original-control-probe.rs').write_bytes((A/'probe.rs').read_bytes())
parent=h.read(R/'protocol.json');command=parent['rustc_command'].copy();command=[x.replace('E125-resource','E125-kernel-control')for x in command]
inputs={k:v for k,v in parent['input_sha256'].items()if str(ROOT/'reference/accepted-e080-deps')in k}
files=[Path(__file__),ROOT/'runs/E125-run-direct.py',ROOT/'runs/E125-read-direct.py',ROOT/'epoch/common.py',R/'report.json',R/'emitted-report.json',R/'emitted-reader-protocol-v2.json',A/'corpus.json',A/'probe.rs']
files += [x for x in H.iterdir()if x.is_file()]
inputs.update({str(p):h.sha(p)for p in files})
h.save(H/'protocol.json',{'id':'E125-direct','at':h.now(),'status':'FROZEN_PRE_APPLICATION_KERNEL',
    'input_sha256':inputs,'rustc_command':command,'cases':1688,'application_kernel_launches':3376,'rounds':1,
    'raw_reservation_bytes':3*1024**3,'required_free_bytes':68*1024**3,'maximum_native_seconds':1200,'maximum_reader_seconds':1200,
    'scope':'Entireoriginal1688case chancecorpus byteexact,alloriginalwidths/geometries/stress/blocked/unblocked/zeros/inverses/signedzero/NaN/Inf/tails/strides preserved. Bothcurrentaccepted/candidatePTXsealed. Typedu16actualGPUinputonlycandidate, no u32 reinterpretcast/truncation: checkedu16::try_from everyoriginalhandpermword. Retainallactualu16devicewordsseparately, widenedlogicalpostforcomparisonwithoriginalu32data. All12actualimmutablebuffers/entirephysicalCFV/allguards exact; unusedallocateda/b fields remainchecked. No applicationmath/scope/samplechange.',
    'raw_contract':'ExistingE068u32vectorstreamformatpreservedwithE1258byteinput/9byteoutputmagic. New8byteE125_U16 streamcontains1688records u32caseid,u64elementcount,littleendianu16everyactualcandidatephysicalhandpermword. Originalunencodedinputandpost preserved alongside typedphysicalfile.',
    'reader_gate':'Independentregenerateall12originalinputbuffers/seedwordsfromoriginalcorpus, fullpostinputequality/typedphysicalu16roundtrip/wholeCFVpair/guards/headerlength/EOF, notsample/fingerprintonly. Originalreadaddressbounds/sourcecontract remain; negativecorruptioncontrols required.',
    'failure':'Anyrealword/address/guardfailure closesfixedu16table sourceform,no width/field/packing/helper/layout/scope/source/quality/sample rescue. Preservealloriginaloutputs; mechanicalobserverrepairs additivewithnocompletednative repeats.',
    'performance_claim':False,'candidate_accepted':False,'later_gate':'86ordinaryunits thenfixed3pairs1%unrounded+fixtureguard; allfullengine/canonical/fresh16/broad/material/capacity/holdout/cumulative/appgatesbeforeadoption.'})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);row=next(x for x in status['experiments']if x['id']=='E125')
    row.update(at=h.now(),stage='Frozen fulloriginal1688case GPUraw table-width controls',correctness='resource_emitted_contract_pass_raw_pending',reason='Actualu16candidatephysicalinput retained; alloriginal12immutablebuffers/physicalCFV/guardsand1688cases preserved. No GPUresult/speedclaim yet, liveE080unchanged.')
    status.update(updated_at=h.now(),active_experiment='E125',stage=row['stage'],activity=row['reason']);h.ar.atomic_json(h.ar.STATUS,status)
print(json.dumps({'protocol_sha256':h.sha(H/'protocol.json'),'source_sha256':h.sha(H/'probe.rs'),'cases':1688,'launches':3376}),flush=True)
