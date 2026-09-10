from pathlib import Path
import difflib
import hashlib
import json

out = Path(__file__).parent
source = Path(r'T:\Dev\GTOpen\target\autoresearch\preflop-20260910\crates\solver\src\preflop\gpu.rs')
raw = source.read_bytes()
old = raw.decode('utf-8').replace('\r\n', '\n')
start = old.index('    #[test]\n    fn coupled_terminal_matches_cpu_across_particle_batches() {')
end = old.index('\n    #[test]', start + 1)
region = old[start:end]
replacements = {
    '        for n in [3usize, 6, 9] {':
        '        // Exercise every exact opponent-count specialization O=2..8.\n        for n in 3usize..=9 {',
    '            let s = PreflopSolver::new(cfg, eq.clone()).unwrap();':
        '            let s = PreflopSolver::new(cfg, eq.clone()).unwrap();\n            assert_eq!(s.multiway_equity_model(), "coupled_deck_v1");',
    '            for &batch in if n == 3 { &[32, 7, 1][..] } else { &[32][..] } {':
        '            for batch in [32u32, 7, 1] {',
    '                gpu.mw_batch = batch;':
        '                gpu.mw_batch = batch;\n                let mut terminal_bits = Vec::<Vec<u32>>::new();',
    '                            "batch {batch}, p {p}, h {h}: {} vs {}", actual[base + h], expected[h]);':
        '                            "n {n}, batch {batch}, p {p}, h {h}: {} vs {}", actual[base + h], expected[h]);',
}
new_region = region
for before, after in replacements.items():
    assert new_region.count(before) == 1, before
    new_region = new_region.replace(before, after)
tail = '''                    }
                }
            }
        }
    }
'''
assert new_region.count(tail) == 1
new_region = new_region.replace(tail, '''                    }
                    terminal_bits.push(actual[base..base + NUM_CLASSES].iter().map(|x| x.to_bits()).collect());
                }
                // Optional exact GPU-control evidence: run this same test patch
                // before/after kernel specialization and compare every f32 bit.
                // Different batch sizes may legitimately round differently, so
                // compare control/candidate only at the same (n, batch).
                if std::env::var("PREFLOP_MW_TERMINAL_BITS").as_deref() == Ok("1") {
                    println!("PREFLOP_MW_TERMINAL_BITS {}", serde_json::json!({
                        "seats": n, "opponents": n-1, "batch": batch,
                        "model": s.multiway_equity_model(), "bits_by_seat": terminal_bits,
                    }));
                }
            }
        }
    }
''')
new = old[:start] + new_region + old[end:]
patch = ''.join(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
    fromfile='a/crates/solver/src/preflop/gpu.rs', tofile='b/crates/solver/src/preflop/gpu.rs'))
(out / 'tests.patch').write_text(patch, encoding='utf-8', newline='\n')
(out / 'expanded-test.rs').write_text(new_region, encoding='utf-8', newline='\n')
(out / 'tests-baseline.json').write_text(json.dumps({
    'source': str(source), 'sha256': hashlib.sha256(raw).hexdigest(),
    'scope': 'Test-only expansion and optional exact f32-bit evidence. No active source edits/build/GPU.',
}, indent=2)+'\n', encoding='utf-8')
assert source.read_bytes() == raw, 'Source changed while generating; regenerate.'
print('Generated all-opponent-count tests.patch; active source untouched.')
