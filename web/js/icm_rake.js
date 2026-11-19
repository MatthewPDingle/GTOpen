// Rake boxes while tournament payouts (ICM) are on. A tournament game is
// solved without rake (the server refuses any other), so the callers set the
// boxes to 0; this greys them out and makes the reason the tooltip of each
// box. Nothing is written beside the boxes, so the form keeps its shape.
// Used by the Preflop Lab (preflop_icm.js) and by SETUP and 3-WAY
// (postflop_icm.js).

export const ICM_RAKE_TIP = 'No rake while tournament payouts are on. Turn them off to set a rake again.';

/** Disable and grey the rake boxes. Safe to call again while they are held. */
export function holdRakeBoxes(inputs) {
  for (const input of inputs) {
    input.disabled = true;
    const label = input.closest('label');
    if (!label || label.classList.contains('icm-rake-off')) continue;
    label.classList.add('icm-rake-off');
    label.dataset.rakeTip = label.dataset.tip ?? '';
    label.dataset.tip = ICM_RAKE_TIP;
  }
}

/** Give the boxes back as they were. The callers decide what numbers go in. */
export function releaseRakeBoxes(inputs) {
  for (const input of inputs) {
    input.disabled = false;
    const label = input.closest('label');
    if (!label?.classList.contains('icm-rake-off')) continue;
    label.classList.remove('icm-rake-off');
    if (label.dataset.rakeTip) label.dataset.tip = label.dataset.rakeTip;
    else delete label.dataset.tip;
    delete label.dataset.rakeTip;
  }
}
