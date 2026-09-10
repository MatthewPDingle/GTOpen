from pathlib import Path
import subprocess,difflib,json,hashlib,sys
p=Path(__file__).parent
root=Path(r'T:\Dev\GTOpen\target\autoresearch\preflop-20260910')
base=sys.argv[1] if len(sys.argv)>1 else '9333943'
paths=['crates/solver/src/preflop/gpu.rs','crates/solver/src/preflop/kernels.cu']
manifest={'base_revision':subprocess.check_output(['git','rev-parse',base],cwd=root,text=True).strip(),
 'literal_revision':subprocess.check_output(['git','rev-parse','1b8fc3f'],cwd=root,text=True).strip(),
 'changed_paths':{},'retained_base_paths':{}}
patch=''
for rel in paths:
 a=subprocess.check_output(['git','show',base+':'+rel],cwd=root)
 b=subprocess.check_output(['git','show','1b8fc3f:'+rel],cwd=root)
 (p/Path(rel).name).write_bytes(b)
 manifest['changed_paths'][rel]={'literal_sha256':hashlib.sha256(b).hexdigest(),
  'literal_git_blob':subprocess.check_output(['git','rev-parse','1b8fc3f:'+rel],cwd=root,text=True).strip(),
  'base_sha256':hashlib.sha256(a).hexdigest()}
 aa=a.decode().replace('\r\n','\n');bb=b.decode().replace('\r\n','\n')
 patch+=''.join(difflib.unified_diff(aa.splitlines(True),bb.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
for rel in ['crates/solver/src/preflop/mod.rs','crates/solver/src/preflop/multiway.rs','crates/solver/Cargo.toml',
 'crates/solver/examples/preflop_research_bench.rs','crates/solver/examples/preflop_budget_control.rs',
 'crates/solver/examples/preflop_convergence_control.rs','crates/solver/examples/preflop_compare_saved.rs']:
 data=subprocess.check_output(['git','show',base+':'+rel],cwd=root)
 manifest['retained_base_paths'][rel]=hashlib.sha256(data).hexdigest()
(p/'literal-control.patch').write_text(patch,encoding='utf-8',newline='\n')
(p/'source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print('Generated literal control against',manifest['base_revision'],'changing',len(paths),'paths')
