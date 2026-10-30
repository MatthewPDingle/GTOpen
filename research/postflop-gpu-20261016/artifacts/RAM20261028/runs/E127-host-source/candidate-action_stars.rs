//! Private deterministic action-star schedule; immutable original plan/CFV storage.
use super::plan::LevelSpan;

pub(super) struct StarWork {
    pub(super) nodes: Vec<u32>,
    pub(super) regular: Vec<LevelSpan>,
    pub(super) fused: Vec<LevelSpan>,
    pub(super) heads: usize,
    pub(super) children: usize,
}

// A missing schedule means the exact original traversal, including tight budgets.
// `kind` reads the original immutable tree; no new per-node GPU encoding is used.
pub(super) fn build(
    n: usize, levels: usize, blocks: usize, ids: &[u32], spans: &[LevelSpan],
    arity: &[i32], starts: &[u32], children: &[u32], chance_children: &[u32],
    slots: &[u32], kind: impl Fn(usize) -> u8,
) -> Option<StarWork> {
    const NONE: u32 = u32::MAX;
    const MANY: u32 = u32::MAX - 1;
    if n == 0 || n >= MANY as usize || levels == 0 || levels >= NONE as usize
        || spans.len() != levels || arity.len() != n || starts.len() != n
        || slots.len() != n || ids.len() > i32::MAX as usize || blocks == 0 {
        return None;
    }
    let mut depth = vec![NONE; n];
    for (level, span) in spans.iter().enumerate() {
        let end = (span.start as usize).checked_add(span.count as usize)?;
        let part = ids.get(span.start as usize..end)?;
        for &node in part {
            let i = node as usize;
            if i >= n || depth[i] != NONE || kind(i) != 0 || arity[i] <= 0
                || (slots[i] as usize) >= blocks { return None; }
            depth[i] = level as u32;
        }
    }
    let kids = |node: usize| -> Option<&[u32]> {
        let start = starts[node] as usize;
        let end = start.checked_add(usize::try_from(arity[node]).ok()?)?;
        children.get(start..end)
    };
    let mut owner = vec![NONE; n];
    for &node in ids {
        for &child in kids(node as usize)? {
            let c = child as usize;
            if c >= n || slots[c] as usize >= blocks { return None; }
            if kind(c) == 0 {
                if depth[c] != depth[node as usize].checked_add(1)? { return None; }
                owner[c] = if owner[c] == NONE { node } else { MANY };
            }
        }
    }
    let mut chance_ref = vec![false; n];
    for &child in chance_children {
        if child == NONE { continue; }
        if child as usize >= n { return None; }
        chance_ref[child as usize] = true;
    }
    let mut safe = vec![false; n];
    let mut row_owner = vec![NONE; blocks];
    let mut stamp = vec![0u32; blocks];
    for level in 0..levels.saturating_sub(1) {
        let epoch = (level + 1) as u32;
        let next = spans[level + 1];
        for &reader in &ids[next.start as usize..next.start as usize + next.count as usize] {
            for &child in kids(reader as usize)? {
                let row = slots[child as usize] as usize;
                let group = owner[reader as usize];
                if stamp[row] != epoch { stamp[row] = epoch; row_owner[row] = group; }
                else if row_owner[row] != group { row_owner[row] = MANY; }
            }
        }
        let span = spans[level];
        for &parent in &ids[span.start as usize..span.start as usize + span.count as usize] {
            let p = parent as usize;
            let mut count = 0;
            let mut valid = true;
            for &child in kids(p)? {
                let c = child as usize;
                match kind(c) {
                    0 => {
                        count += 1;
                        valid &= owner[c] == parent && !chance_ref[c];
                    }
                    2 | 3 => {}
                    _ => valid = false,
                }
            }
            let row = slots[p] as usize;
            safe[p] = valid && count > 0 && (stamp[row] != epoch || row_owner[row] == parent);
        }
    }
    let mut taken = vec![false; n];
    let mut head = vec![false; n];
    let mut eligible = Vec::new();
    let (mut heads, mut removed_children) = (0usize, 0usize);
    for level in (0..levels.saturating_sub(1)).rev() {
        eligible.clear();
        let span = spans[level];
        eligible.extend(ids[span.start as usize..span.start as usize + span.count as usize]
            .iter().copied().filter(|&i| safe[i as usize]));
        eligible.sort_unstable();
        for &parent in &eligible {
            let p = parent as usize;
            if taken[p] || kids(p)?.iter().any(|&c| kind(c as usize) == 0 && taken[c as usize]) { continue; }
            head[p] = true;
            taken[p] = true;
            heads += 1;
            for &child in kids(p)? {
                let c = child as usize;
                if kind(c) == 0 { taken[c] = true; removed_children += 1; }
            }
        }
    }
    if heads == 0 { return None; }
    let mut nodes = Vec::with_capacity(ids.len().checked_sub(removed_children)?);
    let mut regular = Vec::with_capacity(levels);
    let mut fused = Vec::with_capacity(levels);
    for level in 0..levels {
        let start = nodes.len() as u32;
        let span = spans[level];
        nodes.extend(ids[span.start as usize..span.start as usize + span.count as usize]
            .iter().copied().filter(|&i| !taken[i as usize]));
        regular.push(LevelSpan { start, count: nodes.len() as u32 - start });
        let start = nodes.len() as u32;
        if level > 0 {
            let parent_span = spans[level - 1];
            let mut part: Vec<u32> = ids[parent_span.start as usize..parent_span.start as usize + parent_span.count as usize]
                .iter().copied().filter(|&i| head[i as usize]).collect();
            part.sort_unstable();
            nodes.extend(part);
        }
        fused.push(LevelSpan { start, count: nodes.len() as u32 - start });
    }
    debug_assert_eq!(nodes.len(), ids.len() - removed_children);
    Some(StarWork { nodes, regular, fused, heads, children: removed_children })
}
