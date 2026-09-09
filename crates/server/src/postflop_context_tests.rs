//! Both entry points must preserve contextual evidence and the preflop pot type.
use super::*;

fn legacy_stats() -> serde_json::Value {
    serde_json::json!({
        "cbet": [60.0, 50.0, 40.0], "fold_to_bet": [40.0, 45.0, 50.0],
        "raise_bet": 8.0, "donk": 25.25, "bet_size": "min"
    })
}

#[test]
fn contextual_evidence_survives_browse_and_report_requests() {
    let mut stats = legacy_stats();
    stats["contextual_betting"] = serde_json::json!({
        "version": 1, "source": "test histories", "cells": [{
            "street": 0, "kind": "donk", "pot_type": "three_bet_plus",
            "opportunities": 100, "bets": 5
        }]
    });
    let request = serde_json::json!({
        "player": 0, "stats": stats, "aggressor": 1, "pot_type": "three_bet_plus"
    });
    let browse: ProfileLocksRequest = serde_json::from_value(request.clone()).unwrap();
    assert!(browse.pot_type.is_some());
    assert_eq!(serde_json::to_value(&browse.stats).unwrap()["contextual_betting"], stats["contextual_betting"]);

    let mut report = request;
    report["name"] = "fixture".into();
    let villain: ReportVillain = serde_json::from_value(report.clone()).unwrap();
    let saved = serde_json::to_value(&villain).unwrap();
    assert_eq!(saved["pot_type"], "three_bet_plus");
    assert_eq!(saved["stats"]["contextual_betting"], stats["contextual_betting"]);
    let reloaded: ReportVillain = serde_json::from_value(saved).unwrap();
    assert!(reloaded.stats.contextual_betting.is_some());
}

#[test]
fn legacy_browse_and_reports_do_not_invent_context() {
    let request = serde_json::json!({ "player": 0, "stats": legacy_stats() });
    let browse: ProfileLocksRequest = serde_json::from_value(request.clone()).unwrap();
    assert!(browse.pot_type.is_none());
    assert!(browse.stats.contextual_betting.is_none());
    let mut report = request;
    report["name"] = "old report".into();
    let villain: ReportVillain = serde_json::from_value(report).unwrap();
    assert!(villain.pot_type.is_none());
    assert!(villain.stats.contextual_betting.is_none());
}

#[test]
fn invalid_pot_context_is_rejected_instead_of_silently_dropped() {
    let request = serde_json::json!({
        "player": 0, "stats": legacy_stats(), "pot_type": "unknown"
    });
    assert!(serde_json::from_value::<ProfileLocksRequest>(request).is_err());
}
