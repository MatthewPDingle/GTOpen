// Which leaf net "learned flop values" uses: a shipped net (v2, the one a
// new game uses, or v1, the first), a net the leaf-net harness
// (tools/leafnet) kept, or an ensemble it built (one file that averages
// several kept nets). The list comes from the server, which reads the
// harness's work folder; saves remember the net by name.
import { api } from './api.js';

/** The first shipped net: what a game that names no net was solved with. */
export const FIRST_NET = 'v1';
/** The net a new game uses. */
export const DEFAULT_NET = 'v2';
// The remembered pick. A new key since v2 shipped, so that the new default
// reaches a browser that remembered v1 from before.
const STORE = 'pfl-leafnet-2';

/** The value model of a game built from the form: learned flop values when
 *  ticked, except with ICM payouts, which the leaf net does not price. */
export const modelFor = (learned, icm) => (learned && !icm ? 'leafnet' : 'balanced');
/** Engine fields for a pick: none when learned values are off. v1 stays
 *  unnamed, as in every game saved before a second net shipped. */
export const netConfig = (on, id) => (on && id && id !== FIRST_NET ? { leaf_net: id } : {});
/** The net to show for a game: its own when it uses learned values (no name
 *  means v1), else the remembered pick, else the default. */
export const netOf = (cfg, remembered) =>
  (cfg?.realization === 'leafnet' ? (cfg.leaf_net || FIRST_NET) : (remembered || DEFAULT_NET));

const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const k = n => (n >= 1000 ? `${Math.round(n / 1000)}k` : String(n));

export function label(net) {
  if (net.kind === 'shipped') {
    const parts = [net.id, net.default ? 'shipped · default' : 'shipped'];
    if (net.members) parts.push(`mean of ${net.members} nets`);
    if (net.train_examples) parts.push(`${k(net.train_examples)} examples`);
    if (net.available === false) parts.push('missing');
    return parts.join(' · ');
  }
  const parts = [`${(/^snap-(\d+k)/.exec(net.snapshot || '') || [])[1] || net.snapshot} data`];
  if (net.val_class != null) parts.push(`error ${net.val_class.toFixed(4)}`);
  if (net.members) {
    // an ensemble: its description only lists the member runs
    parts.unshift(`mean of ${net.members} nets`);
  } else if (net.desc) {
    parts.push(net.desc.length > 48 ? `${net.desc.slice(0, 47)}…` : net.desc);
  }
  return `${net.best || net.averages_best ? '★ ' : ''}${parts.join(' · ')}`;
}

/** Provenance of one net, one line: run, kept time, training set, ensemble,
 *  real-leaf error and the harness work folder. */
function metadata(net, work) {
  if (!net) return '';
  const parts = [];
  if (net.kind === 'shipped') {
    parts.push(net.available === false ? `${net.id} missing from this build` : `${net.id} · ${net.desc || 'shipped with GTOpen'}`);
    if (net.time) parts.push(`trained ${String(net.time).slice(0, 10)}`);
  } else {
    parts.push(`${net.snapshot}/${net.run}`);
    if (net.time) parts.push(`kept ${net.time.replace('T', ' ').slice(0, 16)}`);
  }
  if (net.train_examples) parts.push(`trained on ${net.train_examples.toLocaleString()} examples`);
  if (net.members && net.kind !== 'shipped') parts.push(`mean of ${net.members} nets`);
  else if (net.kind !== 'shipped' && net.desc) parts.push(net.desc);
  if (net.leaf_class != null) parts.push(`real-leaf error ${net.leaf_class}`);
  if (work && net.kind !== 'shipped') parts.push(`work ${work}`);
  return parts.join(' · ');
}

export function createLeafNetPicker(els, onChange) {
  const row = els.leafNetRow, sel = els.leafNet;
  if (!sel) return { config: () => ({}), load() {}, sync() {}, refresh() {} };
  const meta = document.createElement('p');
  meta.className = 'dim mono';
  meta.style.cssText = 'font-size:10px;margin:2px 0 0;overflow-wrap:anywhere';
  sel.closest('label')?.after(meta);
  let nets = [];
  const remembered = () => localStorage.getItem(STORE);
  let wanted = netOf(null, remembered());
  let work = '';
  let pending = false;
  let error = '';

  // hidden while learned values are off, or unavailable for this game (ICM)
  const sync = () => { if (row) row.hidden = !els.leaf?.checked || !!els.leaf?.disabled; };
  const chosen = () => nets.find(n => n.id === sel.value) || null;

  function render() {
    const known = new Set(nets.map(n => n.id));
    const opts = nets.map(n => `<option value="${esc(n.id)}" title="${esc(metadata(n, work))}">${esc(label(n))}</option>`);
    if (!known.has(wanted)) {
      opts.unshift(`<option value="${esc(wanted)}">${esc(wanted)} (missing)</option>`);
    }
    sel.innerHTML = opts.join('');
    sel.value = wanted;
    renderMeta();
  }

  function renderMeta() {
    const net = chosen();
    meta.setAttribute('role', error ? 'alert' : 'status');
    meta.textContent = error || (pending ? 'looking for nets…' : net ? metadata(net, work) : `${wanted} (missing)`);
  }

  async function refresh() {
    pending = true;
    error = '';
    renderMeta();
    try {
      const out = await api.pfLeafNets();
      nets = out.nets || [];
      work = out.work || '';
    } catch (e) {
      nets = [{ id: DEFAULT_NET, kind: 'shipped', default: true }, { id: FIRST_NET, kind: 'shipped' }];
      error = `leaf nets unavailable: ${e.message}`;
    } finally {
      pending = false;
    }
    if (!nets.some(n => n.id === FIRST_NET)) nets.push({ id: FIRST_NET, kind: 'shipped' });
    render();
  }

  els.leaf?.addEventListener('change', () => { sync(); if (els.leaf.checked) refresh(); });
  sel.addEventListener('focus', refresh);
  sel.addEventListener('change', () => {
    wanted = sel.value;
    localStorage.setItem(STORE, wanted);
    renderMeta();
    onChange?.();
  });
  sync();
  refresh();

  return {
    // fields for the engine config; `on` is whether this game uses learned values
    config: (on = !!els.leaf?.checked) => netConfig(on, sel.value),
    // a loaded game's choice, shown without changing the remembered pick;
    // no game (a fresh scenario) goes back to the remembered pick
    load(cfg) {
      wanted = netOf(cfg, remembered());
      render();
      sync();
    },
    sync,
    refresh,
  };
}
