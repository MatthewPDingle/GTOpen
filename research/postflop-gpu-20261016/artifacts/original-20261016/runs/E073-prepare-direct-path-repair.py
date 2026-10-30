"""Preserve two pre-native preparation faults; do not repeat any GPU case."""
from pathlib import Path
import sys
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as old
old.custody();assert not(R/'gpu-run.lock').exists()
H=R/'runs/E073-kernel-control-r2';assert not(H/'execution').exists()and not(H/'probe.exe').exists()
old.save(H/'pre-native-path-failure.json',{'at':old.now(),'stage':'executor preflight protocol path','error':'Generated executor used unversioned E073-kernel-control, before compiler/native creation.','manager_receipt_sha256':old.sha(R/'runs/E073-direct-manager/direct.exit.json'),'protocol_preserved':True,'compilers':0,'application_kernel_launches':0,'source_changed':False})
src=R/'runs/E073-prepare-direct-r2.py';s=src.read_text(encoding='utf-8').replace('E073-kernel-control-r2','E073-kernel-control-r3').replace('E073-run-direct-r2.py','E073-run-direct-r3.py')
needle="runner=runner.replace('import json,re,shutil,subprocess,sys,time'";assert s.count(needle)==1
s=s.replace(needle,"runner=runner.replace(\"H=ROOT/'runs/E073-kernel-control'\",\"H=Path(__file__).resolve().parent\")\n"+needle)
p=R/'runs/E073-prepare-direct-r3.py';compile(s,str(p),'exec')
with p.open('x',encoding='utf-8',newline='\n')as f:f.write(s)
s=(R/'runs/E073-run-direct-r2.py').read_text(encoding='utf-8').replace('E073-kernel-control-r2','E073-kernel-control-r3').replace('E073-direct-manager','E073-direct-manager-r3')
# Publication and the ledger explicitly preserve failures before any compiler.
s=s.replace("M,R/'runs/D119-boundary-load-audit'", "M,R/'runs/D119-boundary-load-audit',R/'runs/E073-kernel-control',R/'runs/E073-kernel-control-r2',R/'runs/E073-direct-manager'")
s=s.replace('Before first E073numeric launch, prospective364case corpus', 'Two preparation failures preserved: missing token separation caught by ast.parse before protocol/compiler, then unversioned executor path caught before compiler creation. R3derives its own directory; exact same source/corpus/thresholds/PTX, no numerical case or compiler repeated. Original preparation scripts/failure receipts retained. Before first E073numeric launch, prospective364case corpus')
p=R/'runs/E073-run-direct-r3.py';compile(s,str(p),'exec')
with p.open('x',encoding='utf-8',newline='\n')as f:f.write(s)
print('R2 failure preserved; fresh r3 executor derives its directory. No compiler, GPU case or source changed.',flush=True)
