// Flop texture classes shared by the REPORTS views (filters, texture
// tables and the size-sweep Best size view).

export const RANKS = '23456789TJQKA';

export const cardsOf = b => [b.slice(0, 2), b.slice(2, 4), b.slice(4, 6)];
export function texOf(board) {
  const cs = cardsOf(board);
  const rs = cs.map(c => RANKS.indexOf(c[0])).sort((a, b) => b - a);
  const suits = new Set(cs.map(c => c[1]));
  const paired = new Set(rs).size < 3;
  const span = rs[0] - rs[2];
  return {
    all: true,
    rainbow: suits.size === 3,
    twotone: suits.size === 2,
    mono: suits.size === 1,
    paired,
    connected: !paired && span <= 4,
    acehigh: rs[0] === 12,
    broadway: rs[0] === 11 || rs[0] === 10,
    mid: rs[0] >= 7 && rs[0] <= 9,
    low: rs[0] <= 6,
    _rs: rs, _span: span, _suits: suits.size,
  };
}
export const TEX = [
  ['all', 'ALL'], ['rainbow', 'RAINBOW'], ['twotone', 'TWO-TONE'],
  ['mono', 'MONO'], ['paired', 'PAIRED'], ['connected', 'CONNECTED'],
  ['acehigh', 'A-HIGH'], ['broadway', 'K/Q-HIGH'], ['mid', 'MID'], ['low', 'LOW'],
];

