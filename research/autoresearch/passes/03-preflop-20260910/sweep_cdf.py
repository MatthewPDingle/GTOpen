"""Bounded CDF geometry experiments. One source change and one GPU job at a time."""
import datetime as dt
import json,os,subprocess,sys
from pathlib import Path
from measure import HERE,ROOT,LAB,RUN,live_busy
base=sys.argv[1]
base=subprocess.check_output(['git','-C',str(LAB),'rev-parse',base],text=True).strip()
if subprocess.check_output(['git','-C',str(LAB),'status','--porcelain'],text=True).strip():
 raise SystemExit('Research worktree must be clean.')
paths=['crates/solver/src/preflop/gpu.rs','crates/solver/src/preflop/kernels.cu']
original={p:subprocess.check_output(['git','-C',str(LAB),'show',base+':'+p]) for p in paths}
def event(**r):
 r['utc']=dt.datetime.now(dt.timezone.utc).isoformat()
 with (HERE/'events.jsonl').open('a') as f:f.write(json.dumps(r)+'\n')
def call(args,cwd=ROOT,log=None):
 if live_busy():raise SystemExit('User workload active; sweep deferred.')
 if log:
  with log.open('x') as f:r=subprocess.run(args,cwd=cwd,stdout=f,stderr=subprocess.STDOUT)
 else:
  r=subprocess.run(args,cwd=cwd,capture_output=True,text=True)
  print(' '.join(map(str,args[1:3])),r.returncode,r.stdout[-350:],r.stderr[-350:],flush=True)
 if r.returncode:raise SystemExit(r.returncode)
for warps in [8,16,4]:
 if dt.datetime.now(dt.timezone.utc)>=dt.datetime.fromisoformat(RUN['deadline_utc'].replace('Z','+00:00')):
  raise SystemExit('Research deadline reached.')
 tag=f'cdf-w{warps}'
 for path,raw in original.items():
  nl=b'\r\n' if b'\r\n' in raw else b'\n'; s=raw.decode().replace('\r\n','\n')
  if path.endswith('.rs'):
   old='grid_dim: (work_count, sample_count.div_ceil(4), 1), block_dim: (128, 1, 1)'
   assert s.count(old)==1
   s=s.replace(old,f'grid_dim: (work_count, sample_count.div_ceil({warps}), 1), block_dim: ({warps*32}, 1, 1)')
  else:
   old='u32 local = blockIdx.y * 4 + threadIdx.x / 32;'
   assert s.count(old)==2
   s=s.replace(old,f'u32 local = blockIdx.y * {warps} + threadIdx.x / 32;')
   s=s.replace('Four independent warps handle four particles for the same reach.',f'{warps} independent warps handle {warps} particles for the same reach.')
  (LAB/path).write_bytes(s.replace('\n',nl.decode()).encode())
 call(['git','add',*paths],LAB)
 call(['git','commit','--allow-empty','-m',f'Experiment: CDF scans with {warps} independent warps per block'],LAB)
 commit=subprocess.check_output(['git','-C',str(LAB),'rev-parse','HEAD'],text=True).strip()
 event(event='hypothesis',candidate=commit,base=base,cdf_warps=warps,note='Preserve independent warp scan arithmetic and all particles; reduce block scheduling overhead at wider geometry.')
 call(['cargo','test','--release','-p','solver','--features','gpu','--lib','--no-run'],LAB,HERE/'raw'/f'{tag}-test-build.log')
 call(['cargo','build','--release','-p','solver','--features','gpu','--example','preflop_research_bench'],LAB,HERE/'raw'/f'{tag}-bench-build.log')
 exe=LAB/'target/release/deps/solver-361fd64e0c11ad35.exe'
 call([sys.executable,str(HERE/'run_guarded.py'),f'{tag}-internal',str(exe),'preflop::gpu::tests::','--nocapture','--test-threads=1'])
 call([sys.executable,str(HERE/'run_guarded.py'),f'{tag}-boundary',str(exe),'coupled_minimum_budget_direct_and_normalized_paths_match','--ignored','--nocapture','--test-threads=1'])
 for name,fixture,it in [('eight',ROOT/'saves/preflop/Before preflop autoresearch 20260910 2104.gtop',6),('seven',HERE/'fixtures/seven.json',4),('six',HERE/'fixtures/six.json',6),('three',HERE/'fixtures/three.json',30)]:
  call([sys.executable,str(HERE/'measure.py'),f'{tag}-{name}',str(fixture),str(it)])
 call([sys.executable,str(HERE/'verify_gpu.py')])
 call([sys.executable,str(HERE/'render.py')])
 print(f'Completed {tag}; awaiting final cross-candidate selection after controls.',flush=True)
# Final W4 restores the original arithmetic/layout (comment-only difference).
