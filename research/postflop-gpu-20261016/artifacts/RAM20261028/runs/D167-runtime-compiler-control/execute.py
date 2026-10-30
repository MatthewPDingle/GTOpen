import sys,json,shutil,urllib.request
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent;sys.path.insert(0,str(ROOT/'epoch'))
import common as h
assert len(sys.argv)==2;P=h.read(H/'protocol.json')
def verify():
    h.pin(H/'protocol.json',sys.argv[1]);h.custody()
    for path,digest in P['input_sha256'].items():h.pin(path,digest)
def publish(folder,names):
    for name in names:
        p=folder/name;key=folder.name+'/'+name;dest=h.ar.DASHBOARD/'evidence'/key;dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists():assert dest.read_bytes()==p.read_bytes()
        else:shutil.copyfile(p,dest)
        with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
verify();O=H/'execution';O.mkdir(exist_ok=False);publish(H,['protocol.json','nvrtc13.rs'])
publish(ROOT/'runs/D167-runtime-compiler-contract',['design-review.json'])
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);assert not any(x['id']=='D167' for x in status['experiments'])
    status['experiments'].append({'id':'D167','title':'Real optional runtime compiler ownership controls','kind':'diagnostic','status':'running','accepted':False,'correctness':'pending_runtime_API_controls','measurement_epoch':'RAM20261028','stage':'Actual private DLL/API/lifetime,exactPTX andnegative fallback controls','reason':'Postflop-only Windows64/compute120/driver13 optional path withabsolute builtins/primary andownedprogram. One realshadercompile mustequal sealed13PTX;expected invalidsyntax/NUL andnon120/missingpath declines. No applicationkernel/solver/speed sample.','evidence':[{'label':'Prospective runtime compiler contract','url':'evidence/D167-runtime-compiler-contract/design-review.json'},{'label':'Frozen API ownership/fallback probe','url':'evidence/D167-runtime-compiler-control/protocol.json'}]})
    status.update(updated_at=h.now(),active_experiment='D167',stage='CUDA13 real runtime compiler controls',activity='Full canonical rawstate passed. Testactual runtime loading/program lifecycle/close/fallback andexact generatedPTX beforeintegration/timing. E08010.4564s unchanged.')
    h.ar.atomic_json(h.ar.STATUS,status)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
    h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes']
    h.child(P['rustc_command'],O,'rustc',1200);verify();h.save(O/'binary.json',{'sha256':h.sha(H/'probe.exe')})
    h.child([str(H/'probe.exe'),str(H/'output'),P['private_runtime_directory']],O,'probe',1200);verify()
    native=h.read(H/'output/native.json');assert native['actual_runtime_PTX_exact'] and native['unsupported_target_declines'] and native['missing_private_runtime_declines'] and native['expected_syntax_error_declines'] and native['embedded_NUL_declines']
    assert (H/'output/actual-runtime.ptx').read_bytes()==(H/'expected-candidate.ptx').read_bytes()
    log=(O/'probe.stderr.log').read_text(encoding='utf-8');assert log.count('gpu: postflop NVRTC13.0 runtime compiler')==1 and log.count('optional postflop NVRTC13 declined:')==2 and 'cleanup:' not in log
    D=ROOT/'comparisons/D167-runtime-compiler-control';D.mkdir(exist_ok=False)
    report={'id':'D167','at':h.now(),'status':'pass_scoped_runtime_compiler_exact_PTX_and_fallbacks','protocol_sha256':sys.argv[1],'new_runtime_module_sha256':h.sha(H/'nvrtc13.rs'),'actual_generated_PTX_sha256':h.sha(H/'output/actual-runtime.ptx'),'native_controls':native,'all_owned_children_terminal':True,'source_main_live_protected_PTX_custody_pass':True,'production_integration_proven':False,'application_kernel_launches':0,'solver_executions':0,'performance_samples':0,'candidate_accepted':False,'scope':'Actual privateabsolute DLL binding/version/program/lifetime/close andexactnewPTX plusdeclarednegative fallbackcontrols only. Modulepresence observations retained,notuniversalzeroresourcecost. Unsupporteddriver/nonWindows branches needintegration/source/broaderverification;no replacementofactualresource/fullcyclequalification. No main/global/preflop installoractivation.'}
    h.save(D/'report.json',report);verify();h.save(O/'complete.json',{'at':h.now(),'report_sha256':h.sha(D/'report.json'),'all_owned_children_terminal':True,'new_gain_accepted':False})
publish(D,['report.json'])
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);item=next(x for x in status['experiments'] if x['id']=='D167')
    item.update(status='measured',correctness='pass_runtime_PTX_and_declines',stage='Actual runtime13PTX exact;fallback/API lifetime controls pass',reason='Oneactual shadercompile byte-exactsealed13PTX. Non120/missing runtime decline beforeload;expectedsyntaxerror/NULdecline andcleanup pass. Actualpostclosemodulepresence retained. Productioncache/Cargo/cfgintegration andrealresource/speed qualification remain.')
    item.setdefault('evidence',[]).append({'label':'Runtime API andexactPTX outcome','url':'evidence/D167-runtime-compiler-control/report.json'})
    status.update(updated_at=h.now(),active_experiment='D167',stage='Runtime compiler component passed',activity='Actual13runtime producessealedPTX andsafe declared fallbackcontrols. Nextisolated source/cache integration,then fresh buildandrealcompletecycles. No speedup accepted.')
    h.ar.atomic_json(h.ar.STATUS,status)
verify();print(json.dumps({k:report[k] for k in ['status','actual_generated_PTX_sha256','native_controls']}),flush=True)
