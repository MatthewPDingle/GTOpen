// 13x13 range editor with drag painting, weight brush, text sync and presets.

import { cellInfo, cellCombos, comboIndex, weightsToText } from './cards.js';
import { api, toast } from './api.js';

export class RangeEditor {
  constructor(matrixEl, opts) {
    this.el = matrixEl;
    this.textEl = opts.textEl;
    this.countEl = opts.countEl;
    this.brushEl = opts.brushEl;
    this.brushValEl = opts.brushValEl;
    // two ranges: weights arrays of 1326
    this.ranges = [new Float32Array(1326), new Float32Array(1326)];
    this.player = 0;
    this.painting = false;
    this.paintValue = 1.0;
    this.buildGrid();
    this.bind();
    this.render();
  }

  get weights() { return this.ranges[this.player]; }

  buildGrid() {
    this.el.innerHTML = '';
    this.cells = [];
    for (let i = 0; i < 13; i++) {
      for (let j = 0; j < 13; j++) {
        const info = cellInfo(i, j);
        const cell = document.createElement('div');
        cell.className = 'cell';
        cell.dataset.i = i;
        cell.dataset.j = j;
        cell.innerHTML = `<div class="fill"></div><div class="tag">${info.label}</div><div class="sub"></div>`;
        this.el.appendChild(cell);
        this.cells.push(cell);
      }
    }
  }

  bind() {
    const brush = () => {
      this.paintValue = parseInt(this.brushEl.value, 10) / 100;
      this.brushValEl.textContent = `${this.brushEl.value}%`;
    };
    this.brushEl.addEventListener('input', brush);
    brush();

    this.el.addEventListener('mousedown', e => {
      const cell = e.target.closest('.cell');
      if (!cell) return;
      e.preventDefault();
      // toggle: if cell already at brush weight, erase; else paint
      const { i, j } = cell.dataset;
      const current = this.cellWeight(+i, +j);
      this.eraseMode = Math.abs(current - this.paintValue) < 1e-4;
      this.painting = true;
      this.paintCell(+i, +j);
    });
    this.el.addEventListener('mouseover', e => {
      if (!this.painting) return;
      const cell = e.target.closest('.cell');
      if (cell) this.paintCell(+cell.dataset.i, +cell.dataset.j);
    });
    window.addEventListener('mouseup', () => {
      if (this.painting) { this.painting = false; this.syncText(); }
    });
  }

  cellWeight(i, j) {
    const combos = cellCombos(cellInfo(i, j));
    let max = 0;
    for (const [a, b] of combos) max = Math.max(max, this.weights[comboIndex(a, b)]);
    return max;
  }

  paintCell(i, j) {
    const combos = cellCombos(cellInfo(i, j));
    const w = this.eraseMode ? 0 : this.paintValue;
    for (const [a, b] of combos) this.weights[comboIndex(a, b)] = w;
    this.renderCell(i, j);
    this.updateCount();
  }

  renderCell(i, j) {
    const cell = this.cells[i * 13 + j];
    const combos = cellCombos(cellInfo(i, j));
    let sum = 0, max = 0;
    for (const [a, b] of combos) {
      const w = this.weights[comboIndex(a, b)];
      sum += w; max = Math.max(max, w);
    }
    const fill = cell.querySelector('.fill');
    const sub = cell.querySelector('.sub');
    fill.style.height = `${max * 100}%`;
    fill.style.opacity = max > 0 ? 0.35 + 0.5 * (sum / combos.length / Math.max(max, 1e-9)) : 0;
    sub.textContent = max > 0 && max < 0.9995 ? Math.round(max * 100) + '' : '';
    cell.classList.toggle('empty', max <= 0);
  }

  render() {
    for (let i = 0; i < 13; i++) for (let j = 0; j < 13; j++) this.renderCell(i, j);
    this.updateCount();
  }

  updateCount() {
    let n = 0;
    for (const w of this.weights) n += w;
    this.countEl.textContent = `${n.toFixed(1)} combos`;
  }

  syncText() {
    this.textEl.value = weightsToText(Array.from(this.weights));
  }

  setPlayer(p) {
    this.player = p;
    this.render();
    this.syncText();
  }

  async applyText() {
    // capture the target: switching the OOP/IP tab while the parse is in
    // flight must not land these weights on the newly selected player
    const player = this.player;
    try {
      const res = await api.parseRange(this.textEl.value);
      this.ranges[player] = Float32Array.from(res.weights);
      this.render();
      toast(`parsed: ${res.combos.toFixed(1)} combos`);
    } catch (e) {
      toast(`range error: ${e.message}`, true);
    }
  }

  setWeightsFromText(text) {
    this.textEl.value = text;
    return this.applyText();
  }

  clear() {
    this.ranges[this.player].fill(0);
    this.render();
    this.syncText();
  }

  fillAll() {
    this.ranges[this.player].fill(1);
    this.render();
    this.syncText();
  }

  // Range text for sending to the server.
  textFor(p) {
    return weightsToText(Array.from(this.ranges[p]));
  }
}
