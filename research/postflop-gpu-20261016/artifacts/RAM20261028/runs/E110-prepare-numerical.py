import ast,json,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists()
assert h.read(ROOT/'runs/D240-fold-copy-PTX/report.json')['status']=='pass_source_and_param_bound_fused_partial_PTX'and h.read(ROOT/'runs/D241-native-fold-copy/report.json')['status']=='pass_static_native_global_copy_partial_fusion'
# Reuse the exact original production engine type, observer, corpus and complete reader.
parent=ROOT/'runs/D231-prepare-engine.py';source=parent.read_bytes().decode('utf-8');source=source[:source.index("with h.ar.exclusive_lock(h.ar.STATUS")]
source=source.replace('D231-stride-engine-control','D242-fold-copy-engine').replace("'id':'D231'","'id':'D242'").replace('D231_','D242_').replace('d231_','d242_').replace('E109','E110').replace('D229-stride-PTX-r2','D240-fold-copy-PTX').replace('pass_param_qualified_stride_signextension_removal','pass_source_and_param_bound_fused_partial_PTX').replace('D230-native-stride','D241-native-fold-copy').replace('pass_static_native_stride_signcorrection_removal','pass_static_native_global_copy_partial_fusion').replace("ROOT/'runs/D228-CFV-stride-scout/report.json'","ROOT/'runs/D239-fold-copy-sum-scout/source-review.json'")
source=source.replace('pass_scoped_stride_engine_raw_lifecycle_equivalence','pass_scoped_fold_copy_engine_raw_lifecycle_equivalence').replace('Only GPU PTX differs by E110sixscalar signedness declarations; all Rust i32argvalues unchanged.','Only GPU PTX differs by E110same-thread copy/partial fusion inup_fold; all Rust arguments unchanged.').replace('unsignedstride','foldcopypartial').replace('nonnegative-stride','fold-copy-partial').replace('exactsix-type form','exactfoldcopypartial form')
out=ROOT/'runs/D242-prepare-engine.py';assert not out.exists();ast.parse(source);out.write_bytes(source.encode('utf-8'))
# The generated script contains no native/compiler action, only frozen preparation.
exec(compile(source,str(out),'exec'),dict(globals(),__file__=str(out)))
E=ROOT/'runs/D242-fold-copy-engine';U=ROOT/'runs/D235-stride-fold';H=ROOT/'runs/D243-fold-copy-direct';R=ROOT/'runs/E110-resource';H.mkdir(exist_ok=False)
for arm in ['baseline','candidate']:shutil.copyfile(R/('baseline-compute_120.ptx'if arm=='baseline'else'execution/candidate-compute_120.ptx'),H/(arm+'.ptx'))
shutil.copyfile(U/'corpus.json',H/'corpus.json')
for name in ['probe.rs','audit.py']:
 text=(U/name).read_bytes().decode('utf-8').replace('D235','D243');(H/name).write_bytes(text.encode('utf-8'))
ast.parse((H/'audit.py').read_text());h.save(H/'preparation.json',{'at':h.now(),'input_sha256':{p.name:h.sha(p)for p in H.iterdir()if p.is_file()},'scope':'Exactoriginal360foldcorpus/scenarios andCPU/float/guard/referencecode unchanged. Only namespace, E110sealedPTX and evidence paths; same21args andnh_o*4shared botharms.'})
cmd=[x.replace(str(U),str(H))for x in h.read(U/'protocol.json')['rustc_command']];O=H/'execution';raw=O/'raw';report=ROOT/'comparisons/D243-fold-copy-direct/report.json'
files=[Path(__file__),ROOT/'runs/D243-execute-fold-copy.py',U/'protocol.json',U/'probe.rs',U/'audit.py',U/'corpus.json',R/'report.json',ROOT/'runs/E110-source/manifest.json',ROOT/'runs/D240-fold-copy-PTX/report.json',ROOT/'runs/D241-native-fold-copy/report.json',ROOT/'epoch/common.py']+[p for p in H.iterdir()if p.is_file()]+[p for p in(ROOT/'reference/accepted-e080-deps').iterdir()if p.is_file()]
h.save(H/'protocol.json',{'id':'D243','at':h.now(),'status':'FROZEN_PRE_COMPILER_AND_DIRECT_GPU','cases':360,'kernel_launches':720,'rustc_command':cmd,'raw_output':str(raw),'report':str(report),'marker':'D243_FOLD_UNIT ','native_environment':{'D243_FOLD_KERNEL_CONTROL_DIR':str(raw)},'audit_command':[sys.executable,str(H/'audit.py'),'up-fold',str(H),str(raw),str(report)],'required_free_bytes':66*1024**3,'raw_reservation_bytes':12*1024**3,'input_sha256':{str(p):h.sha(p)for p in files},'failure':'Any genuinebit/input/guard/ABI/numericalfailure closesE110 without shape/order/source/helper/width/flags/quality/sample rescue. Completednativecases neverrepeat for mechanicalreader/metadatarepair. Samewholeoriginalcorpus, no subset.'})
for folder,names in [(H,['protocol.json']),(E,['protocol.json','source-review.json'])]:
 for name in names:
  p=folder/name;dst=h.ar.DASHBOARD/'evidence'/folder.name/name;dst.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists():assert dst.read_bytes()==p.read_bytes()
  else:shutil.copyfile(p,dst)
  with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+folder.name+'/'+name,timeout=20)as z:assert z.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E110');e.update(stage='360 direct fold pairs and36case engine matrix frozen',correctness='source_compiled_native_mechanism_pass_numeric_pending',reason='Both120/75zero-seededthreadinduction/globalproducer-FADD-sharedstore bindings andactualdrivercarry acrosscardstage passed. Originalbarriers/sharedlimits retained; reg39to40 warning. Next sameoriginal360foldpairs and36enginecases;no speedclaim.');e['evidence']+=[{'label':p,'url':'evidence/'+p}for p in ['D240-fold-copy-PTX/report.json','D241-native-fold-copy/report.json','D243-fold-copy-direct/protocol.json','D242-fold-copy-engine/protocol.json']];s.update(updated_at=h.now(),active_experiment='E110',stage=e['stage'],activity=e['reason']);h.ar.atomic_json(h.ar.STATUS,s)
print(json.dumps({'direct_protocol_sha256':h.sha(H/'protocol.json'),'engine_protocol_sha256':h.sha(E/'protocol.json')}),flush=True)
