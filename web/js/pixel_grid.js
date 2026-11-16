// Hand grids (.matrix): 13 x 13 cells separated by 1 px lines (the grid's
// background showing through its gap). With columns of 1fr, cell edges fall
// between device pixels, and at display scaling such as 125% or 150% a 1 px
// line is 1.25 or 1.5 device pixels: the browser snaps each one to 1 or 2,
// so some lines look doubled. Here every grid gets cells of a whole number of
// device pixels and lines of exactly one device pixel, so every line is drawn
// the same way, refitted when its container or the zoom changes.

const done = new WeakSet();

function fit(el) {
  const parent = el.parentElement;
  if (!parent || el.offsetParent === null) return; // hidden: fitted when shown
  const dpr = window.devicePixelRatio || 1;
  const ps = getComputedStyle(parent);
  let avail = parent.clientWidth - parseFloat(ps.paddingLeft) - parseFloat(ps.paddingRight);
  const max = parseFloat(getComputedStyle(el).maxWidth);
  if (Number.isFinite(max)) avail = Math.min(avail, max);
  const availDev = Math.floor(avail * dpr);
  const cellDev = Math.floor((availDev - 14) / 13); // 12 gaps and 2 borders of one device pixel
  if (cellDev < 4) return;
  const px = n => `${n / dpr}px`;
  const s = el.style;
  s.gridTemplateColumns = `repeat(13, ${px(cellDev)})`;
  s.gridAutoRows = px(cellDev);
  s.gap = px(1);
  s.borderWidth = px(1);
  s.width = px(13 * cellDev + 14); // border-box
}

function watch(el) {
  if (done.has(el)) return;
  done.add(el);
  const ro = new ResizeObserver(() => fit(el));
  ro.observe(el);
  if (el.parentElement) ro.observe(el.parentElement);
  fit(el);
}

export function initPixelGrids(root = document.body) {
  root.querySelectorAll('.matrix').forEach(watch);
  new MutationObserver(records => {
    for (const r of records) {
      for (const n of r.addedNodes) {
        if (n.nodeType !== 1) continue;
        if (n.classList.contains('matrix')) watch(n);
        n.querySelectorAll?.('.matrix').forEach(watch);
      }
      // a grid shown again (class "hidden" removed) is fitted on its next resize;
      // a class change on the grid itself refits it at once
      if (r.type === 'attributes' && r.target.classList?.contains('matrix')) fit(r.target);
    }
  }).observe(root, { childList: true, subtree: true, attributes: true, attributeFilter: ['class'] });
  let dpr = window.devicePixelRatio;
  window.addEventListener('resize', () => {
    if (window.devicePixelRatio === dpr) return;
    dpr = window.devicePixelRatio;
    root.querySelectorAll('.matrix').forEach(fit);
  });
}
