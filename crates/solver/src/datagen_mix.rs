//! Game mixes: WHAT the pooled data generator draws, as data.
//!
//! `tools/datagen/mixes.json` lists every mix that was ever published; the
//! one with the highest id that is not withdrawn is the current one. A build
//! carries the list as it was when it was built, and a running generator
//! reads the published list again before every job
//! ([`MIX_URL`], through [`MixSync`]) and moves to a newer mix by itself. So
//! changing what contributors solve is a change to that one file, with no
//! update on anyone's machine.
//!
//! A mix is only ever data: shares, ranges of numbers and the names of
//! published situation lists. Everything in it is bounds-checked
//! ([`Mix::check`]) and nothing in it names a program, a path or a web
//! address, so the worst a wrong mix can do is have contributors solve the
//! wrong flop spots.
//!
//! A mix has parts, each with a share of the examples:
//! - `random`: random ranges (`datagen::sample_range`) in a pot drawn from
//!   pot types, table styles and rake structures given with their shares;
//! - `situations`: one entry of a published list of situations (both ranges,
//!   pot, stack and rake, taken from a GTOpen preflop solve) on a random
//!   flop. The list is a file in the public dataset, pinned by its SHA-256.
//!
//! A published mix is never edited: jobs are checked by drawing their inputs
//! again from the mix they name, so an edit would fail every upload made
//! under it. To change anything, add a mix with the next id. To stop one,
//! mark it `"withdrawn": true` (and add the one that replaces it).
//!
//! A mix that needs code this build does not have says so with
//! `needs_generator`; an older generator then keeps to the newest mix it can
//! draw and asks its owner to update.

use crate::datagen::{self, ExampleInputs, Rng};
use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, BTreeSet, HashMap};
use std::path::{Path, PathBuf};

/// Format name of the list of mixes.
pub const MIXES_FORMAT: &str = "gtopen-datagen-mixes";
/// Format name of a situation list file.
pub const SITUATIONS_FORMAT: &str = "gtopen-situations";
/// The list of mixes as it was when this build was made.
pub const BUILT_IN: &str = include_str!("../../../tools/datagen/mixes.json");
/// Where the published list of mixes is read from (`GTOPEN_MIX_URL`
/// replaces it, with a web address or a local file, for tests and forks).
pub const MIX_URL: &str = "https://raw.githubusercontent.com/MatthewPDingle/GTOpen/master/tools/datagen/mixes.json";
/// Where situation lists are read from: this plus `<list>.jsonl`
/// (`GTOPEN_SITUATIONS_URL` replaces it, with a web address or a local folder).
pub const SITUATIONS_URL: &str = "https://huggingface.co/datasets/GTOpen/gtopen-leaf-values/resolve/main/situations/";
/// A running generator reads the published list at most this often.
pub const CHECK_EVERY_S: u64 = 300;
/// Largest list of mixes and largest situation list that are read, in bytes.
const MAX_MIXES_BYTES: u64 = 2_000_000;
const MAX_LIST_BYTES: u64 = 200_000_000;
/// Most entries a situation list may hold.
pub const MAX_SITUATIONS: usize = 20_000;

// ----------------------------------------------------------------- mix ----

/// A range of numbers, `[lo, hi]` (both ends the same for a fixed value).
pub type Span = [f64; 2];

/// One pot type of a random part: its name, share and pot size in bb before
/// the table's scale.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PotShare {
    pub name: String,
    pub share: f64,
    pub pot_bb: Span,
}

/// One table style of a random part: how much bigger than the pot type's
/// usual size the pot is, and the starting stacks (drawn log-uniform).
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Table {
    pub share: f64,
    pub pot_scale: Span,
    pub stack_bb: Span,
}

/// One rake structure of a random part: the rake as a fraction of the pot
/// and its cap in bb (drawn log-uniform). No rake is `[0, 0]` for both.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Rake {
    pub share: f64,
    pub pct: Span,
    pub cap_bb: Span,
}

/// One part of a mix.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case", deny_unknown_fields)]
pub enum Part {
    /// Random ranges in a drawn pot.
    Random { share: f64, pot_types: Vec<PotShare>, tables: Vec<Table>, rake: Vec<Rake> },
    /// Entries of the published situation list `list` (whose file has this SHA-256) on random flops.
    Situations { share: f64, list: String, sha256: String },
}

impl Part {
    pub fn share(&self) -> f64 {
        match self {
            Part::Random { share, .. } | Part::Situations { share, .. } => *share,
        }
    }
}

/// One published game mix.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Mix {
    /// 1 to [`datagen::MAX_MIX_ID`]; a later mix has a higher id.
    pub id: u32,
    /// The first generator version that can draw this mix.
    pub needs_generator: u32,
    /// One plain line for contributors: what is being solved now.
    pub note: String,
    /// A mix that must no longer be drawn or accepted.
    #[serde(default, skip_serializing_if = "is_false")]
    pub withdrawn: bool,
    pub parts: Vec<Part>,
}

fn is_false(x: &bool) -> bool {
    !*x
}

fn shares_ok(shares: impl Iterator<Item = f64>, what: &str) -> Result<(), String> {
    let mut total = 0.0;
    let mut n = 0;
    for s in shares {
        if !(s.is_finite() && s > 0.0 && s <= 1.0) {
            return Err(format!("{what}: a share of {s} (each must be above 0 and at most 1)"));
        }
        total += s;
        n += 1;
    }
    if n == 0 || n > 16 {
        return Err(format!("{what}: {n} entries (1 to 16)"));
    }
    if (total - 1.0).abs() > 1e-6 {
        return Err(format!("{what}: shares add up to {total}, not 1"));
    }
    Ok(())
}

fn span_ok(s: &Span, lo: f64, hi: f64, what: &str) -> Result<(), String> {
    if s[0].is_finite() && s[1].is_finite() && lo <= s[0] && s[0] <= s[1] && s[1] <= hi {
        Ok(())
    } else {
        Err(format!("{what} {s:?} is not a range within {lo} to {hi}"))
    }
}

fn is_sha256(s: &str) -> bool {
    s.len() == 64 && s.bytes().all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b))
}

impl Mix {
    /// Bounds on everything a mix can say. A mix that passes can only make a
    /// generator solve heads-up flop spots of ordinary size.
    pub fn check(&self) -> Result<(), String> {
        let what = format!("mix {}", self.id);
        if self.id == 0 || self.id > datagen::MAX_MIX_ID {
            return Err(format!("{what}: ids run from 1 to {}", datagen::MAX_MIX_ID));
        }
        if self.note.trim().is_empty() || self.note.chars().count() > 200 || self.note.chars().any(|c| c.is_control()) {
            return Err(format!("{what}: the note must be one line of at most 200 characters"));
        }
        shares_ok(self.parts.iter().map(|p| p.share()), &format!("{what}: parts"))?;
        for part in &self.parts {
            match part {
                Part::Random { pot_types, tables, rake, .. } => {
                    shares_ok(pot_types.iter().map(|p| p.share), &format!("{what}: pot types"))?;
                    shares_ok(tables.iter().map(|t| t.share), &format!("{what}: tables"))?;
                    shares_ok(rake.iter().map(|r| r.share), &format!("{what}: rake"))?;
                    for p in pot_types {
                        if !crate::preflop::leafnet::POT_TYPES.contains(&p.name.as_str()) {
                            return Err(format!("{what}: unknown pot type {:?}", p.name));
                        }
                        span_ok(&p.pot_bb, 0.5, 500.0, &format!("{what}: {} pot_bb", p.name))?;
                    }
                    for t in tables {
                        span_ok(&t.pot_scale, 0.25, 20.0, &format!("{what}: pot_scale"))?;
                        span_ok(&t.stack_bb, 2.0, 2000.0, &format!("{what}: stack_bb"))?;
                    }
                    for r in rake {
                        span_ok(&r.pct, 0.0, 0.25, &format!("{what}: rake pct (a fraction of the pot)"))?;
                        if r.pct[1] == 0.0 {
                            span_ok(&r.cap_bb, 0.0, 0.0, &format!("{what}: the cap of no rake"))?;
                        } else {
                            span_ok(&r.cap_bb, 0.05, 1000.0, &format!("{what}: rake cap_bb"))?;
                        }
                    }
                }
                Part::Situations { list, sha256, .. } => {
                    if !datagen::plain_name(list) {
                        return Err(format!("{what}: list name {list:?} is not a plain name (letters, digits, - or _)"));
                    }
                    if !is_sha256(sha256) {
                        return Err(format!("{what}: list {list} needs its SHA-256 as 64 lower-case hex digits"));
                    }
                }
            }
        }
        Ok(())
    }

    /// A short fingerprint of what the mix draws (its id and parts; not the
    /// note). Written in every job header.
    pub fn key(&self) -> String {
        let text = serde_json::to_string(&(self.id, &self.parts)).expect("mix json");
        format!("{:016x}", datagen::fnv1a(text.as_bytes()))
    }

    /// The situation lists the mix draws from: (name, SHA-256).
    pub fn lists(&self) -> Vec<(&str, &str)> {
        self.parts.iter().filter_map(|p| match p {
            Part::Situations { list, sha256, .. } => Some((list.as_str(), sha256.as_str())),
            _ => None,
        }).collect()
    }

    /// The mix in a few plain words per part, for the generator's window.
    pub fn summary(&self) -> String {
        self.parts.iter().map(|p| match p {
            Part::Random { share, .. } => format!("{:.0}% random ranges", share * 100.0),
            Part::Situations { share, list, .. } => format!("{:.0}% situations from the list {list}", share * 100.0),
        }).collect::<Vec<_>>().join(", ")
    }
}

// ---------------------------------------------------- situation lists ----

/// One entry of a situation list: a heads-up flop situation without its flop.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Situation {
    #[serde(rename = "type")]
    pub kind: String,
    /// The entry's name within the list (kept on every example drawn from it).
    pub id: String,
    pub pot_type: String,
    pub pot_bb: f64,
    pub stack_bb: f64,
    pub rake_pct: f64,
    pub rake_cap_bb: f64,
    /// 169-class range weights, 0 = OOP, 1 = IP, as in [`ExampleInputs`].
    pub range: [Vec<f32>; 2],
    /// How often the entry is drawn, relative to the others (default 1).
    #[serde(default = "one", skip_serializing_if = "is_one")]
    pub weight: f64,
    /// Anything that describes the entry for readers (the game, the preflop
    /// line); never read by the generator.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub about: Option<serde_json::Value>,
}

fn one() -> f64 {
    1.0
}

fn is_one(x: &f64) -> bool {
    *x == 1.0
}

/// A parsed situation list.
#[derive(Debug, Clone)]
pub struct SituationList {
    pub name: String,
    pub entries: Vec<Situation>,
    /// Running total of the entries' weights.
    cumulative: Vec<f64>,
}

impl SituationList {
    /// Parse and check the text of a situation list file: a header line
    /// `{"type":"header","format":"gtopen-situations","format_version":1,"list":NAME,"situations":N}`
    /// and one [`Situation`] per line.
    pub fn parse(text: &str) -> Result<SituationList, String> {
        let mut lines = text.lines().filter(|l| !l.trim().is_empty());
        let head: serde_json::Value = serde_json::from_str(lines.next().ok_or("empty file")?)
            .map_err(|e| format!("header: {e}"))?;
        if head["type"] != "header" || head["format"] != SITUATIONS_FORMAT || head["format_version"] != 1 {
            return Err(format!("not a {SITUATIONS_FORMAT} v1 file"));
        }
        let name = head["list"].as_str().unwrap_or("").to_string();
        if !datagen::plain_name(&name) {
            return Err(format!("list name {name:?} is not a plain name (letters, digits, - or _)"));
        }
        let mut entries = Vec::new();
        let mut seen = BTreeSet::new();
        let mut cumulative = Vec::new();
        let mut total = 0.0;
        for (n, line) in lines.enumerate() {
            if entries.len() >= MAX_SITUATIONS {
                return Err(format!("more than {MAX_SITUATIONS} situations"));
            }
            let s: Situation = serde_json::from_str(line).map_err(|e| format!("situation {}: {e}", n + 1))?;
            let bad = |msg: String| format!("situation {} ({}): {msg}", n + 1, s.id);
            if s.kind != "situation" {
                return Err(bad("its type is not \"situation\"".into()));
            }
            if s.id.is_empty() || s.id.chars().count() > 120 || s.id.chars().any(|c| c.is_control()) {
                return Err(format!("situation {}: its id must be 1 to 120 characters", n + 1));
            }
            if !seen.insert(s.id.clone()) {
                return Err(bad("the id is used twice".into()));
            }
            if !(s.weight.is_finite() && s.weight > 0.0 && s.weight <= 1e6) {
                return Err(bad(format!("weight {} out of range", s.weight)));
            }
            // the same plausibility checks as a real-range example, on any flop
            let probe = ExampleInputs {
                job: 0, index: 0, board: "AsKd7c".into(), pot_type: s.pot_type.clone(), pot_bb: s.pot_bb,
                stack_bb: s.stack_bb, rake_pct: s.rake_pct, rake_cap_bb: s.rake_cap_bb, range: s.range.clone(),
                attempt: 0, pot_scale: 1.0, situation: None,
            };
            if let Some(msg) = datagen::check_real_inputs(&probe) {
                return Err(bad(msg));
            }
            total += s.weight;
            cumulative.push(total);
            entries.push(s);
        }
        if entries.is_empty() {
            return Err("no situations".into());
        }
        if head["situations"].as_u64() != Some(entries.len() as u64) {
            return Err(format!("{} situations, header says {}", entries.len(), head["situations"]));
        }
        Ok(SituationList { name, entries, cumulative })
    }

    fn pick(&self, rng: &mut Rng) -> &Situation {
        let x = rng.f64() * self.cumulative[self.cumulative.len() - 1];
        let i = self.cumulative.partition_point(|&c| c <= x).min(self.entries.len() - 1);
        &self.entries[i]
    }
}

// ---------------------------------------------------------------- book ----

/// Every mix this process knows, and the situation lists it has loaded.
#[derive(Debug, Clone, Default)]
pub struct Book {
    /// Mixes this build can draw, by id (withdrawn ones included).
    pub mixes: BTreeMap<u32, Mix>,
    /// Published mixes that need a newer generator than this build: id -> the version needed.
    pub too_new: BTreeMap<u32, u32>,
    /// Loaded situation lists by SHA-256.
    pub lists: HashMap<String, SituationList>,
}

impl Book {
    /// The mixes this build was made with.
    pub fn built_in() -> Book {
        let mut book = Book::default();
        let skipped = book.add_text(BUILT_IN).expect("tools/datagen/mixes.json");
        assert!(skipped.is_empty(), "tools/datagen/mixes.json: {skipped:?}");
        book
    }

    /// Add the mixes of a list of mixes (the text of mixes.json); one that is
    /// already known is replaced. Returns what was skipped and why (a mix
    /// that does not parse or pass [`Mix::check`] is left out; it never
    /// stops the others). Fails when the text is not a list of mixes at all.
    pub fn add_text(&mut self, text: &str) -> Result<Vec<String>, String> {
        let v: serde_json::Value = serde_json::from_str(text).map_err(|e| format!("not JSON: {e}"))?;
        if v["format"] != MIXES_FORMAT {
            return Err(format!("not a {MIXES_FORMAT} file"));
        }
        let list = v["mixes"].as_array().ok_or("no list of mixes")?;
        if list.len() > datagen::MAX_MIX_ID as usize {
            return Err("too many mixes".into());
        }
        let mut skipped = Vec::new();
        let mut seen = BTreeSet::new();
        for m in list {
            let (Some(id), Some(needs)) = (m["id"].as_u64(), m["needs_generator"].as_u64()) else {
                skipped.push("a mix without an id or needs_generator".to_string());
                continue;
            };
            let id = id.min(u32::MAX as u64) as u32;
            if !seen.insert(id) {
                skipped.push(format!("mix {id} is listed twice (the first one counts)"));
                continue;
            }
            if needs > datagen::GENERATOR_VERSION as u64 {
                // written for a newer generator: its parts may be of kinds this build cannot read
                if m["withdrawn"] != true {
                    self.too_new.insert(id, needs.min(u32::MAX as u64) as u32);
                }
                self.mixes.remove(&id);
                continue;
            }
            match serde_json::from_value::<Mix>(m.clone()).map_err(|e| e.to_string()).and_then(|mix| mix.check().map(|_| mix)) {
                Ok(mix) => {
                    self.too_new.remove(&id);
                    self.mixes.insert(id, mix);
                }
                Err(e) => skipped.push(format!("mix {id} is not usable: {e}")),
            }
        }
        Ok(skipped)
    }

    /// True when every situation list the mix draws from is loaded.
    pub fn ready(&self, mix: &Mix) -> bool {
        mix.lists().iter().all(|(_, sha)| self.lists.contains_key(*sha))
    }

    /// Ids of the mixes a generator may draw (not withdrawn), newest first.
    pub fn open_ids(&self) -> Vec<u32> {
        self.mixes.values().rev().filter(|m| !m.withdrawn).map(|m| m.id).collect()
    }

    /// The newest published mix this build cannot draw, when it is newer than every one it can.
    pub fn needs_update(&self) -> Option<(u32, u32)> {
        let newest = self.open_ids().first().copied().unwrap_or(0);
        self.too_new.iter().next_back().filter(|(id, _)| **id > newest).map(|(a, b)| (*a, *b))
    }

    /// The inputs of example `index` of job `job` under mix `mix_id`, for a
    /// GPU that holds trees up to `cap_gb` (as `datagen::example_inputs_capped`).
    /// Fully determined by the mix, its lists and (job, index, cap).
    pub fn inputs(&self, mix_id: u32, job: u64, index: u32, cap_gb: Option<f64>) -> Result<ExampleInputs, String> {
        let mix = self.mixes.get(&mix_id).ok_or_else(|| format!("mix {mix_id} is not known"))?;
        if !self.ready(mix) {
            return Err(format!("a situation list of mix {mix_id} is not loaded"));
        }
        Ok(datagen::capped(cap_gb, |attempt| self.draw(mix, job, index, attempt)))
    }

    fn draw(&self, mix: &Mix, job: u64, index: u32, attempt: u32) -> ExampleInputs {
        let mut rng = Rng::new(datagen::attempt_seed(datagen::GENERATOR_VERSION, job, index, attempt));
        let part = pick(&mut rng, &mix.parts, |p| p.share());
        let mut ex = match part {
            Part::Random { pot_types, tables, rake, .. } => draw_random(&mut rng, pot_types, tables, rake),
            Part::Situations { sha256, .. } => {
                let list = &self.lists[sha256];
                let s = list.pick(&mut rng);
                ExampleInputs {
                    job: 0,
                    index: 0,
                    board: datagen::random_flop(&mut rng),
                    pot_type: s.pot_type.clone(),
                    pot_bb: s.pot_bb,
                    stack_bb: s.stack_bb,
                    rake_pct: s.rake_pct,
                    rake_cap_bb: s.rake_cap_bb,
                    range: s.range.clone(),
                    attempt: 0,
                    pot_scale: 1.0,
                    situation: Some(format!("{}/{}", list.name, s.id)),
                }
            }
        };
        ex.job = job;
        ex.index = index;
        ex.attempt = attempt;
        ex
    }
}

/// One of `items`, each with the chance its share gives it (shares add up to 1).
fn pick<'a, T>(rng: &mut Rng, items: &'a [T], share: impl Fn(&T) -> f64) -> &'a T {
    let u = rng.f64();
    let mut acc = 0.0;
    for item in items {
        acc += share(item);
        if u < acc {
            return item;
        }
    }
    &items[items.len() - 1]
}

fn span(rng: &mut Rng, s: &Span) -> f64 {
    if s[0] == s[1] { s[0] } else { rng.range(s[0], s[1]) }
}

fn log_span(rng: &mut Rng, s: &Span) -> f64 {
    if s[0] == s[1] { s[0] } else { rng.log_range(s[0], s[1]) }
}

/// A random-ranges example: pot type, then table style, then rake, then the
/// flop and both ranges, as generator v4 drew them but from the mix's numbers.
fn draw_random(rng: &mut Rng, pot_types: &[PotShare], tables: &[Table], rake: &[Rake]) -> ExampleInputs {
    let pot_type = pick(rng, pot_types, |p| p.share);
    let table = pick(rng, tables, |t| t.share);
    let pot_scale = datagen::round2(span(rng, &table.pot_scale));
    let pot_bb = datagen::round2(span(rng, &pot_type.pot_bb) * pot_scale);
    let stack_bb = datagen::draw_stack_from(rng, pot_bb, table.stack_bb[0], table.stack_bb[1]);
    let r = pick(rng, rake, |r| r.share);
    let rake = if r.pct[1] == 0.0 {
        (0.0, 0.0)
    } else {
        ((span(rng, &r.pct) * 1000.0).round() / 1000.0, (log_span(rng, &r.cap_bb) * 20.0).round() / 20.0)
    };
    datagen::finish(rng, &pot_type.name, pot_bb, pot_scale, stack_bb, rake)
}

// ------------------------------------------------------------- SHA-256 ----

/// SHA-256 of `data` as 64 lower-case hex digits (FIPS 180-4).
pub fn sha256_hex(data: &[u8]) -> String {
    const K: [u32; 64] = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
        0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
        0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
        0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
    ];
    let mut h: [u32; 8] = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
    ];
    let mut msg = data.to_vec();
    msg.push(0x80);
    while msg.len() % 64 != 56 {
        msg.push(0);
    }
    msg.extend_from_slice(&((data.len() as u64) * 8).to_be_bytes());
    for block in msg.chunks_exact(64) {
        let mut w = [0u32; 64];
        for (i, word) in block.chunks_exact(4).enumerate() {
            w[i] = u32::from_be_bytes([word[0], word[1], word[2], word[3]]);
        }
        for i in 16..64 {
            let s0 = w[i - 15].rotate_right(7) ^ w[i - 15].rotate_right(18) ^ (w[i - 15] >> 3);
            let s1 = w[i - 2].rotate_right(17) ^ w[i - 2].rotate_right(19) ^ (w[i - 2] >> 10);
            w[i] = w[i - 16].wrapping_add(s0).wrapping_add(w[i - 7]).wrapping_add(s1);
        }
        let mut v = h;
        for i in 0..64 {
            let s1 = v[4].rotate_right(6) ^ v[4].rotate_right(11) ^ v[4].rotate_right(25);
            let ch = (v[4] & v[5]) ^ (!v[4] & v[6]);
            let t1 = v[7].wrapping_add(s1).wrapping_add(ch).wrapping_add(K[i]).wrapping_add(w[i]);
            let s0 = v[0].rotate_right(2) ^ v[0].rotate_right(13) ^ v[0].rotate_right(22);
            let maj = (v[0] & v[1]) ^ (v[0] & v[2]) ^ (v[1] & v[2]);
            let t2 = s0.wrapping_add(maj);
            v = [t1.wrapping_add(t2), v[0], v[1], v[2], v[3].wrapping_add(t1), v[4], v[5], v[6]];
        }
        for i in 0..8 {
            h[i] = h[i].wrapping_add(v[i]);
        }
    }
    h.iter().map(|x| format!("{x:08x}")).collect()
}

// ---------------------------------------------------------------- sync ----

/// Read a web address (with the system's `curl`) or a local file.
fn fetch(source: &str, max_bytes: u64, seconds: u32) -> Result<Vec<u8>, String> {
    if !(source.starts_with("https://") || source.starts_with("http://")) {
        let data = std::fs::read(source).map_err(|e| format!("{source}: {e}"))?;
        if data.len() as u64 > max_bytes {
            return Err(format!("{source}: larger than {max_bytes} bytes"));
        }
        return Ok(data);
    }
    let out = std::process::Command::new("curl")
        .args(["--fail", "--silent", "--show-error", "--location", "--connect-timeout", "15", "--max-time", &seconds.to_string(),
               "--max-filesize", &max_bytes.to_string(), source])
        .stdin(std::process::Stdio::null())
        .output()
        .map_err(|e| format!("curl could not be started ({e})"))?;
    if !out.status.success() {
        let why = String::from_utf8_lossy(&out.stderr);
        return Err(why.lines().last().unwrap_or("curl failed").trim().to_string());
    }
    if out.stdout.len() as u64 > max_bytes {
        return Err(format!("larger than {max_bytes} bytes"));
    }
    Ok(out.stdout)
}

fn write_atomic(path: &Path, data: &[u8]) -> Result<(), String> {
    if let Some(dir) = path.parent() {
        std::fs::create_dir_all(dir).map_err(|e| format!("{}: {e}", dir.display()))?;
    }
    let tmp = path.with_extension(format!("tmp{}", std::process::id()));
    std::fs::write(&tmp, data).map_err(|e| format!("{}: {e}", tmp.display()))?;
    std::fs::rename(&tmp, path).map_err(|e| {
        let _ = std::fs::remove_file(&tmp);
        format!("{}: {e}", path.display())
    })
}

/// Keeps a [`Book`] up to date with the published list of mixes, with a
/// folder on disk as its memory (the last list read, and the situation lists
/// fetched so far), so a generator that starts without a network still knows
/// the newest mix it ever saw.
pub struct MixSync {
    pub book: Book,
    dir: PathBuf,
    url: String,
    lists_url: String,
    every: std::time::Duration,
    /// Lists that would not load, with when and why: not tried again before the next read is due.
    failed: HashMap<String, (std::time::Instant, String)>,
}

impl MixSync {
    /// The built-in mixes plus whatever `dir` remembers. Reads nothing from the network yet.
    pub fn open(dir: &Path) -> MixSync {
        let env = |name: &str, default: &str| std::env::var(name).ok().filter(|v| !v.is_empty()).unwrap_or_else(|| default.to_string());
        let mut book = Book::built_in();
        if let Ok(text) = std::fs::read_to_string(dir.join("mixes.json")) {
            // a remembered list that no longer parses is simply not used
            let _ = book.add_text(&text);
        }
        let every = std::env::var("GTOPEN_MIX_EVERY_S").ok().and_then(|v| v.parse().ok()).unwrap_or(CHECK_EVERY_S);
        MixSync {
            book,
            dir: dir.to_path_buf(),
            url: env("GTOPEN_MIX_URL", MIX_URL),
            lists_url: env("GTOPEN_SITUATIONS_URL", SITUATIONS_URL),
            every: std::time::Duration::from_secs(every),
            failed: HashMap::new(),
        }
    }

    /// Read the published list of mixes now. Ok: what was skipped in it.
    pub fn refresh(&mut self) -> Result<Vec<String>, String> {
        // the time of the last read is kept on disk, so that many short runs
        // on one machine (a validator checking file after file) share it
        let _ = write_atomic(&self.dir.join("last-read"), b"");
        let data = fetch(&self.url, MAX_MIXES_BYTES, 20)?;
        let text = String::from_utf8(data).map_err(|_| "the list of mixes is not text".to_string())?;
        let skipped = self.book.add_text(&text)?;
        // remembered for the next start; a folder that cannot be written is no reason to stop
        let _ = write_atomic(&self.dir.join("mixes.json"), text.as_bytes());
        Ok(skipped)
    }

    /// [`MixSync::refresh`] unless the list was read (or tried) in the last
    /// few minutes. None: it was not time yet.
    pub fn refresh_if_due(&mut self) -> Option<Result<Vec<String>, String>> {
        let last = std::fs::metadata(self.dir.join("last-read")).and_then(|m| m.modified()).ok();
        match last.and_then(|t| t.elapsed().ok()) {
            Some(age) if age < self.every => None,
            _ => Some(self.refresh()),
        }
    }

    /// Load the situation lists of mix `id`: from this folder, else from the
    /// dataset (kept in this folder afterwards). A file is used only when
    /// its SHA-256 is the one the mix names.
    pub fn load_lists(&mut self, id: u32) -> Result<(), String> {
        let Some(mix) = self.book.mixes.get(&id) else {
            return Err(format!("mix {id} is not known"));
        };
        let wanted: Vec<(String, String)> = mix.lists().into_iter()
            .filter(|(_, sha)| !self.book.lists.contains_key(*sha))
            .map(|(a, b)| (a.to_string(), b.to_string())).collect();
        for (name, sha) in wanted {
            if let Some((when, why)) = self.failed.get(&sha) {
                if when.elapsed() < self.every {
                    return Err(why.clone());
                }
            }
            match self.load_list(id, &name, &sha) {
                Ok(list) => {
                    self.failed.remove(&sha);
                    self.book.lists.insert(sha, list);
                }
                Err(why) => {
                    self.failed.insert(sha, (std::time::Instant::now(), why.clone()));
                    return Err(why);
                }
            }
        }
        Ok(())
    }

    fn load_list(&self, id: u32, name: &str, sha: &str) -> Result<SituationList, String> {
        {
            let path = self.dir.join("situations").join(format!("{name}-{}.jsonl", &sha[..12]));
            let mut data = std::fs::read(&path).ok().filter(|d| sha256_hex(d) == sha);
            if data.is_none() {
                let sep = if self.lists_url.ends_with('/') || self.lists_url.ends_with('\\') { "" } else { "/" };
                let source = format!("{}{sep}{name}.jsonl", self.lists_url);
                let fetched = fetch(&source, MAX_LIST_BYTES, 300).map_err(|e| format!("situation list {name}: {e}"))?;
                if sha256_hex(&fetched) != sha {
                    return Err(format!("situation list {name}: the file is not the one mix {id} names (its SHA-256 differs)"));
                }
                let _ = write_atomic(&path, &fetched);
                data = Some(fetched);
            }
            let text = String::from_utf8(data.unwrap()).map_err(|_| format!("situation list {name}: not text"))?;
            let list = SituationList::parse(&text).map_err(|e| format!("situation list {name}: {e}"))?;
            if list.name != name {
                return Err(format!("situation list {name}: the file says it is the list {}", list.name));
            }
            Ok(list)
        }
    }

    /// The mix to draw the next job from: the newest one that is not
    /// withdrawn and whose situation lists could be loaded. Also returns why
    /// any newer one was passed over.
    pub fn choose(&mut self) -> (Option<u32>, Vec<String>) {
        let mut notes = Vec::new();
        for id in self.book.open_ids() {
            match self.load_lists(id) {
                Ok(()) => return (Some(id), notes),
                Err(e) => notes.push(format!("mix {id} cannot be drawn here yet ({e})")),
            }
        }
        (None, notes)
    }
}

// --------------------------------------------------------------- tests ----

#[cfg(test)]
mod tests {
    use super::*;

    fn mix(parts: serde_json::Value) -> serde_json::Value {
        serde_json::json!({"id": 2, "needs_generator": 5, "note": "test mix", "parts": parts})
    }

    fn random_part(share: f64) -> serde_json::Value {
        serde_json::json!({"kind": "random", "share": share,
            "pot_types": [{"name": "srp", "share": 0.75, "pot_bb": [4.5, 7.5]}, {"name": "3bet", "share": 0.25, "pot_bb": [15, 26]}],
            "tables": [{"share": 1.0, "pot_scale": [1, 1], "stack_bb": [25, 200]}],
            "rake": [{"share": 0.5, "pct": [0, 0], "cap_bb": [0, 0]}, {"share": 0.5, "pct": [0.05, 0.05], "cap_bb": [2, 4]}]})
    }

    fn list_text(name: &str, n: usize) -> String {
        let mut text = serde_json::json!({"type": "header", "format": SITUATIONS_FORMAT, "format_version": 1,
                                          "list": name, "situations": n}).to_string();
        for i in 0..n {
            let ex = datagen::example_inputs(77, i as u32);
            let s = Situation {
                kind: "situation".into(), id: format!("g1:{i}"), pot_type: "3bet".into(), pot_bb: 20.0 + i as f64,
                stack_bb: 90.0, rake_pct: 0.1, rake_cap_bb: 3.4, range: ex.range, weight: if i == 0 { 3.0 } else { 1.0 },
                about: Some(serde_json::json!({"line": "UTG Raise 3 | BTN Raise 9 | UTG Call 9"})),
            };
            text.push('\n');
            text.push_str(&serde_json::to_string(&s).unwrap());
        }
        text.push('\n');
        text
    }

    fn file(mixes: Vec<serde_json::Value>) -> String {
        serde_json::json!({"format": MIXES_FORMAT, "mixes": mixes}).to_string()
    }

    #[test]
    fn sha256_matches_the_standard_vectors() {
        assert_eq!(sha256_hex(b""), "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");
        assert_eq!(sha256_hex(b"abc"), "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
        assert_eq!(sha256_hex(b"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq"),
                   "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1");
        // two blocks of padding: 55, 56 and 64 bytes sit on the edges
        for (n, want) in [(55usize, "d5e285683cd4efc02d021a5c62014694958901005d6f71e89e0989fac77e4072"), (56, "04c26261370ee7541549d16dee320c723e3fd14671e66a099afe0a377c16888e"), (64, "7ce100971f64e7001e8fe5a51973ecdfe1ced42befe7ee8d5fd6219506b5393c")] {
            assert_eq!(sha256_hex(&vec![b'x'; n]), want, "{n} bytes");
        }
        let million_a = vec![b'a'; 1_000_000];
        assert_eq!(sha256_hex(&million_a), "cdc76e5c9914fb9281a1c7e284d73e67f1809a48a497200e046d39ccc7112cd0");
    }

    #[test]
    fn the_built_in_list_is_valid_and_mix_1_draws_generator_v4s_games() {
        let book = Book::built_in();
        assert!(book.too_new.is_empty());
        let ids: Vec<u32> = book.mixes.keys().copied().collect();
        assert_eq!(ids, (1..=ids.len() as u32).collect::<Vec<_>>(), "ids run from 1 with no gaps");
        for m in book.mixes.values() {
            assert_eq!(m.check(), Ok(()));
            assert!(m.needs_generator >= 5 && m.needs_generator <= datagen::GENERATOR_VERSION);
        }
        // mix 1: the same shares as generator v4 (datagen::tests::v4_mix_matches_its_description)
        let n = 6000;
        let job = datagen::mix_job("alice", 1, 0);
        let mut count = HashMap::new();
        let (mut online, mut live, mut straddled, mut none, mut five, mut ten, mut low_live_cap) = (0, 0, 0, 0, 0, 0, 0);
        for i in 0..n {
            let ex = book.inputs(1, job, i, None).unwrap();
            assert_eq!((ex.job, ex.index, ex.attempt, &ex.situation), (job, i, 0, &None));
            *count.entry(ex.pot_type.clone()).or_insert(0) += 1;
            match ex.pot_scale {
                s if s == 1.0 => online += 1,
                s if (1.3..2.0).contains(&s) => live += 1,
                s => {
                    assert!((2.0..=4.0).contains(&s), "pot_scale {s}");
                    straddled += 1
                }
            }
            assert!(ex.stack_bb > 0.0 && ex.stack_bb <= datagen::MAX_SPR * ex.pot_bb + 1e-9);
            assert!(ex.stack_bb + ex.pot_bb / 2.0 <= 400.0 + 1e-9);
            assert!((0.0..=0.10).contains(&ex.rake_pct) && ex.rake_cap_bb <= 12.0);
            assert!(ex.rake_pct == 0.0 || ex.rake_cap_bb >= 0.5);
            none += (ex.rake_pct == 0.0) as usize;
            five += (ex.rake_pct == 0.05) as usize;
            ten += (ex.rake_pct == 0.10) as usize;
            low_live_cap += (ex.rake_pct == 0.10 && (2.5..=4.5).contains(&ex.rake_cap_bb)) as usize;
            assert!(i >= 20 || crate::Spot::new(ex.spot_config()).is_ok());
        }
        let share = |x: usize| x as f64 / n as f64;
        for (t, want) in [("limped", 0.10), ("srp", 0.55), ("3bet", 0.20), ("4bet", 0.15)] {
            let got = share(count.get(t).copied().unwrap_or(0));
            assert!((got - want).abs() < 0.025, "{t}: {got}");
        }
        for (got, want, what) in [(online, 0.4, "online"), (live, 0.4, "live"), (straddled, 0.2, "straddled"),
                                   (none, 0.2, "no rake"), (five, 0.35, "5%"), (ten, 0.35, "10%")] {
            assert!((share(got) - want).abs() < 0.025, "{what}: {}", share(got));
        }
        assert!(share(low_live_cap) > 0.07, "low live caps {}", share(low_live_cap));
    }

    /// Jobs are checked by drawing their inputs again, so what a published
    /// mix draws must never change: not by editing the mix, not by changing
    /// the code that reads it. This hash was taken when mix 1 was published.
    #[test]
    fn mix_1_draws_are_unchanged() {
        let book = Book::built_in();
        assert_eq!(book.mixes[&1].key(), "b34c7d58284ccd41");
        let mut s = String::new();
        for k in [0u64, 7, 1_000_000] {
            let job = datagen::mix_job("alice", 1, k);
            for i in 0..40 {
                s.push_str(&serde_json::to_string(&book.inputs(1, job, i, None).unwrap()).unwrap());
                s.push_str(&serde_json::to_string(&book.inputs(1, job, i, Some(6.0)).unwrap()).unwrap());
            }
        }
        assert_eq!((datagen::fnv1a(s.as_bytes()), s.len()), (0x4c2c_fd4d_98f1_4397, 416_894));
    }

    #[test]
    fn a_mix_is_bounds_checked() {
        let ok: Mix = serde_json::from_value(mix(serde_json::json!([random_part(1.0)]))).unwrap();
        assert_eq!(ok.check(), Ok(()));
        let bad = |change: &dyn Fn(&mut serde_json::Value)| -> String {
            let mut v = mix(serde_json::json!([random_part(1.0)]));
            change(&mut v);
            match serde_json::from_value::<Mix>(v) {
                Ok(m) => m.check().unwrap_err(),
                Err(e) => format!("parse: {e}"),
            }
        };
        assert!(bad(&|v| v["id"] = 0.into()).contains("ids run from 1"));
        assert!(bad(&|v| v["id"] = 512.into()).contains("ids run from 1"));
        assert!(bad(&|v| v["note"] = "".into()).contains("note"));
        assert!(bad(&|v| v["note"] = "two\nlines".into()).contains("note"));
        assert!(bad(&|v| v["parts"][0]["share"] = 0.5.into()).contains("add up to 0.5"));
        assert!(bad(&|v| v["parts"] = serde_json::json!([])).contains("0 entries"));
        assert!(bad(&|v| v["parts"][0]["pot_types"][0]["name"] = "5bet".into()).contains("unknown pot type"));
        assert!(bad(&|v| v["parts"][0]["pot_types"][0]["share"] = 0.5.into()).contains("pot types: shares add up"));
        assert!(bad(&|v| v["parts"][0]["pot_types"][0]["pot_bb"] = serde_json::json!([7.5, 4.5])).contains("pot_bb"));
        assert!(bad(&|v| v["parts"][0]["pot_types"][0]["pot_bb"] = serde_json::json!([4.5, 9000])).contains("pot_bb"));
        assert!(bad(&|v| v["parts"][0]["tables"][0]["stack_bb"] = serde_json::json!([0, 200])).contains("stack_bb"));
        assert!(bad(&|v| v["parts"][0]["tables"][0]["pot_scale"] = serde_json::json!([1, 50])).contains("pot_scale"));
        assert!(bad(&|v| v["parts"][0]["rake"][1]["pct"] = serde_json::json!([5, 5])).contains("fraction of the pot"));
        assert!(bad(&|v| v["parts"][0]["rake"][1]["cap_bb"] = serde_json::json!([0, 4])).contains("rake cap_bb"));
        assert!(bad(&|v| v["parts"][0]["rake"][0]["cap_bb"] = serde_json::json!([0, 4])).contains("cap of no rake"));
        // nothing but the known fields: a mix cannot carry a command, a path or an address
        assert!(bad(&|v| v["run"] = "calc.exe".into()).contains("unknown field"));
        assert!(bad(&|v| v["parts"][0]["url"] = "https://example.com".into()).contains("unknown field"));
        assert!(bad(&|v| v["parts"][0]["kind"] = "script".into()).contains("unknown variant"));
        let list = |name: &str, sha: &str| -> String {
            let part = serde_json::json!({"kind": "situations", "share": 1.0, "list": name, "sha256": sha});
            serde_json::from_value::<Mix>(mix(serde_json::json!([part]))).unwrap().check().err().unwrap_or_default()
        };
        assert_eq!(list("callfix-1", &"ab".repeat(32)), "");
        assert!(list("../x", &"ab".repeat(32)).contains("plain name"));
        assert!(list("callfix-1", "abc").contains("SHA-256"));
        assert!(list("callfix-1", &"AB".repeat(32)).contains("SHA-256"));
    }

    #[test]
    fn the_key_follows_what_is_drawn_and_nothing_else() {
        let a: Mix = serde_json::from_value(mix(serde_json::json!([random_part(1.0)]))).unwrap();
        let mut b = a.clone();
        b.note = "another note".into();
        b.withdrawn = true;
        assert_eq!(a.key(), b.key());
        assert_eq!(a.key().len(), 16);
        let mut c = a.clone();
        c.id = 3;
        assert_ne!(a.key(), c.key());
        let mut d = a.clone();
        if let Part::Random { tables, .. } = &mut d.parts[0] {
            tables[0].stack_bb = [25.0, 300.0];
        }
        assert_ne!(a.key(), d.key());
        // the same mix written with other spacing or number forms has the same key
        let text = serde_json::to_string_pretty(&mix(serde_json::json!([random_part(1.0)]))).unwrap().replace("4.5", "4.50");
        assert_eq!(serde_json::from_str::<Mix>(&text).unwrap().key(), a.key());
    }

    #[test]
    fn a_list_of_mixes_keeps_what_it_can_read() {
        let mut book = Book::default();
        let mut newer = mix(serde_json::json!([{"kind": "three_way", "share": 1.0, "seats": 3}]));
        newer["id"] = 4.into();
        newer["needs_generator"] = 6.into();
        let mut broken = mix(serde_json::json!([random_part(0.4)]));
        broken["id"] = 3.into();
        let mut one = mix(serde_json::json!([random_part(1.0)]));
        one["id"] = 1.into();
        let skipped = book.add_text(&file(vec![one, mix(serde_json::json!([random_part(1.0)])), broken, newer])).unwrap();
        assert_eq!(book.mixes.keys().copied().collect::<Vec<_>>(), [1, 2]);
        assert_eq!(skipped.len(), 1);
        assert!(skipped[0].contains("mix 3 is not usable"), "{skipped:?}");
        // the newest published mix needs generator 6: this build keeps to mix 2 and can say so
        assert_eq!(book.open_ids(), [2, 1]);
        assert_eq!(book.needs_update(), Some((4, 6)));
        // a later list withdraws mix 2 and the too-new mix: back to mix 1, nothing to update for
        let mut two = mix(serde_json::json!([random_part(1.0)]));
        two["withdrawn"] = true.into();
        let mut gone = mix(serde_json::json!([]));
        gone["id"] = 4.into();
        gone["needs_generator"] = 6.into();
        gone["withdrawn"] = true.into();
        let mut b2 = Book::default();
        b2.add_text(&file(vec![serde_json::json!({"id": 1, "needs_generator": 5, "note": "one", "parts": [random_part(1.0)]}), two, gone])).unwrap();
        assert_eq!(b2.open_ids(), [1]);
        assert_eq!(b2.needs_update(), None);
        assert!(Book::default().add_text("{}").unwrap_err().contains("not a gtopen-datagen-mixes file"));
        assert!(Book::default().add_text("<html>").unwrap_err().contains("not JSON"));
    }

    #[test]
    fn situations_are_drawn_from_their_list_on_random_flops() {
        let text = list_text("callfix-1", 5);
        let sha = sha256_hex(text.as_bytes());
        let part = serde_json::json!({"kind": "situations", "share": 0.5, "list": "callfix-1", "sha256": sha});
        let mut book = Book::default();
        book.add_text(&file(vec![mix(serde_json::json!([random_part(0.5), part]))])).unwrap();
        let job = datagen::mix_job("alice", 2, 0);
        assert!(book.inputs(2, job, 0, None).unwrap_err().contains("not loaded"));
        book.lists.insert(sha, SituationList::parse(&text).unwrap());
        let n = 2000;
        let (mut listed, mut first, mut boards) = (0, 0, BTreeSet::new());
        for i in 0..n {
            let ex = book.inputs(2, job, i, None).unwrap();
            assert_eq!(ex, book.inputs(2, job, i, None).unwrap());
            let Some(name) = &ex.situation else {
                assert!(ex.pot_type == "srp" || ex.pot_type == "3bet");
                continue;
            };
            listed += 1;
            let id: usize = name.strip_prefix("callfix-1/g1:").unwrap().parse().unwrap();
            first += (id == 0) as usize;
            assert_eq!((ex.pot_type.as_str(), ex.pot_bb, ex.stack_bb, ex.rake_pct, ex.rake_cap_bb),
                       ("3bet", 20.0 + id as f64, 90.0, 0.1, 3.4));
            assert_eq!(ex.range, datagen::example_inputs(77, id as u32).range);
            assert_eq!(datagen::check_real_inputs(&ex), None);
            boards.insert(ex.board.clone());
            // the record reads back the same, the situation's name included
            let back: ExampleInputs = serde_json::from_str(&serde_json::to_string(&ex).unwrap()).unwrap();
            assert_eq!(back, ex);
        }
        assert!((listed as f64 / n as f64 - 0.5).abs() < 0.04, "{listed}");
        // entry 0 has weight 3 of 7
        assert!((first as f64 / listed as f64 - 3.0 / 7.0).abs() < 0.05, "{first} of {listed}");
        assert!(boards.len() > 300, "{} flops", boards.len());
    }

    #[test]
    fn a_situation_list_is_checked() {
        assert!(SituationList::parse(&list_text("callfix-1", 3)).is_ok());
        let bad = |change: &dyn Fn(String) -> String| SituationList::parse(&change(list_text("callfix-1", 3))).unwrap_err();
        assert!(bad(&|t| t.replace("\"situations\":3", "\"situations\":4")).contains("header says 4"));
        assert!(bad(&|t| t.replace("gtopen-situations", "something-else")).contains("not a gtopen-situations"));
        assert!(bad(&|t| t.replace("\"list\":\"callfix-1\"", "\"list\":\"a/b\"")).contains("plain name"));
        assert!(bad(&|t| t.replace("g1:1", "g1:0")).contains("used twice"));
        assert!(bad(&|t| t.replace("\"pot_type\":\"3bet\"", "\"pot_type\":\"5bet\"")).contains("pot type"));
        assert!(bad(&|t| t.replace("\"stack_bb\":90.0", "\"stack_bb\":-1.0")).contains("stack"));
        assert!(bad(&|t| t.replace("\"rake_pct\":0.1", "\"rake_pct\":10.0")).contains("rake"));
        assert!(bad(&|t| t.replace("\"weight\":3.0", "\"weight\":0.0")).contains("weight"));
        assert!(bad(&|t| t.replace("\"type\":\"situation\"", "\"type\":\"example\"")).contains("not \"situation\""));
        assert!(bad(&|t| t.replace("\"about\"", "\"run\"")).contains("unknown field"));
        assert!(bad(&|t| t.lines().next().unwrap().to_string()).contains("no situations"));
    }

    #[test]
    fn the_published_list_is_followed_and_remembered() {
        let dir = std::env::temp_dir().join(format!("gtopen-mixsync-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(dir.join("published")).unwrap();
        let published = dir.join("published").join("mixes.json");
        let text = list_text("callfix-1", 4);
        let sha = sha256_hex(text.as_bytes());
        let mut sync = MixSync::open(&dir.join("cache"));
        sync.url = published.to_string_lossy().into_owned();
        sync.lists_url = dir.join("published").to_string_lossy().into_owned();
        sync.every = std::time::Duration::ZERO; // look again every time
        let newest = sync.book.open_ids()[0];
        // nothing published yet: the read fails and the newest built-in mix that needs no list stays
        // (a built-in mix that draws from a list waits for the list like any other)
        assert!(sync.refresh().is_err());
        let built_in = sync.choose().0.expect("a built-in mix that needs no list");
        assert!(built_in <= newest);
        // a new mix with a situation list whose file is not there yet: passed over, with the reason
        let mut next = mix(serde_json::json!([random_part(0.5), {"kind": "situations", "share": 0.5, "list": "callfix-1", "sha256": sha}]));
        next["id"] = (newest + 1).into();
        let mut all: Vec<serde_json::Value> = serde_json::from_str::<serde_json::Value>(BUILT_IN).unwrap()["mixes"].as_array().unwrap().clone();
        all.push(next);
        std::fs::write(&published, file(all.clone())).unwrap();
        assert_eq!(sync.refresh(), Ok(vec![]));
        let (id, notes) = sync.choose();
        assert_eq!(id, Some(built_in));
        assert!(notes[0].contains("situation list callfix-1"), "{notes:?}");
        // a file that is not the pinned one is refused
        std::fs::write(dir.join("published").join("callfix-1.jsonl"), list_text("callfix-1", 5)).unwrap();
        assert!(sync.choose().1[0].contains("SHA-256 differs"));
        // the right file: the new mix is chosen and drawn
        std::fs::write(dir.join("published").join("callfix-1.jsonl"), &text).unwrap();
        assert_eq!(sync.choose(), (Some(newest + 1), vec![]));
        let job = datagen::mix_job("alice", newest + 1, 0);
        assert!((0..50).any(|i| sync.book.inputs(newest + 1, job, i, None).unwrap().situation.is_some()));
        // a later start with no network still knows the new mix and its list
        std::fs::remove_dir_all(dir.join("published")).unwrap();
        let mut again = MixSync::open(&dir.join("cache"));
        again.url = published.to_string_lossy().into_owned();
        again.lists_url = dir.join("published").to_string_lossy().into_owned();
        assert!(again.refresh().is_err());
        assert_eq!(again.choose(), (Some(newest + 1), vec![]));
        // the list was read (tried) a moment ago: not again for a few minutes, here or in another
        // process that shares the folder
        assert!(again.refresh_if_due().is_none());
        assert!(MixSync::open(&dir.join("cache")).refresh_if_due().is_none());
        // and a list that would not load is not fetched again on every job either
        let mut all = all;
        all.push(serde_json::json!({"id": newest + 2, "needs_generator": 5, "note": "another list",
            "parts": [{"kind": "situations", "share": 1.0, "list": "missing", "sha256": "0".repeat(64)}]}));
        again.book.add_text(&file(all)).unwrap();
        let first = again.choose();
        assert_eq!(first.0, Some(newest + 1));
        assert!(first.1[0].contains("situation list missing"), "{:?}", first.1);
        assert!(again.failed.contains_key(&"0".repeat(64)));
        std::fs::create_dir_all(dir.join("published")).unwrap();
        std::fs::write(dir.join("published").join("missing.jsonl"), "x").unwrap();
        assert_eq!(again.choose().1, first.1, "the earlier answer, without reading the file again");
        let _ = std::fs::remove_dir_all(&dir);
    }
}
