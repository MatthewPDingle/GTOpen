#![cfg(feature = "continuation-transfer-research")]

/// Actual probabilities that changed by 1-2 ULP when importing the frozen
/// development policy. Compiler-parsed literals provide independent bits.
#[test]
fn frozen_policy_json_preserves_ieee_probabilities() {
    let raw = r#"{"policy":[0.9999994736406493,9.718912554841223e-06,0.0,1.0]}"#;
    let expected = [0.9999994736406493_f64, 9.718912554841223e-06_f64, 0.0, 1.0];
    let value: serde_json::Value = serde_json::from_str(raw).unwrap();
    let policy: Vec<f64> = serde_json::from_value(value["policy"].clone()).unwrap();
    assert_eq!(policy.iter().map(|v| v.to_bits()).collect::<Vec<_>>(),
               expected.iter().map(|v| v.to_bits()).collect::<Vec<_>>());
    let serialized = serde_json::to_string(&policy).unwrap();
    let restored: Vec<f64> = serde_json::from_str(&serialized).unwrap();
    assert_eq!(restored.iter().map(|v| v.to_bits()).collect::<Vec<_>>(),
               expected.iter().map(|v| v.to_bits()).collect::<Vec<_>>());
}
