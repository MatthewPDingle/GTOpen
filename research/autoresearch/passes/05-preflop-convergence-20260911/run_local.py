from run_experiment import idle, LAB, HERE
import hashlib,json,subprocess,time
if __name__=='__main__':
    reference=LAB/'target/convergence/six-reference-tight-a/final.gtop'
    for name in ['six-native-b','six-s64-a','six-s128-a','six-s128-b','six-s128-c']:
        idle()
        candidate=LAB/'target/convergence'/name/'final.gtop'
        output=HERE/'raw'/f'{name}-local.json'
        if output.exists(): raise RuntimeError('Audit output exists')
        exe=LAB/'target/release/examples/convergence_local.exe'
        started=time.monotonic();reason=None
        with (HERE/'raw'/f'{name}-local.log').open('x') as f:
            p=subprocess.Popen([str(exe),str(candidate),str(reference),str(output)],cwd=LAB,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            try:
                while p.poll() is None:
                    time.sleep(1);idle()
                    if time.monotonic()-started>600:raise RuntimeError('Local audit cap')
            except Exception as e:
                reason=str(e)
                if p.poll() is None:p.kill()
            p.wait(timeout=30)
        record={'name':name,'returncode':p.returncode,'reason':reason,'seconds':time.monotonic()-started,
            'exe_sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),
            'reference_sha256':hashlib.sha256(reference.read_bytes()).hexdigest()}
        (HERE/'raw'/f'{name}-local-exit.json').write_text(json.dumps(record,indent=2))
        print(json.dumps(record),flush=True)
        if reason or p.returncode:raise RuntimeError(reason or 'audit failure')
