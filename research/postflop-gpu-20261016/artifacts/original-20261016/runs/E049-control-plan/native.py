import json,re,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'small-gain-confirmation-plan'));import common as old
ar=old.ar;ROOT=old.ROOT
assert len(sys.argv)==2;old.pin(HERE/'protocol.json',sys.argv[1]);P=old.read(HERE/'protocol.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
old.custody();assert not (ROOT/'gpu-run.lock').exists()
OUT=ROOT/'runs/E049-controls-execution';OUT.mkdir()
records=[]
for mode in P['order']:
 b=P['binaries'][mode];identity=P['ids'][mode]
 old.custody();ar.refuse_active(ar.live_status())
 # A test inventory is executable code too; serialize it, then let ar own
 # the lock for actual unit tests. No ignored benchmarks are admitted here.
 with ar.exclusive_lock(ROOT/'gpu-run.lock'):
  old.child([b['path'],'--list'],OUT,mode+'-inventory',old.env(),120)
 inventory=(OUT/(mode+'-inventory.stdout.log')).read_text(encoding='utf-8')
 listed=re.findall(r'^(.+): test$',inventory,re.M)
 assert len(listed)>30 and len(set(listed))==len(listed)
 cmd=[sys.executable,'-B','tools/postflop_autoresearch.py','--id',identity,'--title','E049 '+mode+' ordinary controls','--kind','validation','--binary',b['path'],'--build-manifest',b['manifest'],'--test','*','--not-ignored']
 old.child(cmd,OUT,identity,old.env(),1200)
 r=old.read(ROOT/'runs'/identity/'report.json');raw=ROOT/'runs'/identity/'stdout.log';old.pin(raw,r['stdout_sha256'])
 text=raw.read_text(encoding='utf-8')
 summary=re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',text)
 assert len(summary)==1
 passed,failed,ignored,measured,filtered=map(int,summary[0])
 assert failed==measured==filtered==0 and passed+ignored==len(listed)
 if mode=='gpu':
  assert (passed,ignored)==(86,4)
  assert 'E049_PREDICATE cases=5600 ' in text
  assert re.search(r'E049_METADATA arena_i16=32 arena_f32=32 store=72',text)
  assert all(name in listed for name in P['required_new_tests'])
 assert r['status']=='measured' and r['returncode']==0
 assert r['binary_sha256']==b['sha256'] and r['binary_build_manifest']['sha256']==b['manifest_sha256']
 assert r['provenance']['source_sha256']==old.BASE
 records.append({'mode':mode,'id':identity,'passed':passed,'ignored':ignored,'inventory_total':len(listed),'stdout_sha256':old.sha(raw),'report_sha256':old.sha(ROOT/'runs'/identity/'report.json')})
 old.custody()
old.save(OUT/'complete.json',{'at':old.now(),'protocol_sha256':sys.argv[1],'records':records,'status':'pass_provenance_controls','predicate_comparisons':5600,'fast_path_witnesses_required':True,'cpu_only_ordinary_passed':True,'gpu_ordinary_passed':True,'candidate_accepted':False,'limits':'Access-history and exact original predicate controls plus ordinary tests. No GPU timing, CPU performance, final codegen, or broader adoption qualification.'})
print(json.dumps({'status':'pass_provenance_controls','records':records,'complete_sha256':old.sha(OUT/'complete.json')}),flush=True)
