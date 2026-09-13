"""Restore only C21 integration if the fixed complete-work screen rejects it."""
import hashlib,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;LAB=HERE.parents[3]
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    result=json.loads((HERE/'raw/c21-timing-screen-verified.json').read_text())
    assert result['verified'] and not result['retained'] and not result['passed_screen']
    base='79aa845';mapping=json.loads((HERE/'artifacts/c21-v2-source-map.json').read_text());restore={}
    for relative,entry in mapping.items():
        p=LAB/relative;assert sha(p.read_bytes())==entry['sha256'],relative
        restore[relative]=subprocess.check_output(['git','show',base+':'+relative],cwd=LAB)
    for relative,data in restore.items():(LAB/relative).write_bytes(data)
    assert not subprocess.check_output(['git','diff','HEAD','--','crates'],cwd=LAB)
    out=dict(baseline=base,integration_removed=True,standalone_diagnostic_retained=True,
        files={p:sha(data) for p,data in restore.items()},
        qualified_r03_sha256=sha((LAB/'target/r03-v3-server-frozen.exe').read_bytes()))
    assert out['qualified_r03_sha256']=='5035a18f206e7364217e86154481faf2c139d6fdce43b936d630bbb64dc88c8e'
    (HERE/'raw/c21-restoration.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
