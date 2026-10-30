import sys, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'))
import common as h
review=ROOT/'comparisons/D149-invalid-fixture/fixture-repair-review.json'
assert h.read(review)['D149_remains_closed_invalid']
def new(name,text):
    p=ROOT/'runs'/name;assert not p.exists();p.write_bytes(text.encode())
main=(ROOT/'runs/D149-main.rs').read_text(encoding='utf-8').replace('D149','D150').replace('d149','d150')
needle='let mut a = Solver::load_with_storage(sa.to_str().unwrap(), storage).unwrap(); let mut c = Solver::load_with_storage(sc.to_str().unwrap(), storage).unwrap(); cpu_pair(&a, &c, &out, id, "loaded");'
fixed='''let mut a = Solver::load_with_storage(sa.to_str().unwrap(), storage).unwrap(); let mut c = Solver::load_with_storage(sc.to_str().unwrap(), storage).unwrap();
        assert_eq!(a.algo, Algorithm::Dcfr); assert_eq!(c.algo, Algorithm::Dcfr); assert!(a.use_isomorphism && c.use_isomorphism);
        a.algo = algo; c.algo = algo; a.use_isomorphism = iso; c.use_isomorphism = iso;
        assert_eq!(a.algo, algo); assert_eq!(c.algo, algo); assert_eq!(a.use_isomorphism, iso); assert_eq!(c.use_isomorphism, iso);
        cpu_pair(&a, &c, &out, id, "loaded");'''
assert main.count(needle)==1
main=main.replace(needle,fixed,1)
main=main.replace('"extra_board": extra_board,','"extra_board": extra_board, "resume_fixture_flags_explicitly_restored": true,',1)
new('D150-main.rs',main)
obs=(ROOT/'runs/D149-observer-template.rs').read_text(encoding='utf-8').replace('D149','D150').replace('d149','d150')
obs=obs.replace('"logical_player": p,','"logical_player": p, "actual_iso_active": self.iso_active,',1)
new('D150-observer-template.rs',obs)
audit=(ROOT/'runs/D149-audit.py').read_text(encoding='utf-8').replace('D149','D150')
audit=audit.replace('req(row[\'case\'] == ident, \'case order\')','req(row[\'case\'] == ident and row[\'resume_fixture_flags_explicitly_restored\'], \'case order and explicit resume fixture controls\')',1)
needle="req(f['hands'][info['logical_player']] == nh, 'logical current player hand count')"
audit=audit.replace(needle,needle+"\n    req(int(f['algorithm'][0]) == expected_algo, 'actual algorithm matches declared fixture before and after resume')\n    req(requested_iso or not info['actual_iso_active'], 'declared noiso remains actual noiso')",1)
needle="stages = ordinary + ("
audit=audit.replace(needle,"expected_algo = 0 if dims[1] == 'Dcfr' else 1\n    requested_iso = dims[3]\n    "+needle,1)
new('D150-audit.py',audit)
execute=(ROOT/'runs/D149-execute.py').read_text(encoding='utf-8').replace('D149','D150')
new('D150-execute.py',execute)
prep=(ROOT/'runs/D149-prepare.py').read_text(encoding='utf-8').replace('D149','D150').replace('d149','d150')
prep=prep.replace("parent, capture_parent, ROOT/", "parent, capture_parent, ROOT/'comparisons/D149-invalid-fixture/fixture-repair-review.json', ROOT/",1)
prep=prep.replace("'scope': 'One native compiler", "'fixture_repair_review_sha256': h.sha(ROOT/'comparisons/D149-invalid-fixture/fixture-repair-review.json'), 'D149_remains_closed_invalid': True, 'scope': 'Fresh separately named full correctness cohort with only the two declared fixture flags restored after load. No partial data pooling or original status regrade. One native compiler",1)
new('D150-prepare.py',prep)
for name in ['D150-prepare.py','D150-execute.py','D150-audit.py']:
    p=ROOT/'runs'/name;compile(p.read_text(encoding='utf-8'),str(p),'exec')
h.save(ROOT/'comparisons/D149-invalid-fixture/D150-adapter-provenance.json',{'at':h.now(),'review_sha256':h.sha(review),'script_sha256':h.sha(__file__),'native_executions_started':0,'originals_unchanged':True,'files':{name:h.sha(ROOT/'runs'/name) for name in ['D150-main.rs','D150-observer-template.rs','D150-audit.py','D150-execute.py','D150-prepare.py']}})
print('Authored separate D150 fixture repair; D149 unchanged and invalid.',flush=True)
