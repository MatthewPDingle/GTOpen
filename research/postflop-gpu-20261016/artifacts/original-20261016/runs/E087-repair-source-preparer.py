"""Preserve a pre-source bookkeeping failure; fix only overlapping reversal."""
from pathlib import Path
import ast
import shutil
import sys
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'))
import common_e080_live as old
old.custody()
S=R/'runs/E087-source'
assert S.exists() and not list(S.iterdir())
original=R/'runs/E087-prepare-source.py'
out=R/'runs/E087-source-preparation-failure'
out.mkdir(exist_ok=False)
shutil.copyfile(original,out/'original-preparer.py')
old.save(out/'report.json',{
    'at':old.now(),'original_preparer_sha256':old.sha(original),
    'error':'AssertionError at line110: reverse==mod',
    'cause':'The strategy-only replacement is textually identical to the second download call in the full-sync replacement. Naive first-occurrence reversal restores the wrong occurrence.',
    'repair':'Reverse the strategy-only occurrence from the end, then reverse the full-sync and constructor replacements. Candidate generated text is unchanged. Recover the verified still-empty output folder without deleting anything.',
    'candidate_source_files_created':0,'compiler_native_executions':0,
    'algorithm_cases_gates_changed':False
})
t=original.read_text()
t=t.replace("S=R/'runs/E087-source';S.mkdir(exist_ok=False)",
    "S=R/'runs/E087-source'\nif S.exists():assert not list(S.iterdir())\nelse:S.mkdir()")
before="for before,after in reversed(mod_edits):reverse=reverse.replace(after,before,1)"
after="""for before,after in reversed(mod_edits):
    if after==strategy_after:
        at=reverse.rfind(after);assert at>=0
        reverse=reverse[:at]+before+reverse[at+len(after):]
    else:
        assert reverse.count(after)==1
        reverse=reverse.replace(after,before,1)"""
assert t.count(before)==1
t=t.replace(before,after,1)
ast.parse(t)
target=R/'runs/E087-prepare-source-r2.py'
assert not target.exists()
target.write_text(t,encoding='utf-8',newline='\n')
print(target,flush=True)
