// Verify the live endpoint and graph calculation keep this screen provisional.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
(async () => {
  const html = await (await fetch('http://127.0.0.1:56709/')).text();
  assert(html.includes('<option value="current" selected>Memory-limited (C24)</option>'));
  const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
  new vm.Script(script);
  const fn = script.slice(script.indexOf('function graphPoints('), script.indexOf('function drawGraph('));
  const data = await (await fetch('http://127.0.0.1:56709/api/progress')).json();
  const context = { data }; vm.createContext(context);
  vm.runInContext(fn + '; result=graphPoints(data,"current","complete_seconds")', context);
  const full = process.argv.includes('--full');
  const verified = JSON.parse(fs.readFileSync(__dirname + '/raw/' + (full ? 'c24-full-verified.json' : 'c24-native-screen-verified.json'), 'utf8'));
  assert.equal(context.result.length, 2);
  const point = context.result.find(p => p.label === 'C24');
  assert(point); assert.equal(point.state, 'pending'); assert.equal(point.pairs, full ? verified.pairs.length : 1);
  assert(Math.abs(point.value - verified.complete_ratio * 100) < 1e-10);
  assert.equal(context.result.filter(p => p.state === 'retained').length, 1);
  assert.equal(data.retained, 5);
  assert.equal(data.experiments.find(e => e.id === 'c24').decision.retained, false);
  console.log(JSON.stringify({ c24: point, retained: data.retained, url: 'http://127.0.0.1:56709/' }));
})().catch(e => { console.error(e); process.exitCode = 1; });
