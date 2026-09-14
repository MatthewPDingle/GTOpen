// Ensure provisional timing is visible without counting it as a retained win.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const html = fs.readFileSync(__dirname + '/dashboard.html', 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
new vm.Script(script);
const fn = script.slice(script.indexOf('function graphPoints('), script.indexOf('function drawGraph('));
(async () => {
  const data = await (await fetch('http://127.0.0.1:56709/api/progress')).json();
  const context = { data }; vm.createContext(context);
  vm.runInContext(fn + '; result=graphPoints(data,"large","complete_seconds")', context);
  const point = context.result.find(p => p.label === 'C23');
  const retained = process.argv.includes('--retained');
  assert(point); assert.equal(point.state, retained ? 'retained' : 'pending'); assert.equal(point.pairs, 3);
  const c24Retained = Boolean(data.experiments.find(e => e.id === 'c24')?.decision.retained);
  assert.equal(data.retained, (retained ? 5 : 4) + Number(c24Retained));
  assert.equal(context.result.filter(p => p.state === 'retained').length, retained ? 6 : 5); // includes baseline
  assert.equal(data.experiments.find(e => e.id === 'c23').decision.retained, retained);
  vm.runInContext('summary=graphSummary(result)', context);
  if(retained)assert.equal(context.summary.gain, '31.7% less time');
  console.log(JSON.stringify({c23: point, retained: data.retained}));
})().catch(e => { console.error(e); process.exitCode = 1; });
