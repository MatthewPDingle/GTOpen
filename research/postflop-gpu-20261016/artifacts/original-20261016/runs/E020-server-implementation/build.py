"""Root-only one-shot isolated E020 compile/freeze; no tests or server launch."""
import common as c
import shutil,subprocess,sys,time
OUT=c.ROOT/'runs/E020-server-build'
def main():
    assert len(sys.argv)==2,'build authorization SHA required';c.initialize('build',sys.argv[1])
    with c.ar.exclusive_lock(c.ROOT/'gpu-run.lock'):
        c.verify();c.ar.refuse_active(c.ar.live_status());assert not OUT.exists() and not c.TARGET.exists()
        assert shutil.disk_usage(c.ROOT).free>=54*1024**3
        for name in ['E020-gto-server','E020-server-tests']:
            for suffix in ['.exe','.manifest.json']:assert not (c.ROOT/'binaries'/(name+suffix)).exists()
        OUT.mkdir();c.TARGET.mkdir();before=c.live_identity();c.heartbeat('Preparing isolated E020 server build; live deployment remains blocked.',OUT)
        c.save(OUT/'started.json',{'at':c.now(),'authorization_sha256':sys.argv[1],'prepared_manifest_sha256':c.sha(c.HERE/'prepared-manifest.json'),'source_sha256':c.SOURCES,'target_previously_absent':True,'live_identity':before,'rustc':c.capture(['rustc','-Vv']),'cargo':c.capture(['cargo','-V'])})
        outputs=[]
        try:
            for index,verb in enumerate(['build','test']):
                folder=OUT/str(index);folder.mkdir();command=['cargo',verb,'--release','--locked','-p','server','--features','gpu','--bin','gto-server']
                if verb=='test':command+=['--no-run']
                command+=['--message-format=json'];e=c.env(True);proc=None;error=None;cleanup=None;start=time.monotonic()
                c.save(folder/'invocation.json',{'at':c.now(),'args':command,'cwd':str(c.REPO),'timeout_seconds':1800,'environment':{'CARGO_TARGET_DIR':e['CARGO_TARGET_DIR'],'RAYON_NUM_THREADS':e['RAYON_NUM_THREADS']},'compiler_override_absence_checked':True})
                try:
                    with (folder/'stdout.jsonl').open('xb') as out,(folder/'stderr.log').open('xb') as err:
                        proc=subprocess.Popen(command,cwd=c.REPO,env=e,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
                        assert proc.pid!=c.LIVE['pid'];last=start
                        while proc.poll() is None:
                            if time.monotonic()-start>1800:raise TimeoutError('server compile1800s')
                            if time.monotonic()-last>=10:
                                c.heartbeat(f'Isolated E020 compile {index}: {time.monotonic()-start:.0f}s; no live executable changes.',OUT)
                                try:print(f'E020 isolated compile {index}: {time.monotonic()-start:.0f}s',flush=True)
                                except Exception:pass
                                last=time.monotonic()
                            time.sleep(.25)
                        assert proc.returncode==0,folder
                except BaseException as exc:
                    error=repr(exc)
                    if proc is not None and proc.pid!=c.LIVE['pid']:cleanup=c.ar.cleanup_child(proc)
                    raise
                finally:c.save(folder/'exit.json',{'at':c.now(),'returncode':proc.returncode if proc else None,'error':error,'cleanup':cleanup,'wall_ms':(time.monotonic()-start)*1000})
                c.verify()
                logs=[c.json.loads(x) for x in (folder/'stdout.jsonl').read_text(encoding='utf-8').splitlines()]
                assert any(x.get('reason')=='build-finished' and x.get('success') is True for x in logs)
                artifacts=[x for x in logs if x.get('reason')=='compiler-artifact']
                for item in artifacts:
                    for f in item.get('filenames',[])+([item['executable']] if item.get('executable') else []):assert c.Path(f).resolve().is_relative_to(c.TARGET.resolve()),f
                rows=[x for x in artifacts if x.get('executable') and x['target']['name']=='gto-server'];assert len(rows)==1
                item=rows[0];assert item['profile']['test']==(verb=='test') and item['fresh'] is False
                assert c.Path(item['manifest_path']).resolve()==c.REPO/'crates/server/Cargo.toml'
                assert c.Path(item['target']['src_path']).resolve()==c.REPO/'crates/server/src/main.rs'
                solver=[x for x in artifacts if x['target']['name']=='solver' and x['target']['kind']==['lib']];assert len(solver)==1
                assert c.Path(solver[0]['target']['src_path']).resolve()==c.REPO/'crates/solver/src/lib.rs'
                if index==0:assert solver[0]['fresh'] is False
                name='E020-gto-server' if index==0 else 'E020-server-tests';dest=c.ROOT/'binaries'/(name+'.exe');assert not dest.exists()
                shutil.copyfile(item['executable'],dest)
                manifest={'candidate':'E020','source_root':str(c.REPO),'source_commit':c.read(c.pin(c.AUTH['acceptance']))['research_commit'],'source_sha256':c.SOURCES,'source_matches_prebuild':True,'binary_sha256':c.sha(dest),'prepared_manifest_sha256':c.sha(c.HERE/'prepared-manifest.json'),'acceptance':c.AUTH['acceptance'],'built_at':c.now(),'cargo_artifact':item,'solver_artifact':solver[0],'target_dir':str(c.TARGET),'command':command,'build_log_sha256':c.sha(folder/'stdout.jsonl'),'build_stderr_sha256':c.sha(folder/'stderr.log'),'embedded_cuda_occurrences':c.embedded(dest),'dependency_sha256':{f:c.sha(f) for x in artifacts for f in x.get('filenames',[]) if c.Path(f).suffix in {'.rlib','.rmeta','.lib','.dll'}},'live_executable_touched':False,'scope':'Isolated compile-only, no deployment or performance claim'}
                c.save(dest.with_suffix('.manifest.json'),manifest);outputs.append({'path':str(dest),'sha256':c.sha(dest),'manifest_sha256':c.sha(dest.with_suffix('.manifest.json'))})
            c.verify();assert c.live_identity()==before
            c.heartbeat('Isolated E020 server build complete; native unit/API validation pending, live deployment blocked.',OUT)
            c.save(OUT/'report.json',{'status':'pass','at':c.now(),'outputs':outputs,'source_unchanged':True,'tests_executed':0,'server_launched':False,'live_executable_touched':False})
        except BaseException as error:
            c.save(OUT/'failure.json',{'at':c.now(),'status':'failed','error':repr(error),'preserve_all_evidence':True,'no_equivalent_live_retry':True});raise
if __name__=='__main__':main()
