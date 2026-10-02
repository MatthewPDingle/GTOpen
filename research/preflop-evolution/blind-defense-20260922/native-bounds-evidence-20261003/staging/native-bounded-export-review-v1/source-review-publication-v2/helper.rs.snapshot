//! Prospective research-only output accounting; no poker calculations.
use std::error::Error;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::Path;

/// Kept inside the registered aggregate limit, including a partial-I/O failure.
pub const FAILURE_RESERVE: usize = 256;
const ERROR: &[u8] = b"Research exporter failed\n";
const PANIC: &[u8] = b"Research exporter panicked\n";
const LIMIT_FLAG: &str = "--output-byte-limit=";

/// Optional final limit argument can only tighten this binary's fixed ceiling.
/// Removing this resource argument leaves the original calculation arguments.
pub fn arguments(ceiling: usize) -> Result<(Vec<String>, usize), Box<dyn Error>> {
    let mut args: Vec<String> = std::env::args().skip(1).collect();
    let limit = if let Some(value) = args.last().and_then(|arg| arg.strip_prefix(LIMIT_FLAG)) {
        let limit: usize = value.parse()?;
        args.pop();
        limit
    } else {
        ceiling
    };
    if limit < FAILURE_RESERVE || limit > ceiling {
        return Err("Invalid output byte limit".into());
    }
    Ok((args, limit))
}

/// Serializers must complete before calling this once at the end of a run.
/// File/stdout/stderr lengths are checked together before opening any output.
pub fn emit(
    direct: Option<(&Path, &[u8])>,
    stdout: &[u8],
    stderr: &[u8],
    limit: usize,
) -> Result<(), Box<dyn Error>> {
    let direct_len = direct.map_or(0, |(_, bytes)| bytes.len());
    let complete = direct_len.checked_add(stdout.len())
        .and_then(|bytes| bytes.checked_add(stderr.len()))
        .and_then(|bytes| bytes.checked_add(FAILURE_RESERVE))
        .ok_or("Output byte count overflow")?;
    if complete > limit {
        return Err("Output byte budget exceeded".into());
    }
    if let Some((path, bytes)) = direct {
        // A path appearing since validation must never be overwritten.
        let mut output = OpenOptions::new().write(true).create_new(true).open(path)?;
        output.write_all(bytes)?;
        output.flush()?;
    }
    let mut output = std::io::stdout().lock();
    output.write_all(stdout)?;
    output.flush()?;
    let mut diagnostic = std::io::stderr().lock();
    diagnostic.write_all(stderr)?;
    diagnostic.flush()?;
    Ok(())
}

/// Suppress variable-length Rust error/panic text and backtraces. Each run
/// writes at most one fixed failure message in the already-reserved space.
pub fn entry(run: fn() -> Result<(), Box<dyn Error>>) {
    std::panic::set_hook(Box::new(|_| {}));
    match std::panic::catch_unwind(run) {
        Ok(Ok(())) => {},
        Ok(Err(_)) => {
            let _ = std::io::stderr().lock().write_all(ERROR);
            std::process::exit(1);
        },
        Err(_) => {
            let _ = std::io::stderr().lock().write_all(PANIC);
            std::process::exit(101);
        },
    }
}
