"""Prepare the unchanged three-pair protocol generator; no GPU/score execution."""
import ast,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'runs/E099-prepare-primary.py';target=ROOT/'runs/E104-prepare-primary.py'
assert not target.exists()
code=source.read_text(encoding='utf-8').replace('E099','E104').replace('V099','V104').replace('D186-paired-canonical-control','D210-resident-canonical-controls').replace('D185-paired-engine-controls','D209-resident-engine-controls')
for a,b in [('B311','B317'),('B312','B318'),('B313','B319')]:code=code.replace(a,b)
code=code.replace("['cases']==68","['cases']==36").replace("ROOT/'runs/E104-resource/report.json'","ROOT/'runs/D207-resident-resource/report.json'").replace("ROOT/'runs/E104-source/manifest.json'","ROOT/'runs/E104-source/manifest-r2.json'")
needle="ROOT/'comparisons/E104-direct-controls/report.json',";assert code.count(needle)==1;code=code.replace(needle,'',1)
code=code.replace('Allresource/direct/68case/fullcanonicalraw gates passed','Allresource/sourceprojection/36case/fullcanonicalraw gates passed').replace('Paired action full solve speed screen','Resident cooperative full solve speed screen').replace('Paired action accuracy','Resident cooperative accuracy')
code=code.replace("'BroaderF32/state/menu/save/resume/paging/stored-continuation/cache/fallback compatibility,actualCPU/process/memory/capacity/graph/resource costs; lower down theoreticaloccupancy is not dismissed by faster timing.'","'Direct exceptional/zero/arity/full-reuse comparisons plusbroaderF32/state/menu/save/resume/paging/stored-continuation/cache/fallback compatibility,actualCPU/process/memory/capacity/graph/resource costs; lowerdown theoreticaloccupancy isnotdismissedbyfastertiming. Headerdistribution/portableproductiondelivery remainsrequired.'")
needle="for stem in ['E104-feature-solver'";assert code.count(needle)==1;code=code.replace(needle,"files.extend(Path(p) for p in b['input_sha256'] if '/include/' in p.replace('\\\\','/'))\n"+needle,1)
ast.parse(code);target.write_text(code,encoding='utf-8',newline='\n')
print(target)
