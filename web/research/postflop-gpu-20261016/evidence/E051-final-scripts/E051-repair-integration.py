import difflib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
old.custody();I=ROOT/'runs/E051-main-integration';original=ROOT/'runs/E051-qualify-and-integrate.py'
old.save(I/'failure.json',{'at':old.now(),'returncode':1,'failure':'Default git diff --check treats exact tested CRLF candidate source as trailing whitespace; baseline is LF. Stopped before any commit or main mutation. Research file restored byte-exact acceptedE020.','all_sources_restored':True,'native_outcomes_changed':False})
src=original.read_text().replace("Q=ROOT/'comparisons/E051-qualification';I=ROOT/'runs/E051-main-integration'","Q=ROOT/'comparisons/E051-qualification-r2';I=ROOT/'runs/E051-main-integration-r2'")
src=src.replace("['git','diff','--check','--',rel]","['git','-c','core.whitespace=cr-at-eol','diff','--check','--',rel]")
src=src.replace("cmd=['git','commit','--only'","cmd=['git','-c','core.autocrlf=false','commit','--only'")
script=ROOT/'runs/E051-qualify-and-integrate-r2.py';script.write_text(src,encoding='utf-8',newline='\n')
b=(ROOT/'runs/E051-source/baseline.cu').read_text();c=(ROOT/'runs/E051-source/candidate.cu').read_text();patch=''.join(difflib.unified_diff(b.splitlines(True),c.splitlines(True),fromfile='acceptedE020',tofile='testedE051'))
old.save(I/'repair.json',{'at':old.now(),'status':'prepared_no_behavior_or_evidence_change','same_exact_tested_crlf_bytes':True,'reason':'Recognize CR at line endings only for whitespace check; no source byte normalization. Per-command core.autocrlf=false preserves tested bytes in commit. No global Git setting changes.','normalized_diff':patch,'new_script':str(script),'new_script_sha256':old.sha(script),'original_script_sha256':old.sha(original)})
print(old.sha(script),flush=True)
