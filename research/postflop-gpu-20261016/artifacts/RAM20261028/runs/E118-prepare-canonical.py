import ast,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()
S=ROOT/'runs/E118-source';m=h.read(S/'manifest.json')
h.save(S/'source-review.json',{'id':'E118','at':h.now(),'source_manifest_sha256':h.sha(S/'manifest.json'),'scope':m['scope'],'inverse_exact':m['entire_CRLF_source_inverse_exact'],'original_noneligible_loop_exact':m['original_full_noneligible_hand_loop_byte_exact'],'arithmetic_scout_sha256':h.sha(ROOT/'runs/D281-zero-tie-scout/arithmetic-contract.json'),'PTX_report_sha256':h.sha(ROOT/'runs/D282-zero-tie-PTX/report.json'),'native_report_sha256':h.sha(ROOT/'runs/D283-zero-tie-native/report.json'),'direct_full_raw_report_sha256':h.sha(ROOT/'comparisons/E118-kernel-control-root-check/report.json'),'limits':m['risks']})
parent=ROOT/'runs/D222-prepare-canonical.py';code=parent.read_text(encoding='utf-8')
for a,b in [('E107','E118'),('D222-early-payout-canonical','D284-zero-tie-canonical'),('D222','D284'),('pass_scoped_full_early_payout_raw_equivalence','pass_scoped_full_zero_tie_raw_equivalence'),('3820','12140'),('7640','24280'),('E118-direct-audit/audit.exit.json','E118-direct-audit/root-reader.exit.json'),('D221-showdown-native-scheduling/report.json','D283-zero-tie-native/report.json'),('Only CUDA declaration relocation differs.','Only the fixed guarded zero-tie CUDA form differs. All other original host/observer/state contracts are retained.'),('Earlier payout full canonical raw lifecycle','Zero-tie full canonical raw lifecycle'),('Earlier payout full canonical accuracy controls','Zero-tie full canonical accuracy controls'),('Earlier payout','Zero-tie'),('Earlier payout-load','Zero-tie'),('early-payout','zero-tie'),('source placement/volatile/asm/helper/flags/entry subset/threshold/quality/sample rescue','predicate/bound/architecture/loop/source/helper/flags/width/quality/sample rescue')]:
 code=code.replace(a,b)
assert 'D221-showdown'not in code and 'E107'not in code
out=ROOT/'runs/D284-prepare-canonical.py';assert not out.exists();ast.parse(code);out.write_bytes(code.encode('utf-8'))
exec(compile(code,str(out),'exec'),dict(globals(),__file__=str(out)))
