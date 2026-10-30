//! Thread-local pool of f32 scratch buffers. CFR traversal needs a handful of
//! short-lived per-node vectors on every node visit across many threads;
//! pooling them removes the per-visit malloc/free entirely.

use std::cell::RefCell;

const MAX_POOLED: usize = 64;

thread_local! {
    static POOL: RefCell<Vec<Vec<f32>>> = const { RefCell::new(Vec::new()) };
}

/// A pooled f32 buffer. Returns to the dropping thread's pool on drop, so
/// buffers may migrate between rayon workers without issue.
///
/// Pooled vectors only ever grow (high-water mark) and growth is
/// zero-initialized, so handing out `for_overwrite` views of stale contents
/// is safe — just not zeroed.
pub struct Buf {
    v: Vec<f32>,
    len: usize,
}

impl Buf {
    #[inline]
    fn acquire(len: usize) -> Vec<f32> {
        let mut v = POOL
            .with(|p| p.borrow_mut().pop())
            .unwrap_or_default();
        if v.len() < len {
            v.resize(len, 0.0);
        }
        v
    }

    #[inline]
    pub fn zeroed(len: usize) -> Buf {
        Buf::filled(len, 0.0)
    }

    #[inline]
    pub fn filled(len: usize, value: f32) -> Buf {
        let mut v = Buf::acquire(len);
        v[..len].fill(value);
        Buf { v, len }
    }

    /// Contents are arbitrary (stale) — caller must fully overwrite before
    /// reading.
    #[inline]
    pub fn for_overwrite(len: usize) -> Buf {
        Buf {
            v: Buf::acquire(len),
            len,
        }
    }
}

impl Drop for Buf {
    fn drop(&mut self) {
        let v = std::mem::take(&mut self.v);
        POOL.with(|p| {
            let mut p = p.borrow_mut();
            if p.len() < MAX_POOLED {
                p.push(v);
            }
        });
    }
}

impl std::ops::Deref for Buf {
    type Target = [f32];
    #[inline(always)]
    fn deref(&self) -> &[f32] {
        &self.v[..self.len]
    }
}

impl std::ops::DerefMut for Buf {
    #[inline(always)]
    fn deref_mut(&mut self) -> &mut [f32] {
        &mut self.v[..self.len]
    }
}
