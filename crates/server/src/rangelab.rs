//! Range Lab reference charts for the Preflop Lab.
//!
//! Range Lab (github.com/MatthewPDingle/range-lab) is Pan's preflop trainer
//! with the canonical preflop charts. Its data files are private, so
//! they are never committed here: the server reads them from local folders
//! (`cache/rangelab/`, which is gitignored, and the sibling `../Range Lab/`
//! checkout), or from the `;`-separated folders in `GTOPEN_RANGELAB_DIR`.
//!
//! Accepted files: `data.js` (`window.RANGE_DATA=…;`), `cash-data.js`
//! (`window.CASH_DATA=…;`) and raw crawl JSON (`{"v":1,"spots":[…]}`).
//! Each record is `[family, tag, gametype, players, depth, hero, vs, caller,
//! position, actions, freqs, evloss, reach, history(, open)]`, with hands in
//! ASCII-sorted class-name order, frequencies as base64url digits
//! (`round(v*63)`) and EV loss as `round(9*ln(1+loss/0.02))`. Records are
//! decoded into GTOpen's 169-class order (`class_label`) on request.

use serde::Deserialize;
use serde_json::{json, Value};
use std::collections::{BTreeMap, HashMap, HashSet, VecDeque};
use std::path::{Path, PathBuf};
use std::sync::{Arc, Mutex, OnceLock};
use std::time::SystemTime;

const B64: &[u8; 64] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_";

fn b64_digit(c: u8) -> Option<u8> {
    B64.iter().position(|&x| x == c).map(|p| p as u8)
}

fn valid_vec(s: &str) -> bool {
    s.len() == 169 && s.bytes().all(|c| b64_digit(c).is_some())
}

/// Range Lab hand k (ASCII-sorted class names) -> GTOpen class index.
fn rl_to_class() -> &'static [usize; 169] {
    static MAP: OnceLock<[usize; 169]> = OnceLock::new();
    MAP.get_or_init(|| {
        let mut names: Vec<(String, usize)> =
            (0..169).map(|i| (solver::preflop::equity::class_label(i), i)).collect();
        names.sort();
        let mut out = [0usize; 169];
        for (k, (_, idx)) in names.into_iter().enumerate() {
            out[k] = idx;
        }
        out
    })
}

/// One 169-character vector, in GTOpen class order.
fn decode_vec(s: &str, f: impl Fn(u8) -> f64) -> Vec<f64> {
    let map = rl_to_class();
    let mut out = vec![0.0; 169];
    for (k, c) in s.bytes().enumerate() {
        out[map[k]] = f(b64_digit(c).unwrap_or(0));
    }
    out
}

fn freq_digit(d: u8) -> f64 {
    d as f64 / 63.0
}

#[derive(Clone)]
struct RawAction {
    code: String,
    size: f64,
    allin: bool,
    total_freq: f64,
}

#[derive(Clone)]
struct Record {
    family: String,
    tag: String,
    gametype: String,
    players: usize,
    depth: f64,
    hero: i64,
    vs: i64,
    caller: i64,
    position: String,
    actions: Vec<RawAction>,
    freqs: Vec<String>,
    loss: Vec<String>,
    reach: String,
    hist: String,
    open: Option<String>,
    source: String,
}

impl Record {
    fn parse(v: &Value, source: &str) -> Option<Record> {
        let a = v.as_array()?;
        if a.len() != 14 && a.len() != 15 {
            return None;
        }
        let strs = |x: &Value| -> Option<Vec<String>> {
            x.as_array()?.iter().map(|s| s.as_str().map(str::to_string)).collect()
        };
        let actions: Vec<RawAction> = a[9]
            .as_array()?
            .iter()
            .map(|x| {
                let x = x.as_array()?;
                Some(RawAction {
                    code: x.first()?.as_str()?.to_string(),
                    size: x.get(2)?.as_f64()?,
                    allin: x.get(3)?.as_f64()? != 0.0,
                    total_freq: x.get(4)?.as_f64()?,
                })
            })
            .collect::<Option<_>>()?;
        let freqs = strs(&a[10])?;
        let loss = strs(&a[11])?;
        let reach = a[12].as_str()?.to_string();
        let ok = !actions.is_empty()
            && actions.len() == freqs.len()
            && actions.len() == loss.len()
            && freqs.iter().chain(&loss).all(|s| valid_vec(s))
            && (reach.is_empty() || valid_vec(&reach));
        if !ok {
            return None;
        }
        Some(Record {
            family: a[0].as_str()?.to_string(),
            tag: a[1].as_str()?.to_string(),
            gametype: a[2].as_str()?.to_string(),
            players: a[3].as_u64()? as usize,
            depth: a[4].as_f64()?,
            hero: a[5].as_i64()?,
            vs: a[6].as_i64()?,
            caller: a[7].as_i64()?,
            position: a[8].as_str()?.to_string(),
            actions,
            freqs,
            loss,
            reach,
            hist: a[13].as_str().unwrap_or("").to_string(),
            open: a.get(14).and_then(Value::as_str).map(str::to_string),
            source: source.to_string(),
        })
    }

    /// The configuration axis next to depth: the open size in cash games,
    /// the gametype (chip EV / ICM stage) in tournaments.
    fn variant(&self) -> &str {
        self.open.as_deref().unwrap_or(&self.gametype)
    }

    /// Per-action frequencies (rows) per class, renormalized per hand: the
    /// 64-level rounding leaves sums near (not at) 1, and Range Lab
    /// renormalizes the same way.
    fn strategy(&self) -> Vec<Vec<f64>> {
        let mut strategy: Vec<Vec<f64>> = self.freqs.iter().map(|s| decode_vec(s, freq_digit)).collect();
        for h in 0..169 {
            let t: f64 = strategy.iter().map(|row| row[h]).sum();
            if t > 0.0 {
                for row in strategy.iter_mut() {
                    row[h] /= t;
                }
            }
        }
        strategy
    }

    /// Kind-only history tokens (F, X, C, R), sizes dropped.
    fn line(&self) -> Vec<char> {
        line_tokens(&self.hist)
    }
}

fn line_tokens(hist: &str) -> Vec<char> {
    hist.split('-')
        .filter(|t| !t.is_empty())
        .map(|t| t.chars().next().unwrap().to_ascii_uppercase())
        .collect()
}

/// Leading number of an open-size label ("2.5x", "5bb") in big blinds.
fn open_bb(open: &str) -> Option<f64> {
    let n: String = open.chars().take_while(|c| c.is_ascii_digit() || *c == '.').collect();
    n.parse().ok()
}

fn game_label(tag: &str) -> String {
    match tag {
        "reg" => "Live cash · 8-max · 10% rake".into(),
        "str" => "Live cash · 8-max · 2bb straddle".into(),
        "cev9" => "Tournament · 9-max · chip EV".into(),
        "icm8" => "Tournament · 8-max · chip EV and ICM stages".into(),
        other => other.into(),
    }
}

/// Tournament stages in the order a tournament reaches them.
const STAGES: [&str; 7] = [
    "MTTGeneralV2",
    "MTTGeneral_8m",
    "MTTGeneral_ICM8m1000PTPCT50",
    "MTTGeneral_ICM8m1000PTBUBBLE152PT",
    "MTTGeneral_ICM8m1000PTPCT10",
    "MTTGeneral_ICM8m1000PTT2",
    "MTTGeneral_ICM8m1000PTFT",
];

/// Sort key for variants: open size in bb, else tournament stage order.
fn variant_rank(variant: &str) -> f64 {
    open_bb(variant).unwrap_or_else(|| STAGES.iter().position(|s| *s == variant).unwrap_or(STAGES.len()) as f64)
}

fn variant_label(variant: &str) -> String {
    match variant {
        "MTTGeneralV2" | "MTTGeneral_8m" => "Chip EV".into(),
        "MTTGeneral_ICM8m1000PTPCT50" => "Half the field left".into(),
        "MTTGeneral_ICM8m1000PTBUBBLE152PT" => "Bubble".into(),
        "MTTGeneral_ICM8m1000PTPCT10" => "In the money, 10% left".into(),
        "MTTGeneral_ICM8m1000PTT2" => "Two tables left".into(),
        "MTTGeneral_ICM8m1000PTFT" => "Final table".into(),
        v if open_bb(v).is_some() => format!("{v} open"),
        v => v.into(),
    }
}

/// Situations in the order a hand reaches them.
fn family_rank(family: &str) -> usize {
    const ORDER: [&str; 11] = [
        "RFI", "BBvsLimp", "BBvsOpen", "vsOpen", "Squeeze", "vs3bet", "OpenVs3bet", "vs4bet", "vsJam", "BBvsJam", "OpenVsJam",
    ];
    ORDER.iter().position(|f| *f == family).unwrap_or(ORDER.len())
}

fn family_label(family: &str, tag: &str) -> String {
    match family {
        "RFI" => "First in".into(),
        "BBvsOpen" if tag == "str" => "Straddle vs open".into(),
        "BBvsOpen" => "BB vs open".into(),
        "BBvsLimp" if tag == "str" => "Straddle vs limp".into(),
        "BBvsLimp" => "BB vs SB limp".into(),
        "vsOpen" => "Facing an open".into(),
        "vs3bet" | "OpenVs3bet" => "Facing a 3-bet".into(),
        "vs4bet" => "Facing a 4-bet".into(),
        "Squeeze" => "Open + caller".into(),
        "BBvsJam" => "BB vs jam".into(),
        "vsJam" => "Facing a jam".into(),
        "OpenVsJam" => "Opened, facing a jam".into(),
        other => other.into(),
    }
}

struct FileInfo {
    path: String,
    records: usize,
    error: Option<String>,
}

pub struct Library {
    dirs: Vec<String>,
    files: Vec<FileInfo>,
    records: Vec<Record>,
    /// tag -> seat names, from every record's (hero, position).
    positions: BTreeMap<String, Vec<String>>,
    /// (tag, variant, depth bits, history) -> the chart decided there.
    by_line: HashMap<LineKey, usize>,
    /// Every history prefix some chart starts from, same key shape.
    prefixes: HashSet<LineKey>,
}

type LineKey = (String, String, u64, String);

type Stamp = Vec<(PathBuf, Option<SystemTime>, u64)>;

fn search_dirs() -> Vec<PathBuf> {
    match std::env::var("GTOPEN_RANGELAB_DIR") {
        Ok(v) if !v.trim().is_empty() => {
            v.split(';').filter(|s| !s.trim().is_empty()).map(|s| PathBuf::from(s.trim())).collect()
        }
        _ => vec![PathBuf::from("cache/rangelab"), PathBuf::from("../Range Lab")],
    }
}

/// Candidate data files, oldest first so newer crawls win on merge.
fn candidate_files(dirs: &[PathBuf]) -> Stamp {
    let mut out: Stamp = Vec::new();
    for dir in dirs {
        let Ok(rd) = std::fs::read_dir(dir) else { continue };
        for e in rd.flatten() {
            let p = e.path();
            let ext = p.extension().and_then(|x| x.to_str()).unwrap_or("").to_ascii_lowercase();
            if ext != "js" && ext != "json" {
                continue;
            }
            let Ok(md) = e.metadata() else { continue };
            if md.is_file() {
                out.push((p, md.modified().ok(), md.len()));
            }
        }
    }
    out.sort_by(|a, b| a.1.cmp(&b.1).then_with(|| a.0.cmp(&b.0)));
    out
}

fn read_spots(path: &Path) -> Result<Vec<Value>, String> {
    let text = std::fs::read_to_string(path).map_err(|e| e.to_string())?;
    let mut body = text.trim().trim_start_matches('\u{feff}');
    if body.starts_with("window.") {
        let eq = body.find('=').ok_or("no assignment")?;
        body = body[eq + 1..].trim().trim_end_matches(';');
    }
    if !body.starts_with('{') {
        return Err("not a Range Lab data file".into());
    }
    let mut v: Value = serde_json::from_str(body).map_err(|e| e.to_string())?;
    match v.get_mut("spots").map(Value::take) {
        Some(Value::Array(a)) => Ok(a),
        _ => Err("no spots array".into()),
    }
}

impl Library {
    fn load(dirs: &[PathBuf], files: &Stamp) -> Library {
        let mut merged: HashMap<(String, String, String, String, i64, i64, i64), Record> = HashMap::new();
        let mut infos = Vec::new();
        for (path, _, _) in files {
            let name = path.display().to_string();
            match read_spots(path) {
                Ok(spots) => {
                    let mut n = 0;
                    for v in &spots {
                        if let Some(r) = Record::parse(v, &name) {
                            // Range Lab's merge key; the gametype carries the open size.
                            let key = (
                                r.gametype.clone(),
                                format!("{}", r.depth),
                                r.hist.clone(),
                                r.family.clone(),
                                r.hero,
                                r.vs,
                                r.caller,
                            );
                            merged.insert(key, r);
                            n += 1;
                        }
                    }
                    let error = (n == 0).then(|| "no valid Range Lab records".to_string());
                    infos.push(FileInfo { path: name, records: n, error });
                }
                // Unrelated .js/.json files in the folder are expected; list
                // them only when they look like they were meant to be data.
                Err(e) => {
                    let lower = path.file_name().map(|f| f.to_string_lossy().to_ascii_lowercase()).unwrap_or_default();
                    if lower.contains("range") || lower.contains("data") {
                        infos.push(FileInfo { path: name, records: 0, error: Some(e) });
                    }
                }
            }
        }
        let mut records: Vec<Record> = merged.into_values().collect();
        records.sort_by(|a, b| {
            (&a.tag, variant_rank(a.variant()), a.variant(), a.depth, family_rank(&a.family), &a.family, a.hero, a.vs, a.caller)
                .partial_cmp(&(&b.tag, variant_rank(b.variant()), b.variant(), b.depth, family_rank(&b.family), &b.family, b.hero, b.vs, b.caller))
                .unwrap_or(std::cmp::Ordering::Equal)
        });
        let mut positions: BTreeMap<String, Vec<String>> = BTreeMap::new();
        for r in &records {
            let seats = positions.entry(r.tag.clone()).or_default();
            if seats.len() < r.players {
                seats.resize(r.players, String::new());
            }
            if r.hero >= 0 && (r.hero as usize) < seats.len() {
                seats[r.hero as usize] = r.position.clone();
            }
        }
        for seats in positions.values_mut() {
            for (i, s) in seats.iter_mut().enumerate() {
                if s.is_empty() {
                    *s = format!("Seat {}", i + 1);
                }
            }
        }
        let mut by_line = HashMap::new();
        let mut prefixes = HashSet::new();
        for (i, r) in records.iter().enumerate() {
            let key = |h: &str| (r.tag.clone(), r.variant().to_string(), r.depth.to_bits(), h.to_string());
            by_line.insert(key(&r.hist), i);
            let tokens: Vec<&str> = r.hist.split('-').filter(|t| !t.is_empty()).collect();
            for k in 0..=tokens.len() {
                prefixes.insert(key(&tokens[..k].join("-")));
            }
        }
        Library {
            dirs: dirs.iter().map(|d| d.display().to_string()).collect(),
            files: infos,
            records,
            positions,
            by_line,
            prefixes,
        }
    }

    fn seat_name(&self, tag: &str, seat: i64) -> String {
        if seat < 0 {
            return String::new();
        }
        self.positions
            .get(tag)
            .and_then(|p| p.get(seat as usize))
            .cloned()
            .unwrap_or_else(|| format!("Seat {}", seat + 1))
    }

    fn situation_label(&self, r: &Record) -> String {
        let mut s = self.seat_name(&r.tag, r.hero);
        if r.vs >= 0 {
            s += &format!(" vs {}", self.seat_name(&r.tag, r.vs));
        }
        if r.caller >= 0 {
            s += &format!(" + {} call", self.seat_name(&r.tag, r.caller));
        }
        s
    }

    pub fn summary(&self) -> Value {
        // tag -> (players, variants in sort order with their depths, count)
        let mut games: BTreeMap<&str, (usize, Vec<(&str, Vec<f64>)>, usize)> = BTreeMap::new();
        for r in &self.records {
            let g = games.entry(&r.tag).or_insert((r.players, Vec::new(), 0));
            if g.1.last().map(|v| v.0) != Some(r.variant()) {
                g.1.push((r.variant(), Vec::new()));
            }
            let depths = &mut g.1.last_mut().unwrap().1;
            if !depths.contains(&r.depth) {
                depths.push(r.depth);
            }
            g.2 += 1;
        }
        let games: Vec<Value> = games
            .into_iter()
            .map(|(tag, (players, variants, count))| {
                json!({
                    "tag": tag,
                    "label": game_label(tag),
                    "players": players,
                    "positions": self.positions.get(tag),
                    "variants": variants.iter().map(|(v, depths)| json!({
                        "key": v, "label": variant_label(v), "open_bb": open_bb(v), "depths": depths,
                    })).collect::<Vec<_>>(),
                    "spots": count,
                })
            })
            .collect();
        json!({
            "dirs": self.dirs,
            "files": self.files.iter().map(|f| json!({"path": f.path, "records": f.records, "error": f.error})).collect::<Vec<_>>(),
            "total": self.records.len(),
            "games": games,
        })
    }

    pub fn situations(&self, tag: &str, variant: &str, depth: f64) -> Value {
        let list: Vec<Value> = self
            .records
            .iter()
            .enumerate()
            .filter(|(_, r)| r.tag == tag && r.variant() == variant && r.depth == depth)
            .map(|(id, r)| {
                json!({
                    "id": id,
                    "family": r.family,
                    "family_label": family_label(&r.family, &r.tag),
                    "label": self.situation_label(r),
                    "hist": r.hist,
                })
            })
            .collect();
        json!(list)
    }

    pub fn spot(&self, id: usize) -> Option<Value> {
        let r = self.records.get(id)?;
        let loss = |d: u8| 0.02 * ((d as f64 / 9.0).exp() - 1.0);
        let strategy = r.strategy();
        let ev_loss: Vec<f64> = r.loss.iter().flat_map(|s| decode_vec(s, loss)).collect();
        let reach = (!r.reach.is_empty()).then(|| decode_vec(&r.reach, freq_digit));
        let actions: Vec<Value> = r
            .actions
            .iter()
            .map(|a| {
                let (kind, label) = match a.code.chars().next().unwrap_or('F') {
                    'F' => ("fold", "Fold".to_string()),
                    'X' => ("check", "Check".to_string()),
                    'C' if a.allin => ("call", format!("Call all-in {} bb", fmt_bb(a.size))),
                    'C' if r.family == "RFI" => ("call", "Limp".to_string()),
                    'C' => ("call", format!("Call {} bb", fmt_bb(a.size))),
                    _ if a.allin => ("jam", format!("All-in {} bb", fmt_bb(a.size))),
                    _ => ("raise", format!("Raise to {} bb", fmt_bb(a.size))),
                };
                json!({"code": a.code, "kind": kind, "label": label, "to": a.size, "freq": a.total_freq})
            })
            .collect();
        Some(json!({
            "id": id,
            "tag": r.tag,
            "game": game_label(&r.tag),
            "variant": r.variant(),
            "variant_label": variant_label(r.variant()),
            "gametype": r.gametype,
            "family": r.family,
            "family_label": family_label(&r.family, &r.tag),
            "label": self.situation_label(r),
            "players": r.players,
            "depth": r.depth,
            "hero": r.hero,
            "hero_pos": r.position,
            "positions": self.positions.get(&r.tag),
            "hist": r.hist,
            "source": r.source,
            "actions": actions,
            "strategy": strategy.concat(),
            "ev_loss": ev_loss,
            "reach": reach,
        }))
    }

    /// Best chart for a preflop line: same game and seat count, identical
    /// kind-only action history; then the nearest open size and depth.
    pub fn find(&self, q: &MatchRequest) -> Option<usize> {
        let line: Vec<char> = q.line.iter().filter_map(|t| t.chars().next()).map(|c| c.to_ascii_uppercase()).collect();
        let open_dist = |r: &Record| match (&q.variant, q.open_to, open_bb(r.variant())) {
            (Some(v), _, _) if v == r.variant() => 0.0,
            (Some(_), _, _) => 1e6,
            (None, Some(o), Some(x)) => (x - o).abs(),
            _ => 0.0,
        };
        self.records
            .iter()
            .enumerate()
            .filter(|(_, r)| r.tag == q.tag && r.players == q.players && r.line() == line)
            .min_by(|(_, a), (_, b)| {
                let ka = (open_dist(a), ((a.depth - q.stack) / q.stack.max(1.0)).abs());
                let kb = (open_dist(b), ((b.depth - q.stack) / q.stack.max(1.0)).abs());
                ka.partial_cmp(&kb).unwrap_or(std::cmp::Ordering::Equal)
            })
            .map(|(i, _)| i)
    }
}

// ----- the canonical action tree -----
//
// A game (tag + open size or stage + depth) is walked like a preflop tree:
// each chart is the decision at the history it records, and taking one of
// its actions appends that action's code to the history. Seats without a
// chart fold when later charts assume they do (Range Lab's lines record those
// folds, e.g. `R3-R9-F-F-F-F-F-F` for the opener facing a 3-bet); a seat with
// neither ends the line. Reach multiplies each seat's chart frequencies along
// the line, so a flop node carries both conditional ranges.

/// A line through one Range Lab game, as action indices like /api/preflop/node.
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TreeRequest {
    pub tag: String,
    pub variant: String,
    pub depth: f64,
    #[serde(default)]
    pub path: Vec<usize>,
    /// Follow seats without a chart (forced folds) past the end of `path`,
    /// so a branch lands on the next real decision. The response's `path`
    /// includes the added folds.
    #[serde(default)]
    pub extend: bool,
    /// Export only: rake carried into the postflop spot.
    #[serde(default)]
    pub rake_pct: f64,
    #[serde(default)]
    pub rake_cap: f64,
}

fn class_combos(h: usize) -> f64 {
    let (hi, lo, suited) = solver::preflop::equity::class_parts(h);
    if hi == lo {
        6.0
    } else if suited {
        4.0
    } else {
        12.0
    }
}

#[derive(Clone)]
struct TreeAction {
    code: String,
    kind: &'static str,
    label: String,
    to: f64,
}

#[derive(Clone, Copy, PartialEq)]
enum Point {
    Chart(usize),
    /// No chart for this seat, but later charts assume it folds.
    Forced,
    /// No chart for this seat and none further down this line.
    Missing,
    FoldWin,
    Flop,
}

struct Walk<'a> {
    lib: &'a Library,
    req: &'a TreeRequest,
    positions: Vec<String>,
    posts: Vec<f64>,
    ante: f64,
    bet: Vec<f64>,
    folded: Vec<bool>,
    queue: VecDeque<usize>,
    level: f64,
    raises: usize,
    hist: Vec<String>,
    /// Fraction of each class's combos each seat still holds.
    reach: Vec<Vec<f64>>,
}

impl<'a> Walk<'a> {
    fn new(lib: &'a Library, req: &'a TreeRequest) -> Result<Self, String> {
        let positions = lib.positions.get(&req.tag).cloned().ok_or("no Range Lab charts for this game")?;
        let n = positions.len();
        // Range Lab's table setup: blinds by name, a 2 bb straddle acting
        // last, and a 12.5% ante in the tournament games.
        let posts: Vec<f64> = positions
            .iter()
            .map(|p| match p.as_str() {
                "SB" => 0.5,
                "BB" => 1.0,
                "STR" => 2.0,
                _ => 0.0,
            })
            .collect();
        let ante = if req.tag.starts_with("cev") || req.tag.starts_with("icm") { 0.125 } else { 0.0 };
        Ok(Walk {
            lib,
            req,
            level: posts.iter().cloned().fold(0.0, f64::max),
            bet: posts.clone(),
            posts,
            ante,
            folded: vec![false; n],
            queue: (0..n).collect(),
            raises: 0,
            hist: Vec::new(),
            reach: vec![vec![1.0; 169]; n],
            positions,
        })
    }

    fn n(&self) -> usize {
        self.positions.len()
    }

    fn pot(&self) -> f64 {
        self.bet.iter().sum::<f64>() + self.ante * self.n() as f64
    }

    fn live(&self) -> Vec<bool> {
        self.folded.iter().map(|f| !f).collect()
    }

    fn key(&self, hist: &str) -> LineKey {
        (self.req.tag.clone(), self.req.variant.clone(), self.req.depth.to_bits(), hist.to_string())
    }

    fn all_in(&self, p: usize) -> bool {
        self.bet[p] >= self.req.depth - 1e-9
    }

    /// What happens next, and who acts there.
    fn point(&mut self) -> (Point, Option<usize>) {
        if self.folded.iter().filter(|f| !**f).count() <= 1 {
            return (Point::FoldWin, None);
        }
        while let Some(&p) = self.queue.front() {
            if self.folded[p] || self.all_in(p) {
                self.queue.pop_front();
            } else {
                break;
            }
        }
        let Some(&p) = self.queue.front() else { return (Point::Flop, None) };
        let hist = self.hist.join("-");
        if let Some(&id) = self.lib.by_line.get(&self.key(&hist)) {
            if self.lib.records[id].hero == p as i64 {
                return (Point::Chart(id), Some(p));
            }
        }
        let fold = if hist.is_empty() { "F".to_string() } else { format!("{hist}-F") };
        if self.lib.prefixes.contains(&self.key(&fold)) {
            (Point::Forced, Some(p))
        } else {
            (Point::Missing, Some(p))
        }
    }

    fn actions(&self, point: Point) -> Vec<TreeAction> {
        let depth = self.req.depth;
        let fold = || TreeAction { code: "F".into(), kind: "fold", label: "Fold".into(), to: 0.0 };
        match point {
            Point::Chart(id) => self.lib.records[id]
                .actions
                .iter()
                .map(|a| match a.code.chars().next().unwrap_or('F') {
                    'F' => fold(),
                    'X' => TreeAction { code: a.code.clone(), kind: "check", label: "Check".into(), to: self.level },
                    'C' => {
                        let to = if a.allin { depth } else { self.level.min(depth) };
                        TreeAction { code: a.code.clone(), kind: "call", label: format!("Call {}", fmt_bb(to)), to }
                    }
                    _ => {
                        let size = if a.code == "RAI" { depth } else { a.size };
                        if a.code == "RAI" || a.allin || size >= depth - 0.2 {
                            TreeAction { code: a.code.clone(), kind: "jam", label: format!("All-in {}", fmt_bb(depth)), to: depth }
                        } else {
                            let verb = if self.raises == 0 { "Raise".to_string() } else { format!("{}-bet", self.raises + 2) };
                            TreeAction { code: a.code.clone(), kind: "raise", label: format!("{verb} {}", fmt_bb(size)), to: size }
                        }
                    }
                })
                .collect(),
            Point::Forced => vec![fold()],
            _ => Vec::new(),
        }
    }

    fn sigma(&self, point: Point) -> Vec<Vec<f64>> {
        match point {
            Point::Chart(id) => self.lib.records[id].strategy(),
            Point::Forced => vec![vec![1.0; 169]],
            _ => Vec::new(),
        }
    }

    /// Combo-weighted frequency of each action over the actor's range here.
    fn freqs(&self, p: usize, sigma: &[Vec<f64>]) -> Vec<f64> {
        let w: Vec<f64> = (0..169).map(|h| self.reach[p][h] * class_combos(h)).collect();
        let tot: f64 = w.iter().sum();
        sigma
            .iter()
            .map(|row| if tot > 0.0 { (0..169).map(|h| w[h] * row[h]).sum::<f64>() / tot } else { 0.0 })
            .collect()
    }

    fn apply(&mut self, p: usize, act: &TreeAction, row: &[f64]) {
        for (r, f) in self.reach[p].iter_mut().zip(row) {
            *r *= f;
        }
        self.hist.push(act.code.clone());
        self.queue.pop_front();
        match act.kind {
            "fold" => self.folded[p] = true,
            "check" => {}
            "call" => self.bet[p] = act.to,
            _ => {
                self.raises += 1;
                self.bet[p] = act.to;
                self.level = act.to;
                let n = self.n();
                self.queue = (1..n).map(|k| (p + k) % n).filter(|&q| !self.folded[q]).collect();
            }
        }
    }

    /// Postflop order: the small blind first, then around the table.
    fn postflop_order(&self) -> Vec<usize> {
        let n = self.n();
        let sb = self.positions.iter().position(|p| p == "SB").unwrap_or(0);
        (0..n).map(|k| (sb + k) % n).collect()
    }

    fn eff_stack(&self) -> f64 {
        (0..self.n())
            .filter(|&i| !self.folded[i])
            .map(|i| self.req.depth - self.ante - self.bet[i])
            .fold(f64::MAX, f64::min)
            .max(0.0)
    }
}

struct TreeRun<'a> {
    walk: Walk<'a>,
    point: Point,
    actor: Option<usize>,
    history: Vec<Value>,
    path: Vec<usize>,
}

fn point_kind(point: Point) -> &'static str {
    match point {
        Point::FoldWin => "fold_win",
        Point::Flop => "pot_share",
        _ => "action",
    }
}

fn actions_json(acts: &[TreeAction], freqs: &[f64]) -> Vec<Value> {
    acts.iter()
        .enumerate()
        .map(|(i, a)| json!({"label": a.label, "kind": a.kind, "to": a.to, "code": a.code, "freq": freqs.get(i).copied().unwrap_or(0.0)}))
        .collect()
}

impl Library {
    fn run<'a>(&'a self, req: &'a TreeRequest) -> Result<TreeRun<'a>, String> {
        let mut walk = Walk::new(self, req)?;
        let mut path = req.path.clone();
        let mut history = Vec::new();
        let mut i = 0;
        loop {
            let (point, actor) = walk.point();
            let acts = walk.actions(point);
            let sigma = walk.sigma(point);
            let freqs = actor.map(|p| walk.freqs(p, &sigma)).unwrap_or_default();
            let next = if i < path.len() {
                Some(path[i])
            } else if req.extend && point == Point::Forced {
                path.push(0);
                Some(0)
            } else {
                None
            };
            let step = |chosen: Option<usize>| {
                json!({
                    "kind": point_kind(point),
                    "actor_pos": actor.map(|p| walk.positions[p].clone()).unwrap_or_default(),
                    "pot": walk.pot(),
                    "actions": actions_json(&acts, &freqs),
                    "chosen": chosen,
                    "strategy_note": Value::Null,
                    "forced": point == Point::Forced,
                })
            };
            match next {
                Some(a) => {
                    let p = actor.filter(|_| a < acts.len()).ok_or("bad path")?;
                    history.push(step(Some(a)));
                    walk.apply(p, &acts[a], &sigma[a]);
                    i += 1;
                }
                None => {
                    history.push(step(None));
                    return Ok(TreeRun { walk, point, actor, history, path });
                }
            }
        }
    }

    /// The node at the end of `req.path`, shaped like /api/preflop/node.
    pub fn tree(&self, req: &TreeRequest) -> Result<Value, String> {
        let TreeRun { walk, point, actor, history, path } = self.run(req)?;
        let live = walk.live();
        let n_live = live.iter().filter(|l| **l).count();
        let acts = walk.actions(point);
        let sigma = walk.sigma(point);
        let freqs = actor.map(|p| walk.freqs(p, &sigma)).unwrap_or_default();
        let pos = |p: usize| walk.positions[p].clone();
        let (strategy_note, note, chart) = match (point, actor) {
            (Point::Missing, Some(p)) => (
                Some(format!(
                    "Range Lab has no chart for {} after this line. Its charts cover unopened pots, single raises (with one caller for squeezes), 3-bets and 4-bets, and the big blind against a small-blind limp. Pick another action in the ribbon.",
                    pos(p)
                )),
                None,
                Value::Null,
            ),
            (Point::Forced, Some(p)) => (
                None,
                Some(format!("Range Lab has no chart for {} here. Its later charts assume {} folds, so the line continues with a fold.", pos(p), pos(p))),
                Value::Null,
            ),
            (Point::Chart(id), _) => {
                let r = &self.records[id];
                (None, None, json!({"id": id, "label": self.situation_label(r), "family_label": family_label(&r.family, &r.tag)}))
            }
            _ => (None, None, Value::Null),
        };
        let flop = point == Point::Flop;
        let eff = walk.eff_stack();
        Ok(json!({
            "kind": point_kind(point),
            "actor": actor,
            "actor_pos": actor.map(pos),
            "positions": walk.positions,
            "posts": walk.posts,
            "pot": walk.pot(),
            "invested": walk.bet,
            "live": live,
            "actions": actions_json(&acts, &freqs),
            "strategy": if strategy_note.is_none() && !sigma.is_empty() { Some(sigma.concat()) } else { None },
            "reach": actor.map(|p| walk.reach[p].clone()),
            "strategy_note": strategy_note,
            "note": note,
            "chart": chart,
            "exportable": flop && n_live == 2 && eff > 0.0,
            "spr": if flop { Some(eff / walk.pot()) } else { None },
            "history": history,
            "reaches_all": (0..walk.n()).map(|i| if live[i] { walk.reach[i].clone() } else { Vec::new() }).collect::<Vec<_>>(),
            "branch_probability": 1.0,
            "low_reach": false,
            "path": path,
            "game": {"label": game_label(&req.tag), "variant_label": variant_label(&req.variant), "depth": req.depth},
        }))
    }

    /// A heads-up flop at the end of `req.path`, in the shape
    /// /api/preflop/export returns.
    pub fn export(&self, req: &TreeRequest) -> Result<Value, String> {
        let TreeRun { walk, point, .. } = self.run(req)?;
        let live: Vec<usize> = walk.postflop_order().into_iter().filter(|&i| !walk.folded[i]).collect();
        if point != Point::Flop || live.len() != 2 {
            return Err("export needs a flop with exactly two players".into());
        }
        let eff = walk.eff_stack();
        if eff <= 0.0 {
            return Err("both players are all-in; there is no postflop play to solve".into());
        }
        let range_of = |seat: usize| -> String {
            (0..169)
                .filter_map(|h| {
                    let w = walk.reach[seat][h].min(1.0);
                    let label = solver::preflop::equity::class_label(h);
                    if w > 0.995 {
                        Some(label)
                    } else if w > 0.005 {
                        Some(format!("{label}:{w:.3}"))
                    } else {
                        None
                    }
                })
                .collect::<Vec<_>>()
                .join(",")
        };
        let (oop, ip) = (live[0], live[1]);
        Ok(json!({
            "pot_type": match walk.raises { 0 => "limped", 1 => "single_raised", _ => "three_bet_plus" },
            "oop_pos": walk.positions[oop],
            "ip_pos": walk.positions[ip],
            "range_oop": range_of(oop),
            "range_ip": range_of(ip),
            "pot_bb": walk.pot(),
            "eff_stack_bb": eff,
            "rake_pct": req.rake_pct,
            "rake_cap": req.rake_cap,
            "source": format!("Range Lab · {} · {} · {} bb", game_label(&req.tag), variant_label(&req.variant), fmt_bb(req.depth)),
        }))
    }
}

fn fmt_bb(x: f64) -> String {
    let s = format!("{:.2}", x);
    s.trim_end_matches('0').trim_end_matches('.').to_string()
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MatchRequest {
    pub tag: String,
    pub players: usize,
    /// Kind-only tokens of the actions before the decision: F, X, C, R.
    pub line: Vec<String>,
    pub stack: f64,
    #[serde(default)]
    pub open_to: Option<f64>,
    #[serde(default)]
    pub variant: Option<String>,
}

/// The current library, reloaded when any data file is added, removed or
/// changed (the folder listing is cheap; parsing the files is not).
pub fn library() -> Arc<Library> {
    static CACHE: OnceLock<Mutex<Option<(Stamp, Arc<Library>)>>> = OnceLock::new();
    let dirs = search_dirs();
    let stamp = candidate_files(&dirs);
    let mut guard = CACHE.get_or_init(|| Mutex::new(None)).lock().unwrap_or_else(|p| p.into_inner());
    if let Some((s, lib)) = guard.as_ref() {
        if *s == stamp {
            return lib.clone();
        }
    }
    let lib = Arc::new(Library::load(&dirs, &stamp));
    *guard = Some((stamp, lib.clone()));
    lib
}

#[cfg(test)]
mod tests {
    use super::*;

    fn rec(fam: &str, hero: i64, vs: i64, hist: &str, open: &str, depth: f64, first: char) -> Value {
        let f: String = std::iter::repeat(first).take(169).collect();
        let zero: String = std::iter::repeat('A').take(169).collect();
        json!([fam, "reg", format!("Cash_{open}"), 8, depth, hero, vs, -1, "BTN",
            [["F","F",0,0,0.5],["R9","R",9,0,0.5]], [zero.clone(), f], [zero.clone(), zero], "", hist, open])
    }

    /// A 169-character chart vector from a per-class function.
    fn vec_of(f: impl Fn(usize) -> f64) -> String {
        let map = rl_to_class();
        (0..169).map(|k| B64[(f(map[k]) * 63.0).round() as usize] as char).collect()
    }

    #[test]
    fn walks_charts_as_a_tree_and_exports_the_flop() {
        // 3-handed: BTN opens AA only; SB has no chart (BB's chart assumes
        // SB folds); BB calls with everything.
        const AA: usize = 12 * 14;
        let rec = |fam: &str, hero: i64, pos: &str, hist: &str, acts: Value, freqs: Vec<String>| {
            let n = freqs.len();
            json!([fam, "reg", "Cash3_R3", 3, 100.0, hero, -1, -1, pos, acts, freqs,
                vec![vec_of(|_| 0.0); n], "", hist, "3x"])
        };
        let records = vec![
            rec("RFI", 0, "BTN", "", json!([["F","F",0,0,0.9],["R3","R",3,0,0.1]]),
                vec![vec_of(|h| if h == AA { 0.0 } else { 1.0 }), vec_of(|h| if h == AA { 1.0 } else { 0.0 })]),
            rec("BBvsOpen", 2, "BB", "R3-F", json!([["F","F",0,0,0.0],["C","C",3,0,1.0]]),
                vec![vec_of(|_| 0.0), vec_of(|_| 1.0)]),
        ];
        // SB first in (after a BTN fold) can limp, and nothing follows a limp.
        let mut records = records;
        records.push(rec("RFI", 1, "SB", "F", json!([["F","F",0,0,0.5],["C","C",1,0,0.5]]),
            vec![vec_of(|_| 0.5), vec_of(|_| 0.5)]));
        let dir = std::env::temp_dir().join(format!("gtopen-rangelab-tree-{}", std::process::id()));
        std::fs::create_dir_all(&dir).unwrap();
        std::fs::write(dir.join("cash-data.js"), format!("window.CASH_DATA={};", json!({"v":1,"spots":records}))).unwrap();
        let dirs = vec![dir.clone()];
        let lib = Library::load(&dirs, &candidate_files(&dirs));
        let req = |path: Vec<usize>, extend: bool| TreeRequest {
            tag: "reg".into(), variant: "3x".into(), depth: 100.0, path, extend, rake_pct: 5.0, rake_cap: 3.0,
        };
        let root = lib.tree(&req(vec![], false)).unwrap();
        assert_eq!(root["actor_pos"], "BTN");
        assert_eq!(root["actions"][1]["label"], "Raise 3");
        // BTN raises; SB has no chart, so extend folds it and lands on BB.
        let bb = lib.tree(&req(vec![1], true)).unwrap();
        assert_eq!(bb["path"], json!([1, 0]));
        assert_eq!(bb["actor_pos"], "BB");
        assert_eq!(bb["history"][1]["forced"], true);
        let flop = lib.tree(&req(vec![1, 0, 1], false)).unwrap();
        assert_eq!(flop["kind"], "pot_share");
        assert_eq!(flop["exportable"], true);
        assert!((flop["pot"].as_f64().unwrap() - 6.5).abs() < 1e-9);
        let btn_reach = flop["reaches_all"][0].as_array().unwrap();
        assert_eq!(btn_reach[AA], 1.0);
        assert_eq!(btn_reach[0], 0.0);
        let ex = lib.export(&req(vec![1, 0, 1], false)).unwrap();
        assert_eq!((ex["oop_pos"].as_str(), ex["ip_pos"].as_str()), (Some("BB"), Some("BTN")));
        assert_eq!(ex["range_ip"], "AA");
        assert_eq!(ex["pot_type"], "single_raised");
        assert_eq!(ex["eff_stack_bb"], 97.0);
        assert_eq!(ex["rake_pct"], 5.0);
        // BTN folds, SB limps: BB has no chart there and the line ends.
        let end = lib.tree(&req(vec![0, 1], false)).unwrap();
        assert_eq!(end["actor_pos"], "BB");
        assert!(end["strategy_note"].as_str().unwrap().contains("no chart for BB"));
        assert_eq!(lib.tree(&req(vec![0, 0], false)).unwrap()["kind"], "fold_win");
        assert!(lib.export(&req(vec![1, 0], false)).is_err());
        assert!(lib.tree(&req(vec![5], false)).is_err());
        std::fs::remove_dir_all(&dir).ok();
    }

    #[test]
    fn hand_order_matches_range_lab() {
        let map = rl_to_class();
        // JavaScript's default sort (code units): digits before letters,
        // so the order runs 22, 32o, 32s, … AA, AKo, AKs, … TT.
        let label = |k: usize| solver::preflop::equity::class_label(map[k]);
        assert_eq!((label(0), label(1), label(2)), ("22".into(), "32o".into(), "32s".into()));
        assert_eq!(label(168), "TT");
        let mut seen = map.to_vec();
        seen.sort();
        seen.dedup();
        assert_eq!(seen.len(), 169);
    }

    #[test]
    fn decodes_merges_and_matches() {
        let dir = std::env::temp_dir().join(format!("gtopen-rangelab-{}", std::process::id()));
        std::fs::create_dir_all(&dir).unwrap();
        let old = json!({"v":1,"spots":[rec("vsOpen",5,4,"F-F-F-F-R3","3x",100.0,'A')]});
        std::fs::write(dir.join("cash-data.js"), format!("window.CASH_DATA={old};\n")).unwrap();
        std::thread::sleep(std::time::Duration::from_millis(20));
        let new = json!({"v":1,"spots":[
            rec("vsOpen",5,4,"F-F-F-F-R3","3x",100.0,'_'),
            rec("vsOpen",5,4,"F-F-F-F-R2.5","2.5x",150.0,'_'),
            rec("RFI",5,-1,"F-F-F-F-F","3x",100.0,'_'),
        ]});
        std::fs::write(dir.join("ranges.json"), new.to_string()).unwrap();
        std::fs::write(dir.join("notes.json"), "[1,2,3]").unwrap();
        let dirs = vec![dir.clone()];
        let lib = Library::load(&dirs, &candidate_files(&dirs));
        assert_eq!(lib.records.len(), 3, "the newer crawl replaces the older record");
        let sm = lib.summary();
        assert_eq!(sm["files"].as_array().unwrap().len(), 2, "unrelated JSON is not listed");
        let variants = &sm["games"][0]["variants"];
        assert_eq!((variants[0]["key"].as_str(), variants[0]["depths"].clone()), (Some("2.5x"), json!([150.0])));
        assert_eq!(variants[1]["depths"], json!([100.0]), "depths are listed per open size");
        let q = MatchRequest {
            tag: "reg".into(), players: 8, stack: 110.0, open_to: Some(3.0), variant: None,
            line: ["F", "F", "F", "F", "R"].iter().map(|s| s.to_string()).collect(),
        };
        let id = lib.find(&q).unwrap();
        let spot = lib.spot(id).unwrap();
        assert_eq!(spot["variant"], "3x");
        assert_eq!(spot["label"], "BTN vs Seat 5");
        let strat = spot["strategy"].as_array().unwrap();
        assert_eq!(strat.len(), 2 * 169);
        // newer record: every hand raises
        assert!((strat[169].as_f64().unwrap() - 1.0).abs() < 1e-9);
        assert_eq!(spot["actions"][1]["label"], "Raise to 9 bb");
        let q2 = MatchRequest { open_to: Some(2.4), ..q };
        assert_eq!(lib.spot(lib.find(&q2).unwrap()).unwrap()["variant"], "2.5x");
        std::fs::remove_dir_all(&dir).ok();
    }
}
