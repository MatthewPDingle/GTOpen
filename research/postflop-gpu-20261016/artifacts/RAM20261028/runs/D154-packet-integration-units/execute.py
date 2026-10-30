import sys,re,shutil
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent;sys.path.insert(0,str(ROOT/'epoch'))
import common as h
assert len(sys.argv)==2;P=h.read(H/'protocol.json')
def verify():
    h.pin(H/'protocol.json',sys.argv[1]);h.custody()
    for p,d in P['input_sha256'].items():h.pin(p,d)
verify();O=H/'execution';O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
    h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes']
    h.child(P['rustc_command'],O,'rustc',1200);verify()
    h.save(O/'binary.json',{'at':h.now(),'sha256':h.sha(H/'probe.exe')})
    h.child([str(H/'probe.exe'),'--test-threads=1'],O,'units',1200);verify()
    log=(O/'units.stdout.log').read_text(encoding='utf-8')
    result=re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored;',log)
    assert result==[(str(P['expected_test_count']),'0','0')],result
    report={'id':'D154','at':h.now(),'status':'pass_isolated_integration_unit_prerequisites','protocol_sha256':sys.argv[1],'tests_passed':P['expected_test_count'],'tests_failed':0,'tests_ignored':0,'unsafe_layout_scatter_prefix_controls':3,'all_children_terminal':True,'source_main_live_PTX_custody_pass':True,'candidate_source_activated':False,'performance_measurement':False,'candidate_accepted':False,'scope':'Original candidate GPU/arena unit tests and appended unsafe guard controls. Public16MiB admission may leave small original GPU fixtures on fallback. Forced internal-path full engine controls and actual resource/capacity/performance qualification remain required.'}
    h.save(H/'report.json',report);h.save(O/'complete.json',{'at':h.now(),'report_sha256':h.sha(H/'report.json'),'all_owned_children_terminal':True});verify()
print(report,flush=True)
