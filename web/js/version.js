// The app's version in the header: a quiet link to the change log.
//
// The server reads the version and release date from the newest entry of
// CHANGELOG.md (GET /api/version), so the link shows what the checkout holds
// at this page load. Against an older server, or outside a checkout, the link
// keeps its plain "change log" text.

// The page and the change log come from disk, so a pull alone updates them.
// The server program does not change until it is rebuilt and restarted. It
// reports what it can do as a number (`server_level`, SERVER_LEVEL in
// crates/server/src/version.rs); when that is below what this page needs,
// the header asks for a restart. Raise both together whenever the page
// starts to need something new from the server.
export const NEEDS_SERVER_LEVEL = 4;

export const RESTART_LABEL = '\u26a0 restart GTOpen';
export const RESTART_TIP = 'This page is newer than the GTOpen program that is running, so some things will be missing or wrong. ' +
  'Save your work, close GTOpen, start it again (it rebuilds itself, which takes a few minutes), then refresh this page.';

/** True when the running server is older than this page needs (no reply = older still). */
export function needsRestart(info) {
  return !((info?.server_level ?? 0) >= NEEDS_SERVER_LEVEL);
}

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

/** `notice` is the header's restart note: shown only when the server is older than the page. */
export async function initVersion(link, fetchInfo, notice = null) {
  if (!link) return;
  let info = null;
  try { info = await fetchInfo(); } catch { /* an older server has no /api/version */ }
  if (notice) {
    const stale = needsRestart(info);
    notice.textContent = stale ? RESTART_LABEL : '';
    if (stale) notice.dataset.tip = RESTART_TIP;
    notice.classList.toggle('hidden', !stale);
  }
  link.textContent = versionLabel(info);
  link.dataset.tip = versionTip(info);
  if (/^https:\/\//.test(info?.changelog_url || '')) link.href = info.changelog_url;
}
