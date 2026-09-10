"""Freeze the independent extended final protocol after candidate selection."""
import datetime as dt, hashlib, json, sys
from pathlib import Path
from measure import HERE, LAB

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

candidate=Path(sys.argv[1]).resolve(); source=sys.argv[2]
old=json.loads((HERE/'convergence-protocol.json').read_text(encoding='utf8'))
manifest=json.loads((HERE/'build-binaries.json').read_text(encoding='utf8'))
control=next(x for x in manifest if x.get('harness')=='preflop_convergence_control' and x.get('kind')=='literal_prepass_gpu_control')
assert sha(control['path'])==control['sha256']
registered=[x for x in manifest if x['sha256']==sha(candidate)]
assert len(registered)==1 and registered[0]['source_commit']==source
protocol={'version':1,'frozen_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
 'deadline_utc':old['deadline_utc'],'calibration_fit':old['calibration_fit'],
 'frozen_dependencies':old['frozen_dependencies'],
 'purpose':'Independent longer final comparison against literal deployed pre-pass GPU, preserving targets, samples, precision, menus and native policy state. The original 100-iteration eight-seat target miss remains unchanged evidence.',
 'exception':'Predeclared long final gate. Original native eight-seat iteration174 is used equally by both; maximum900 additional iterations, unchanged0.005bb target. Modeled pair starts fresh, literal19GB grouping, maximum100 iterations at0.004bb. Timeouts and target misses remain explicit; no adaptive extension.',
 'runs':{}}
for fixture in ['modeled','eight']:
    input=LAB/'target/fixtures/fresh-coupled-validated.gtop' if fixture=='modeled' else LAB/'target/research-convergence/convergence-eight-original-a.gtop'
    digest=sha(input)
    for side in ['original','compatible']:
        rid=f'extended-convergence-{fixture}-{side}-a'
        exe=Path(control['path']) if side=='original' else candidate
        entry={'executable':str(exe),'executable_sha256':sha(exe),
          'compiled_source':control['source_commit'] if side=='original' else source,
          'input':str(input),'input_sha256':digest,
          'budget_mb':19000 if fixture=='modeled' else 23000,
          'additional_iterations':100 if fixture=='modeled' else 900,
          'target_gap_bb':0.004 if fixture=='modeled' else 0.005,
          'check_every':10 if fixture=='modeled' else 50,
          'output':str(LAB/'target/research-convergence'/f'{rid}.gtop'),
          'timeout_seconds':(1000 if side=='original' else 600) if fixture=='modeled' else (9000 if side=='original' else 5500)}
        assert not Path(entry['output']).exists() and not (HERE/'raw'/f'{rid}.log').exists()
        protocol['runs'][rid]=entry
with (HERE/'extended-convergence-protocol.json').open('x',encoding='utf8') as f: json.dump(protocol,f,indent=2)
print(json.dumps({'protocol_sha256':sha(HERE/'extended-convergence-protocol.json'),'source':source}))
