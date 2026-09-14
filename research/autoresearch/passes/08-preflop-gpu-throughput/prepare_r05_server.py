"""Reuse the established isolated HTTP release checks with the combined build."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
s=(HERE/'r04_server_qualify.py').read_text(encoding='utf-8').replace('r04','r05').replace('R04','R05')
(HERE/'r05_server_qualify.py').write_text(s,encoding='utf-8')
s=(HERE/'run_r04_server.py').read_text(encoding='utf-8').replace('r04','r05').replace('R04','R05')
s=s.replace("assert read(RAW/'r05-saved-verified.json')['passed']","assert read(RAW/'r05-current-v1-exit.json')['returncode']==0")
(HERE/'run_r05_server.py').write_text(s,encoding='utf-8')
