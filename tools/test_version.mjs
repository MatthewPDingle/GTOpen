import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { releaseDate, versionLabel, versionTip, initVersion } from '../web/js/version.js';

assert.equal(releaseDate('2026-11-18'), '18 Nov 2026');
assert.equal(releaseDate('2027-01-05'), '5 Jan 2027');
for (const bad of ['', null, undefined, '18 Nov 2026', '2026-13-01', '2026-00-10']) assert.equal(releaseDate(bad), '');

const info = { version: '1.0.0', date: '2026-11-18', commit: 'b1f653ddc', changelog_url: 'https://example.org/CHANGELOG.md' };
assert.equal(versionLabel(info), 'v1.0.0 · 18 Nov 2026');
assert.equal(versionLabel({ version: '1.2.3', date: null }), 'v1.2.3');
// an older server, or a folder with no change log: the link stays a plain link
for (const none of [null, undefined, {}, { version: null, date: null }]) {
  assert.equal(versionLabel(none), 'change log');
  assert.match(versionTip(none), /^Click to see what changed/);
}
assert.match(versionTip(info), /^GTOpen 1\.0\.0, released 18 Nov 2026 \(commit b1f653ddc\)\.\nClick to see what changed/);
assert.match(versionTip({ version: '1.0.0', date: '2026-11-18', commit: null }), /^GTOpen 1\.0\.0, released 18 Nov 2026\.\n/);

const link = () => ({ textContent: 'change log', href: 'https://github.com/default', dataset: {} });
let el = link();
await initVersion(el, async () => info);
assert.equal(el.textContent, 'v1.0.0 · 18 Nov 2026');
assert.equal(el.href, info.changelog_url);
assert.match(el.dataset.tip, /commit b1f653ddc/);
el = link();
await initVersion(el, async () => { throw new Error('404'); });
assert.equal(el.textContent, 'change log');
assert.equal(el.href, 'https://github.com/default');
// only an https link replaces the page's own
el = link();
await initVersion(el, async () => ({ ...info, changelog_url: 'javascript:alert(1)' }));
assert.equal(el.href, 'https://github.com/default');
await initVersion(null, async () => info);

// the label for the version this checkout is on
const top = /^## (\d+\.\d+\.\d+) - (\d{4}-\d{2}-\d{2})$/m.exec(readFileSync(new URL('../CHANGELOG.md', import.meta.url), 'utf8'));
assert.ok(top, 'CHANGELOG.md needs a `## 1.2.3 - YYYY-MM-DD` heading');
assert.match(versionLabel({ version: top[1], date: top[2] }), /^v\d+\.\d+\.\d+ · \d{1,2} [A-Z][a-z]{2} \d{4}$/);
console.log('version label tests passed');
