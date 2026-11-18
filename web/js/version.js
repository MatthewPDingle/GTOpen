// The app's version in the header: a quiet link to the change log.
//
// The server reads the version and release date from the newest entry of
// CHANGELOG.md (GET /api/version), so the link shows what the checkout holds
// at this page load. Against an older server, or outside a checkout, the link
// keeps its plain "change log" text.

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

/** '2026-11-18' as '18 Nov 2026'; '' for anything else. */
export function releaseDate(iso) {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso || '');
  if (!m || +m[2] < 1 || +m[2] > 12) return '';
  return `${+m[3]} ${MONTHS[+m[2] - 1]} ${m[1]}`;
}

/** The link's text: 'v1.0.0 · 18 Nov 2026'. */
export function versionLabel(info) {
  if (!info?.version) return 'change log';
  const date = releaseDate(info.date);
  return date ? `v${info.version} · ${date}` : `v${info.version}`;
}

/** The link's tooltip. */
export function versionTip(info) {
  const open = 'Click to see what changed in each version (opens the change log on GitHub).';
  if (!info?.version) return open;
  const date = releaseDate(info.date);
  const commit = info.commit ? ` (commit ${info.commit})` : '';
  return `GTOpen ${info.version}${date ? `, released ${date}` : ''}${commit}.\n${open}`;
}

export async function initVersion(link, fetchInfo) {
  if (!link) return;
  let info = null;
  try { info = await fetchInfo(); } catch { /* an older server has no /api/version */ }
  link.textContent = versionLabel(info);
  link.dataset.tip = versionTip(info);
  if (/^https:\/\//.test(info?.changelog_url || '')) link.href = info.changelog_url;
}
