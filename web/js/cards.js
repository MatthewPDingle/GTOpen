// Card utilities mirroring the Rust encoding: card = rank*4 + suit,
// rank 0=2..12=A, suit 0=c 1=d 2=h 3=s.

export const RANKS = ['2','3','4','5','6','7','8','9','T','J','Q','K','A'];
export const SUITS = ['c','d','h','s'];
export const SUIT_GLYPH = { c: '♣', d: '♦', h: '♥', s: '♠' };

export const rank = c => c >> 2;
export const suit = c => c & 3;
export const makeCard = (r, s) => (r << 2) | s;

export function cardToString(c) {
  return RANKS[rank(c)] + SUITS[suit(c)];
}

export function cardFromString(s) {
  const r = RANKS.indexOf(s[0].toUpperCase());
  const su = SUITS.indexOf(s[1].toLowerCase());
  if (r < 0 || su < 0) throw new Error(`bad card: ${s}`);
  return makeCard(r, su);
}

export function comboIndex(c1, c2) {
  const hi = Math.max(c1, c2), lo = Math.min(c1, c2);
  return (hi * (hi - 1)) / 2 + lo;
}

// The 169 hand classes as a 13x13 grid. Row i, col j (0 = A at top-left):
// i === j pair; i < j suited (row rank is higher); i > j offsuit.
export function cellInfo(i, j) {
  const r1 = 12 - i, r2 = 12 - j; // displayed ranks
  if (i === j) return { type: 'pair', hi: r1, lo: r1, label: RANKS[r1] + RANKS[r1] };
  if (i < j) return { type: 'suited', hi: r1, lo: r2, label: RANKS[r1] + RANKS[r2] + 's' };
  return { type: 'offsuit', hi: r2, lo: r1, label: RANKS[r2] + RANKS[r1] + 'o' };
}

// All combos (pairs of card ids) belonging to a cell class.
export function cellCombos(info) {
  const out = [];
  if (info.type === 'pair') {
    for (let s1 = 0; s1 < 4; s1++)
      for (let s2 = 0; s2 < s1; s2++)
        out.push([makeCard(info.hi, s1), makeCard(info.hi, s2)]);
  } else if (info.type === 'suited') {
    for (let s = 0; s < 4; s++)
      out.push([makeCard(info.hi, s), makeCard(info.lo, s)]);
  } else {
    for (let s1 = 0; s1 < 4; s1++)
      for (let s2 = 0; s2 < 4; s2++)
        if (s1 !== s2) out.push([makeCard(info.hi, s1), makeCard(info.lo, s2)]);
  }
  return out;
}

// Compact text from a 1326-weight array (class-grouped where uniform).
export function weightsToText(weights) {
  const parts = [];
  for (let i = 0; i < 13; i++) {
    for (let j = 0; j < 13; j++) {
      const info = cellInfo(i, j);
      const combos = cellCombos(info);
      const ws = combos.map(([a, b]) => weights[comboIndex(a, b)] || 0);
      const present = ws.filter(w => w > 0);
      if (!present.length) continue;
      const uniform = present.length === ws.length && present.every(w => Math.abs(w - present[0]) < 1e-4);
      if (uniform) {
        parts.push(present[0] >= 0.9995 ? info.label : `${info.label}:${trimW(present[0])}`);
      } else {
        combos.forEach(([a, b], k) => {
          const w = ws[k];
          if (w <= 0) return;
          const name = comboName(a, b);
          parts.push(w >= 0.9995 ? name : `${name}:${trimW(w)}`);
        });
      }
    }
  }
  return parts.join(',');
}

function trimW(w) {
  return parseFloat(w.toFixed(3)).toString();
}

export function comboName(c1, c2) {
  let [a, b] = c1 > c2 ? [c1, c2] : [c2, c1];
  if (rank(a) < rank(b)) [a, b] = [b, a];
  return cardToString(a) + cardToString(b);
}

// Pretty combo with suit glyphs for display.
export function comboPretty(c1, c2) {
  let [a, b] = rank(c1) >= rank(c2) ? [c1, c2] : [c2, c1];
  return [a, b];
}
