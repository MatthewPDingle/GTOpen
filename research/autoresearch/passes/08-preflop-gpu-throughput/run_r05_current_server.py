import sys
from pathlib import Path
from run_c23 import HERE,RAW,read,run07
helper=HERE/'saved_arena_fingerprint.rs';exe=run07.LAB/'target/r05-saved-fingerprint.exe'
run07.run('r05-fingerprint-build-v1',['rustc','-O',helper,'-o',exe],60,[helper],{})
run07.run('r05-current-server-v1',[sys.executable,HERE/'r05_current_server.py'],600,
 [HERE/'R05_PROTOCOL.md',Path(__file__),HERE/'r05_current_server.py',HERE/'r05_server_qualify.py',exe,
  run07.LAB/'target/r05-server-frozen.exe',run07.LAB/'target/c24-user-fixture/iteration53.gtop'],{})
assert read(RAW/'r05-current-server-v1.json')['passed']
