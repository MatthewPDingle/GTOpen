use super::*;

fn request() -> serde_json::Value {
    let p=serde_json::json!({"call":vec![0.2;169],"raise":vec![0.3;169],"jam":vec![0.0;169]});
    serde_json::json!({"cfg":{"positions":["BTN","SB","BB"],"posts":[0,0.5,1],"stack":100,
        "open_raises":[2.5],"raise_mults":[3],"realization":"raw"},"seat":0,"bucket":0,
        "profile":{"name":"Old saved fixture","buckets":[p.clone(),p.clone(),p.clone(),p.clone(),p]}})
}

#[tokio::test]
async fn model_evidence_needs_no_live_session_and_returns_a_direct_object() {
    let req=serde_json::from_value(request()).unwrap();
    let Json(evidence)=pf_model_evidence(Json(req)).await.unwrap();
    assert_eq!(evidence.kind,"saved_policy");
    let json=serde_json::to_value(evidence).unwrap();
    assert!(json.get("summary").is_some());
    assert!(json.get("profile").is_none());
    assert!(json.get("sample_count").is_none());
}

#[tokio::test]
async fn model_evidence_rejects_bad_input_without_building_a_game() {
    let mut value=request();value["seat"]=serde_json::json!(3);
    let error=pf_model_evidence(Json(serde_json::from_value(value).unwrap())).await.unwrap_err();
    assert_eq!(error.0,StatusCode::BAD_REQUEST);
    let mut value=request();value["unexpected"]=serde_json::json!(true);
    assert!(serde_json::from_value::<PfModelEvidenceRequest>(value).is_err());
}
