import re
def boundary_loads(entry):
 # Track pointer-address arithmetic only, never the loaded boundary's value.
 origins={};loads=[]
 for raw in entry.splitlines():
  t=raw.strip().split('//',1)[0].strip()
  m=re.fullmatch(r'ld\.param\.u64\s+(%\w+),\s*\[up_show_param_(12|13)\];',t)
  if m:origins[m[1]]={int(m[2])};continue
  m=re.search(r'\bld\.global(?:\.[A-Za-z0-9_]+)*\.(u|b)(16|32|64)\s+(%\w+),\s*\[(%\w+)(?:\+\d+)?\];',t)
  if m:
   if origins.get(m[4]):loads.append({'parameters':sorted(origins[m[4]]),'bits':int(m[2]),'line':t})
   origins.pop(m[3],None);continue
  m=re.match(r'(?:@!?%\w+\s+)?(?:add|sub|mul|mad|shl|shr|mov|cvt|cvta)(?:\.[A-Za-z0-9_]+)*\s+(%\w+),\s*(.*);$',t)
  if m:
   source=set().union(*(origins.get(reg,set())for reg in re.findall(r'%\w+',m[2])));origins[m[1]]=source
 return loads
