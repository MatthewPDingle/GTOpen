import ast,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D291-static-fold-control';O=H/'execution';P=h.read(H/'protocol.json');h.custody()
assert not(ROOT/'gpu-run.lock').exists();assert h.read(O/'probe.exit.json')['returncode']==0
C=h.read(O/'complete.json')
for p,d in C['raw_file_sha256'].items():h.pin(p,d)
reader=H/'audit-r2.py';code=(H/'audit.py').read_text().replace('D243','D291');ast.parse(code);reader.write_bytes(code.encode())
files=[H/n for n in ['audit.py','baseline.ptx','candidate.ptx','corpus.json','probe.rs']]+[reader]
h.save(H/'preparation.json',{'at':h.now(),'input_sha256':{p.name:h.sha(p)for p in files},'scope':'Same entire original360fold cases. Mechanical packaging correction after native0: missing preparation metadata and reader namespace matched to original frozen D291 native magic; no reader numerical gate changes, no native rerun.'})
protocol=H/'reader-protocol-r2.json';h.save(protocol,{'at':h.now(),'status':'FROZEN_BEFORE_FIRST_NUMERICAL_RAW_DECODE','input_sha256':{str(p):h.sha(p)for p in files+[H/'preparation.json',H/'protocol.json',O/'complete.json',O/'audit.stderr.log',Path(__file__)]},'raw_sha256':C['raw_file_sha256'],'repair':'Original reader exited1 before opening raw files at absent preparation.json. New preparation manifest and D243->D291 namespace only. Full360/720 exact output/input/guard corpus retained; never repeat completed native.'})
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());h.child([sys.executable,str(reader),'up-fold',str(H),P['raw_output'],P['report']],O,'audit-r2',1200)
 for p,d in C['raw_file_sha256'].items():h.pin(p,d)
 r=h.read(P['report']);assert r['cases']==360 and r['kernel_launches']==720
 h.save(O/'reader-complete.json',{'at':h.now(),'report_sha256':h.sha(P['report']),'reader_protocol_sha256':h.sha(protocol),'all_owned_children_terminal':True,'native0_original_reader1_repaired_reader0':True,'completed_native_repeated':False})
dst=h.ar.DASHBOARD/'evidence'/Path(P['report']).parent.name/'report.json';dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(P['report'],dst)
h.custody();print({k:r[k]for k in ['status','cases','kernel_launches','checks','output_words_both_arms','immutable_words_both_arms','guard_words_both_arms']},flush=True)
