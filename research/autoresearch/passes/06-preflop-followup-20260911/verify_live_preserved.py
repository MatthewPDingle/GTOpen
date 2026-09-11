"""Read-only final verification. Never modify live sessions or processes."""
from run_experiment import HERE,ROOT,idle
import datetime,json,subprocess,urllib.request

idle()
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
if head!='92c86ed73aa0856df8479b5c7635e1469f48f1e8': raise RuntimeError('Main checkout changed; inspect')
command='$gtopenListener = Get-NetTCPConnection -LocalPort 56708 -State Listen; Get-CimInstance Win32_Process -Filter "ProcessId=$($gtopenListener.OwningProcess)" | Select-Object ProcessId,ExecutablePath | ConvertTo-Json -Compress'
process=json.loads(subprocess.check_output(['powershell','-NoProfile','-Command',command],text=True,creationflags=subprocess.CREATE_NO_WINDOW))
expected=str(ROOT/'target/autoresearch/preflop-interactive-production-20260911/target/qualification/gto-server.exe')
if process['ProcessId']!=99900 or process['ExecutablePath'].lower()!=expected.lower(): raise RuntimeError('Live process changed; inspect')
statuses={}
for route in ('/api/preflop/status','/api/status','/api/reports/status'):
    with urllib.request.urlopen('http://127.0.0.1:56708'+route,timeout=3) as f: data=json.load(f)
    statuses[route]={k:v for k,v in data.items() if k in ('state','running','iteration','iter','engine')}
(HERE/'live-preservation.json').write_text(json.dumps(dict(checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),main_head=head,process=process,statuses=statuses,actions='Read-only verification; no deployment, session mutation or server restart'),indent=2)+'\n',encoding='utf-8',newline='\n')
