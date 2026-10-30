"""Serially run, assess and independently replay the fixed fresh16 confirmation."""
import sys
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051-live-20261018'));import common_e051_live as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
old.custody();out=ROOT/'runs/E080-confirmation-wrapper';assert not out.exists();out.mkdir()
old.child([sys.executable,str(H/'native.py'),sys.argv[1]],out,'native',old.env(),1800)
ex=ROOT/'runs/E080-confirmation-execution'
receipt=old.read(out/'native.exit.json');assert receipt['returncode']==0 and receipt['error'] is None
old.save(ex/'terminal.json',{'at':old.now(),'returncode':0,'complete_sha256':old.sha(ex/'complete.json'),'wrapper_receipt_sha256':old.sha(out/'native.exit.json')})
old.child([sys.executable,str(H/'assess.py'),sys.argv[1]],out,'assessment',old.env(),120)
old.child([sys.executable,str(H/'root-check.py'),sys.argv[1]],out,'root-replay',old.env(),120)
old.custody();q=old.read(ROOT/'comparisons/E080-fresh16-confirmation/report.json')
old.save(out/'complete.json',{'at':old.now(),'all_children_terminal':True,'decision':q['decision'],'assessment_sha256':old.sha(ROOT/'comparisons/E080-fresh16-confirmation/report.json'),'root_replay_sha256':old.sha(ROOT/'comparisons/E080-fresh16-root-check/report.json')})
print({'decision':q['decision'],'performance':q['performance']},flush=True)
