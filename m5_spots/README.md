# M5 spot configs

Inputs for `solve-cli realization <spot.json> <boards> [iters] [target] [out.jsonl]`.
Each file is a postflop `SpotConfig` (the `board` field is overwritten per
board). Phase B runs ~20 of these × a ~100-flop subset:

    ./target/release/solve-cli flops 100 > m5_spots/flops100.txt
    ./target/release/solve-cli realization m5_spots/srp_btn_bb_100bb.json m5_spots/flops100.txt 1500 0.3 realization_obs.jsonl

Build configs from REAL lab exports so the fit covers the spots you study:
solve a lab game, walk a heads-up line to the flop, SEND TO POSTFLOP — the
range texts appear in SETUP's two range boxes; copy them plus pot/stack/rake
into a file here. Vary SPR (single-raised / limped / 3-bet pots) and keep
the bet-size menus you actually study — R is conditional on the menu.
