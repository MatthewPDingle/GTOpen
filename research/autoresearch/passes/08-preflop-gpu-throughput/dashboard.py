"""Local, read-only progress view of this pass's on-disk evidence."""
import argparse, json, os, re, statistics, time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / 'raw'

def read(path, default=None):
    try: return json.loads(path.read_text(encoding='utf-8-sig'))
    except (OSError, ValueError): return default

def progress():
    trials=[]
    for log in sorted(RAW.glob('*.log'),key=lambda p:p.stat().st_mtime,reverse=True):
        name=log.stem; result=read(RAW/(name+'-exit.json'))
        state='awaiting result' if result is None else ('passed' if result['returncode']==0 and result.get('reason') is None else 'failed')
        tail=log.read_text(encoding='utf-8',errors='replace')[-2600:]
        trials.append(dict(name=name,state=state,seconds=None if result is None else result.get('seconds'),
            reason=None if result is None else result.get('reason'),updated=log.stat().st_mtime,tail=tail))
    measurements=[]
    for f in RAW.glob('c*-*-bench.json'):
        x=read(f)
        if not x or not x.get('rows'): continue
        warm=[r for r in x['rows'] if not r['warmup']]
        measurements.append(dict(name=f.stem,enabled='-candidate-' in f.stem,nodes=x['nodes'],
            iteration_ms=statistics.median(r['iteration_seconds'] for r in warm)*1000,
            check_ms=statistics.median(r['check_seconds'] for r in warm)*1000,
            complete_seconds=x['complete_seconds'],extra_mb=x['extra_bytes']/1e6,
            fingerprint=x['arena_fingerprint'],age=x['iteration']))
    verified=read(RAW/'c01-verified.json',{})
    experiments=[]
    for spec in read(HERE/'experiments.json',[]):
        decision=read(RAW/(spec['id']+'-verified.json'),{})
        fixtures={}
        for fixture in ['small','large']:
            candidates=[r for r in measurements if r['name'].startswith(spec['id']+'-'+fixture+'-candidate-')]
            ratios={k:[] for k in ['complete_seconds','iteration_ms','check_ms']}
            for candidate in candidates:
                control=next((r for r in measurements if r['name']==candidate['name'].replace('-candidate-','-control-')),None)
                if not control:continue
                for k in ratios:ratios[k].append(candidate[k]/control[k])
            if ratios['complete_seconds']:
                fixtures[fixture]={k:dict(value=statistics.median(v),low=min(v),high=max(v),pairs=len(v)) for k,v in ratios.items()}
        experiments.append(dict(**spec,decision=decision,fixtures=fixtures))
    inventory=[]
    for label in ['small','large']:
        x=read(RAW/f'd01-{label}-v1.json')
        if not x: continue
        for mode in [0,1]:
            rows=[r for r in x['rows'] if r['mode']==mode]
            total=sum(r['active_slots'] for r in rows); unique=sum(r['unique_distributions'] for r in rows)
            inventory.append(dict(fixture=label,policy='Current play' if mode==0 else 'Average play',
                active=total,unique=unique,duplicate_pct=100*(1-unique/total)))
    return dict(now=time.time(),trials=trials,measurements=measurements,inventory=inventory,verified=verified,experiments=experiments,
        completed=sum(t['state']!='awaiting result' for t in trials),
        phase='Benchmarking exact CDF reuse' if measurements else 'Validating exact CDF reuse',
        retained=sum(bool(e['decision'].get('retained')) for e in experiments))

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        route=self.path.split('?',1)[0]
        if route=='/api/progress':
            body=json.dumps(progress()).encode(); mime='application/json'
        elif route in ['/','/index.html']:
            body=(HERE/'dashboard.html').read_bytes();mime='text/html; charset=utf-8'
        else:
            self.send_error(404);return
        self.send_response(200);self.send_header('Content-Type',mime)
        self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(body)))
        self.end_headers();self.wfile.write(body)
    def log_message(self,*args): pass

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=56709);args=parser.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    # Runtime file lives outside tracked research artifacts.
    runtime=HERE.parents[3]/'target'/'gpu-throughput-dashboard.json'
    runtime.write_text(json.dumps(dict(pid=os.getpid(),port=server.server_port,url=f'http://127.0.0.1:{server.server_port}',
        started=datetime.now(timezone.utc).isoformat()),indent=2)+'\n',encoding='utf-8')
    print(f'Progress dashboard: http://127.0.0.1:{server.server_port}',flush=True)
    server.serve_forever()
