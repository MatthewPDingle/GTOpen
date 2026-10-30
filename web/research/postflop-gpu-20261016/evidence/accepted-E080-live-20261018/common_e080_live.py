"""Accepted E080 source and live deployment epoch."""
import subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
sys.path.insert(0,str(ROOT/'runs/accepted-E080'));import common_e080 as previous
historical=previous.historical
read,sha,pin,save,now,env,child=previous.read,previous.sha,previous.pin,previous.save,previous.now,previous.env,previous.child
ar,compare,REPO=previous.ar,previous.compare,previous.REPO
BASE=read(HERE/'baseline.json')['source_sha256']
def custody():
 assert ar.source_identity()['source_sha256']==BASE
 targets=read(HERE/'preexisting-target-artifacts.json')
 for n,r in targets.items():pin(REPO/n,r['sha256']);assert(REPO/n).stat().st_size==r['bytes']
 m=read(HERE/'protected-main.json');app=Path(m['root'])
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=app,text=True).strip()==m['git_head']
 for n,h in m['source_sha256'].items():pin(app/n,h)
 for n in m['absent_research_paths']:assert not(app/n).exists()
 pin(m['live_path'],m['live_sha256'])
 assert not subprocess.check_output(['git','diff','--name-only','HEAD','--','crates/solver'],cwd=REPO,text=True).strip()
 assert set(subprocess.check_output(['git','ls-files','--others','--exclude-standard','--','crates/solver'],cwd=REPO,text=True).splitlines())==set(targets)
 return BASE
