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
  assert(point); assert.equal(point.state, 'pending'); assert.equal(point.pairs, 3);
  assert.equal(data.retained, 4);
  assert.equal(context.result.filter(p => p.state === 'retained').length, 5); // includes baseline
  assert.equal(data.experiments.at(-1).decision.retained, false);
  console.log(JSON.stringify({pending_c23: point, retained: data.retained}));
})().catch(e => { console.error(e); process.exitCode = 1; });
