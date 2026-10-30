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
use std::collections::{BTreeMap, HashMap};
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
}

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
        Library {
            dirs: dirs.iter().map(|d| d.display().to_string()).collect(),
            files: infos,
            records,
            positions,
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
        let map = rl_to_class();
        let decode = |s: &str, f: &dyn Fn(u8) -> f64| -> Vec<f64> {
            let mut out = vec![0.0; 169];
            for (k, c) in s.bytes().enumerate() {
                out[map[k]] = f(b64_digit(c).unwrap_or(0));
            }
            out
        };
        let freq = |d: u8| d as f64 / 63.0;
        let loss = |d: u8| 0.02 * ((d as f64 / 9.0).exp() - 1.0);
        let na = r.actions.len();
        let mut strategy: Vec<Vec<f64>> = r.freqs.iter().map(|s| decode(s, &freq)).collect();
        // The 64-level rounding leaves sums near (not at) 1; renormalize per
        // hand exactly as Range Lab does.
        for h in 0..169 {
            let t: f64 = (0..na).map(|a| strategy[a][h]).sum();
            if t > 0.0 {
                for row in strategy.iter_mut() {
                    row[h] /= t;
                }
            }
        }
        let ev_loss: Vec<f64> = r.loss.iter().flat_map(|s| decode(s, &loss)).collect();
        let reach = (!r.reach.is_empty()).then(|| decode(&r.reach, &freq));
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
