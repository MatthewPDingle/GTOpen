"""Freeze and publish SDK materiality audit before compilation or native queries."""
import json, shutil, subprocess, sys, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
H=ROOT/'runs/D094-resource-materiality';assert not (H/'protocol.json').exists()
sdk=ROOT/'runs/D085-cupti-activity/vendor/cuda_cudart/cuda_cudart-windows-x86_64-12.9.79-archive/include'
prior=old.read(ROOT/'runs/D085-cupti-activity/build-plan-r3.json');vcvars=prior['vcvars'];cl=prior['cl_exe'];B=H/'build'
args=['cl','/nologo','/O2','/MT','/EHsc','/std:c++17','/W4','/I'+str(sdk),str(H/'probe.cpp'),'/Fo:'+str(B/'probe.obj'),'/Fe:'+str(B/'probe.exe')]
body='call "'+vcvars+'" >nul && '+subprocess.list2cmdline(args)
command='cmd.exe /d /s /c "'+body+'"'
inputs=[*H.iterdir(),Path(__file__),ROOT/'runs/D094-prepare.py',ROOT/'runs/accepted-E051/common_e051.py',ROOT/'runs/D085-cupti-activity/bootstrap.json',ROOT/'runs/E057-resource/protocol.json',ROOT/'runs/E057-resource/report.json',ROOT/'runs/E057-resource/execution/probe.stdout.log',ROOT/'runs/E057-closure/decision.json',Path(vcvars),Path(cl),*sdk.rglob('*.h')]
P={'id':'D094-resource-materiality','at':old.now(),'status':'FROZEN_PRE_COMPILE_AND_NATIVE','command':command,'compiler_arguments':args,'vcvars':vcvars,'cl_exe':cl,'sdk_header_sha256':old.sha(sdk/'cuda_occupancy.h'),'input_sha256':{str(p):old.sha(p) for p in inputs if p.is_file()},'expected_rows':20480,'expected_retained_driver_matches':60,'kernel_launches':0,'solver_executions':0,'no_new_candidate_or_historical_rescue':True,'gate':'All model rows/independent allocation formula/pair metrics exact and all60 retained driver occupancies match; otherwise no resource filter change.'}
assert not B.exists() and not (H/'execution').exists();old.save(H/'protocol.json',P)
published={}
for p in H.iterdir():
    if not p.is_file():continue
    key='evidence/'+H.name+'/'+p.name;dst=old.ar.DASHBOARD/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
    with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=15) as response:assert response.read()==p.read_bytes()
    published[key]=old.sha(p)
old.save(H/'pre-execution-publication.json',{'at':old.now(),'published':published,'http_bytes_verified':True,'native_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=old.read(old.ar.STATUS);assert not any(e['id']=='D094' for e in s['experiments'])
    s['experiments'].append({'id':'D094','at':old.now(),'title':'Audit nominal registers against actual allocation units','kind':'diagnostic','status':'running','correctness':'pending','stage':'Frozen CPU SDK model and live device-property query','reason':'A nominal register increase need not consume a larger allocation quantum. Check NVIDIAcompute12.0 allocation model against60 retained driver occupancy observations and20,480 complete model rows. No historical reopening, source candidate, kernel execution or performance claim.','evidence':[{'label':'Audit rationale and official references','url':'evidence/D094-resource-materiality/proposal.json'},{'label':'Frozen all-block-size audit protocol','url':'evidence/D094-resource-materiality/protocol.json'}]})
    s.update(updated_at=old.now(),state='running',active_experiment='D094',stage='Resource materiality audit',activity='Audit whether nominal register-count filters reject changes with the same allocated resources. The1% accuracy/no-repeatable-slowdown policy and historical decisions remain unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print(json.dumps({'protocol_sha256':old.sha(H/'protocol.json'),'published':len(published),'expected_rows':20480}),flush=True)
