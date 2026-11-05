// TRUST THE READ — the exploit dial for a locked villain profile.
//
// With a villain's postflop profile locked (Browse "LOCK IP TO …"), the
// dial sets how sure the hero is of the read: with probability p the
// villain plays the profile, otherwise he plays freely and adapts to the
// hero (Restricted Nash Response, crates/solver/src/rnr.rs). 100% is the
// max exploit (today's lock and re-adapt), 0% is GTO.
//
// After each solve the server reports what the level buys and costs
// (status.trust_readout): the hero's EV against the read, and his worst
// case, the EV left when the villain knows the hero's strategy and best
// responds. SWEEP solves a row of levels warm-started from each other and
// draws the tradeoff curve; clicking a point picks that level.

import { api } from './api.js';

const esc = s => String(s).replace(/[&<>"']/g, c =>
  ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const pct = t => `${Math.round(t * 100)}%`;
const chips = x => (x == null ? '—' : (+x).toFixed(1));

// series colors: validated (dataviz validate_palette.js, dark, on --panel)
const C_READ = '#29ad62';
const C_WORST = '#3d86c6';

/**
 * @param {HTMLElement} panel  the #trust-panel container (Browse)
 * @param {object} o
 * @param {(msg: string, err?: boolean) => void} o.toast
 * @param {() => number|null} o.villain  the profile-locked player, or null
 * @param {(p: number) => string} o.posLabel  "OOP"/"IP" or the seat name
 * @param {() => Promise<void>} o.startSweep  start a sweep solve (app.js)
 */
export function initTrust(panel, { toast, villain, posLabel, startSweep }) {
  const S = {
    trust: null,      // server's dial (null = unset, plays as 100%)
    readout: null,    // status.trust_readout
    sweep: null,      // status.trust_sweep
    running: false,
    pot: null,
    busy: false,
    stamp: '',        // last rendered status, to skip no-op repaints
    showCurve: true,  // the sweep curve's <details> (kept across repaints)
    showTable: false,
  };

  async function setTrust(t) {
    if (S.busy) return;
    S.busy = true;
    try {
      await api.trust(t);
      S.trust = t;
      S.readout = null;
      toast(S.running
        ? `trust ${pct(t)} — applied to the running solve`
        : `trust the read: ${pct(t)} — RE-SOLVE to adapt`);
    } catch (e) {
      toast(e.message, true);
    } finally {
      S.busy = false;
      render(true);
    }
  }

  function readoutText() {
    const r = S.readout;
    if (!r) return S.running ? 'solving…' : 'RE-SOLVE to see what this level buys and costs';
    const parts = [`EV vs the read <b>${chips(r.hero_ev_vs_read)}</b>`];
    if (r.hero_worst_case_ev != null) parts.push(`worst case <b>${chips(r.hero_worst_case_ev)}</b>`);
    else parts.push(`villain best response <b>${chips(r.villain_best_response_ev)}</b>`);
    return `${parts.join(' · ')} <span class="dim">chips at ${pct(r.trust)}${S.pot ? `, pot ${chips(S.pot)}` : ''}</span>`;
  }

  function render(force = false) {
    const v = villain();
    if (v === null || v === undefined) {
      panel.classList.add('hidden');
      panel.innerHTML = '';
      S.stamp = '';
      return;
    }
    const stamp = JSON.stringify([v, S.trust, S.readout, S.sweep, S.running, S.busy]);
    if (!force && stamp === S.stamp) return;
    S.stamp = stamp;
    panel.classList.remove('hidden');
    const t = S.trust ?? 1;
    const sweeping = !!S.sweep?.running;
    const hero = posLabel(1 - v), vill = posLabel(v);
    panel.innerHTML = `
      <div class="trust-row">
        <span class="trust-head">TRUST THE READ <span class="info-dot" tabindex="0" data-tip="How sure are you of ${esc(vill)}'s profile? At p% the solve assumes he plays the profile p% of the time and otherwise adapts to you like a solver. 100% = max exploit (the profile is a fact); 0% = GTO. In between, ${esc(hero)} keeps most of the exploit's EV while risking much less if the read is wrong. Manual node locks stay facts at every level.">?</span></span>
        <input type="range" class="trust-slider" min="0" max="100" step="5" value="${Math.round(t * 100)}"
          aria-label="Trust the read, percent" ${sweeping || S.busy ? 'disabled' : ''}>
        <span class="trust-val mono">${pct(t)}</span>
        <button class="btn ghost sm trust-sweep" ${S.running ? 'disabled' : ''}
          data-tip="Solve 100%, 90%, 80%, 70%, 50%, 25% and 0% in a row (each warm-starts from the last; uses the SOLVE tab's target and max iterations per level) and chart EV vs the read against the worst case. Click a point to pick that level.">${sweeping ? `SWEEPING ${S.sweep.current + 1}/${S.sweep.levels.length}…` : 'SWEEP'}</button>
        <span class="trust-readout mono">${readoutText()}</span>
      </div>
      ${S.sweep && S.sweep.points.length ? `<details class="trust-curve"${S.showCurve ? ' open' : ''}>
        <summary>sweep curve · ${S.sweep.points.length} level${S.sweep.points.length > 1 ? 's' : ''}</summary>${chart()}</details>` : ''}`;
    panel.querySelector('.trust-curve')?.addEventListener('toggle', e => { S.showCurve = e.target.open; });
    panel.querySelector('.trust-table')?.addEventListener('toggle', e => { S.showTable = e.target.open; });
    const slider = panel.querySelector('.trust-slider');
    const val = panel.querySelector('.trust-val');
    slider.addEventListener('input', () => { val.textContent = `${slider.value}%`; });
    slider.addEventListener('change', () => setTrust(+slider.value / 100));
    panel.querySelector('.trust-sweep').addEventListener('click', async () => {
      try { await startSweep(); } catch (e) { toast(e.message, true); }
    });
    panel.querySelectorAll('[data-trust]').forEach(el => {
      el.addEventListener('click', () => setTrust(+el.dataset.trust));
      el.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setTrust(+el.dataset.trust); }
      });
    });
  }

  /** The tradeoff curve: x = trust, y = chips; EV vs the read (solid)
   *  and the worst case (dashed). One y-axis: both are the hero's EV. */
  function chart() {
    const pts = [...S.sweep.points].sort((a, b) => a.trust - b.trust);
    const worst = p => p.hero_worst_case_ev ?? null;
    const hasWorst = pts.some(p => worst(p) != null);
    const W = 520, H = 170, L = 46, R = 92, T = 12, B = 26;
    const ys = pts.flatMap(p => [p.hero_ev_vs_read, worst(p)]).filter(y => y != null);
    let yMin = Math.min(...ys), yMax = Math.max(...ys);
    if (yMax - yMin < 1e-9) { yMin -= 1; yMax += 1; }
    const pad = (yMax - yMin) * 0.08;
    yMin -= pad; yMax += pad;
    const x = t => L + t * (W - L - R);
    const y = v => T + (1 - (v - yMin) / (yMax - yMin)) * (H - T - B);
    // recessive grid: ~4 nice ticks
    const step = niceStep((yMax - yMin) / 4);
    let grid = '';
    for (let g = Math.ceil(yMin / step) * step; g <= yMax; g += step) {
      grid += `<line x1="${L}" x2="${W - R}" y1="${y(g)}" y2="${y(g)}" class="tg"/>` +
        `<text x="${L - 6}" y="${y(g) + 3}" text-anchor="end" class="tl">${+g.toFixed(1)}</text>`;
    }
    for (const t of [0, 0.25, 0.5, 0.75, 1]) {
      grid += `<text x="${x(t)}" y="${H - 8}" text-anchor="middle" class="tl">${pct(t)}</text>`;
    }
    const path = f => pts.filter(p => f(p) != null)
      .map((p, k) => `${k ? 'L' : 'M'}${x(p.trust).toFixed(1)},${y(f(p)).toFixed(1)}`).join('');
    const sel = S.trust ?? 1;
    const marks = pts.map(p => {
      const on = Math.abs(p.trust - sel) < 1e-6;
      const tip = `trust ${pct(p.trust)}: EV vs the read ${chips(p.hero_ev_vs_read)}` +
        (worst(p) != null ? `, worst case ${chips(worst(p))}` : `, villain best response ${chips(p.villain_best_response_ev)}`) +
        ` chips · ${p.iterations} iterations, ${p.seconds.toFixed(1)} s · click to use this level`;
      const dots = [[p.hero_ev_vs_read, C_READ], [worst(p), C_WORST]]
        .filter(([v]) => v != null)
        .map(([v, c]) => `<circle cx="${x(p.trust)}" cy="${y(v)}" r="${on ? 5 : 4}" fill="${c}" class="tm"/>`).join('');
      // hit target: the whole column, larger than the marks
      return `<g class="tp${on ? ' on' : ''}" data-trust="${p.trust}" tabindex="0" role="button" aria-label="${esc(tip)}">` +
        `<rect x="${x(p.trust) - 14}" y="${T}" width="28" height="${H - T - B}" class="th"/>` +
        `${on ? `<line x1="${x(p.trust)}" x2="${x(p.trust)}" y1="${T}" y2="${H - B}" class="ts"/>` : ''}` +
        `${dots}<title>${esc(tip)}</title></g>`;
    }).join('');
    // direct labels at the right end (the 100% end of each series)
    const last = pts[pts.length - 1];
    const lab = [];
    lab.push([y(last.hero_ev_vs_read), 'EV vs the read', C_READ]);
    if (worst(last) != null) lab.push([y(worst(last)), 'worst case', C_WORST]);
    if (lab.length === 2 && Math.abs(lab[0][0] - lab[1][0]) < 12) {
      const mid = (lab[0][0] + lab[1][0]) / 2, up = lab[0][0] <= lab[1][0] ? -1 : 1;
      lab[0][0] = mid + up * 6; lab[1][0] = mid - up * 6;
    }
    const labels = lab.map(([ly, txt]) =>
      `<text x="${x(last.trust) + 8}" y="${ly + 3}" class="tdl">${txt}</text>`).join('');
    const rows = pts.map(p => `<tr><td>${pct(p.trust)}</td><td>${chips(p.hero_ev_vs_read)}</td>` +
      `<td>${worst(p) != null ? chips(worst(p)) : '—'}</td><td>${chips(p.villain_best_response_ev)}</td>` +
      `<td>${p.iterations}</td></tr>`).join('');
    return `
      <div class="trust-chart">
        <div class="trust-legend">
          <span><i style="background:${C_READ}"></i>${esc(posLabel(1 - villain()))} EV vs the read</span>
          ${hasWorst ? `<span><i class="dash" style="border-color:${C_WORST}"></i>worst case (villain best responds)</span>` : ''}
          <span class="dim">chips · x = trust in the read</span>
        </div>
        <svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img"
          aria-label="Trust sweep: hero EV against the read and worst case by trust level">
          ${grid}
          <path d="${path(p => p.hero_ev_vs_read)}" stroke="${C_READ}" class="tline"/>
          ${hasWorst ? `<path d="${path(worst)}" stroke="${C_WORST}" class="tline dash"/>` : ''}
          ${marks}${labels}
        </svg>
        <details class="trust-table"${S.showTable ? ' open' : ''}><summary>table</summary>
          <table><thead><tr><th>trust</th><th>EV vs read</th><th>worst case</th><th>villain BR EV</th><th>iterations</th></tr></thead>
          <tbody>${rows}</tbody></table>
        </details>
      </div>`;
  }

  return {
    /** Fold in a /api/status poll. */
    update(st) {
      S.trust = st.trust ?? null;
      S.readout = st.trust_readout || null;
      S.sweep = st.trust_sweep || null;
      S.running = st.state === 'running';
      S.pot = st.spot_request?.starting_pot ?? S.pot;
      render();
    },
    /** The villain lock changed (Browse): show or hide the dial. */
    refresh() { render(true); },
    /** The locks changed under the readout. */
    invalidate() { S.readout = null; render(true); },
  };
}

function niceStep(raw) {
  const m = Math.pow(10, Math.floor(Math.log10(raw || 1)));
  const f = raw / m;
  return (f < 1.5 ? 1 : f < 3 ? 2 : f < 7 ? 5 : 10) * m;
}
