//! The app's version, read from the change log.
//!
//! The newest entry of `CHANGELOG.md` at the repository root IS the app's
//! version and release date; no other file holds a version number. The file
//! is read on every request, like `web/` (the server runs from the repository
//! root), so an update that was only pulled shows its new version at the next
//! page load, with no rebuild.

use std::path::{Path, PathBuf};

use axum::Json;

/// What this server can do for the page, as a number. The page and the change
/// log are read from disk, so a pull alone updates them while a server that
/// was not rebuilt and restarted keeps running old code. The page knows the
/// level it needs (`NEEDS_SERVER_LEVEL` in web/js/version.js) and asks for a
/// restart when the server reports less. Raise both together whenever the
/// page starts to need something new from the server.
pub const SERVER_LEVEL: u32 = 8;

/// Where the app's change log link points.
pub const CHANGELOG_URL: &str = "https://github.com/MatthewPDingle/GTOpen/blob/master/CHANGELOG.md";

#[derive(Debug, PartialEq, Eq)]
pub struct Release {
    pub version: String,
    /// Release date, `YYYY-MM-DD`.
    pub date: String,
}

fn parse_version(text: &str) -> Option<[u32; 3]> {
    let mut parts = text.split('.');
    let mut out = [0u32; 3];
    for slot in &mut out {
        let part = parts.next()?;
        if part.is_empty() || part.len() > 6 || !part.bytes().all(|b| b.is_ascii_digit()) {
            return None;
        }
        *slot = part.parse().ok()?;
    }
    parts.next().is_none().then_some(out)
}

fn valid_date(text: &str) -> bool {
    let b = text.as_bytes();
    if b.len() != 10 || b[4] != b'-' || b[7] != b'-' {
        return false;
    }
    let num = |range: std::ops::Range<usize>| text[range].parse::<u32>().ok();
    let digits = b.iter().enumerate().all(|(i, c)| i == 4 || i == 7 || c.is_ascii_digit());
    digits
        && matches!(num(0..4), Some(2000..=2999))
        && matches!(num(5..7), Some(1..=12))
        && matches!(num(8..10), Some(1..=31))
}

/// A release heading: `## 1.2.3 - 2026-11-18`.
fn release_heading(line: &str) -> Option<Release> {
    let (version, date) = line.strip_prefix("## ")?.trim().split_once(" - ")?;
    (parse_version(version).is_some() && valid_date(date))
        .then(|| Release { version: version.to_string(), date: date.to_string() })
}

/// Every release in the change log, newest first (file order).
#[cfg(test)]
fn releases(changelog: &str) -> Vec<Release> {
    changelog.lines().filter_map(release_heading).collect()
}

/// The newest release: the first release heading in the file.
pub fn latest_release(changelog: &str) -> Option<Release> {
    changelog.lines().find_map(release_heading)
}

fn resolve(base: &Path, path: &str) -> PathBuf {
    let path = Path::new(path.trim());
    if path.is_absolute() { path.to_path_buf() } else { base.join(path) }
}

/// The commit a checkout is on, shortened, read straight from its git files
/// (no `git` program needed). `None` outside a checkout.
pub fn checkout_commit(repo: &Path) -> Option<String> {
    let dot_git = repo.join(".git");
    // A linked worktree's `.git` is a file that names its own git directory.
    let git_dir = if dot_git.is_dir() {
        dot_git
    } else {
        let pointer = std::fs::read_to_string(&dot_git).ok()?;
        resolve(repo, pointer.trim().strip_prefix("gitdir:")?)
    };
    let head = std::fs::read_to_string(git_dir.join("HEAD")).ok()?;
    let head = head.trim();
    let full = match head.strip_prefix("ref:") {
        None => head.to_string(),
        Some(reference) => {
            let reference = reference.trim();
            // ...and keeps its branches in the main checkout's git directory.
            let common = std::fs::read_to_string(git_dir.join("commondir"))
                .map(|dir| resolve(&git_dir, &dir))
                .unwrap_or_else(|_| git_dir.clone());
            match std::fs::read_to_string(common.join(reference)) {
                Ok(hash) => hash.trim().to_string(),
                Err(_) => std::fs::read_to_string(common.join("packed-refs"))
                    .ok()?
                    .lines()
                    .find_map(|line| {
                        let (hash, name) = line.split_once(' ')?;
                        (name.trim() == reference).then(|| hash.to_string())
                    })?,
            }
        }
    };
    (full.len() >= 9 && full.bytes().all(|b| b.is_ascii_hexdigit())).then(|| full[..9].to_string())
}

/// `GET /api/version`: `{version, date, commit, changelog_url, server_level}`.
/// `version` and `date` are null when no change log is found, `commit`
/// outside a git checkout. `server_level` is this program's own, not the
/// checkout's.
pub fn version_info(repo: &Path) -> serde_json::Value {
    let release = std::fs::read_to_string(repo.join("CHANGELOG.md"))
        .ok()
        .and_then(|text| latest_release(&text));
    serde_json::json!({
        "version": release.as_ref().map(|r| r.version.as_str()),
        "date": release.as_ref().map(|r| r.date.as_str()),
        "commit": checkout_commit(repo),
        "changelog_url": CHANGELOG_URL,
        "server_level": SERVER_LEVEL,
    })
}

pub async fn get_version() -> Json<serde_json::Value> {
    Json(version_info(Path::new(".")))
}

#[cfg(test)]
mod tests {
    use super::*;

    fn repo_root() -> PathBuf {
        Path::new(env!("CARGO_MANIFEST_DIR")).join("../..")
    }

    #[test]
    fn the_first_release_heading_is_the_version() {
        let text = "# Change log\n\nIntro.\n\n## 1.2.0 - 2026-12-01\n\n- New.\n\n## 1.1.9 - 2026-11-30\n\n## Before version numbers\n";
        assert_eq!(
            latest_release(text),
            Some(Release { version: "1.2.0".into(), date: "2026-12-01".into() })
        );
        assert_eq!(releases(text).len(), 2);
        assert_eq!(latest_release("# Change log\n\n## Before version numbers\n"), None);
    }

    #[test]
    fn malformed_headings_are_not_releases() {
        for line in [
            "## 1.2 - 2026-12-01",
            "## v1.2.0 - 2026-12-01",
            "## 1.2.0 – 2026-12-01",
            "## 1.2.0 - 2026-13-01",
            "## 1.2.0 - 1 Dec 2026",
            "## 1.2.0",
            "### 1.2.0 - 2026-12-01",
        ] {
            assert_eq!(release_heading(line), None, "{line}");
        }
    }

    /// Guards the next version bump: a heading that is meant as a release
    /// but does not parse would silently leave the app on the old version.
    #[test]
    fn the_repository_change_log_is_well_formed() {
        let text = std::fs::read_to_string(repo_root().join("CHANGELOG.md")).unwrap();
        for line in text.lines().filter(|l| l.starts_with("## ")) {
            let looks_like_release = line[3..].trim_start().starts_with(|c: char| c.is_ascii_digit() || c == 'v');
            assert!(
                !looks_like_release || release_heading(line).is_some(),
                "write release headings as `## 1.2.3 - YYYY-MM-DD`, got `{line}`"
            );
        }
        let all = releases(&text);
        assert!(!all.is_empty(), "CHANGELOG.md needs a release heading");
        for pair in all.windows(2) {
            let (newer, older) = (&pair[0], &pair[1]);
            assert!(
                parse_version(&newer.version) > parse_version(&older.version),
                "versions must go down the file: {} is above {}",
                newer.version, older.version
            );
            assert!(newer.date >= older.date, "{} is dated before {}", newer.version, older.version);
        }
    }

    #[test]
    fn reads_the_commit_of_a_checkout_and_of_a_linked_worktree() {
        let dir = std::env::temp_dir().join(format!("gtopen-version-test-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&dir);
        let main = dir.join("main");
        let git = main.join(".git");
        std::fs::create_dir_all(git.join("refs/heads")).unwrap();
        let a = "0123456789abcdef0123456789abcdef01234567";
        let b = "fedcba9876543210fedcba9876543210fedcba98";
        assert_eq!(checkout_commit(&main), None);
        // on a branch, loose ref
        std::fs::write(git.join("HEAD"), "ref: refs/heads/master\n").unwrap();
        std::fs::write(git.join("refs/heads/master"), format!("{a}\n")).unwrap();
        assert_eq!(checkout_commit(&main).as_deref(), Some("012345678"));
        // on a branch, packed ref
        std::fs::remove_file(git.join("refs/heads/master")).unwrap();
        std::fs::write(git.join("packed-refs"), format!("# pack-refs with: peeled\n{b} refs/heads/other\n{a} refs/heads/master\n")).unwrap();
        assert_eq!(checkout_commit(&main).as_deref(), Some("012345678"));
        // detached
        std::fs::write(git.join("HEAD"), format!("{b}\n")).unwrap();
        assert_eq!(checkout_commit(&main).as_deref(), Some("fedcba987"));
        // a linked worktree on a branch kept in the main git directory
        let tree = dir.join("tree");
        let tree_git = git.join("worktrees/tree");
        std::fs::create_dir_all(&tree).unwrap();
        std::fs::create_dir_all(&tree_git).unwrap();
        std::fs::write(tree.join(".git"), format!("gitdir: {}\n", tree_git.display())).unwrap();
        std::fs::write(tree_git.join("HEAD"), "ref: refs/heads/other\n").unwrap();
        std::fs::write(tree_git.join("commondir"), "../..\n").unwrap();
        assert_eq!(checkout_commit(&tree).as_deref(), Some("fedcba987"));
        // no change log there: version and date are null, the link stays
        let info = version_info(&tree);
        assert!(info["version"].is_null() && info["date"].is_null());
        assert_eq!(info["commit"], "fedcba987");
        assert_eq!(info["changelog_url"], CHANGELOG_URL);
        std::fs::remove_dir_all(&dir).unwrap();
    }

    #[test]
    fn version_info_reports_the_repository_change_log() {
        let text = std::fs::read_to_string(repo_root().join("CHANGELOG.md")).unwrap();
        let newest = latest_release(&text).unwrap();
        let info = version_info(&repo_root());
        assert_eq!(info["version"], newest.version.as_str());
        assert_eq!(info["date"], newest.date.as_str());
    }

    /// The page asks for a restart when the server's level is below the one
    /// it needs, so the two numbers move together.
    #[test]
    fn the_page_needs_exactly_this_server_level() {
        let js = std::fs::read_to_string(repo_root().join("web/js/version.js")).unwrap();
        let needs = js
            .lines()
            .find_map(|line| line.strip_prefix("export const NEEDS_SERVER_LEVEL = "))
            .and_then(|rest| rest.trim_end_matches(';').trim().parse::<u32>().ok())
            .expect("web/js/version.js needs `export const NEEDS_SERVER_LEVEL = N;`");
        assert_eq!(needs, SERVER_LEVEL, "raise SERVER_LEVEL and NEEDS_SERVER_LEVEL together");
        assert_eq!(version_info(&repo_root())["server_level"], SERVER_LEVEL);
    }
}
