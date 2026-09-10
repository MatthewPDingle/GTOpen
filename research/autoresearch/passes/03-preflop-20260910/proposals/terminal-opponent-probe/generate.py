from pathlib import Path
import subprocess,difflib,json
p=Path(__file__).parent
root=Path(r'T:\Dev\GTOpen\target\autoresearch\preflop-20260910')
rel='crates/solver/src/preflop/kernels.cu'
old=subprocess.check_output(['git','show','5f4f42c:'+rel],cwd=root).decode().replace('\r\n','\n')
begin=old.index('extern "C" __global__ void pf_multiway_terminal(')
end=old.index('// Minimum-memory compatibility entry:',begin)
body=old[begin:end]
new=old
extra='// Register probe entry points only. Host must route exactly O+1 live seats.\n'
for o in [2,3,4]:
 q=(o+2)//2
 s=body.replace('pf_multiway_terminal(',f'pf_multiway_terminal_o{o}(',1)
 s=s.replace('__shared__ size_t opponent_bases[9];',f'__shared__ size_t opponent_bases[{o}];',1)
 s=s.replace('    __shared__ int nopponents;\n','',1).replace('        nopponents = 0;','        int nopponents = 0;',1)
 start=s.index('        // Q-point Gauss is exact')
 stop=s.index('        float increment =',start)
 s=s[:start]+f'''        // Known live count eliminates the dynamic switch; same Q/O instantiation.
        float sum = pf_multiway_sum<{q}, {o}>(h, opponent_bases, cdf, lower, upper, sample_start, sample_count);
'''+s[stop:]
 extra+=s
new=old[:end]+extra+old[end:]
(p/'kernels.cu').write_bytes(new.encode())
(p/'probe.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel)),encoding='utf-8',newline='\n')
print('Kernel-only probe adds',len(new)-len(old),'bytes; no host dispatch changes')
