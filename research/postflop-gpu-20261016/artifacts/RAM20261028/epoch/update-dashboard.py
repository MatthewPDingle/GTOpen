import sys,json,shutil,urllib.request
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import common as h
h.custody();assert not(h.ROOT/'gpu-run.lock').exists()
q=h.read(h.ROOT/'comparisons/RAM20261028-baseline/report.json')
assert q['status']=='pass_current_hardware_baseline'and q['scored_run_count']==5
P=h.read(h.EPOCH/'baseline-protocol.json');index=h.ar.DASHBOARD/'index.html';raw=index.read_bytes()
assert h.sha(index)==P['input_sha256'][str(index)]
preserved=h.EPOCH/'dashboard-at-measurement.html';preserved.write_bytes(raw);h.pin(preserved,P['input_sha256'][str(index)])
t=raw.decode()
edits=[
('<div class="label">Accepted complete-run gain</div>','<div class="label" id="gain-label">Accepted complete-run gain</div>'),
('<div class="label">Baseline complete run</div>','<div class="label" id="baseline-label">Baseline complete run</div>'),
('<div class="label">Best validated complete run</div>','<div class="label" id="best-label">Best validated complete run</div>'),
('<h2>Accepted progress</h2>','<h2 id="chart-title">Accepted progress</h2>'),
('<p>The headline results below belong to the earlier RAM settings. A fresh E080 baseline is being collected on X; the tracker will publish its measurements separately.</p>','<p id="epoch-summary">Loading the current baseline.</p><p class="metric-note" id="epoch-storage"></p>'),
]
for a,b in edits:assert t.count(a)==1,a;t=t.replace(a,b,1)
assert t.count('items(data.fixtures)')==2
t=t.replace('items(data.fixtures)','items(data.current_hardware_baseline?.fixtures || data.fixtures)')
needle='      renderChart(); renderFixtures(); renderExperiments();'
extra=r'''
      const epoch = data.measurement_epoch, fresh = data.current_hardware_baseline;
      if (epoch && fresh) {
        const historical = result.measurement_epoch_id !== epoch.id;
        $('epoch-summary').textContent = fresh.status === 'measured'
          ? 'Current E080 baseline: ' + duration(fresh.aggregate_ms) + ' across the three fixtures, from five fresh measurements after the RAM changes. No new optimizer gain is claimed.'
          : 'Collecting the best accepted E080 configuration under the new RAM timings.';
        $('epoch-storage').textContent = 'New evidence: ' + epoch.output_root + '. Earlier RAM timing cohorts are historical and are not pooled.';
        $('gain-label').textContent = historical ? 'Prior accepted gain · earlier RAM' : 'Accepted gain · current RAM';
        if (historical) $('gain-note').textContent = 'Historical result under earlier RAM settings. It is not a gain measured against the new baseline.';
        $('baseline-label').textContent = 'Current baseline · E080';
        $('best-label').textContent = 'Best config · current RAM';
        $('baseline-time').textContent = duration(fresh.aggregate_ms);
        $('baseline-note').textContent = fresh.status === 'measured' ? fresh.repetitions + ' fresh runs · ' + stamp(fresh.measured_at) : 'Fresh measurements pending.';
        $('best-time').textContent = fresh.status === 'measured' ? duration(fresh.aggregate_ms) : 'Pending';
        $('best-note').textContent = 'E080 · GPU / compressed / 16 threads';
        $('correctness').textContent = fresh.correctness === 'pass' ? 'Pass' : 'Pending';
        $('correctness').className = 'metric-value small ' + (fresh.correctness === 'pass' ? 'good' : '');
        $('validation-summary').textContent = fresh.correctness === 'pass' ? 'All five fresh full results, stops and convergence checkpoints match the original reference; 86 ordinary tests passed.' : 'Checking the accepted configuration under the changed RAM timings.';
        $('chart-title').textContent = historical ? 'Accepted progress · previous RAM' : 'Accepted progress · current RAM';
        $('comparison-method').textContent = historical ? 'This chart records the earlier RAM epoch. New improvements need fresh matched controls against the current E080 baseline; percentages across epochs are never added.' : result.method;
      }
'''
assert t.count(needle)==1;t=t.replace(needle,needle+extra,1)
nl=b'\r\n'if b'\r\n'in raw else b'\n';index.write_bytes(t.replace('\r\n','\n').encode().replace(b'\n',nl))
h.save(h.EPOCH/'post-measurement-ui-transition.json',{'at':h.now(),'native_measurements_already_terminal':True,'original_UI_path':str(index),'original_protocol_UI_sha256':P['input_sha256'][str(index)],'preserved_exact_measurement_UI':str(preserved),'preserved_sha256':h.sha(preserved),'current_UI_sha256':h.sha(index),'scope':'Presentation update after all measurements. The original UI input bytes are preserved; frozen protocol, baseline report, native binaries/source/data/results and all other protocol inputs remain unchanged.'})
for p,digest in P['input_sha256'].items():
 if p!=str(index):h.pin(p,digest)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/',timeout=20)as z:assert z.read()==index.read_bytes()
h.custody();print('Dashboard now shows the new RAM baseline and labels earlier gains historical.',flush=True)
