//! D067: CPU-only reconstruction of planned showdown mappings at D066 fixtures.
use super::plan::{GpuPlan, LevelSpan};
use crate::{Spot, SpotConfig};
use crate::tree::{KIND_TERM_FOLD, KIND_TERM_SHOWDOWN};
use serde_json::{json, Value};
use std::io::{self, BufReader, BufWriter, Read, Write};
use std::path::Path;

type DiagResult<T> = Result<T, String>;
const GIB: u64 = 1 << 30;

fn e(error: impl std::fmt::Display) -> String { error.to_string() }
fn require(ok: bool, message: &str) -> DiagResult<()> {
    if ok { Ok(()) } else { Err(message.into()) }
}
fn emit(value: Value) -> DiagResult<()> {
    let stdout = io::stdout();
    let mut out = stdout.lock();
    writeln!(out, "D067_PLANNED_SHOW_INCIDENCE {value}").map_err(e)?;
    out.flush().map_err(e)
}

#[cfg(windows)]
fn available_ram() -> DiagResult<u64> {
    #[repr(C)]
    struct MemoryStatus { length: u32, load: u32, total: u64, available: u64,
        total_page: u64, available_page: u64, total_virtual: u64,
        available_virtual: u64, extended: u64 }
    #[link(name = "kernel32")]
    extern "system" { fn GlobalMemoryStatusEx(status: *mut MemoryStatus) -> i32; }
    let mut status: MemoryStatus = unsafe { std::mem::zeroed() };
    status.length = std::mem::size_of::<MemoryStatus>() as u32;
    if unsafe { GlobalMemoryStatusEx(&mut status) } == 0 {
        return Err(format!("GlobalMemoryStatusEx: {}", io::Error::last_os_error()));
    }
    Ok(status.available)
}
#[cfg(not(windows))]
fn available_ram() -> DiagResult<u64> { Err("D067 admission is registered for Windows only".into()) }

struct Fingerprint(u64);
impl Fingerprint {
    fn new() -> Self { Self(0xcbf29ce484222325) }
    fn bytes(&mut self, bytes: &[u8]) {
        for &byte in bytes { self.0 = (self.0 ^ byte as u64).wrapping_mul(0x100000001b3); }
    }
    fn finish(&self) -> String { format!("{:016x}", self.0) }
}

fn spans(spans: &[LevelSpan], nodes: &[u32], levels: usize) -> DiagResult<Value> {
    require(spans.len() == levels, "span count differs from plan levels")?;
    let mut cursor = 0usize;
    let mut result = Vec::with_capacity(levels);
    for (level, span) in spans.iter().enumerate() {
        require(span.start as usize == cursor, "span partition is not contiguous")?;
        let end = cursor.checked_add(span.count as usize).ok_or("span overflow")?;
        require(end <= nodes.len(), "span exceeds list")?;
        require(nodes[cursor..end].windows(2).all(|v| v[0] < v[1]), "level node IDs not strictly ascending")?;
        result.push(json!({"level":level,"start":span.start,"count":span.count}));
        cursor = end;
    }
    require(cursor == nodes.len(), "span partition does not cover full list")?;
    Ok(json!(result))
}

fn validate_plan(spot: &Spot, plan: &GpuPlan) -> DiagResult<()> {
    let n = plan.num_nodes;
    require(n == spot.tree.nodes.len(), "node count differs")?;
    require(plan.node_player.len() == n && plan.node_twin.len() == n
        && plan.node_tlose.len() == n && plan.node_ttie.len() == n
        && plan.node_river_slot.len() == n, "per-node map lengths differ")?;
    for p in 0..2 {
        require(plan.nh[p] == spot.hands[p].len() && plan.nh[p] > 0,
            "logical hand length differs or empty")?;
        require(plan.reach_slot[p].len() == n && plan.reach_blocks[p] > 0,
            "reach slot geometry differs")?;
        require(plan.riv_off[p].len() == plan.num_slots && plan.riv_cnt[p].len() == plan.num_slots,
            "river slot geometry differs")?;
        let mut cursor = 0usize;
        for slot in 0..plan.num_slots {
            let start = plan.riv_off[p][slot] as usize;
            let count = plan.riv_cnt[p][slot] as usize;
            let end = start.checked_add(count).ok_or("river range overflow")?;
            require(start == cursor && count <= plan.nh[p] && end <= plan.riv_sorted_idx[p].len(),
                "river logical list range invalid")?;
            let mut seen = vec![false; plan.nh[p]];
            for &idx in &plan.riv_sorted_idx[p][start..end] {
                let idx = idx as usize;
                require(idx < plan.nh[p], "river hand index out of logical bounds")?;
                require(!seen[idx], "duplicate river hand index")?;
                seen[idx] = true;
            }
            cursor = end;
        }
        require(cursor == plan.riv_sorted_idx[p].len(), "river lists do not cover sorted index array")?;
    }
    Ok(())
}

fn compare_fold(input: &Path, spot: &Spot, plan: &GpuPlan, expected: &Value) -> DiagResult<Value> {
    let name = expected["mapping"]["file"].as_str().ok_or("missing retained fold filename")?;
    let mut reader = BufReader::new(std::fs::File::open(input.join(name)).map_err(e)?);
    let mut hash = Fingerprint::new();
    let mut seen = vec![false; plan.num_nodes];
    for &node in &plan.fold_nodes {
        let n = node as usize;
        require(n < plan.num_nodes, "fold node out of bounds")?;
        require(!seen[n] && spot.tree.nodes[n].kind == KIND_TERM_FOLD, "invalid or duplicate fold node")?;
        seen[n] = true;
        let slots = [plan.reach_slot[0][n], plan.reach_slot[1][n]];
        for p in 0..2 { require((slots[p] as usize) < plan.reach_blocks[p], "fold reach slot out of bounds")?; }
        let amount = std::array::from_fn::<u32, 2, _>(|p| {
            (if plan.node_player[n] == p as i32 { plan.node_tlose[n] } else { plan.node_twin[n] }).to_bits()
        });
        let words = [node, slots[0], slots[1], amount[0], amount[1]];
        let mut actual = [0u8; 20];
        reader.read_exact(&mut actual).map_err(e)?;
        for (i, word) in words.iter().enumerate() {
            require(actual[4*i..4*i+4] == word.to_le_bytes(), "retained fold record differs")?;
        }
        hash.bytes(&actual);
    }
    let mut tail = [0u8; 1];
    require(reader.read(&mut tail).map_err(e)? == 0, "retained fold mapping has trailing bytes")?;
    let mapping = json!({"file":name,"bytes":plan.fold_nodes.len()*20,"fnv1a64":hash.finish(),
        "record":"five little-endian u32: node,slot0,slot1,amount0bits,amount1bits"});
    require(mapping == expected["mapping"], "retained fold metadata differs")?;
    Ok(mapping)
}

fn write_show(output: &Path, id: &str, spot: &Spot, plan: &GpuPlan) -> DiagResult<Value> {
    let name = format!("{id}-planned-show-mapping.u32le");
    let file = std::fs::OpenOptions::new().write(true).create_new(true).open(output.join(&name)).map_err(e)?;
    let mut out = BufWriter::new(file);
    let mut hash = Fingerprint::new();
    let mut seen = vec![false; plan.num_nodes];
    for &node in &plan.show_nodes {
        let n = node as usize;
        require(n < plan.num_nodes, "show node out of bounds")?;
        require(!seen[n] && spot.tree.nodes[n].kind == KIND_TERM_SHOWDOWN, "invalid or duplicate show node")?;
        seen[n] = true;
        let slot = plan.node_river_slot[n];
        require(slot >= 0 && (slot as usize) < plan.num_slots, "show river slot out of bounds")?;
        let slot = slot as usize;
        for q in 0..2 { require((plan.reach_slot[q][n] as usize) < plan.reach_blocks[q], "show reach slot out of bounds")?; }
        let payoffs = [plan.node_twin[n].to_bits(), plan.node_tlose[n].to_bits(), plan.node_ttie[n].to_bits()];
        let original = &spot.tree.nodes[n];
        require(payoffs == [(original.t_win as f32).to_bits(), (original.t_lose as f32).to_bits(),
            (original.t_tie as f32).to_bits()], "show f32 payoff casts differ")?;
        let words = [node, plan.reach_slot[0][n], plan.reach_slot[1][n], slot as u32,
            payoffs[0], payoffs[1], payoffs[2], plan.riv_cnt[0][slot], plan.riv_cnt[1][slot]];
        for word in words {
            let bytes = word.to_le_bytes();
            out.write_all(&bytes).map_err(e)?;
            hash.bytes(&bytes);
        }
    }
    out.flush().map_err(e)?;
    out.get_ref().sync_all().map_err(e)?;
    Ok(json!({"file":name,"bytes":plan.show_nodes.len()*36,"fnv1a64":hash.finish(),
        "record":"nine little-endian u32: node,slot0,slot1,river_slot,win_bits,lose_bits,tie_bits,m0,m1"}))
}

fn fixture(anchor: &Value, input: &Path, output: &Path) -> DiagResult<()> {
    let id = anchor["fixture_id"].as_str().ok_or("missing fixture ID")?;
    require(available_ram()? >= 16*GIB, "less than16GiB available RAM before Spot")?;
    let config: SpotConfig = serde_json::from_value(anchor["config"].clone()).map_err(e)?;
    let spot = Spot::new(config)?;
    let plan = GpuPlan::build(&spot, true);
    validate_plan(&spot, &plan)?;
    let expected = &anchor["geometry"];
    let fold_spans = spans(&plan.fold_spans, &plan.fold_nodes, plan.num_levels)?;
    require(json!(plan.num_nodes) == expected["nodes"] && json!(plan.nh) == expected["nh"]
        && json!(plan.reach_blocks) == expected["reach_blocks"]
        && json!(plan.fold_nodes.len()) == expected["fold_ctas_per_traverser"]
        && fold_spans == expected["fold_spans"]
        && expected["physical_reach_has_padding"] == false, "recorded D066 geometry differs")?;
    let fold_mapping = compare_fold(input, &spot, &plan, expected)?;
    let show_spans = spans(&plan.show_spans, &plan.show_nodes, plan.num_levels)?;
    let mapping = write_show(output, id, &spot, &plan)?;
    let record = json!({"stage":"fixture_mapping","fixture_id":id,"fixture_index":anchor["fixture_index"],
        "nodes":plan.num_nodes,"nh":plan.nh,"reach_blocks":plan.reach_blocks,"num_levels":plan.num_levels,
        "num_slots":plan.num_slots,"fold_ctas_per_traverser":plan.fold_nodes.len(),"fold_spans":fold_spans,
        "fold_mapping_exact":true,"fold_mapping":fold_mapping,"show_ctas_per_traverser":plan.show_nodes.len(),
        "show_spans":show_spans,"mapping":mapping,"planned_source_only":true,"new_show_upload_validation":false,
        "cleanup_complete":true});
    drop(plan);
    drop(spot);
    emit(record)
}

fn run() -> DiagResult<()> {
    let input = std::env::var_os("D067_CENSUS_DIR").ok_or("D067_CENSUS_DIR is required")?;
    let output = std::env::var_os("D067_MAPPING_DIR").ok_or("D067_MAPPING_DIR is required")?;
    let input = Path::new(&input);
    let output = Path::new(&output);
    require(input.is_dir() && output.is_dir(), "input/output directory missing")?;
    require(std::fs::read_dir(output).map_err(e)?.next().is_none(), "output directory is not empty")?;
    let inputs: Value = serde_json::from_str(INPUTS_JSON).map_err(e)?;
    let inputs = inputs.as_array().ok_or("inputs is not an array")?;
    require(inputs.len() == 3, "fixture count differs")?;
    for (index, id) in ["rainbow", "two-tone", "river"].iter().enumerate() {
        require(inputs[index]["fixture_id"] == *id && inputs[index]["fixture_index"] == index,
            "fixture order differs")?;
    }
    let ram = available_ram()?;
    require(ram >= 16*GIB, "less than16GiB available RAM")?;
    emit(json!({"stage":"admission","fixtures":3,"available_host_ram_bytes":ram,
        "required_available_host_ram_bytes":16*GIB,"cpu_only":true,"gpu_calls":0}))?;
    for anchor in inputs { fixture(anchor, input, output)?; }
    emit(json!({"stage":"complete","fixtures":3,"fold_mapping_exact":true,"fold_mapping_checks":3,
        "planned_show_mapping_files":3,"cpu_only":true,"gpu_calls":0,"planned_source_only":true,
        "new_show_upload_validation":false,"performance_measurement":false,"candidate_accepted":false}))
}

#[test]
#[ignore = "D067 requires frozen historical maps, host RAM admission and root-owned output"]
fn planned_show_incidence_mapping() { run().expect("D067 planned-show mapping failed"); }

const INPUTS_JSON: &str = r###"[
  {
    "fixture_id": "rainbow",
    "fixture_index": 0,
    "config": {
      "board": "Ks7h2d",
      "range_ip": "22+,A2s+,K6s+,Q8s+,J8s+,T8s+,97s+,87s,76s,65s,A8o+,KTo+,QTo+,JTo",
      "range_oop": "55-22,A8s-A2s,K9s-K6s,Q9s-Q6s,J9s-J7s,T8s-T7s,97s,98s,86s,87s,75s,76s,64s,65s,53s,54s,43s,AJo-A8o,KTo-K9o,QTo,QJo,JTo,T9o,98o",
      "tree": {
        "add_allin": false,
        "allin_threshold": 0.85,
        "carry_aggressor_through_checks": null,
        "effective_stack": 970.0,
        "ip": [
          {
            "bet": [
              {
                "PotPct": 33.0
              },
              {
                "PotPct": 75.0
              }
            ],
            "donk": [],
            "raise": [
              {
                "PotPct": 60.0
              }
            ]
          },
          {
            "bet": [
              {
                "PotPct": 75.0
              }
            ],
            "donk": [],
            "raise": [
              {
                "PotPct": 60.0
              }
            ]
          },
          {
            "bet": [
              {
                "PotPct": 75.0
              }
            ],
            "donk": [],
            "raise": [
              {
                "PotPct": 60.0
              }
            ]
          }
        ],
        "max_raises": 10,
        "oop": [
          {
            "bet": [
              {
                "PotPct": 33.0
              }
            ],
            "donk": [],
            "raise": [
              {
                "PotPct": 60.0
              }
            ]
          },
          {
            "bet": [
              {
                "PotPct": 75.0
              }
            ],
            "donk": [],
            "raise": [
              {
                "PotPct": 60.0
              }
            ]
          },
          {
            "bet": [
              {
                "PotPct": 75.0
              }
            ],
            "donk": [],
            "raise": [
              {
                "PotPct": 60.0
              }
            ]
          }
        ],
        "rake_cap": 3.0,
        "rake_pct": 0.0,
        "starting_pot": 60.0
      }
    },
    "geometry": {
      "fixture_id": "rainbow",
      "fold_ctas_per_traverser": 319985,
      "fold_spans": [
        {
          "count": 0,
          "level": 0,
          "start": 0
        },
        {
          "count": 0,
          "level": 1,
          "start": 0
        },
        {
          "count": 1,
          "level": 2,
          "start": 0
        },
        {
          "count": 3,
          "level": 3,
          "start": 1
        },
        {
          "count": 3,
          "level": 4,
          "start": 4
        },
        {
          "count": 101,
          "level": 5,
          "start": 7
        },
        {
          "count": 199,
          "level": 6,
          "start": 108
        },
        {
          "count": 492,
          "level": 7,
          "start": 307
        },
        {
          "count": 10045,
          "level": 8,
          "start": 799
        },
        {
          "count": 26607,
          "level": 9,
          "start": 10844
        },
        {
          "count": 66150,
          "level": 10,
          "start": 37451
        },
        {
          "count": 96432,
          "level": 11,
          "start": 103601
        },
        {
          "count": 89376,
          "level": 12,
          "start": 200033
        },
        {
          "count": 30576,
          "level": 13,
          "start": 289409
        }
      ],
      "mapping": {
        "bytes": 6399700,
        "file": "rainbow-fold-mapping.u32le",
        "fnv1a64": "35a9257cdf387a0e",
        "record": "five little-endian u32: node,slot0,slot1,amount0bits,amount1bits"
      },
      "nh": [
        257,
        319
      ],
      "nodes": 1346813,
      "physical_reach_has_padding": false,
      "reach_blocks": [
        750803,
        724734
      ],
      "stage": "geometry",
      "uploaded_metadata_exact_both_arms": true
    }
  },
  {
    "fixture_id": "two-tone",
    "fixture_index": 1,
    "config": {
      "board": "Ks7s2d",
      "range_ip": "22+,A2s+,K6s+,Q8s+,J8s+,T8s+,97s+,87s,76s,65s,A8o+,KTo+,QTo+,JTo",
      "range_oop": "55-22,A8s-A2s,K9s-K6s,Q9s-Q6s,J9s-J7s,T8s-T7s,97s,98s,86s,87s,75s,76s,64s,65s,53s,54s,43s,AJo-A8o,KTo-K9o,QTo,QJo,JTo,T9o,98o",
      "tree": {
        "add_allin": false,
        "allin_threshold": 0.85,
        "carry_aggressor_through_checks": null,
        "effective_stack": 970.0,
        "ip": [
          {
            "bet": [
              {
                "PotPct": 33.0
              },
              {
                "PotPct": 75.0
              }
            ],
            "donk": [],
            "raise": [
              {
                "PotPct": 60.0
              }
            ]
          },
          {
            "bet": [
              {
                "PotPct": 75.0
              }
            ],
            "donk": [],
            "raise": [
              {
                "PotPct": 60.0
              }
            ]
          },
          {
            "bet": [
              {
                "PotPct": 75.0
              }
            ],
            "donk": [],
            "raise": [
              {
                "PotPct": 60.0
              }
            ]
          }
        ],
        "max_raises": 10,
        "oop": [
          {
            "bet": [
              {
                "PotPct": 33.0
              }
            ],
            "donk": [],
            "raise": [
              {
                "PotPct": 60.0
              }
            ]
          },
          {
            "bet": [
              {
                "PotPct": 75.0
              }
            ],
            "donk": [],
            "raise": [
              {
                "PotPct": 60.0
              }
            ]
          },
          {
            "bet": [
              {
                "PotPct": 75.0
              }
            ],
            "donk": [],
            "raise": [
              {
                "PotPct": 60.0
              }
            ]
          }
        ],
        "rake_cap": 3.0,
        "rake_pct": 0.05,
        "starting_pot": 60.0
      }
    },
    "geometry": {
      "fixture_id": "two-tone",
      "fold_ctas_per_traverser": 194730,
      "fold_spans": [
        {
          "count": 0,
          "level": 0,
          "start": 0
        },
        {
          "count": 0,
          "level": 1,
          "start": 0
        },
        {
          "count": 1,
          "level": 2,
          "start": 0
        },
        {
          "count": 3,
          "level": 3,
          "start": 1
        },
        {
          "count": 3,
          "level": 4,
          "start": 4
        },
        {
          "count": 75,
          "level": 5,
          "start": 7
        },
        {
          "count": 147,
          "level": 6,
          "start": 82
        },
        {
          "count": 362,
          "level": 7,
          "start": 229
        },
        {
          "count": 6184,
          "level": 8,
          "start": 591
        },
        {
          "count": 16259,
          "level": 9,
          "start": 6775
        },
        {
          "count": 40228,
          "level": 10,
          "start": 23034
        },
        {
          "count": 58589,
          "level": 11,
          "start": 63262
        },
        {
          "count": 54302,
          "level": 12,
          "start": 121851
        },
        {
          "count": 18577,
          "level": 13,
          "start": 176153
        }
      ],
      "mapping": {
        "bytes": 3894600,
        "file": "two-tone-fold-mapping.u32le",
        "fnv1a64": "5fba17f827a8b8e0",
        "record": "five little-endian u32: node,slot0,slot1,amount0bits,amount1bits"
      },
      "nh": [
        258,
        320
      ],
      "nodes": 1346813,
      "physical_reach_has_padding": false,
      "reach_blocks": [
        456834,
        440970
      ],
      "stage": "geometry",
      "uploaded_metadata_exact_both_arms": true
    }
  },
  {
    "fixture_id": "river",
    "fixture_index": 2,
    "config": {
      "board": "Ks7h2dQhTc",
      "range_ip": "22+,A2s+,K6s+,Q8s+,J8s+,T8s+,97s+,87s,76s,65s,A8o+,KTo+,QTo+,JTo",
      "range_oop": "55-22,A8s-A2s,K9s-K6s,Q9s-Q6s,J9s-J7s,T8s-T7s,97s,98s,86s,87s,75s,76s,64s,65s,53s,54s,43s,AJo-A8o,KTo-K9o,QTo,QJo,JTo,T9o,98o",
      "tree": {
        "add_allin": false,
        "allin_threshold": 0.85,
        "carry_aggressor_through_checks": null,
        "effective_stack": 970.0,
        "ip": [
          {
            "bet": [
              {
                "PotPct": 33.0
              },
              {
                "PotPct": 75.0
              }
            ],
            "donk": [],
            "raise": [
              {
                "PotPct": 60.0
              }
            ]
          },
          {
            "bet": [
              {
                "PotPct": 75.0
              }
            ],
            "donk": [],
            "raise": [
              {
                "PotPct": 60.0
              }
            ]
          },
          {
            "bet": [
              {
                "PotPct": 75.0
              }
            ],
            "donk": [],
            "raise": [
              {
                "PotPct": 60.0
              }
            ]
          }
        ],
        "max_raises": 10,
        "oop": [
          {
            "bet": [
              {
                "PotPct": 33.0
              }
            ],
            "donk": [],
            "raise": [
              {
                "PotPct": 60.0
              }
            ]
          },
          {
            "bet": [
              {
                "PotPct": 75.0
              }
            ],
            "donk": [],
            "raise": [
              {
                "PotPct": 60.0
              }
            ]
          },
          {
            "bet": [
              {
                "PotPct": 75.0
              }
            ],
            "donk": [],
            "raise": [
              {
                "PotPct": 60.0
              }
            ]
          }
        ],
        "rake_cap": 3.0,
        "rake_pct": 0.05,
        "starting_pot": 60.0
      }
    },
    "geometry": {
      "fixture_id": "river",
      "fold_ctas_per_traverser": 10,
      "fold_spans": [
        {
          "count": 0,
          "level": 0,
          "start": 0
        },
        {
          "count": 0,
          "level": 1,
          "start": 0
        },
        {
          "count": 1,
          "level": 2,
          "start": 0
        },
        {
          "count": 2,
          "level": 3,
          "start": 1
        },
        {
          "count": 2,
          "level": 4,
          "start": 3
        },
        {
          "count": 2,
          "level": 5,
          "start": 5
        },
        {
          "count": 2,
          "level": 6,
          "start": 7
        },
        {
          "count": 1,
          "level": 7,
          "start": 9
        }
      ],
      "mapping": {
        "bytes": 200,
        "file": "river-fold-mapping.u32le",
        "fnv1a64": "f259bb6479e3842d",
        "record": "five little-endian u32: node,slot0,slot1,amount0bits,amount1bits"
      },
      "nh": [
        233,
        280
      ],
      "nodes": 33,
      "physical_reach_has_padding": false,
      "reach_blocks": [
        17,
        17
      ],
      "stage": "geometry",
      "uploaded_metadata_exact_both_arms": true
    }
  }
]
"###;
