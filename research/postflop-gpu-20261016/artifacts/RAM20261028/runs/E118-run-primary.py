import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2;P=ROOT/'runs/E118-primary-plan/protocol.json';h.pin(P,sys.argv[1]);h.custody();O=ROOT/'runs/E118-primary-wrapper';O.mkdir(exist_ok=False)
for label in ['native','assess','root-check']:
 h.child([sys.executable,str(ROOT/'runs'/('E118-primary-'+label+'.py')),sys.argv[1]],O,label,1800);h.custody();h.pin(P,sys.argv[1])
h.save(O/'complete.json',{'at':h.now(),'protocol_sha256':sys.argv[1],'all_owned_children_terminal':True,'no_extra_native_samples':True,'candidate_accepted':False})
q=h.read(ROOT/'comparisons/E118-three-pair-comparison/report.json');print(q['decision'],q['performance'],flush=True)
