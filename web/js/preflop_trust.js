// TRUST THE READ in Preflop Lab hero mode.
//
// In hero mode every other seat is frozen, and a seat with a profile plays
// it (the "read"). The dial sets how sure the hero is of those reads: each
// profiled seat plays its profile with probability p and otherwise adapts
// to the hero like a solver seat, independently per seat (Restricted Nash
// Response, crates/solver/src/preflop/rnr.rs). 100% is the max exploit,
// lower levels give up some exploit EV for safety when a read is wrong.
//
// After each accuracy check the server reports (status.trust_readout) the
// hero's EV against the reads, against the mix he solved for, and against
// seats that adapt to him (the "if the reads are wrong" number; with 3+
// players an adapting seat maximizes its own EV, so it is not a strict
// worst case).

import { api } from './api.js';

const esc = s => String(s).replace(/[&<>"']/g, c =>
  ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const pct = t => `${Math.round(t * 100)}%`;
const bb = x => (x == null ? '—' : `${x >= 0 ? '+' : ''}${(+x).toFixed(3)}`);

const TIP = 'At p% each profiled seat plays its read p% of the time and otherwise adapts to you, independently. '
  + '100% is the max exploit; lower levels give up EV against the read for safety.';

/**
 * @param {HTMLElement} panel  the #pfl-trust container
 * @param {object} o
 * @param {(msg: string, err?: boolean) => void} o.toast
 * @param {() => string[]} o.positions  seat names
 */
export function initPreflopTrust(panel, { toast, positions }) {
  const S = { st: null, busy: false, stamp: '', draft: null };

  async function setTrust(t) {
    if (S.busy) return;
    S.busy = true;
    try {
      await api.pfTrust(t);
      if (S.st) { S.st.trust = t; S.st.trust_readout = null; }
      toast(`trust the read: ${pct(t)} — RE-SOLVE to adapt`);
    } catch (e) {
      toast(e.message, true);
    } finally {
      S.busy = false;
      S.draft = null;
      render(true);
    }
  }

  function readoutHtml(st) {
    const r = st.trust_readout;
    if (!r) {
      if (st.state === 'running') return 'solving…';
      return 'the hero plays the max exploit — RE-SOLVE to see what this level buys and costs';
    }
    return `EV vs the reads <b>${bb(r.hero_ev_vs_read)}</b> · vs the mix <b>${bb(r.hero_ev_vs_mixture)}</b>`
      + ` · if they adapt <b>${bb(r.hero_ev_vs_adapting)}</b> <span class="dim">bb/hand at ${pct(r.trust)}</span>`;
  }

  function render(force = false) {
    const st = S.st;
    const seats = st && Array.isArray(st.trust_seats) ? st.trust_seats : [];
    if (!st || st.hero == null || !seats.length) {
      panel.classList.add('hidden');
      panel.innerHTML = '';
      S.stamp = '';
      return;
    }
    const running = st.state === 'running';
    if (!force && S.draft != null) return; // mid-drag: keep the slider
    // null means the max-exploit level: one slider, one state, no "off".
    const t = st.trust == null ? 1 : st.trust;
    const stamp = JSON.stringify([st.trust, running, seats, st.trust_readout, S.busy]);
    if (!force && stamp === S.stamp) return;
    S.stamp = stamp;
    panel.classList.remove('hidden');
    const names = seats.map(i => esc(positions()[i] ?? i)).join(', ');
    panel.innerHTML = `
      <div class="trust-row">
        <span class="trust-head" data-tip="${esc(TIP)}">TRUST THE READ</span>
        <input type="range" class="trust-slider" min="0" max="100" step="5" value="${Math.round(t * 100)}"
          aria-label="Trust the read, percent" ${running || S.busy ? 'disabled' : ''}>
        <span class="trust-val">${pct(t)}</span>
        <span class="dim">applies to ${names}</span>
      </div>
      <div class="trust-row"><span class="trust-readout">${readoutHtml(st)}</span></div>`;
    const slider = panel.querySelector('.trust-slider');
    const val = panel.querySelector('.trust-val');
    slider.addEventListener('input', () => { S.draft = +slider.value / 100; val.textContent = pct(S.draft); });
    slider.addEventListener('change', () => setTrust(+slider.value / 100));
  }

  return {
    /** Feed every /api/preflop/status response. */
    update(st) {
      S.st = st;
      render();
    },
  };
}
