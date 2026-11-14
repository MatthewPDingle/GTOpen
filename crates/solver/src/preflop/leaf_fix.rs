//! Corrections from a file, added to the leaf net's output at heads-up flop
//! leaves (a research setting, off by default).
//!
//! The leaf net prices a leaf from the two ranges, the pot, the stack and
//! the rake. Exact flop solves of one game's own leaves say how far off it
//! is there, and a preflop solve of that game can then be run with the
//! difference added back ("refine this game"). The same setting runs a
//! solve under a change of known size, to see how far the ranges move for a
//! given error in the values.
//!
//! Env PREFLOP_LEAF_FIX names a JSON file, read when a game with learned
//! leaves is built or loaded:
//!
//! ```json
//! {"format": "gtopen-leaf-fix", "version": 1, "note": "free text",
//!  "entries": [
//!    {"oop": 0.002, "ip": -0.002},
//!    {"pot_type": "srp", "ip": [169 numbers]},
//!    {"line": "CO Fold | BTN Raise 2.5 | SB Fold | BB Call 2.5", "oop": [169 numbers], "ip": [169 numbers]}
//!  ]}
//! ```
//!
//! - An entry with "line" is for one leaf: the action labels from the root,
//!   folds included, joined with " | " (`datagen::line_key`, the name leaf
//!   exports use). An entry with "pot_type" (limped, srp, 3bet, 4bet) is for
//!   every learned leaf of that pot type. An entry with neither is for every
//!   learned leaf. At most one entry of each kind per leaf; the entries
//!   that fit a leaf add up.
//! - "oop" and "ip" are added to the net's output for the out-of-position
//!   and the in-position player: one number for every class, or 169 numbers
//!   in the class order of equity.rs. They are fractions of the pot (0.01 is
//!   1% of the pot), like the net's own output. A missing side is zero.
//! - A line that is not a heads-up flop leaf with chips behind in the game
//!   being built is an error, and so is any key this does not know: a typo
//!   must not run a long solve with the correction silently missing.
//!
//! The sum is then held to what a hand can win or lose at the leaf, and the
//! pin and the blocking of leaf_total.rs apply after it, as they do to the
//! net's output alone. The corrections are part of the values a solve is
//! measured against, like the net's output. A save does not keep them.
use super::equity::NUM_CLASSES;
use super::leafnet::POT_TYPES;

/// Largest correction a file may carry, as a fraction of the pot. The nets'
/// errors are a few percent of the pot at most; a file in percent instead of
/// fractions, or in bb, shows up here.
pub const MAX_FIX: f32 = 0.5;

/// Corrections for one leaf or one kind of leaf: out of position 169, then in position 169.
type Both = Box<[f32]>;

#[derive(Debug, Clone, PartialEq, Default)]
pub struct LeafFix {
    /// Where the corrections came from (the file), for messages.
    pub source: String,
    pub note: String,
    all: Option<Both>,
    by_type: [Option<Both>; 4],
    lines: Vec<(String, Both)>,
}

impl LeafFix {
    /// No corrections yet (`set_all`, `set_pot_type` and `set_line` add them); `source` is for messages.
    pub fn named(source: &str) -> Self {
        LeafFix { source: source.to_string(), ..Default::default() }
    }

    /// The file named by env PREFLOP_LEAF_FIX, or None when it is not set.
    pub fn from_env() -> Result<Option<Self>, String> {
        let path = std::env::var("PREFLOP_LEAF_FIX").unwrap_or_default();
        let path = path.trim();
        if path.is_empty() {
            return Ok(None);
        }
        let text = std::fs::read_to_string(path).map_err(|e| format!("PREFLOP_LEAF_FIX: cannot read {path}: {e}"))?;
        Self::from_json(&text, path).map(Some)
    }

    pub fn from_json(text: &str, source: &str) -> Result<Self, String> {
        let bad = |what: String| format!("{source}: {what}");
        let v: serde_json::Value = serde_json::from_str(text).map_err(|e| bad(format!("not JSON: {e}")))?;
        let top = v.as_object().ok_or_else(|| bad("must be a JSON object".into()))?;
        if let Some(key) = top.keys().find(|k| !["format", "version", "note", "entries"].contains(&k.as_str())) {
            return Err(bad(format!("unknown key \"{key}\"")));
        }
        if top.get("format").and_then(|f| f.as_str()) != Some("gtopen-leaf-fix") || top.get("version").and_then(|n| n.as_u64()) != Some(1) {
            return Err(bad("must say \"format\": \"gtopen-leaf-fix\", \"version\": 1".into()));
        }
        let mut fix = LeafFix::named(source);
        fix.note = top.get("note").and_then(|n| n.as_str()).unwrap_or("").to_string();
        let entries = top.get("entries").and_then(|e| e.as_array()).ok_or_else(|| bad("\"entries\" must be a list".into()))?;
        for (i, entry) in entries.iter().enumerate() {
            let at = |what: String| bad(format!("entry {}: {what}", i + 1));
            let e = entry.as_object().ok_or_else(|| at("must be an object".into()))?;
            if let Some(key) = e.keys().find(|k| !["line", "pot_type", "oop", "ip"].contains(&k.as_str())) {
                return Err(at(format!("unknown key \"{key}\"")));
            }
            let mut both = vec![0f32; 2 * NUM_CLASSES];
            for (side, key) in ["oop", "ip"].iter().enumerate() {
                let out = &mut both[side * NUM_CLASSES..(side + 1) * NUM_CLASSES];
                match e.get(*key) {
                    None => {}
                    Some(serde_json::Value::Number(n)) => out.fill(n.as_f64().unwrap_or(f64::NAN) as f32),
                    Some(serde_json::Value::Array(a)) if a.len() == NUM_CLASSES => {
                        for (o, x) in out.iter_mut().zip(a) {
                            *o = x.as_f64().ok_or_else(|| at(format!("\"{key}\" must hold numbers")))? as f32;
                        }
                    }
                    Some(_) => return Err(at(format!("\"{key}\" must be one number or {NUM_CLASSES} numbers"))),
                }
            }
            let text_of = |key: &str| match e.get(key) {
                None => Ok(None),
                Some(serde_json::Value::String(s)) => Ok(Some(s.as_str())),
                Some(_) => Err(at(format!("\"{key}\" must be text"))),
            };
            match (text_of("line")?, text_of("pot_type")?) {
                (Some(_), Some(_)) => return Err(at("give \"line\" or \"pot_type\", not both".into())),
                (Some(line), None) => fix.set_line(line, &both).map_err(at)?,
                (None, Some(name)) => {
                    let t = POT_TYPES.iter().position(|p| *p == name)
                        .ok_or_else(|| at(format!("\"pot_type\" must be one of {}, not \"{name}\"", POT_TYPES.join(", "))))?;
                    fix.set_pot_type(t, &both).map_err(at)?;
                }
                (None, None) => fix.set_all(&both).map_err(at)?,
            }
        }
        Ok(fix)
    }

    fn checked(both: &[f32]) -> Result<Both, String> {
        if both.len() != 2 * NUM_CLASSES {
            return Err(format!("a correction is {} numbers, out of position first", 2 * NUM_CLASSES));
        }
        if let Some(v) = both.iter().find(|v| !v.is_finite() || v.abs() > MAX_FIX) {
            return Err(format!("{v} is not a correction: the numbers are fractions of the pot (0.01 is 1% of the pot), at most {MAX_FIX} either way"));
        }
        Ok(both.into())
    }

    /// The correction for every learned leaf: out of position 169, then in position 169.
    pub fn set_all(&mut self, both: &[f32]) -> Result<(), String> {
        if self.all.is_some() {
            return Err("a second entry for every leaf".into());
        }
        self.all = Some(Self::checked(both)?);
        Ok(())
    }

    /// The correction for every learned leaf of a pot type (an index into `POT_TYPES`).
    pub fn set_pot_type(&mut self, pot_type: usize, both: &[f32]) -> Result<(), String> {
        let slot = self.by_type.get_mut(pot_type).ok_or("no such pot type")?;
        if slot.is_some() {
            return Err(format!("a second entry for pot type {}", POT_TYPES[pot_type]));
        }
        *slot = Some(Self::checked(both)?);
        Ok(())
    }

    /// The correction for the leaf a line ends at (`datagen::line_key` of its path).
    pub fn set_line(&mut self, line: &str, both: &[f32]) -> Result<(), String> {
        if line.trim().is_empty() {
            return Err("an empty line".into());
        }
        if self.lines.iter().any(|(l, _)| l == line) {
            return Err(format!("a second entry for line \"{line}\""));
        }
        self.lines.push((line.to_string(), Self::checked(both)?));
        Ok(())
    }

    /// The lines with an entry of their own, in file order.
    pub fn lines(&self) -> impl Iterator<Item = &str> {
        self.lines.iter().map(|(l, _)| l.as_str())
    }

    /// True when the file corrects nothing.
    pub fn is_empty(&self) -> bool {
        self.all.is_none() && self.by_type.iter().all(|t| t.is_none()) && self.lines.is_empty()
    }

    /// What the file holds, in words.
    pub fn summary(&self) -> String {
        let types: Vec<&str> = POT_TYPES.iter().zip(&self.by_type).filter(|(_, t)| t.is_some()).map(|(n, _)| *n).collect();
        let mut parts = Vec::new();
        if self.all.is_some() {
            parts.push("every leaf".to_string());
        }
        if !types.is_empty() {
            parts.push(format!("pot types {}", types.join(", ")));
        }
        if !self.lines.is_empty() {
            parts.push(format!("{} lines", self.lines.len()));
        }
        format!("leaf corrections from {} ({})", self.source, if parts.is_empty() { "none".to_string() } else { parts.join("; ") })
    }

    /// Adds what the file holds for a leaf to `corr` (out of position 169,
    /// then in position 169): the entry for every leaf, the one for its pot
    /// type and the one for its line (`line`, an index into the file's
    /// lines). True when any entry applied.
    pub(crate) fn add(&self, pot_type: usize, line: Option<usize>, corr: &mut [f32]) -> bool {
        let mut any = false;
        let entries = [self.all.as_ref(), self.by_type.get(pot_type).and_then(|t| t.as_ref()), line.and_then(|i| self.lines.get(i)).map(|(_, b)| b)];
        for both in entries.into_iter().flatten() {
            for (c, f) in corr.iter_mut().zip(both.iter()) {
                *c += f;
            }
            any = true;
        }
        any
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_file_is_read_as_written() {
        let classes: Vec<f32> = (0..NUM_CLASSES).map(|h| h as f32 * 1e-4).collect();
        let text = serde_json::json!({
            "format": "gtopen-leaf-fix", "version": 1, "note": "a test",
            "entries": [
                {"oop": 0.002, "ip": -0.002},
                {"pot_type": "3bet", "ip": classes},
                {"line": "P0 Raise 2.5 | P1 Call 2.5", "oop": classes},
            ],
        }).to_string();
        let fix = LeafFix::from_json(&text, "test.json").unwrap();
        assert_eq!((fix.note.as_str(), fix.lines().collect::<Vec<_>>()), ("a test", vec!["P0 Raise 2.5 | P1 Call 2.5"]));
        assert!(!fix.is_empty() && fix.summary().contains("every leaf") && fix.summary().contains("3bet") && fix.summary().contains("1 lines"));
        // a single-raised leaf without a line of its own: the entry for every leaf alone
        let mut corr = vec![0.01f32; 2 * NUM_CLASSES];
        assert!(fix.add(1, None, &mut corr));
        assert!(corr[..NUM_CLASSES].iter().all(|&c| (c - 0.012).abs() < 1e-7) && corr[NUM_CLASSES..].iter().all(|&c| (c - 0.008).abs() < 1e-7));
        // a 3-bet leaf at the named line: all three add up, each on its own side and class
        let mut corr = vec![0f32; 2 * NUM_CLASSES];
        assert!(fix.add(2, Some(0), &mut corr));
        for h in 0..NUM_CLASSES {
            assert!((corr[h] - (0.002 + classes[h])).abs() < 1e-7 && (corr[NUM_CLASSES + h] - (-0.002 + classes[h])).abs() < 1e-7, "class {h}");
        }
        // nothing for a leaf no entry fits
        let only_type = LeafFix::from_json(r#"{"format":"gtopen-leaf-fix","version":1,"entries":[{"pot_type":"4bet","oop":0.01}]}"#, "t").unwrap();
        let mut corr = vec![0f32; 2 * NUM_CLASSES];
        assert!(!only_type.add(1, None, &mut corr) && corr.iter().all(|&c| c == 0.0));
        assert!(LeafFix::from_json(r#"{"format":"gtopen-leaf-fix","version":1,"entries":[]}"#, "t").unwrap().is_empty());
    }

    #[test]
    fn a_file_that_could_be_a_mistake_is_refused() {
        let file = |entries: &str| format!(r#"{{"format":"gtopen-leaf-fix","version":1,"entries":[{entries}]}}"#);
        for (entries, says) in [
            (r#"{"oop": 1.5}"#, "fractions of the pot"),                    // percent, not a fraction
            (r#"{"oop": [0.01, 0.02]}"#, "169 numbers"),
            (r#"{"oop": "0.01"}"#, "169 numbers"),
            (r#"{"pot_type": "srp", "line": "P0 Call 1", "oop": 0.01}"#, "not both"),
            (r#"{"pot_type": "5bet", "oop": 0.01}"#, "pot_type"),
            (r#"{"pot": "srp", "oop": 0.01}"#, "unknown key"),
            (r#"{"oop": 0.01}, {"ip": 0.01}"#, "second entry"),
            (r#"{"line": "A | B", "oop": 0.01}, {"line": "A | B", "ip": 0.01}"#, "second entry"),
            (r#"{"line": " ", "oop": 0.01}"#, "empty line"),
        ] {
            let err = LeafFix::from_json(&file(entries), "t.json").unwrap_err();
            assert!(err.starts_with("t.json: ") && err.contains(says), "{entries}: {err}");
        }
        for text in ["[]", r#"{"format":"gtopen-leaf-fix","version":2,"entries":[]}"#, r#"{"format":"gtopen-leaf-fix","version":1}"#,
                     r#"{"format":"gtopen-leaf-fix","version":1,"entries":[],"entry":[]}"#, "not json"] {
            assert!(LeafFix::from_json(text, "t.json").is_err(), "{text}");
        }
    }
}
