"""Additive preparer-only text locator repair before any compiler/native case."""
import ast,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();old=ROOT/'runs/D272-metadata-canonical';assert old.is_dir()and not list(old.iterdir())
p=ROOT/'runs/D272-prepare-canonical.py';text=p.read_text(encoding='utf-8')
before="helper.index('fn d271_expected_rows(')";assert text.count(before)==1;text=text.replace(before,"helper.index('fn d271_expected_rows<')",1)
before="+audit[end:]";assert text.count(before)==1;text=text.replace(before,"+audit[end+1:]",1)
text=text.replace('D272-metadata-canonical','D272-metadata-canonical-v2')
ast.parse(text);dest=ROOT/'runs/D272-prepare-canonical-v2.py'
with dest.open('x',encoding='utf-8',newline='\n')as f:f.write(text)
h.save(old/'generation-failure.json',{'at':h.now(),'old_generator_sha256':h.sha(p),'new_generator_sha256':h.sha(dest),'reason':'Preparer searched for generic fn d271_expected_rows using parenthesis rather than type-parameter bracket, before creating any source/protocol/compiler/native output. Additive successor also corrects planned audit string closing delimiter before syntax check. Actual E115 source, cases, mapping, resource and numerical/performance gates unchanged.','compiled_or_native_cases':0,'source_activated':False})
print(h.sha(dest),flush=True)
