// Lightweight styled tooltips. Add data-tip="..." to any element (works for
// dynamically rendered content via event delegation).

let tipEl = null;
let showTimer = null;
let currentTarget = null;

export function initTooltips() {
  tipEl = document.createElement('div');
  tipEl.id = 'tip';
  document.body.appendChild(tipEl);

  document.addEventListener('mouseover', e => {
    const t = e.target.closest('[data-tip]');
    if (t === currentTarget) return;
    hide();
    if (!t) return;
    currentTarget = t;
    showTimer = setTimeout(() => show(t), 400);
  });
  document.addEventListener('mouseout', e => {
    const t = e.target.closest('[data-tip]');
    if (t && t === currentTarget && !(e.relatedTarget && t.contains(e.relatedTarget))) {
      hide();
    }
  });
  document.addEventListener('mousedown', hide, true);
  window.addEventListener('scroll', hide, true);
}

function show(t) {
  if (!document.body.contains(t)) return;
  const text = t.dataset.tip;
  if (!text) return;
  tipEl.textContent = text;
  tipEl.classList.add('show');
  const r = t.getBoundingClientRect();
  const tw = tipEl.offsetWidth;
  const th = tipEl.offsetHeight;
  const x = Math.min(Math.max(8, r.left + r.width / 2 - tw / 2), window.innerWidth - tw - 8);
  let y = r.bottom + 9;
  if (y + th > window.innerHeight - 8) y = r.top - th - 9;
  tipEl.style.left = `${x}px`;
  tipEl.style.top = `${y}px`;
}

function hide() {
  clearTimeout(showTimer);
  currentTarget = null;
  if (tipEl) tipEl.classList.remove('show');
}
