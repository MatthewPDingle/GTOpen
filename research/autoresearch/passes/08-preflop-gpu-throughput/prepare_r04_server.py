"""Adapt the qualified isolated-server harness without touching user sessions."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
source=(HERE/'r03_server_qualify_v3.py').read_text(encoding='utf-8')
source=source.replace('import hashlib,json,os,shutil,socket,subprocess,time,urllib.request', 'import hashlib,json,os,re,shutil,socket,subprocess,time,urllib.request')
source=source.replace('target/r03-server-qualification-v3','target/r04-server-qualification-v1')
source=source.replace('target/r03-v3-server-frozen.exe','target/r04-server-frozen.exe')
source=source.replace('r03-server-live-v3','r04-server-live-v1')
source=source.replace('r03-{fixture}-','r04-{fixture}-')
source=source.replace("RAW/f'r04-{fixture}-retained-v1.json'", "RAW/f'r03-{fixture}-retained-v1.json'")
source=source.replace("            for fixture,age in [('small',1000),('large',1050)]:", "            for fixture,age in [('small',1000),('large',1050)]:\n                fixture_started=time.monotonic()")
source=source.replace("                print(json.dumps({'fixture':fixture", "                assert time.monotonic()-fixture_started <= 180, 'fixture exceeded registered cap'\n                print(json.dumps({'fixture':fixture")
source=source.replace("            result['passed']=True", """            log.flush()
            selected=[json.loads(x) for x in re.findall(r'preflop solving on GPU: (\\{[^\\n]+\\})',log_path.read_text(encoding='utf8'))]
            assert len(selected)==10, len(selected)
            assert all(s['static_cdf'] and s['narrow_offsets'] and s['mode']=='retained_cohorts' and s['fallback_reason'] is None and s['static_cdf_fallback_reason'] is None for s in selected)
            result['static_cdf_selections']=selected
            result['passed']=True""")
dest=HERE/'r04_server_qualify.py';assert not dest.exists()
dest.write_text(source,encoding='utf-8')
