// Which leaf net "learned flop values" uses: the shipped v1 or a net the
// leaf-net harness (tools/leafnet) kept. The list comes from the server,
// which reads the harness's work folder; saves remember the net by name.
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
  if (net.desc) parts.push(net.desc.length > 48 ? `${net.desc.slice(0, 47)}…` : net.desc);
  return `${net.best ? '★ ' : ''}${parts.join(' · ')}`;
}

function tip(net) {
  if (net.kind === 'shipped') return 'The net shipped with GTOpen.';
  const lines = [`${net.snapshot}/${net.run}`, net.time ? `kept ${net.time.replace('T', ' ')}` : ''];
  if (net.train_examples) lines.push(`trained on ${net.train_examples.toLocaleString()} examples`);
  if (net.sizes) lines.push(`layers ${net.sizes.join(' → ')}`);
  if (net.leaf_class) lines.push(`real-leaf class error ${net.leaf_class}`);
  return lines.filter(Boolean).join('\n');
}

export function createLeafNetPicker(els, onChange) {
  const row = els.leafNetRow, sel = els.leafNet;
  if (!sel) return { config: () => ({}), load() {}, refresh() {} };
  let nets = [];
  let wanted = localStorage.getItem(STORE) || SHIPPED;

  const sync = () => { if (row) row.hidden = !els.leaf?.checked; };

  function render() {
    const known = new Set(nets.map(n => n.id));
    const opts = nets.map(n => `<option value="${esc(n.id)}" title="${esc(tip(n))}">${esc(label(n))}</option>`);
    if (!known.has(wanted)) {
      opts.unshift(`<option value="${esc(wanted)}">${esc(wanted)} (not found on this machine)</option>`);
    }
    sel.innerHTML = opts.join('');
    sel.value = wanted;
  }

  async function refresh() {
    try {
      const out = await api.pfLeafNets();
      nets = out.nets || [];
      sel.dataset.work = out.work || '';
    } catch {
      nets = [{ id: SHIPPED, kind: 'shipped' }];
    }
    if (!nets.some(n => n.id === SHIPPED)) nets.push({ id: SHIPPED, kind: 'shipped' });
    render();
  }

  els.leaf?.addEventListener('change', () => { sync(); if (els.leaf.checked) refresh(); });
  sel.addEventListener('focus', refresh);
  sel.addEventListener('change', () => {
    wanted = sel.value;
    localStorage.setItem(STORE, wanted);
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
