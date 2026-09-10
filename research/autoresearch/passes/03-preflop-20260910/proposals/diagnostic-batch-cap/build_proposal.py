from pathlib import Path
import subprocess, difflib, hashlib, json

HERE = Path(__file__).resolve().parent
ROOT = Path('T:/Dev/GTOpen/target/autoresearch/preflop-20260910')
REV = '739c68d'
REL = 'crates/solver/src/preflop/gpu.rs'
baseline = subprocess.check_output(['git','show',f'{REV}:{REL}'], cwd=ROOT).decode('utf-8')
anchor = '''            mw_batch = plan.batch;
            mw_cache_len = plan.cache_len;
'''
replacement = '''            // Diagnostic-only cap, applied AFTER normal minimum-fit/normalization
            // planning. Unset preserves the original plan exactly. This cannot
            // enlarge a batch or force a different model when memory is tight.
            let mut plan = plan;
            match std::env::var("PREFLOP_MW_DIAGNOSTIC_BATCH_CAP") {
                Ok(value) if value == "30" => {
                    let planned_batch = plan.batch;
                    plan.batch = plan.batch.min(30);
                    plan.cache_len = compact.capacity.checked_mul(NUM_CLASSES + 1)
                        .and_then(|n| n.checked_mul(plan.batch))
                        .ok_or_else(|| "diagnostic multiway CDF scratch size overflow".to_string())?;
                    println!("preflop gpu diagnostic batch cap: {}", serde_json::json!({
                        "requested_cap":30,"planned_batch":planned_batch,"actual_batch":plan.batch,
                        "cdf_slots":compact.capacity,"cdf_allocated_bytes":plan.cache_len * 4,
                        "normalized_bytes":plan.normalized_bytes
                    }));
                }
                Ok(value) => return Err(format!("PREFLOP_MW_DIAGNOSTIC_BATCH_CAP supports only 30, got {value:?}")),
                Err(std::env::VarError::NotPresent) => {},
                Err(err) => return Err(format!("invalid PREFLOP_MW_DIAGNOSTIC_BATCH_CAP: {err}")),
            }
            mw_batch = plan.batch;
            mw_cache_len = plan.cache_len;
'''
assert baseline.count(anchor) == 1
candidate = baseline.replace(anchor, replacement)
(HERE / 'gpu.rs').write_text(candidate, encoding='utf-8', newline='\n')
(HERE / 'batch-cap-30.patch').write_text(''.join(difflib.unified_diff(baseline.splitlines(True), candidate.splitlines(True), 'a/'+REL, 'b/'+REL)), encoding='utf-8', newline='\n')
revision = subprocess.check_output(['git','rev-parse',REV], cwd=ROOT).decode().strip()
manifest = {'baseline_revision':revision, 'baseline_gpu_sha256':hashlib.sha256(baseline.encode()).hexdigest(), 'candidate_gpu_sha256':hashlib.sha256(candidate.encode()).hexdigest(), 'status':'proposal only; not compiled or run; active gpu.rs untouched'}
(HERE / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
