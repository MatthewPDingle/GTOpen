import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();old=ROOT/'runs/D173-prepare.py';source=old.read_text(encoding='utf-8')
h.save(ROOT/'runs/D173-constructor-diagnostic/failure.json',{'at':h.now(),'status':'observer_packager_failed_before_protocol_source_activation_or_compiler','error':'Unscoped build_lock_table anchor occurs in constructor and update_locks; restrict every marker/reversal operation to original new_with_budget body','original_script_sha256':h.sha(old),'original_partial_directory_preserved':True,'compiler_native_and_timing_runs':0})
before="base=(h.REPO/'crates/solver/src/gpu/mod.rs').read_text(encoding='utf-8');code=base;changes=[]"
after="base=(h.REPO/'crates/solver/src/gpu/mod.rs').read_text(encoding='utf-8');left=base.index('    pub fn new_with_budget(');right=base.index('    fn cfg(',left);prefix,suffix=base[:left],base[right:];base=base[left:right];code=base;changes=[]"
assert source.count(before)==1
fixed=source.replace("H=ROOT/'runs/D173-constructor-diagnostic';","H=ROOT/'runs/D173-constructor-diagnostic-r2';",1).replace('D.mkdir(exist_ok=False)','D.mkdir(exist_ok=True)',1).replace("h.save(D/'report.json',","if not(D/'report.json').exists():h.save(D/'report.json',",1).replace(before,after,1).replace('assert reverse==base\n','assert reverse==base\ncode=prefix+code+suffix;base=prefix+base+suffix\n',1)
assert fixed!=source;compile(fixed,'D173-prepare-r2.py','exec');new=ROOT/'runs/D173-prepare-r2.py';assert not new.exists();new.write_text(fixed,encoding='utf-8',newline='\n');print(str(new),flush=True)
