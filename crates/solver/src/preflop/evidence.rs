//! Read-only policy provenance. Saved generation stats are not proof that a
//! stored range was left unedited; measured labels require a probability match.
use super::*;
use std::collections::BTreeMap;

#[derive(Debug, Clone, Serialize)]
pub struct ModelEvidence {
    pub kind: String,
    pub label: String,
    pub summary: String,
    pub details: Vec<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub source: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub policy_key: Option<String>,
    /// Aggregate same-seat/entry/depth coverage, pooled over price and stack.
    /// This is not per-hand support or a confidence score.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub sample_count: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub session_count: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub observed_classes: Option<u16>,
    /// Size evidence is independent of the hand/action probabilities above.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub sizing: Option<SizingEvidence>,
}

#[derive(Debug, Clone, Serialize)]
pub struct SizingEvidence {
    pub kind:String, pub label:String, pub summary:String, pub details:Vec<String>,
    pub basis:String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub source:Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub policy_key:Option<String>,
}

impl ModelEvidence {
    fn new(kind: &str, label: &str, summary: impl Into<String>) -> Self {
        Self { kind: kind.into(), label: label.into(), summary: summary.into(),
            details: vec![], source: None, policy_key: None, sample_count:None,
            session_count:None, observed_classes:None, sizing:None }
    }
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct LimpEvidenceContext { pub limpers: u8, pub free_check: bool }

#[derive(Debug, Clone, Default, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct EvidenceContext {
    pub bucket: u8,
    #[serde(default)]
    pub limp_context: Option<LimpEvidenceContext>,
    #[serde(default)]
    pub cold: bool,
    #[serde(default)]
    pub context: Option<contextual::ContextualInput>,
}

fn key(bucket: u8) -> &'static str {
    match bucket { BUCKET_UNOPENED=>"unopened", BUCKET_VS_LIMPS=>"limps",
        BUCKET_VS_RAISE=>"raise", BUCKET_SQUEEZE=>"squeeze", _=>"reraise" }
}

fn same_probabilities(a: &BucketPolicy, b: &BucketPolicy) -> bool {
    a.call == b.call && a.raise == b.raise && a.jam == b.jam
}

fn size_distribution(policy:&BucketPolicy)->(&'static str,&[(f64,f64)]) {
    if policy.raise_multiples.is_empty() {("bb",&policy.raise_sizes)}
    else {("previous",&policy.raise_multiples)}
}

fn same_sizes(a:&BucketPolicy,b:&BucketPolicy)->bool {
    let (ab,ap)=size_distribution(a);let (bb,bp)=size_distribution(b);
    if ab!=bb || ap.is_empty() || bp.is_empty() {return false;}
    let normalized=|samples:&[(f64,f64)]| {
        let total:f64=samples.iter().map(|x|x.1).sum();
        let mut bins=BTreeMap::<u64,f64>::new();
        for &(size,weight) in samples {*bins.entry(size.to_bits()).or_default()+=weight/total;}
        bins
    };
    let a=normalized(ap);let b=normalized(bp);
    a.len()==b.len() && a.iter().all(|(size,w)|b.get(size).is_some_and(|v|(*v-*w).abs()<=1e-10))
}

fn jam_conversion(policy:&BucketPolicy,original:&BucketPolicy,stats:Option<&HudStats>)->bool {
    stats.is_some_and(|s|s.raise_size=="jam") && policy.call==original.call &&
        policy.raise.iter().all(|p|*p==0.0) &&
        policy.jam.iter().zip(original.jam.iter().zip(&original.raise)).all(|(p,(j,r))|*p==j+r)
}

fn sizing_evidence(cfg:&PreflopConfig,seat:usize,profile:&SeatProfile,policy:&BucketPolicy,policy_key:&str)->SizingEvidence {
    let (basis,samples)=size_distribution(policy);
    let mut e=SizingEvidence{kind:if samples.is_empty(){"fallback"}else{"stored_policy"}.into(),
        label:if samples.is_empty(){"Min/max rule"}else{"Stored sizes"}.into(),
        summary:if samples.is_empty(){format!("No measured ordinary-size distribution; uses the {} legal non-jam raise.",if policy.raise_size=="min"{"smallest"}else{"largest"})}
            else {"Stored non-jam size weights; their historical origin is not verified.".into()},
        details:vec![],basis:basis.into(),source:None,policy_key:Some(policy_key.into())};
    if !samples.is_empty() {
        e.details.push(if basis=="previous" {"Values are multiples of the actual faced raise-to amount, excluding antes; they are not multiples of the incremental call or pot."}
            else {"Values are absolute raise-to amounts in big blinds, including the player's existing investment and excluding antes."}.into());
        e.details.push("Ordinary size weights map to the nearest legal non-jam option in log space; ties go smaller. Sizes are independent of the hand, conditional on an ordinary raise. Weights are not sample counts.".into());
    }
    e.details.push("Jams use the separate action probability. If no ordinary raise is legal, the existing fallback routing applies.".into());
    let stats=profile.response.as_ref().and_then(|r|r.source_stats.as_ref());
    let Some(d)=stats.and_then(|s|s.dataset.as_ref()).filter(|d|d.validate().is_ok()) else {return e;};
    let row=d.resolve(cfg,seat).ok();
    let original=row.and_then(|r|if policy_key=="unopened" {r.opening.as_ref()}
        else {r.responses.get(policy_key).and_then(|i|d.response_policies.get(*i))});
    let pooled=original.is_none() && policy_key.starts_with("raise_");
    let original=original.or_else(||if pooled {row.and_then(|r|r.responses.get("raise")).and_then(|i|d.response_policies.get(*i))}else{None});
    if let Some(original)=original {
        if jam_conversion(policy,original,stats) && !same_probabilities(policy,original) {
            e.kind="assumption".into();e.label="Jam assumption".into();
            e.summary="The selected rule converts ordinary raising probability to jams; this is not measured jam sizing.".into();
        } else if same_sizes(policy,original) {
            let limits=format_limits(d,cfg);
            e.kind=if !limits.is_empty(){"extrapolated"}else if pooled{"fallback"}else{"measured"}.into();
            e.label=if !limits.is_empty(){"Extrapolated sizes"}else if pooled{"Pooled sizes"}else{"History-backed sizes"}.into();
            e.summary=if !limits.is_empty(){"Size weights match supplied histories but are transferred outside the source format; transfer is unvalidated."}
                else if pooled{"No separate size-band distribution; uses the pooled supplied size distribution."}
                else{"Size weights and units match the supplied historical size distribution before legal-menu projection."}.into();
            e.source=Some(d.site.clone());e.details.extend(limits);
            e.details.push("Matching checks the supplied distribution, not source authenticity or calibration. Sparse situations can borrow pooled size estimates.".into());
        }
    }
    for key in [format!("sizing_{policy_key}"),if policy_key=="unopened"{"opening_sizes".into()}else{"action_sizes".into()}] {
        if let Some(note)=d.response_notes.get(&key) {e.details.push(note.clone());}
    }
    e
}

fn format_limits(d: &dataset::DatasetModel, cfg: &PreflopConfig) -> Vec<String> {
    let mut out = Vec::new();
    if cfg.posts.len()<d.min_players || cfg.posts.len()>d.max_players {
        out.push(format!("Table size extrapolated: {} players; source {}–{}. Extra positions are estimates, not direct observations.",cfg.posts.len(),d.min_players,d.max_players));
    }
    if (cfg.ante>0.0)!=d.ante { out.push("Ante format differs from the source; transfer is unvalidated.".into()); }
    if let Some(sb)=d.small_blind_bb {
        let posts:Vec<f64>=cfg.posts.iter().copied().filter(|p|*p>0.0).collect();
        if posts.len()>=2 && (posts[0]/posts[posts.len()-1]-sb).abs()>1e-6 {
            out.push("Blind ratio differs from the source; transfer is unvalidated.".into());
        }
    }
    out
}

fn fixed(cfg: &PreflopConfig, seat: usize, profile: &SeatProfile, policy: &BucketPolicy,
         policy_key: &str, fresh: bool) -> ModelEvidence {
    let mut result=ModelEvidence::new(if fresh {"stat_derived"} else {"saved_policy"},
        if fresh {"Stat-derived"} else {"Stored policy"},
        if fresh {"Hand ranges inferred from aggregate stats and reference ordering."}
        else {"Stored probabilities; their hand-history origin is not verified."});
    result.policy_key=Some(policy_key.into());
    result.sizing=Some(sizing_evidence(cfg,seat,profile,policy,policy_key));
    let stats=profile.response.as_ref().and_then(|r|r.source_stats.as_ref());
    let Some(d)=stats.and_then(|s|s.dataset.as_ref()) else {
        if stats.is_some() && !fresh { result.details.push("Generation stats are retained, but this range may have been edited or copied.".into()); }
        result.details.push("These probabilities are not a sample count or a confidence estimate.".into());
        return result;
    };
    result.source=Some(d.site.clone());
    if d.validate().is_err() {
        result.details.push("Saved dataset metadata is invalid; no measured provenance claim is made.".into());
        return result;
    }
    let limits=format_limits(d,cfg);
    let row=d.resolve(cfg,seat).ok();
    let original=row.and_then(|r|if policy_key=="unopened" {r.opening.as_ref()}
        else {r.responses.get(policy_key).and_then(|i|d.response_policies.get(*i))});
    let pooled_band=original.is_none() && policy_key.starts_with("raise_");
    let original=original.or_else(||if pooled_band {
        row.and_then(|r|r.responses.get("raise")).and_then(|i|d.response_policies.get(*i))
    } else {None});
    if let Some(original)=original {
        if same_probabilities(policy,original) {
            result.kind=if !limits.is_empty() {"extrapolated"} else if pooled_band {"fallback"} else {"measured"}.into();
            result.label=if !limits.is_empty() {"Extrapolated"} else if pooled_band {"Pooled fallback"} else {"History-backed"}.into();
            result.summary=if !limits.is_empty() {"History-backed probabilities transferred outside the source format; transfer is unvalidated."}
                else if pooled_band {"No separate size-band policy supplied; using the pooled history-backed response."}
                else {"Selected probabilities match the supplied smoothed hand-history policy before legal-action routing."}.into();
            result.details.push("Sparse hands and contexts may borrow pooled estimates. A history-backed range does not mean every hand has direct observations.".into());
            result.details.push("This verifies stored probability matching, not dataset authenticity or calibration. Raise sizes are routed separately through the configured menu.".into());
            result.details.push("Displayed actions may combine probability mass when checking is free or the menu omits a raise. Legal-action routing is not additional hand-history evidence.".into());
        } else if jam_conversion(policy,original,stats) {
            result.kind="fallback".into(); result.label="Sizing assumption".into();
            result.summary="Raising probabilities match a conversion to jams by the selected sizing rule.".into();
            result.details.push("This jam frequency is an assumption, not a measured jam probability.".into());
        } else {
            result.details.push("Current probabilities differ from the supplied dataset policy. Saved source stats do not certify painted or modified ranges.".into());
        }
    } else {
        result.details.push("No matching hand-history policy is supplied for this situation; aggregate stats alone do not identify hand probabilities.".into());
    }
    result.details.extend(limits);
    if !d.scope.is_empty() {result.details.push(d.scope.clone());}
    // Notes are explanatory text only. Never parse prose into confidence/counts.
    if let Some(note)=d.response_notes.get(policy_key) {result.details.push(note.clone());}
    result
}

#[derive(Deserialize)]
struct CoverageFile {
    schema:u8, model_id:String, model_sha256:String, source_scope:String,
    support_definition:String, validation:String, decisions:u64,
    #[serde(default)] coverage_complete:bool,
    #[serde(default)] coverage_note:String,
    contexts:Vec<CoverageRow>,
}
#[derive(Deserialize)]
struct CoverageRow {
    players:usize, role:i32, entry:contextual::Entry, depth:u8,
    decisions:u64, sessions:u64, observed_classes:u16,
}

fn valid_coverage(d:&CoverageFile)->bool {
    let mut keys=std::collections::BTreeSet::new();
    d.schema==1 && d.model_id==contextual::MODEL_ID &&
        d.model_sha256=="d4951da8fadfd5f76da95df7e5f87a3965dc7bf042c1480854e14ef3d5883ae5" &&
        d.contexts.iter().all(|r| {
            let entry=match r.entry {contextual::Entry::Cold=>0,contextual::Entry::Called=>1,contextual::Entry::Raised=>2};
            (3..=6).contains(&r.players) && (-2..=(r.players as i32-3)).contains(&r.role) &&
                matches!(r.depth,2|3) && r.sessions>0 && (1..=169).contains(&r.observed_classes) &&
                r.decisions>=r.sessions && r.decisions>=r.observed_classes as u64 &&
                keys.insert((r.players,r.role,entry,r.depth))
        }) && d.contexts.iter().try_fold(0u64,|sum,r|sum.checked_add(r.decisions))==Some(d.decisions)
}

fn contextual_evidence(profile: &SeatProfile, note: String, cfg: &PreflopConfig,
                       seat:usize, input:Option<&contextual::ContextualInput>) -> ModelEvidence {
    let mut e=ModelEvidence::new("contextual_estimate","Contextual estimate",
        "Model prediction conditioned on entry, raise depth and call price.");
    e.source=profile.response.as_ref().and_then(|r|r.contextual_reraise.clone());
    e.policy_key=Some("reraise".into());
    if let Some(input)=input {
        let base=profile.buckets.get(BUCKET_VS_3BET as usize).and_then(|p|p.as_ref());
        let cold=if input.entry==contextual::Entry::Cold {profile.response.as_ref().and_then(|r|r.cold_reraise.as_ref())}else{None};
        if let Some(policy)=cold.or(base) {
            e.sizing=Some(sizing_evidence(cfg,seat,profile,policy,if cold.is_some(){"cold_reraise"}else{"reraise"}));
        } else {
            e.sizing=Some(SizingEvidence{kind:"fallback".into(),label:"Min/max rule".into(),
                summary:"No stored size distribution; contextual action probabilities use the largest legal non-jam raise.".into(),
                details:vec!["The contextual predictor estimates fold/call/raise probabilities; it does not predict individual raise sizes.".into()],
                basis:"bb".into(),source:None,policy_key:Some("reraise".into())});
        }
    }
    e.details.push(note);
    e.details.push("This is an estimated response, not direct observations of this exact hand and history. Rare contexts can remain poorly calibrated. Ordinary raise sizing is described separately; jams follow the model action probabilities.".into());
    static COVERAGE:std::sync::OnceLock<Option<CoverageFile>>=std::sync::OnceLock::new();
    let coverage=COVERAGE.get_or_init(|| {
        let d:CoverageFile=serde_json::from_str(include_str!("../../../../research/preflop-evolution/behavior/pass3/evidence-metadata.json")).ok()?;
        valid_coverage(&d).then_some(d)
    });
    if let (Some(d),Some(input))=(coverage,input) {
        let role=if seat+1==cfg.posts.len() {-2} else if seat+2==cfg.posts.len() {-1}
            else {(cfg.posts.len()-3-seat) as i32};
        if let Some(row)=d.contexts.iter().find(|r|r.players==cfg.posts.len() && r.role==role && r.entry==input.entry && r.depth==if input.raises>=3 {3}else{2}) {
            e.sample_count=Some(row.decisions);e.session_count=Some(row.sessions);e.observed_classes=Some(row.observed_classes);
        } else if d.coverage_complete {
            e.sample_count=Some(0);e.session_count=Some(0);e.observed_classes=Some(0);
            e.summary="No observations for this table/position/entry/depth; prediction borrows other contexts.".into();
            e.details.push(d.coverage_note.clone());
        }
        e.details.push(d.source_scope.clone());
        e.details.push(d.support_definition.clone());
        e.details.push(format!("Evidence is {}. Counts are not an independent test or confidence level.",d.validation));
    }
    e
}

fn solver_evidence(frozen: bool, adaptive: bool) -> ModelEvidence {
    if frozen {ModelEvidence::new("frozen_solver","Frozen strategy","Stored solved strategy; this seat is not learning at this node.")}
    else if adaptive {ModelEvidence::new("adaptive","Adaptive solver","The solver learns this response because the faced amount reaches the adaptive threshold.")}
    else {ModelEvidence::new("solver","Solver","Strategy from the configured solver model; no fixed player policy applies here.")}
}

fn with_fallback(mut e: ModelEvidence, note: Option<String>) -> ModelEvidence {
    if let Some(note)=note {
        let previous=e.summary.clone();
        e.kind="fallback".into(); e.label="Contextual fallback".into();
        e.summary="Contextual inference is inactive; the stored non-contextual policy applies.".into();
        e.details.insert(0,previous); e.details.insert(0,note);
    }
    e
}

/// Pure editor inspection, independent of either live solver session. The
/// optional context describes a re-raise preview, not an actual game history.
pub fn profile_evidence(cfg: &PreflopConfig, seat: usize, profile: &SeatProfile,
                        request: &EvidenceContext) -> Result<ModelEvidence,String> {
    inspect_profile(cfg,seat,profile,request,false)
}

fn inspect_profile(cfg: &PreflopConfig, seat: usize, profile: &SeatProfile,
                   request: &EvidenceContext, fresh: bool) -> Result<ModelEvidence,String> {
    let n=super::validate(cfg)?;
    if seat>=n || request.bucket as usize>=NUM_BUCKETS {return Err("Invalid evidence seat or bucket".into());}
    super::validate_profiles(&[Some(profile.clone())])?;
    if request.context.is_some() && request.bucket!=BUCKET_VS_3BET {return Err("Re-raise context requires the Vs 3-bet+ bucket".into());}
    if let Some(c)=&request.limp_context {
        if request.bucket!=BUCKET_VS_LIMPS || !(1..=3).contains(&c.limpers) {return Err("Invalid limp evidence context".into());}
    }
    if request.bucket==BUCKET_UNOPENED && cfg.posts.iter().rposition(|p|*p>0.0)==Some(seat) {
        return Ok(ModelEvidence::new("unavailable","Not applicable","When everyone folds, the big blind wins without an opening decision."));
    }
    let response=profile.response.as_ref();
    // Validate a supplied hypothetical re-raise even for legacy profiles.
    // Adaptive precedence belongs to every profile, not only contextual v1.
    let preview=if let Some(input)=&request.context {
        let version=response.and_then(|r|r.contextual_reraise.as_deref()).unwrap_or(contextual::MODEL_ID);
        let prediction=contextual::predict(version,cfg,seat,input)?;
        if response.and_then(|r|r.adaptive_from).is_some_and(|f|input.to_call+1e-9>=cfg.stack*f) {
            let mut e=solver_evidence(false,true);
            e.summary="Game uses adaptive solver; preview shows the underlying model estimate.".into();
            e.details.push("The preview is not a solved strategy. At this faced amount the game learns the response instead of forcing the preview probabilities.".into());
            return Ok(e);
        }
        Some(prediction)
    } else {None};
    let mut fallback=None;
    if request.bucket==BUCKET_VS_3BET {
        if response.and_then(|r|r.contextual_reraise.as_ref()).is_some() {
            if let Some(input)=&request.context {
                let prediction=preview.as_ref().unwrap();
                if prediction.policy.is_some() { return Ok(contextual_evidence(profile,prediction.note.clone(),cfg,seat,Some(input))); }
                fallback=Some(prediction.note.clone());
            } else if let Some(note)=contextual::support_note(cfg) {fallback=Some(note);}
            else {return Ok(contextual_evidence(profile,"Select a concrete entry, raise depth and price to inspect the prediction. Adaptive or point locks can override it in a game.".into(),cfg,seat,None));}
        }
    }
    let mut policy_key=key(request.bucket).to_string();
    let mut selected=profile.buckets.get(request.bucket as usize).and_then(|p|p.as_ref());
    if let Some(c)=&request.limp_context {
        if let Some(found)=response.and_then(|r|r.limp_contexts.iter().find(|p|p.limpers==c.limpers && p.free_check==c.free_check)) {
            selected=Some(&found.policy);
            policy_key=format!("limps_{}_{}",if c.free_check {"free"}else{"paid"},c.limpers);
        }
    } else if request.bucket==BUCKET_VS_LIMPS {
        let free=cfg.posts[seat]+1e-9>=cfg.posts.iter().copied().fold(0.0,f64::max);
        if let Some(c)=response.and_then(|r|r.limp_contexts.iter().find(|p|p.limpers==1 && p.free_check==free)) {
            selected=Some(&c.policy); policy_key=format!("limps_{}_1",if free {"free"}else{"paid"});
        }
    }
    let cold=request.context.as_ref().map(|c|c.entry==contextual::Entry::Cold).unwrap_or(request.cold);
    if request.bucket==BUCKET_VS_3BET && cold && selected.is_some() {
        if let Some(p)=response.and_then(|r|r.cold_reraise.as_ref()) {selected=Some(p);policy_key="cold_reraise".into();}
        else if let Some(vr)=profile.buckets.get(BUCKET_VS_RAISE as usize).and_then(|p|p.as_ref()) {
            let derived=cold_vs_3bet_policy(vr,selected.unwrap());
            let mut e=ModelEvidence::new("fallback","Cold-response fallback",
                "Cold re-raise response is derived from the stored vs-raise and re-raise policies; no separate measured cold policy is supplied.");
            e.sizing=Some(sizing_evidence(cfg,seat,profile,&derived,"reraise"));
            return Ok(with_fallback(e,fallback));
        }
    }
    let Some(policy)=selected else {return Ok(solver_evidence(false,false));};
    let mut e=with_fallback(fixed(cfg,seat,profile,policy,&policy_key,fresh),fallback);
    if request.bucket==BUCKET_VS_RAISE && profile.vs_raise_bands.as_ref().is_some_and(|b|!b.is_empty()) {
        e.details.push("This editor grid is the pooled vs-raise policy. Actual game nodes select the applicable size band or after-entry defense first.".into());
    }
    if response.and_then(|r|r.adaptive_from).is_some() {
        e.details.push("At the configured adaptive threshold the game uses a solver response instead of forcing this range.".into());
    }
    Ok(e)
}

/// Metadata returned with newly generated probabilities; it is not persisted
/// as a certificate, and subsequent edits are checked independently.
pub fn generated_evidence(cfg: &PreflopConfig, seat: usize, profile: &SeatProfile) -> BTreeMap<String,ModelEvidence> {
    let mut out=BTreeMap::new();
    for bucket in 0..NUM_BUCKETS as u8 {
        if let Ok(e)=inspect_profile(cfg,seat,profile,&EvidenceContext{bucket,..Default::default()},true) {out.insert(key(bucket).into(),e);}
    }
    if let Ok(e)=inspect_profile(cfg,seat,profile,&EvidenceContext{bucket:BUCKET_VS_3BET,cold:true,..Default::default()},true) {out.insert("cold_reraise".into(),e);}
    out
}

impl PreflopSolver {
    /// Mirror forced_sigma's precedence without altering policy, cache, or
    /// strategy. Queries must report the selected policy, not just source stats.
    pub fn node_model_evidence(&self, node: usize, strategy_note: Option<&str>) -> Option<ModelEvidence> {
        let mut e=self.node_model_evidence_inner(node,strategy_note)?;
        if let Some(sizing)=e.sizing.as_mut() {
            if !self.nodes[node].actions.iter().any(|a|a.kind=="raise") {
                sizing.details.insert(0,sizing.summary.clone());
                sizing.kind="fallback".into();sizing.label="No ordinary raise".into();
                sizing.summary="This node has no legal non-jam raise; ordinary raise mass follows the existing jam/passive/fold fallback.".into();
            }
        }
        Some(e)
    }

    fn node_model_evidence_inner(&self, node: usize, strategy_note: Option<&str>) -> Option<ModelEvidence> {
        let nd=self.nodes.get(node)?;
        if nd.kind!=KIND_ACTION {return None;}
        if let Some(note)=strategy_note {return Some(ModelEvidence::new("unavailable","Strategy unavailable",note));}
        if self.point_locks.contains_key(&(node as u32)) {return Some(ModelEvidence::new("manual_lock","Point lock","A node-specific lock overrides the player model here; it may be painted or frozen from a solve."));}
        let seat=nd.actor as usize;
        if self.hero==Some(seat) {return Some(solver_evidence(false,false));}
        let Some(profile)=self.seat_profiles[seat].as_ref() else {return Some(solver_evidence(self.seat_frozen[seat],false));};
        let response=profile.response.as_ref();
        if nd.bucket==BUCKET_VS_LIMPS {
            let free=nd.actions.iter().any(|a|a.kind=="check");
            let limpers=(0..self.n).filter(|&i|i!=seat && nd.invested[i]>self.cfg.posts[i]+self.cfg.ante+1e-9).count().clamp(1,3) as u8;
            if let Some(c)=response.and_then(|r|r.limp_contexts.iter().find(|c|c.free_check==free && c.limpers==limpers)) {
                return Some(fixed(&self.cfg,seat,profile,&c.policy,&format!("limps_{}_{limpers}",if free {"free"}else{"paid"}),false));
            }
        }
        if nd.bucket>=BUCKET_VS_RAISE && response.and_then(|r|r.adaptive_from).is_some_and(|f|self.faced_to(node)+1e-9>=self.cfg.stack*f) {
            return Some(solver_evidence(self.seat_frozen[seat],true));
        }
        let status=self.contextual_status(node);
        if let Some(status)=&status {if status.active {return Some(contextual_evidence(profile,status.note.clone(),&self.cfg,seat,Some(&status.context)));}}
        let fallback=status.map(|s|s.note);
        if (nd.bucket==BUCKET_VS_RAISE || nd.bucket==BUCKET_SQUEEZE) && !self.is_cold(nd) {
            let behind=(0..seat).any(|i|nd.invested[i]>self.cfg.posts[i]+self.cfg.ante+1e-9);
            let p=if behind {profile.limp_defense.as_ref()}else {response.and_then(|r|r.limp_unopened.as_ref()).or(profile.limp_defense.as_ref())};
            if let Some(p)=p {return Some(fixed(&self.cfg,seat,profile,p,"limp_defense",false));}
        }
        if nd.bucket==BUCKET_VS_RAISE {
            if let Some(bands)=profile.vs_raise_bands.as_ref().filter(|b|!b.is_empty()) {
                let faced=self.faced_to(node);
                let (bound,p)=bands.iter().find(|(bound,_)|faced<=*bound+1e-9).unwrap_or(&bands[bands.len()-1]);
                let mut e=fixed(&self.cfg,seat,profile,p,&format!("raise_{bound}"),false);
                e.details.insert(0,format!("Actual response band: faced total {faced} bb; upper band threshold {bound} bb."));
                return Some(e);
            }
        }
        let Some(mut policy)=profile.buckets.get(nd.bucket as usize).and_then(|p|p.as_ref()) else {return Some(solver_evidence(self.seat_frozen[seat],false));};
        let mut policy_key=key(nd.bucket);
        if nd.bucket==BUCKET_VS_3BET && self.is_cold(nd) {
            if let Some(p)=response.and_then(|r|r.cold_reraise.as_ref()) {policy=p;policy_key="cold_reraise";}
            else if let Some(vr)=profile.buckets.get(BUCKET_VS_RAISE as usize).and_then(|p|p.as_ref()) {
                let derived=cold_vs_3bet_policy(vr,policy);
                let mut e=ModelEvidence::new("fallback","Cold-response fallback",
                    "Cold re-raise response is derived from stored policies; no separate measured cold policy is supplied.");
                e.sizing=Some(sizing_evidence(&self.cfg,seat,profile,&derived,"reraise"));
                return Some(with_fallback(e,fallback));
            }
        }
        Some(with_fallback(fixed(&self.cfg,seat,profile,policy,policy_key,false),fallback))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn coverage_metadata_rejects_mismatched_totals_duplicate_keys_and_model() {
        let source=include_str!("../../../../research/preflop-evolution/behavior/pass3/evidence-metadata.json");
        let load=||serde_json::from_str::<CoverageFile>(source).unwrap();
        let d=load();assert!(valid_coverage(&d));assert!(d.coverage_complete);
        let mut d=load();d.decisions+=1;assert!(!valid_coverage(&d));
        let mut d=load();d.contexts[1].players=d.contexts[0].players;d.contexts[1].role=d.contexts[0].role;
        d.contexts[1].entry=d.contexts[0].entry;d.contexts[1].depth=d.contexts[0].depth;
        assert!(!valid_coverage(&d));
        let mut d=load();d.model_sha256="unknown".into();assert!(!valid_coverage(&d));
    }
}
