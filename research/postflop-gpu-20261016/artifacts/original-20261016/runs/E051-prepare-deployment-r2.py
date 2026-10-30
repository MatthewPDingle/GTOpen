"""Preserve no-operation deployment failure and seal dependency/precision repair."""
from pathlib import Path
import sys
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');sys.path.insert(0,str(R/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not(R/'gpu-run.lock').exists()
first=R/'runs/E051-live-deployment-plan';prior=R/'runs/E051-live-deployment';H=R/'runs/E051-live-deployment-plan-r2'
if H.exists():assert not any(H.iterdir())
else:H.mkdir()
exit_record=old.read(prior/'deployment.exit.json');assert exit_record['returncode']==1 and exit_record['error'] is None and exit_record['cleanup'] is None
assert not(prior/'native-result.json').exists()and not(prior/'original-gto-server.exe').exists()
stderr=(prior/'deployment.stderr.log').read_text(encoding='utf-8');assert "Get-FileHash"in stderr and 'not recognized'in ' '.join(stderr.split())
code=(first/'deploy.ps1').read_text(encoding='utf-8')
guard="if ((Get-FileHash -LiteralPath $Protocol -Algorithm SHA256).Hash.ToLowerInvariant() -ne $ProtocolSha256)"
assert code.count(guard)==1
hashfn="""function Get-TaskHash([string]$TaskPath) {
    $taskStream = [IO.File]::OpenRead($TaskPath)
    $taskHasher = [Security.Cryptography.SHA256]::Create()
    try { return [BitConverter]::ToString($taskHasher.ComputeHash($taskStream)).Replace('-','').ToLowerInvariant() }
    finally { $taskHasher.Dispose(); $taskStream.Dispose() }
}
"""
oldfn="function Get-TaskHash([string]$TaskPath) { (Get-FileHash -LiteralPath $TaskPath -Algorithm SHA256).Hash.ToLowerInvariant() }\n"
assert code.count(oldfn)==1;code=code.replace(oldfn,'').replace(guard,hashfn+"if ((Get-TaskHash $Protocol) -ne $ProtocolSha256)")
code=code.replace('runs\\E051-live-deployment\\','runs\\E051-live-deployment-r2\\')
oldtime="$taskExpectedProcess.StartTime.ToUniversalTime().ToString('o') -ne $taskPlan.old_identity.created"
assert code.count(oldtime)==1;code=code.replace(oldtime,"$taskExpectedProcess.StartTime.ToUniversalTime().ToString('o').Substring(0,26) -ne $taskPlan.old_identity.created.Substring(0,26)")
assert 'Get-FileHash'not in code
with(H/'deploy.ps1').open('x',encoding='utf-8',newline='\n')as out:out.write(code)
with(H/'common_e051_live.py').open('x',encoding='utf-8',newline='\n')as out:out.write((first/'common_e051_live.py').read_text(encoding='utf-8'))
repair={'at':old.now(),'status':'preserved_pre_live_operation_failure','old_protocol_sha256':old.sha(first/'protocol.json'),'old_exit_sha256':old.sha(prior/'deployment.exit.json'),'old_stderr_sha256':old.sha(prior/'deployment.stderr.log'),'original_process37268_still_live_and_hash_exact':True,'backup_not_created':True,'replacement_or_stop_or_start_operations':0,'reported_failure':'Get-FileHash unavailable in the launched child PowerShell despite read-only later interactive command discovery succeeding; exact autoload cause unproven.','repair':'Use .NET SHA256 over an owned file stream instead of the Get-FileHash cmdlet. Algorithm/output unchanged. Retain the original evidence.','additional_preflight_precision_alignment':'.NET reports2026-10-16T02:58:55.0784386Z, while frozen CIM reports2026-10-16T02:58:55.0784380Z. Compare creation at the microsecond precision supported by CIM, while still verifying exact frozen PID/CIM creation/executable/hash/listener and authenticated process handle before stopping.','same_deployment_candidate_and_session_guards':True,'new_GPU_or_performance_samples':0}
old.save(H/'repair.json',repair)
original=R/'runs/E051-deploy-qualified-server.py';new=R/'runs/E051-deploy-qualified-server-r2.py';controller=original.read_text(encoding='utf-8')
controller=controller.replace("H=R/'runs/E051-live-deployment-plan';O=R/'runs/E051-live-deployment'","H=R/'runs/E051-live-deployment-plan-r2';O=R/'runs/E051-live-deployment-r2'")
needle="inputs=[Path(__file__),H/'deploy.ps1'";assert controller.count(needle)==1
controller=controller.replace(needle,"inputs=[Path(__file__),H/'repair.json',R/'runs/E051-live-deployment/deployment.exit.json',R/'runs/E051-live-deployment/deployment.stderr.log',H/'deploy.ps1'")
needle="'source_changes':[],'performance_samples':0";assert controller.count(needle)==1
controller=controller.replace(needle,"'preserved_pre_live_repair':old.read(H/'repair.json'),'source_changes':[],'performance_samples':0")
compile(controller,str(new),'exec')
with new.open('x',encoding='utf-8',newline='\n')as out:out.write(controller)
print('Deployment R2 prepared; original source/live executable custody passes.',flush=True)
