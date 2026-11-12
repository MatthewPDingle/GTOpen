// Lightweight styled tooltips. Add data-tip="..." to any element (works for
// dynamically rendered content via event delegation). Tips show on mouse
// hover AND on keyboard focus, and their text is live: if the element's
// data-tip attribute changes while its tip is up (e.g. an updating readout),
// the tip re-reads and repositions.
//
// Contract: while a tip is up the tip element is role="tooltip" and the
// target carries aria-describedby="tip", so assistive tech reads the same
// text the pointer shows; both are removed on hide. Keyboard focus shows at
// once (no hover delay). Escape hides.
//
// An explanatory dot is a real button, not a focusable span:
//   <button type="button" class="info-dot" aria-label="WHAT THIS EXPLAINS"
//     data-tip="THE EXPLANATION">?</button>
// (aria-label names the subject; the tip stays the explanation.)

let tipEl = null;
let showTimer = null;
let currentTarget = null;
let tipObserver = null; // watches the current target's data-tip for live edits
let pointer = null;

export function initTooltips() {
  tipEl = document.createElement('div');
  tipEl.id = 'tip';
  tipEl.setAttribute('role', 'tooltip');
  document.body.appendChild(tipEl);
  tipObserver = new MutationObserver(() => {
    if (currentTarget && tipEl.classList.contains('show')) show(currentTarget);
  });

  const tipTarget = n => n instanceof Element ? n.closest('[data-tip]') : null;
  const enter = (t, immediate = false) => {
    if (t === currentTarget) return;
    hide();
    if (!t) return;
    currentTarget = t;
    if (immediate) show(t);
    else showTimer = setTimeout(() => show(t), 400);
  };
  const leave = (t, next) => {
    if (t && t === currentTarget && !(next instanceof Element && t.contains(next))) hide();
  };

  document.addEventListener('mouseover', e => {
    pointer = { x: e.clientX, y: e.clientY };
    enter(tipTarget(e.target));
  });
  // Large surfaces (report charts) opt into a cursor anchor. Re-enter after
  // crossing an empty part of the canvas without requiring a mouseout first.
  document.addEventListener('mousemove', e => {
    const t = tipTarget(e.target);
    if (!t?.hasAttribute('data-tip-follow-pointer')) return;
    pointer = { x: e.clientX, y: e.clientY };
    enter(t);
    if (tipEl.classList.contains('show')) position(t);
  });
  document.addEventListener('mouseout', e => leave(tipTarget(e.target), e.relatedTarget));
  // keyboard: focused elements (buttons, tabindexed surfaces) get the same
  // tips at once — but only when the focus is keyboard-driven (:focus-visible
  // semantics). Clicks also move focus (buttons, and the tabindexed
  // containers via any non-focusable child), and without this gate the
  // focusin that follows every mousedown would resurrect the very tip the
  // mousedown just hid, parking it over whatever the user clicked.
  let keyboardFocus = false;
  document.addEventListener('keydown', e => {
    keyboardFocus = true;
    if (e.key === 'Escape') hide();
  }, true);
  document.addEventListener('pointerdown', () => { keyboardFocus = false; }, true);
  document.addEventListener('focusin', e => {
    if (keyboardFocus) { pointer = null; enter(tipTarget(e.target), true); }
  });
  document.addEventListener('focusout', e => leave(tipTarget(e.target), e.relatedTarget));
  document.addEventListener('mousedown', hide, true);
  window.addEventListener('scroll', hide, true);
  window.addEventListener('resize', hide);
  document.addEventListener('close', hide, true);
}

function describe(t) {
  const prior = t.getAttribute('aria-describedby');
  const ids = (prior || '').split(/\s+/).filter(Boolean);
  if (ids.includes(tipEl.id)) return;
  t.dataset.tipDescribed = prior || '';
  t.setAttribute('aria-describedby', [...ids, tipEl.id].join(' '));
}

function undescribe() {
  if (!currentTarget) return;
  const prior = currentTarget.dataset.tipDescribed;
  delete currentTarget.dataset.tipDescribed;
  if (prior) currentTarget.setAttribute('aria-describedby', prior);
  else currentTarget.removeAttribute('aria-describedby');
}

function show(t) {
  if (!document.body.contains(t)) return hide();
  const text = t.dataset.tip;
  if (!text) return hide();
  // A modal dialog is in the browser's top layer; its field help must live
  // inside that dialog to remain visible above the backdrop.
  const host = t.closest('dialog[open]') || document.body;
  if (tipEl.parentElement !== host) host.appendChild(tipEl);
  // data-tip-html: an optional richer rendering of the same tip as trusted
  // markup built by the app (the hand grids' aligned action tables) — never
  // user or server text unescaped. data-tip stays the plain-text version, so
  // a client running an older tooltip.js still gets a readable tip.
  const html = t.dataset.tipHtml;
  if (html) tipEl.innerHTML = html;
  else tipEl.textContent = text;
  if (currentTarget !== t) { undescribe(); currentTarget = t; }
  describe(t);
  tipEl.classList.add('show');
  // live content: re-invoke show() when this element's data-tip changes
  // (re-observing the same node just replaces the options — no duplicates)
  tipObserver.observe(t, { attributes: true, attributeFilter: ['data-tip', 'data-tip-html'] });
  position(t);
}

function position(t) {
  const r = t.getBoundingClientRect();
  const tw = tipEl.offsetWidth;
  const th = tipEl.offsetHeight;
  const follow = pointer && t.hasAttribute('data-tip-follow-pointer');
  const proposedX = follow ? pointer.x + 14 : r.left + r.width / 2 - tw / 2;
  const x = Math.max(8, Math.min(proposedX, window.innerWidth - tw - 8));
  let y = follow ? pointer.y + 16 : r.bottom + 9;
  if (y + th > window.innerHeight - 8) y = (follow ? pointer.y : r.top) - th - 12;
  y = Math.max(8, Math.min(y, window.innerHeight - th - 8));
  tipEl.style.left = `${x}px`;
  tipEl.style.top = `${y}px`;
}

function hide() {
  clearTimeout(showTimer);
  undescribe();
  currentTarget = null;
  if (tipObserver) tipObserver.disconnect();
  if (tipEl) tipEl.classList.remove('show');
}
