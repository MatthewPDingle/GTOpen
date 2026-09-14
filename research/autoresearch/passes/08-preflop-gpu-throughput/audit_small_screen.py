"""Retrospective: would the existing small fixture preserve retained winners?

This is a selected subset of historical experiments, not a calibrated predictor.
No benchmark or GPU work runs here; each candidate uses its paired own control.
"""
import hashlib,json,re,statistics
from pathlib import Path
HERE=Path(__file__).resolve().parent;RAW=HERE/'raw'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
    rows={};sources={}
    for f in sorted(RAW.glob('c*-*-candidate-*-bench.json')):
        match=re.fullmatch(r'(c\d+)-(small|large)-candidate-(\d+)-bench.json',f.name)
        if not match:continue
        control=RAW/f.name.replace('-candidate-','-control-')
        if not control.exists():continue
        a,b=read(control),read(f)
        assert a['input']==b['input'] and a['nodes']==b['nodes'] and len(a['rows'])==len(b['rows'])==6
        for path in [control,f]:sources[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
        rows.setdefault(match[1],{}).setdefault(match[2],[]).append(b['complete_seconds']/a['complete_seconds'])
    paired={k:{size:dict(pairs=len(v),median_ratio=statistics.median(v)) for size,v in values.items()} for k,values in rows.items() if len(values)==2}
    retained=[k for k in paired if read(RAW/(k+'-verified.json')).get('retained')]
    assert sorted(retained)==['c01','c07','c09','c14']
    lost=[k for k in retained if paired[k]['small']['median_ratio']>.99]
    assert sorted(lost)==['c01','c09']
    out=dict(verified=True,kind='retrospective',paired_experiments=paired,retained_ids=retained,
        small_one_percent_screen_would_discard=lost,
        selection_bias='Only experiments with both fixture sizes are included; many rejected candidates have large-only results. This cannot estimate general predictive accuracy.',
        recommendation='Do not require a small-game gain before large-game timing. Calibrate a medium fixture on held-out historical candidates before making it a rejection gate.',sources=sources)
    dest=RAW/'small-screen-audit.json'
    if dest.exists():assert read(dest)==out
    else:dest.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in out.items() if k!='sources'},indent=2))
if __name__=='__main__':main()
