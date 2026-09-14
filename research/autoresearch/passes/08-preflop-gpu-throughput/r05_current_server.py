"""Normal-feature HTTP C24 selection, save/reload, and full-arena audit."""
import json,os,shutil,socket,subprocess,time
import r05_server_qualify as h
h.ROOT=h.LAB/'target/r05-current-server-v1'
OUT=h.RAW/'r05-current-server-v1.json'
def main():
 assert not h.ROOT.exists() and not OUT.exists()
 with socket.socket() as s:s.bind(('127.0.0.1',h.PORT))
 (h.ROOT/'cache').mkdir(parents=True);(h.ROOT/'saves/preflop').mkdir(parents=True)
 for name in ['preflop_eq169.bin','realization_fit.json']:shutil.copyfile(h.LAB/'cache'/name,h.ROOT/'cache'/name)
 source=h.LAB/'target/c24-user-fixture/iteration53.gtop'
 shutil.copyfile(source,h.ROOT/'saves/preflop/source.gtop')
 env=os.environ.copy();env.update(PORT=str(h.PORT),SOLVER_GPU='1',SOLVER_GPU_MEM_MB='23911',SOLVER_THREADS='8',
  REALIZATION_FIT=str(h.ROOT/'cache/realization_fit.json'))
 result={'executable_sha256':h.sha(h.EXE),'port':h.PORT,'source_sha256':h.sha(source),'checkpoints':[]}
 child=None;log_path=h.RAW/'r05-current-server-v1-server.log'
 try:
  with log_path.open('x',encoding='utf-8') as log:
   child=subprocess.Popen([str(h.EXE)],cwd=h.ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
   until=time.monotonic()+20
   while True:
    assert child.poll() is None
    try:h.api('/api/status',timeout=1);break
    except OSError:
     assert time.monotonic()<until;time.sleep(.2)
   loaded=h.api('/api/preflop/load',{'name':'source'});assert loaded['iteration']==53
   reference=h.read(h.RAW/'c24-current-candidate-full1-bench.json')
   for age in [56,59]:
    h.api('/api/preflop/solve',{'iterations':3,'check_every':3,'target_gap':0})
    state=h.finished(child,180)
    assert state['gpu'] and state['gpu_note']=='Memory-efficient GPU evaluation',state
    assert state['state']=='done' and state['iteration']==age
    expected=reference['rows'][age-54]
    for k in ['gaps','evs']:assert state[k]==expected[k],(age,k)
    saved=h.save('checkpoint'+str(age));root=h.api('/api/preflop/node',{'path':[]})
    h.api('/api/preflop/load',{'name':'checkpoint'+str(age)})
    reloaded=h.api('/api/preflop/node',{'path':[]});root.pop('publication',None);reloaded.pop('publication',None);assert root==reloaded
    result['checkpoints'].append({'iteration':age,'status':state,'saved':saved,'root_reload_exact':True})
    print(json.dumps({'normal_server_checkpoint':age,'exact':True}),flush=True)
   fingerprint=json.loads(subprocess.check_output([str(h.LAB/'target/r05-saved-fingerprint.exe'),saved['path']],text=True))
   for k in ['arena_fingerprint','arena_entries']:assert fingerprint[k]==reference[k]
   result.update(fingerprint);result['passed']=True
 except Exception as e:result.update(passed=False,error=repr(e));raise
 finally:
  if child is not None:
   if child.poll() is None:child.terminate()
   child.wait(timeout=15)
  with socket.socket() as s:result['owned_port_closed']=s.connect_ex(('127.0.0.1',h.PORT))!=0
  OUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
