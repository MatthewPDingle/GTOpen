//! Optional measured entry contexts. Old HUD profiles remain compatible.
use super::{BucketPolicy, PreflopConfig};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DatasetModel {
    pub site: String,
    pub min_players: usize,
    pub max_players: usize,
    pub ante: bool,
    #[serde(default)]
    pub small_blind_bb: Option<f64>,
    pub empirical_opening: bool,
    pub scope: String,
    pub rows: Vec<DatasetRow>,
    /// Shared policies avoid repeating extrapolated contexts in every row.
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub response_policies: Vec<BucketPolicy>,
    #[serde(default, skip_serializing_if = "std::collections::BTreeMap::is_empty")]
    pub response_notes: std::collections::BTreeMap<String, String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DatasetRow {
    pub players: usize,
    /// BTN=0, CO=1, continuing backwards; SB=-1, BB=-2.
    pub role: i32,
    pub open_raise: f64,
    pub open_limp: f64,
    pub iso_raise: f64,
    pub limp_behind: f64,
    #[serde(default)]
    pub opening: Option<BucketPolicy>,
    #[serde(default, skip_serializing_if = "std::collections::BTreeMap::is_empty")]
    pub responses: std::collections::BTreeMap<String, usize>,
}

impl DatasetModel {
    pub fn validate(&self) -> Result<(), String> {
        if !(2..=9).contains(&self.min_players) || self.max_players < self.min_players || self.max_players > 9 || self.rows.is_empty() || self.rows.len() > 72 {
            return Err("dataset: invalid player coverage".into());
        }
        let mut seen = std::collections::HashSet::new();
        if self.response_policies.len()>512 { return Err("dataset: too many response policies".into()); }
        let shaped = |p: &BucketPolicy| -> bool {
            p.raise_sizes.iter().all(|(size,w)|size.is_finite() && *size>0.0 && w.is_finite() && *w>0.0) && p.raise_sizes.iter().map(|x|x.1).sum::<f64>().is_finite() && p.call.len()==169 && p.raise.len()==169 && p.jam.len()==169 && (0..169).all(|h| {
                let v=[p.call[h],p.raise[h],p.jam[h]];
                v.iter().all(|x| x.is_finite() && *x>=0.0) && v.iter().sum::<f32>()<=1.000001
            })
        };
        if self.response_policies.iter().any(|p|!shaped(p)) { return Err("dataset: invalid response probabilities".into()); }
        if self.small_blind_bb.is_some_and(|v|!v.is_finite() || v<=0.0 || v>1.0) {
            return Err("dataset: invalid small blind ratio".into());
        }
        for r in &self.rows {
            for (key, index) in &r.responses {
                if !["limps","raise","squeeze","reraise","cold_reraise","limp_defense","raise_2.5","raise_3.5","raise_5","raise_999",
                    "limps_paid_1","limps_paid_2","limps_paid_3","limps_free_1","limps_free_2","limps_free_3"].contains(&key.as_str()) || *index>=self.response_policies.len() {
                    return Err("dataset: invalid response reference".into());
                }
            }
            if !(2..=9).contains(&r.players) || r.role < -2 || r.role >= r.players as i32 - 2 || !seen.insert((r.players,r.role)) {
                return Err("dataset: invalid or duplicate position".into());
            }
            for (a,b) in [(r.open_raise,r.open_limp),(r.iso_raise,r.limp_behind)] {
                if !a.is_finite() || !b.is_finite() || a < 0.0 || b < 0.0 || a+b > 100.000001 {
                    return Err("dataset: entry frequencies must be disjoint percentages".into());
                }
            }
            if self.empirical_opening != r.opening.is_some() {
                return Err("dataset: empirical openings need a policy for every context".into());
            }
            if let Some(p) = &r.opening {
                if !shaped(p) { return Err("dataset: invalid opening probabilities or sizes".into()); }
                if p.call.len()!=169 || p.raise.len()!=169 || p.jam.len()!=169 {
                    return Err("dataset: opening policies require 169 hands".into());
                }
                for h in 0..169 {
                    let vals=[p.call[h],p.raise[h],p.jam[h]];
                    if vals.iter().any(|v| !v.is_finite() || *v<0.0) || vals.iter().sum::<f32>()>1.000001 {
                        return Err("dataset: invalid per-hand probabilities".into());
                    }
                }
            }
        }
        Ok(())
    }

    pub fn resolve(&self, cfg: &PreflopConfig, seat: usize) -> Result<&DatasetRow, String> {
        let blinds: Vec<usize> = (0..cfg.posts.len()).filter(|&s|cfg.posts[s]>0.0).collect();
        let role = if blinds.last()==Some(&seat) {-2}
        else if blinds.contains(&seat) {-1}
        else {(seat+1..cfg.posts.len()).filter(|&s|cfg.posts[s]<=0.0).count() as i32};
        self.rows.iter().find(|r|r.players==cfg.posts.len() && r.role==role)
            .ok_or_else(||"dataset: this table position has no supplied context".into())
    }

    pub fn note(&self, cfg: &PreflopConfig) -> String {
        let mut note = format!("{} · {}. {}",self.site,
            if !self.response_policies.is_empty() {"known-card policies in validated situations; each tab identifies its source"}
            else if self.empirical_opening {"opening hand probabilities learned from histories; other ranges inferred"}
            else {"entry frequencies learned by position/player count; hand composition inferred"}, self.scope);
        if cfg.posts.len()<self.min_players || cfg.posts.len()>self.max_players {
            note.push_str(&format!(" Table size extrapolated: {} players; source {}–{}.",cfg.posts.len(),self.min_players,self.max_players));
        }
        if (cfg.ante>0.0)!=self.ante {note.push_str(" Ante format differs from the source; transfer is unvalidated.");}
        if let Some(sb) = self.small_blind_bb {
            let blinds: Vec<f64> = cfg.posts.iter().copied().filter(|p|*p>0.0).collect();
            if blinds.len()>=2 && (blinds[0]/blinds[blinds.len()-1]-sb).abs()>1e-6 {
                note.push_str(" Blind ratio differs from the source; transfer is unvalidated.");
            }
        }
        note
    }
}
