"""Validate the full regression records following R01's saved-state checks."""
import json
import re
from check_r01 import HERE, RAW, LAB, read, sha

def main():
    source=read(RAW/'r01-selection-tests-v2-exit.json')['solver_source_files']
    records={}
    for name,expected,command in [
        ('r01-native-regressions-v1',19,['cargo','test','--release','-p','solver','--features','gpu','--test','gpu','--test','preflop_gpu','--','--test-threads=1']),
        ('r01-default-regressions-v1',181,['cargo','test','--release','-p','solver']),
    ]:
        r=read(RAW/(name+'-exit.json'));text=(RAW/(name+'.log')).read_text()
        assert r['returncode']==0 and r['reason'] is None and r['seconds']<300
        assert r['command']==command and r['solver_source_files']==source
        assert 'test result: FAILED' not in text
        totals=re.findall(r'test result: ok\. (\d+) passed; (\d+) failed;',text)
        assert sum(int(p) for p,f in totals)==expected and all(int(f)==0 for p,f in totals)
        for p,h in r['inputs'].items():assert sha(p)==h,p
        records[name]=dict(passed=expected,seconds=r['seconds'])
    for p,h in source.items():assert sha(LAB/p)==h,p
    result=dict(status='Regression checks passed',records=records,
        source_hashes_verified=True,scope='Research opt-in preparation. No production integration or deployment; real allocation-failure recovery remains unqualified.')
    target=RAW/'r01-regressions-verified.json'
    if target.exists():assert read(target)==result
    else:target.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
