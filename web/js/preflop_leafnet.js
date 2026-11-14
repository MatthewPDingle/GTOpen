// Which leaf net "learned flop values" uses: the shipped v1, a net the
// leaf-net harness (tools/leafnet) kept, or an ensemble it built (one file
// that averages several kept nets). The list comes from the server, which
// reads the harness's work folder; saves remember the net by name.
import { api } from './api.js';

const SHIPPED = 'v1';
const STORE = 'pfl-leafnet';

const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const k = n => (n >= 1000 ? `${Math.round(n / 1000)}k` : String(n));

function label(net) {
  if (net.kind === 'shipped') {
    return `v1 · shipped${net.train_examples ? ` · ${k(net.train_examples)} examples` : ''}`;
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
  if (net.kind === 'shipped') parts.push(net.available === false ? 'v1 missing from this build' : 'v1 · shipped with GTOpen');
  else {
    parts.push(`${net.snapshot}/${net.run}`);
    if (net.time) parts.push(`kept ${net.time.replace('T', ' ').slice(0, 16)}`);
  }
  if (net.train_examples) parts.push(`trained on ${net.train_examples.toLocaleString()} examples`);
  if (net.members) parts.push(`mean of ${net.members} nets`);
  else if (net.kind !== 'shipped' && net.desc) parts.push(net.desc);
  if (net.leaf_class != null) parts.push(`real-leaf error ${net.leaf_class}`);
  if (work && net.kind !== 'shipped') parts.push(`work ${work}`);
  return parts.join(' · ');
}

export function createLeafNetPicker(els, onChange) {
  const row = els.leafNetRow, sel = els.leafNet;
  if (!sel) return { config: () => ({}), load() {}, refresh() {} };
  const meta = document.createElement('p');
  meta.className = 'dim mono';
  meta.style.cssText = 'font-size:10px;margin:2px 0 0;overflow-wrap:anywhere';
  sel.closest('label')?.after(meta);
  let nets = [];
  let wanted = localStorage.getItem(STORE) || SHIPPED;
  let work = '';
  let pending = false;
  let error = '';

  const sync = () => { if (row) row.hidden = !els.leaf?.checked; };
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
      nets = [{ id: SHIPPED, kind: 'shipped' }];
      error = `leaf nets unavailable: ${e.message}`;
    } finally {
      pending = false;
    }
    if (!nets.some(n => n.id === SHIPPED)) nets.push({ id: SHIPPED, kind: 'shipped' });
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
    // fields for the engine config; nothing when unticked or the shipped net
    config: () => (els.leaf?.checked && sel.value && sel.value !== SHIPPED ? { leaf_net: sel.value } : {}),
    // a loaded game's choice, shown without changing the remembered default
    load(cfg) {
      wanted = cfg.realization === 'leafnet' ? (cfg.leaf_net || SHIPPED) : (localStorage.getItem(STORE) || SHIPPED);
      render();
      sync();
    },
    refresh,
  };
}
