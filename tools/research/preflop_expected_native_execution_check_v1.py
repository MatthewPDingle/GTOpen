"""Process/receipt software checks; Python fixtures, no poker native/science/GPU."""
import copy
import json
import os
from pathlib import Path
import sys
import time

import preflop_expected_native_execution_v1 as native


def main():
    root=Path(sys.argv[1]).resolve(); root.mkdir(parents=True,exist_ok=False)
    began=time.monotonic(); refused=[]; scripts={}
    for name,source in dict(echo='import sys; sys.stdout.buffer.write(sys.stdin.buffer.read()); sys.stderr.write("fixture")',
            immediate='print("complete")',failed='import sys; print("preserved"); sys.exit(7)',
            delayed='import time; time.sleep(3)', large='print("x"*10000)').items():
        path=root/(name+'.py'); path.write_text(source,encoding='utf-8'); scripts[name]=path
    incoming=root/'request.bin'; incoming.write_bytes(b'qualified-process-fixture\n')
    exe=str(Path(sys.executable).resolve()); shared={exe:native.sha(exe),str(Path(native.__file__).resolve()):native.sha(native.__file__)}
    def invoke(name,label,**options):
        ids=dict(shared,**{str(scripts[name]):native.sha(scripts[name])})
        if options.get('stdin_path'): ids[str(incoming)]=native.sha(incoming)
        return native.run_native(exe,['-B',str(scripts[name])],folder=root,label=label,
            expected_identities=ids,guard=lambda:None,**options),ids
    echo,echo_ids=invoke('echo','echo',stdin_path=incoming)
    assert Path(echo['stdout_path']).read_bytes()==incoming.read_bytes()
    immediate,ids=invoke('immediate','immediate')
    assert immediate['receipt']['process']['creation_time']>0
    assert immediate['receipt']['process']['parent_pid']==os.getpid()
    for name,opts in [('failed',{}),('delayed',dict(timeout=.05)),('large',dict(max_output_bytes=100))]:
        try: invoke(name,'refused-'+name,**opts)
        except (ValueError,RuntimeError,TimeoutError):
            receipt=json.loads((root/('refused-'+name+'-receipt.json')).read_bytes())
            assert receipt['outcome']=='failed' and receipt['terminal_unix'] is not None
            refused.append(name)
        else: raise AssertionError('Unsafe process accepted '+name)
    alterations=dict(format=lambda r:r.update(format=True), method=lambda r:r.update(method='other'),
        outcome=lambda r:r.update(outcome='running'), returncode=lambda r:r.update(returncode=7),
        argv=lambda r:r['argv'].append('other'), parent=lambda r:r['process'].update(parent_pid=1),
        process=lambda r:r.update(process=None), creation=lambda r:r['process'].update(creation_time=1),
        caller=lambda r:r['caller'].update(creation_time=r['terminal_unix']+1),
        output_hash=lambda r:r['stdout'].update(sha256='0'*64),
        output_size=lambda r:r['stdout'].update(bytes=-1),
        output_budget=lambda r:r.update(max_output_bytes=1),
        source=lambda r:r['expected_identities'].update({exe:'0'*64}),
        stdin=lambda r:r.update(stdin=dict(path=str(incoming),sha256=native.sha(incoming),bytes=incoming.stat().st_size)))
    for name,change in alterations.items():
        result=copy.deepcopy(immediate); change(result['receipt'])
        path=root/('invalid-'+name+'.json'); native._write(path,result['receipt'])
        result['receipt_path']=str(path); result['receipt_sha256']=native.sha(path)
        try: native.verify_native(result,executable=exe,arguments=['-B',str(scripts['immediate'])],expected_identities=ids)
        except (ValueError,TypeError,KeyError): refused.append(name)
        else: raise AssertionError('Invalid receipt accepted '+name)
    native.verify_native(echo,executable=exe,arguments=['-B',str(scripts['echo'])],expected_identities=echo_ids,stdin_path=incoming)
    native.verify_native(immediate,executable=exe,arguments=['-B',str(scripts['immediate'])],expected_identities=ids)
    result=dict(passed=True,scope='Owned Python subprocess software fixtures only; no native poker or scientific attempt',
        seconds=time.monotonic()-began,refused=refused,successful=[echo,immediate],
        source_sha256=native.sha(__file__),implementation_sha256=native.sha(native.__file__),
        artifacts={str(p):native.sha(p) for p in root.iterdir() if p.is_file()})
    native._write(root/'result.json',result); print(json.dumps(dict(passed=True,seconds=result['seconds'],refusals=len(refused))))


if __name__=='__main__': main()
