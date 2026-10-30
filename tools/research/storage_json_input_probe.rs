//! Standalone CPU input-readback probe, linked to the exact retained serde_json library.
fn main() {
    let path=std::env::args().nth(1).expect("manifest path");
    let value:serde_json::Value=serde_json::from_slice(&std::fs::read(path).unwrap()).unwrap();
    let bits:Vec<u64>=value["boards"].as_array().unwrap().iter()
        .map(|b|b["weight"].as_f64().unwrap().to_bits()).collect();
    println!("{}",serde_json::json!({"manifest":value,"weight_bits":bits}));
}
