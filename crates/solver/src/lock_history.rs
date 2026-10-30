//! Undo / redo for node locks, and freezing the line that leads to a lock.
//!
//! Lock edits made from the UI (point locks, unlocks, profile compiles) run
//! inside `Solver::record_lock_edit`, which journals the value every touched
//! node had BEFORE the edit. On commit the journal becomes one history entry
//! holding both sides of each change, so undo restores the old locks
//! exactly. Replaying the old request instead would rebuild the lock from the
//! current solve, which a re-solve may have moved. A failed edit is rolled
//! back, so an edit either lands whole or not at all.
//!
//! History lives with the session only (saves don't carry it) and is bounded
//! by entry count and bytes. Lock mutations outside a recorded edit (report
//! workers, tests) are not journaled; undo checks that every node it restores
//! still holds the value the edit left and refuses (clearing the history)
//! when something else changed it in between.

use crate::cards::card_to_string;
use crate::cfr::Solver;
use crate::query::{LockMode, PathStep, PROFILE_LABEL};
use crate::tree::KIND_ACTION;
use serde::Serialize;
use std::collections::HashMap;

/// A node's lock state: (sigma, label), or None when unlocked.
type LockValue = Option<(Vec<f32>, String)>;

/// Undo + redo entries kept at most.
const MAX_EDITS: usize = 100;
/// Bytes of lock data history may hold. A whole-tree profile compile on a big
/// tree can exceed this on its own; it then lands without an undo entry and
/// the older entries are dropped (they would no longer replay in order).
const MAX_BYTES: usize = 256 << 20;

struct LockEdit {
    label: String,
    /// (node, before, after), sorted by node.
    changes: Vec<(u32, LockValue, LockValue)>,
    bytes: usize,
}

#[derive(Default)]
pub struct LockHistory {
    undo: Vec<LockEdit>,
    redo: Vec<LockEdit>,
    /// Open edit: each touched node's value before its first change.
    journal: Option<HashMap<u32, LockValue>>,
}

impl LockHistory {
    fn bytes(&self) -> usize {
        self.undo.iter().chain(&self.redo).map(|e| e.bytes).sum()
    }

    fn clear(&mut self) {
        self.undo.clear();
        self.redo.clear();
    }

    /// Drop the oldest undo entries until both bounds hold.
    fn trim(&mut self) {
        while !self.undo.is_empty()
            && (self.undo.len() + self.redo.len() > MAX_EDITS || self.bytes() > MAX_BYTES)
        {
            self.undo.remove(0);
        }
    }
}

/// What the UI needs to label its undo / redo controls.
#[derive(Debug, Clone, Serialize)]
pub struct LockHistoryView {
    /// Edit labels, most recent first.
    pub undo: Vec<String>,
    /// Undone edits that redo would re-apply, next first.
    pub redo: Vec<String>,
    /// Players (0 = OOP, 1 = IP) whose tree holds profile-generated locks.
    pub profile_players: Vec<usize>,
    /// Locked nodes in total (manual and profile).
    pub locked_nodes: usize,
}

fn value_bytes(v: &LockValue) -> usize {
    v.as_ref().map_or(0, |(s, l)| s.len() * 4 + l.len())
}

impl Solver {
    /// Insert or replace a lock. Every lock mutation goes through this or
    /// `take_lock` so an open edit can journal it.
    pub(crate) fn put_lock(&mut self, idx: u32, sigma: Vec<f32>, label: String) {
        self.journal_lock(idx);
        self.locks.insert(idx, sigma);
        self.lock_labels.insert(idx, label);
    }

    /// Remove a lock; true if the node was locked.
    pub(crate) fn take_lock(&mut self, idx: u32) -> bool {
        self.journal_lock(idx);
        self.lock_labels.remove(&idx);
        self.locks.remove(&idx).is_some()
    }

    fn journal_lock(&mut self, idx: u32) {
        if self.lock_history.journal.as_ref().is_some_and(|j| !j.contains_key(&idx)) {
            let before = self.lock_value(idx);
            self.lock_history.journal.as_mut().unwrap().insert(idx, before);
        }
    }

    fn lock_value(&self, idx: u32) -> LockValue {
        self.locks
            .get(&idx)
            .map(|s| (s.clone(), self.lock_labels.get(&idx).cloned().unwrap_or_default()))
    }

    /// Whether node `idx` holds `v` right now (compares without cloning).
    fn lock_holds(&self, idx: u32, v: &LockValue) -> bool {
        match v {
            None => !self.locks.contains_key(&idx),
            Some((sigma, label)) => {
                self.locks.get(&idx) == Some(sigma)
                    && self.lock_labels.get(&idx).map_or("", String::as_str) == label
            }
        }
    }

    /// Set a node's lock state directly, bypassing the journal.
    fn restore_lock(&mut self, idx: u32, v: LockValue) {
        match v {
            Some((sigma, label)) => {
                self.locks.insert(idx, sigma);
                self.lock_labels.insert(idx, label);
            }
            None => {
                self.locks.remove(&idx);
                self.lock_labels.remove(&idx);
            }
        }
    }

    /// Run `edit` as one undoable lock edit. The closure returns its result
    /// and the label the history shows for it. An edit that changes nothing
    /// adds no entry; one that fails is rolled back. Nested calls fold into
    /// the outer edit.
    pub fn record_lock_edit<R>(
        &mut self,
        edit: impl FnOnce(&mut Solver) -> Result<(R, String), String>,
    ) -> Result<R, String> {
        if self.lock_history.journal.is_some() {
            return edit(self).map(|(r, _)| r);
        }
        self.lock_history.journal = Some(HashMap::new());
        let out = edit(self);
        let journal = self.lock_history.journal.take().unwrap_or_default();
        let (result, label) = match out {
            Ok(x) => x,
            Err(e) => {
                if !journal.is_empty() {
                    for (idx, before) in journal {
                        self.restore_lock(idx, before);
                    }
                    self.mark_sym_dirty();
                }
                return Err(e);
            }
        };
        let mut changes: Vec<(u32, LockValue, LockValue)> = journal
            .into_iter()
            .filter(|(idx, before)| !self.lock_holds(*idx, before))
            .map(|(idx, before)| (idx, before, self.lock_value(idx)))
            .collect();
        if changes.is_empty() {
            return Ok(result);
        }
        changes.sort_unstable_by_key(|c| c.0);
        let bytes = label.len()
            + changes.iter().map(|(_, b, a)| value_bytes(b) + value_bytes(a)).sum::<usize>();
        let h = &mut self.lock_history;
        h.redo.clear();
        if bytes > MAX_BYTES {
            h.undo.clear();
        } else {
            h.undo.push(LockEdit { label, changes, bytes });
            h.trim();
        }
        Ok(result)
    }

    /// Undo the most recent recorded lock edit. Ok(None) when there is
    /// nothing to undo; Ok(Some(label)) names the edit undone.
    pub fn undo_lock_edit(&mut self) -> Result<Option<String>, String> {
        self.step_history(true)
    }

    /// Re-apply the most recently undone lock edit.
    pub fn redo_lock_edit(&mut self) -> Result<Option<String>, String> {
        self.step_history(false)
    }

    fn step_history(&mut self, undo: bool) -> Result<Option<String>, String> {
        let h = &mut self.lock_history;
        let Some(edit) = (if undo { h.undo.pop() } else { h.redo.pop() }) else {
            return Ok(None);
        };
        // the state this step starts from: what the edit left (undo) or
        // what it found (redo)
        let current_ok = edit.changes.iter().all(|(idx, before, after)| {
            self.lock_holds(*idx, if undo { after } else { before })
        });
        if !current_ok {
            self.lock_history.clear();
            return Err("locks changed outside the edit history since this edit; \
                        the history has been cleared"
                .to_string());
        }
        for (idx, before, after) in &edit.changes {
            self.restore_lock(*idx, if undo { before.clone() } else { after.clone() });
        }
        self.mark_sym_dirty();
        let label = edit.label.clone();
        let h = &mut self.lock_history;
        if undo { h.redo.push(edit) } else { h.undo.push(edit) }
        Ok(Some(label))
    }

    pub fn lock_history(&self) -> LockHistoryView {
        let mut profile = [false; 2];
        for (idx, label) in &self.lock_labels {
            if label.starts_with(PROFILE_LABEL) {
                profile[self.spot.tree.nodes[*idx as usize].player as usize] = true;
            }
        }
        let h = &self.lock_history;
        LockHistoryView {
            undo: h.undo.iter().rev().map(|e| e.label.clone()).collect(),
            redo: h.redo.iter().rev().map(|e| e.label.clone()).collect(),
            profile_players: (0..2).filter(|&p| profile[p]).collect(),
            locked_nodes: self.locks.len(),
        }
    }

    /// Readable description of a path, in the style the UI labels locks
    /// with: the flop, then each action label or dealt card ("Ks7d2c Check >
    /// Bet 3.3 (33%)"); "<flop> root" for the empty path.
    pub fn path_description(&self, path: &[PathStep]) -> Result<String, String> {
        let canon = self.canonical_path(path);
        let board: String = self.spot.board.iter().map(|&c| card_to_string(c)).collect();
        let mut parts = Vec::with_capacity(path.len());
        for (i, step) in path.iter().enumerate() {
            match step {
                PathStep::Card { card } => parts.push(card.clone()),
                PathStep::Action { index } => {
                    let node = self.walk_path(&canon[..i])?.node_idx;
                    let label = self
                        .action_views(node)
                        .get(*index)
                        .map(|a| a.label.clone())
                        .ok_or_else(|| format!("action index {index} out of range"))?;
                    parts.push(label);
                }
            }
        }
        Ok(if parts.is_empty() {
            format!("{board} root")
        } else {
            format!("{board} {}", parts.join(" > "))
        })
    }

    /// Lock the node at `path`; with `freeze_path`, also freeze (lock as
    /// solved) every earlier decision on the line that is not locked yet, so
    /// a re-solve can't shift the play leading up to the lock. Existing locks
    /// on the line are kept. Returns how many earlier decisions were frozen.
    /// Call inside `record_lock_edit` to make it one undoable edit.
    pub fn lock_node_on_line(
        &mut self,
        path: &[PathStep],
        mode: LockMode,
        label: String,
        freeze_path: bool,
    ) -> Result<usize, String> {
        // the target first: a refused lock must not leave frozen ancestors
        // behind when this runs outside a recorded edit
        self.lock_node(path, mode, label.clone())?;
        if !freeze_path {
            return Ok(0);
        }
        let mut frozen = 0;
        for (i, step) in path.iter().enumerate() {
            if !matches!(step, PathStep::Action { .. }) {
                continue;
            }
            let prefix = &path[..i];
            let walk = self.walk_path(&self.canonical_path(prefix))?;
            debug_assert_eq!(self.spot.tree.nodes[walk.node_idx as usize].kind, KIND_ACTION);
            if self.locks.contains_key(&walk.node_idx) {
                continue;
            }
            let desc = self.path_description(prefix)?;
            self.lock_node(prefix, LockMode::Freeze, format!("{desc} (frozen on the line to {label})"))?;
            frozen += 1;
        }
        Ok(frozen)
    }
}
