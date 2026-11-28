//! One GPU solve at a time per card, across processes.
//!
//! A data generator and a validator on the same machine are separate
//! `solve-cli` processes. Each sizes its solve from the card's free memory
//! just before it allocates, so two that start close together both see the
//! card as free, both allocate, and together they overflow it. On Windows
//! the overflow spills into shared system memory and both solves crawl for
//! as long as both are alive (an hour was seen with two 20 GB trees on a
//! 32 GB card). Taking turns costs nothing: two solves that share a card
//! only time-slice it anyway.
//!
//! The turn is an advisory lock on a small file that every `solve-cli` on
//! the machine can open. The operating system releases it when the process
//! ends, however it ends, so a crashed solve never leaves the card locked.
//! `GTOPEN_GPU_TURN=0` switches it off; any other value is the lock file
//! to use.

use std::{
    fs::{File, OpenOptions},
    path::{Path, PathBuf},
};

/// Holds this process's turn on the card until dropped.
pub struct GpuTurn {
    file: Option<File>,
}

impl GpuTurn {
    /// A turn that excludes nobody (the lock is switched off or its file
    /// could not be opened).
    fn none() -> GpuTurn {
        GpuTurn { file: None }
    }

    /// True when a lock is held (false: switched off or unavailable).
    pub fn held(&self) -> bool {
        self.file.is_some()
    }
}

impl Drop for GpuTurn {
    fn drop(&mut self) {
        if let Some(f) = self.file.take() {
            let _ = f.unlock();
        }
    }
}

/// The lock file for the card this process solves on: one per value of
/// `CUDA_VISIBLE_DEVICES`, so generators on different cards do not wait
/// for each other. `None` when the lock is switched off.
pub fn default_path() -> Option<PathBuf> {
    match std::env::var("GTOPEN_GPU_TURN") {
        Ok(v) if v == "0" => return None,
        Ok(v) if !v.is_empty() => return Some(PathBuf::from(v)),
        _ => {}
    }
    let card: String = std::env::var("CUDA_VISIBLE_DEVICES")
        .unwrap_or_default()
        .chars()
        .filter(|c| c.is_ascii_alphanumeric() || *c == '-')
        .take(40)
        .collect();
    let card = if card.is_empty() {
        "0".to_string()
    } else {
        card
    };
    Some(shared_dir().join(format!("gtopen-gpu-{card}.lock")))
}

/// A folder every user of the machine can reach: an elevated validator and
/// a plain generator must open the same file.
fn shared_dir() -> PathBuf {
    if cfg!(windows) {
        if let Some(dir) = std::env::var_os("ProgramData").filter(|v| !v.is_empty()) {
            return PathBuf::from(dir);
        }
    }
    std::env::temp_dir()
}

/// Wait for this process's turn on the card. Never fails: when the lock
/// file cannot be opened or locked the solve goes ahead without a turn, as
/// it did before there were turns.
pub fn take() -> GpuTurn {
    match default_path() {
        Some(path) => take_at(&path, |p| {
            eprintln!(
                "  waiting for the GPU: another GTOpen solve has it ({})",
                p.display()
            )
        }),
        None => GpuTurn::none(),
    }
}

/// `take` on a given lock file; `waiting` is called once if the lock is
/// taken by someone else and this call has to wait.
pub fn take_at(path: &Path, waiting: impl FnOnce(&Path)) -> GpuTurn {
    // Another user may have made the file, and then it may only be readable
    // here: a lock needs no more than that.
    let file = OpenOptions::new()
        .read(true)
        .write(true)
        .create(true)
        .truncate(false)
        .open(path)
        .or_else(|_| File::open(path));
    let Ok(file) = file else {
        return GpuTurn::none();
    };
    match file.try_lock() {
        Ok(()) => return GpuTurn { file: Some(file) },
        Err(std::fs::TryLockError::WouldBlock) => waiting(path),
        Err(std::fs::TryLockError::Error(_)) => return GpuTurn::none(),
    }
    match file.lock() {
        Ok(()) => GpuTurn { file: Some(file) },
        Err(_) => GpuTurn::none(),
    }
}

#[cfg(test)]
mod tests {
    use std::{
        sync::{
            atomic::{AtomicBool, AtomicU32, Ordering},
            Arc,
        },
        time::Duration,
    };

    use super::*;

    fn lock_file(name: &str) -> PathBuf {
        let dir = std::env::temp_dir().join(format!("gtopen-gpu-turn-test-{}", std::process::id()));
        std::fs::create_dir_all(&dir).unwrap();
        dir.join(name)
    }

    #[test]
    fn a_second_solve_waits_until_the_first_lets_go() {
        let path = lock_file("waits.lock");
        let first = take_at(&path, |_| panic!("nobody else holds it yet"));
        assert!(first.held());

        let got = Arc::new(AtomicBool::new(false));
        let told = Arc::new(AtomicBool::new(false));
        let (g, t, p) = (got.clone(), told.clone(), path.clone());
        let second = std::thread::spawn(move || {
            let turn = take_at(&p, |_| t.store(true, Ordering::SeqCst));
            g.store(true, Ordering::SeqCst);
            turn.held()
        });
        std::thread::sleep(Duration::from_millis(300));
        assert!(
            told.load(Ordering::SeqCst),
            "the second solve says it is waiting"
        );
        assert!(
            !got.load(Ordering::SeqCst),
            "and does not start while the first holds the card"
        );

        drop(first);
        assert!(
            second.join().unwrap(),
            "it gets its turn once the first is done"
        );
        assert!(got.load(Ordering::SeqCst));
    }

    #[test]
    fn solves_never_overlap() {
        let path = lock_file("overlap.lock");
        let inside = Arc::new(AtomicU32::new(0));
        let workers: Vec<_> = (0..4)
            .map(|_| {
                let (path, inside) = (path.clone(), inside.clone());
                std::thread::spawn(move || {
                    for _ in 0..20 {
                        let turn = take_at(&path, |_| {});
                        assert!(turn.held());
                        assert_eq!(
                            inside.fetch_add(1, Ordering::SeqCst),
                            0,
                            "two solves held the card at once"
                        );
                        std::thread::sleep(Duration::from_millis(2));
                        inside.fetch_sub(1, Ordering::SeqCst);
                    }
                })
            })
            .collect();
        for w in workers {
            w.join().unwrap();
        }
    }

    #[test]
    fn a_lock_file_that_cannot_be_opened_does_not_stop_the_solve() {
        let path = lock_file("no-such-folder").join("deeper").join("x.lock");
        let turn = take_at(&path, |_| panic!("nothing to wait for"));
        assert!(!turn.held());
    }

    #[test]
    fn a_read_only_lock_file_still_gives_turns() {
        let path = lock_file("readonly.lock");
        std::fs::write(&path, b"").unwrap();
        let mut perms = std::fs::metadata(&path).unwrap().permissions();
        perms.set_readonly(true);
        std::fs::set_permissions(&path, perms).unwrap();
        let first = take_at(&path, |_| panic!("nobody else holds it yet"));
        assert!(first.held());
        let waited = AtomicBool::new(false);
        let file = File::open(&path).unwrap();
        assert!(matches!(
            file.try_lock(),
            Err(std::fs::TryLockError::WouldBlock)
        ));
        drop(first);
        let second = take_at(&path, |_| waited.store(true, Ordering::SeqCst));
        assert!(second.held() && !waited.load(Ordering::SeqCst));
    }
}
