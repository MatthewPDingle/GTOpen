import sys,json,shutil,ast,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'))
import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()
build=ROOT/'runs/E093-final-build/complete.json';done=h.read(build);assert done['all_compilers_terminal'] and done['native_executions']==0
for path,digest in done['evidence_sha256'].items():h.pin(path,digest)
bp=ROOT/'runs/E093-build-plan/protocol.json';b=h.read(bp);H=ROOT/'runs/E093-primary-plan';H.mkdir(exist_ok=False)
scripts={}
for name in ['primary-native','primary-assess','primary-root-check']:
    parent=ROOT/'runs'/('E091-'+name+'.py');code=parent.read_text(encoding='utf-8').replace('E091','E093')
    if name=='primary-native':
        code=code.replace('import sys,json,re,shutil','import sys,json,re,shutil,os',1)
        needle="verify();assert not(ROOT/'gpu-run.lock').exists();O.mkdir(exist_ok=False)"
        insert=needle+"\nassert os.environ.get('GTOPEN_POSTFLOP_NVRTC13_DIR') is None\nos.environ['GTOPEN_POSTFLOP_NVRTC13_DIR']=P['runtime_directory']\nh.save(O/'runtime-environment.json',{'at':h.now(),'GTOPEN_POSTFLOP_NVRTC13_DIR':P['runtime_directory'],'same_value_for_both_arms':True,'scope':'Onlythiscontrolleranditschildren;notpersistentuser/global/PATHsetting'})"
        assert code.count(needle)==1;code=code.replace(needle,insert,1)
        needle="  assert r['provenance']['source_sha256']==P['accepted_source_sha256']and r['binary_build_manifest']['data']==m"
        insert=needle+"\n  stderr=(ROOT/'runs'/record['id']/'stderr.log').read_text(encoding='utf-8')\n  expected_backend=1 if stem.startswith('E093') else 0\n  assert stderr.count('gpu: postflop NVRTC13.0 runtime compiler')==expected_backend\n  assert 'optional postflop NVRTC13 declined:' not in stderr and 'optional NVRTC13 cleanup:' not in stderr"
        assert code.count(needle)==1;code=code.replace(needle,insert,1)
        code=code.replace("print('E093 primary execution complete; assess retained observations.',flush=True)","os.environ.pop('GTOPEN_POSTFLOP_NVRTC13_DIR')\nprint('E093 primary execution complete;assess retained observations.',flush=True)",1)
    path=ROOT/'runs'/('E093-'+name+'.py');assert not path.exists();ast.parse(code);path.write_bytes(code.encode());scripts[name]=path
sequence=[{'id':'V093-unit','binary':'E093-solver','unit':True}]+[{'id':ident,'binary':'E080-postflop_autoresearch' if ident.startswith('B') else 'E093-postflop_autoresearch','unit':False} for ident in ['B299','E093R1','E093R2','B300','B301','E093R3']]
status=h.read(h.ar.STATUS)
for row in sequence:assert not(ROOT/'runs'/row['id']).exists() and not any(x['id']==row['id'] for x in status['experiments'])
tool=ROOT/'runs/D161-toolchain-scout';runtime=tool/'toolchain/nvidia/cu13/bin/x86_64'
files=[Path(__file__),bp,build,ROOT/'runs/E093-build.py',ROOT/'epoch/runner.py',ROOT/'epoch/common.py',ROOT/'epoch/exact-anchor.json',ROOT/'epoch/accepted-source.json',ROOT/'epoch/protected-main.json',ROOT/'epoch/preexisting-target-artifacts.json',ROOT/'comparisons/D167-runtime-compiler-control/report.json',ROOT/'comparisons/D166-canonical-compiler-control/report.json',ROOT/'comparisons/RAM20261028-baseline/report.json',ROOT/'runs/E093-source-r2/manifest.json',ROOT/'runs/E093-source-r2/source-review.json',tool/'toolchain-files.json',h.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md']+list(scripts.values())+list(runtime.glob('*.dll'))
for stem in ['E093-feature-solver','E093-solver','E093-postflop_autoresearch','E080-postflop_autoresearch']:
    exe=ROOT/'binaries'/(stem+'.exe');mp=exe.with_suffix('.manifest.json');m=h.read(mp);h.pin(exe,m['binary_sha256']);assert m['source_sha256']==b['accepted_source_sha256']|(b['candidate_owned_sha256'] if stem.startswith('E093') else {});files +=[exe,mp]
P={'id':'E093-primary','at':h.now(),'status':'FROZEN_PRE_ORDINARY_UNITS_AND_PRIMARY_TIMING','measurement_epoch':'RAM20261028','build_protocol_sha256':h.sha(bp),'accepted_source_sha256':b['accepted_source_sha256'],'candidate_owned_sha256':b['candidate_owned_sha256'],'runtime_directory':str(runtime),'runtime_backend_requirement':'Exactlyone NVRTC13success markerperE093process,zero inbaseline,andnooptionalerrorfallback/cleanup marker. Sameprivatepathenvironment botharms. Missingbackendfailscohort,notsilentbaselinecredit. RealDLL/path/driver/program/close/NVRTC/moduleJITworkinsideoriginalGPUinit/fullcycle.','sequence':sequence,'pairs':[{'baseline':'B299','candidate':'E093R1'},{'baseline':'B300','candidate':'E093R2'},{'baseline':'B301','candidate':'E093R3'}],'required_ordinary_units':86,'required_aggregate_gain_pct':1.0,'fixture_guard':'Rejectpositive median slowdowntogetherwithatleast2/3slowerpairs,evenbelow3%.','excluded_samples_allowed':False,'extension_runs_allowed':False,'historical_or_RAM_baseline_timing_pooling_allowed':False,'required_free_bytes':66*1024**3,'adoption_requirements':['Separately frozen fresh16pairs:unroundedaggregate>=1%,>=13improvingpairs,positivepaired/block/ordermedians,norepeatablefixture slowdown.','Broaderruntime exactstate/F32/menu/save/resume/continuation,actualgraph/launch/memory/capacity/materialCPUandwholeprocessresource costs. Explicitoptionalpackage diskcost disclosure.','Fixedholdout,freshoriginal cumulativecomparisonandserverqualification beforeadoption. No significance,universalbehavior ordeployment frominitialscreen.'],'scope':'Samefrozen3completecycles,compressed/Rayon16/freshnativeprocesses/warmdrivercache/currentRAM. Includes tree/CPUallocation,all GPUinit/actualoptionalruntimeDLLchecks/acquisition/program/compile/close/NVRTC/JIT,samequalitysolve/checks/fullreadback. ExcludesCargo,fingerprints,finaldestruction/API/browser/saving;wholeprocessdestruction/resourcegate remainsmandatory. No changes tobenchmark clocks/source/cfg/quality,candidateversion/flags/thresholds orsamples afterfailure. AlloutputsX;E080main/liveunchanged.','input_sha256':{str(p):h.sha(p) for p in files},'candidate_accepted':False}
h.save(H/'protocol.json',P)
for folder,names in [(H,['protocol.json']),(ROOT/'runs/E093-final-build',['complete.json'])]:
    for name in names:
        path=folder/name;key=folder.name+'/'+name;dest=h.ar.DASHBOARD/'evidence'/key;dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.exists();shutil.copyfile(path,dest)
        with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==path.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);item=next(x for x in status['experiments'] if x['id']=='E093')
    item.update(status='running',stage='86ordinaryunits then3actual-runtime complete-solve pairs',reason='Freshfeature/primary builds passedandacceptedsource restored. Requireactual13backendperprocess,allscienceexact,unrounded>=1%andstrictfixtureguards. No exclusions/extensions/pooling oradoption fromscreen.')
    item.setdefault('evidence',[]).extend([{'label':'Freshbuild provenance','url':'evidence/E093-final-build/complete.json'},{'label':'Frozen actual-runtime speedcomparison','url':'evidence/E093-primary-plan/protocol.json'}])
    status.update(updated_at=h.now(),active_experiment='E093',stage='E093 actual-runtime fullsolve comparison',activity='Run86units then B299/E093R1,E093R2/B300,B301/E093R3. Compiler/DLLcosts insiderealcompleteclocks;strict1%/fixturegates. No newgainaccepted.')
    h.ar.atomic_json(h.ar.STATUS,status)
h.custody();print(h.sha(H/'protocol.json'),flush=True)
