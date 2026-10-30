"""Validate the generated read-only decoder before sealing any native plan."""
from pathlib import Path
p=Path(r'S:\GTOpen-research\postflop-gpu-20261016\runs\E075-prepare-resource.py');s=p.read_text(encoding='utf-8');lines=s.splitlines(True)
found=0
for i,line in enumerate(lines):
 if line.startswith('  sites=lambda t:'):
  lines[i]="  sites=lambda t:re.findall(r'ldu[.]global[.](?:u32|s32|u64|s64)',t)\n";found+=1
 if 'assert data[:6]=='in line:
  a=line.index('assert data[:6]==');b=line.index(';assert marks',a);lines[i]=line[:a]+'assert data[:6]==bytes([127,69,76,70,2,1])'+line[b:];found+=1
assert found==2;s=''.join(lines);a=s.index('# The assessment text is a raw literal');b=s.index('prior=old.read(',a)
replacement='''parsed=ast.parse(code);assignments=[n for n in ast.walk(parsed)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='sites'for t in n.targets)];assert len(assignments)==1
ns={'re':__import__('re')};exec(compile(ast.Module(body=assignments,type_ignores=[]),'<precompile-LDU-decoder-fixture>','exec'),ns)
assert ns['sites']('ldu.global.u32 %r1, [%rd1];')==['ldu.global.u32'];assert ns['sites']('ld.global.nc.u32 %r1, [%rd1];')==[]
executor=R/'runs/E075-resource-execute.py';assert not executor.exists();executor.write_text(code,encoding='utf-8',newline='\\n')
'''
s=s[:a]+replacement+s[b:];compile(s,str(p),'exec');p.write_text(s,encoding='utf-8',newline='\n');print('Unexecuted preparation syntax/decoder fixtures ready; no protocol/compiler/GPU execution.',flush=True)
