"""Review exact final publication, preserve original evidence, write local notes."""
import hashlib,json
from pathlib import Path
STAGE=Path(__file__).resolve().parent
TOOLS=Path(r'T:\Dev\GTOpen\tools\research')
OUT=TOOLS.parents[1]/'research/preflop-evolution/blind-defense-20260922'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
publication=json.loads((OUT/'preflop-expected-training-publication-v1.json').read_bytes());inputs={}
for path,row in publication['byte_copies'].items():assert sha(path)==row['sha256'];inputs[path]=sha(path)
for name,h in publication['original_pins'].items():assert sha(OUT/name)==h;inputs[str(OUT/name)]=h
preserved=json.loads((OUT/'preflop-expected-training-initial-preservation-v1.json').read_bytes())
for name,h in preserved['results'].items():
    assert sha(OUT/name)==h
    value=json.loads((OUT/name).read_bytes());assert value['passed'] and not value['scientific_attempt']
    for original,identity in value['inputs'].items():
        reference=publication['initial_source_snapshots'].get(original)
        path=Path(reference['path']) if reference else Path(original)
        assert sha(path)==identity;inputs[str(path)]=identity
results={}
for name in ('preflop-expected-training-checkpoint-check-v1-result.json','preflop-expected-training-cuda-check-v1-result.json'):
    path=OUT/name;value=json.loads(path.read_bytes());assert value['passed'] and not value['scientific_attempt']
    for p,h in value['inputs'].items():assert sha(p)==h;inputs[p]=h
    inputs[str(path)]=sha(path);results[name]=value
cpu=results['preflop-expected-training-checkpoint-check-v1-result.json']
gpu=results['preflop-expected-training-cuda-check-v1-result.json']
assert len(cpu['refused_cases'])==31,len(cpu['refused_cases'])
assert len(cpu['cases'])==len(gpu['cases'])==2
rows=[]
for case in cpu['cases']:
    assert case['fit_depths']==[20,40,100,200,400] and case['heldout_depths']==[60,150]
    assert case['restart_next_cycle_bit_identical'] and case['played_bank_excludes_final_unplayed_model']
    for objective in case['objectives']:rows.append(objective)
fits=[x for c in gpu['cases'] for x in c['fits']]
doc=f'''# Complete preflop learning cycles: integration, 2 October 2026

The experimental trainer now has a separate complete-round checkpoint and a shared-network fitting objective that uses accumulated evidence at every supported preflop decision. Published synthetic CPU and CUDA controls pass. The authenticated native collection workers and complete scientific runner are still to be connected and qualified. No new scientific comparison has started, and this does not establish accurate poker ranges or production readiness.

## What changes

At fitted stacks, the typed played policy already uses cumulative preflop regrets instead of letting a single retained hand visit dictate a later decision. The new fitting path teaches the shared network those complete supported preflop targets as well. This matters because predictions at withheld stacks depend on that network rather than a fitted-stack table.

For each supported hand class, the target is cumulative regret divided by the generation scale, original actor class mass, completed updates and starting stack. Original class mass then weights the loss once. It does not multiply an already weighted target a second time. A class with no supported counterfactual generation is excluded from training truth. No premium-hand action floor or invented observations are added.

Postflop uses retained importance-weighted physical-visit advantages in the same stack-normalized units. Each fitted context has an explicit positive loss weight, and its preflop/postflop proportions are explicit. **The 25%/75% proportions, four fitting steps, two board draws and seven-visit reservoirs here are synthetic software-control settings, not a selected scientific recipe or a sufficient sampling budget.** Changing these choices in a future study requires prospective declaration.

The network and Adam optimizer start fresh from the declared seed for each actor fit. Only complete rounds can be restored; an unfinished optimizer step is not a restart boundary.

## Complete rounds and restoration

The checkpoint includes both newly fitted networks, every fitted context's cumulative preflop state, class-stratified deal sampler, action RNG, both postflop retention RNGs/data, and the ordered played-model bank. Every collection must identify the same frozen played model. Board contributions are replayed from the previous state and frozen recipe before accepting the staged cumulative update. Both fit receipts bind the actual dense/sampled target calculation, context mixture, networks, generation and registered numeric path.

Saved cumulative histories must extend the previous histories and identify the model that actually played that generation. The model produced at the end remains outside the played bank until it has generated a subsequent round. Canonical array types/shapes, unused tails, public action geometry, card visibility, iteration bounds and fixed configuration are checked on publication/restoration. A deliberately interrupted publication leaves the previous checkpoint usable; orphan immutable objects are not a resume pointer. The eventual runner must publish that pointer only after complete collection/fit metrics exist.

Checkpoint validation reuses the qualified visible-input checks without constructing all fitted preflop policies merely to check a postflop row. Full state, model and catalog authentication remains mandatory. This removes unnecessary preparation; the small-control timings below are not a production speed benchmark.

## Actual software evidence

The [published CPU control](preflop-expected-training-checkpoint-check-v1-result.json) completed in {cpu['seconds']:.3f} seconds. It covers 362 and 387 input representations, both players, fitting at 20/40/100/200/400bb, and registry-only withheld 60/150bb contexts. It executes three complete synthetic rounds for 362 inputs and one for 387. Restoration reproduces the next source deals, board plans, action draws, retained visits and retention RNG state exactly, including reservoir overflow.

An independent scalar reference checks {rows[0]['independent_legal_preflop_targets']+rows[1]['independent_legal_preflop_targets']} legal preflop target entries per representation plus the weighted postflop grouped targets, context proportions and within-observation variance. Maximum target/weight error is {max(x['maximum_target_weight_error'] for x in rows):.3g}; maximum chunked-versus-direct CPU gradient error is {max(x['chunked_gradient_error'] for x in rows):.3g}. All 31 invalid/interrupted cases are refused, including partial contexts, mixed collection models, missing boards/fits, changed target/objective/network identities, preflop visits in the postflop reservoir, noncanonical arrays, changed boundary labels and detached/rewritten histories.

The [published CUDA control](preflop-expected-training-cuda-check-v1-result.json) completed in {gpu['seconds']:.3f} seconds on the RTX 3090, Torch {gpu['torch_version']} / CUDA {gpu['cuda_version']}, with TF32 disabled. Both representations and both actors fit all five contexts using four synthetic steps each. Captured fitting agrees with an independent eager CUDA loss/backward/Adam implementation: maximum parameter difference {max(x['captured_eager_maximum_parameter_error'] for x in fits):.3g}, maximum final-loss difference {max(x['captured_eager_loss_error'] for x in fits):.3g}. All four synthetic fits reduce their declared objective. Actual returned fits publish/restored complete joint checkpoints. Peak allocated CUDA tensors: {gpu['peak_cuda_allocated_bytes']} bytes; this excludes desktop allocations and says nothing about full native-board memory requirements.

Initial passed source/evidence is preserved separately before the history/allocation hardening and redundant preparation removal. The initial sandbox invocation could not access existing user-site NumPy and stopped before fixture/test execution; its environment failure remains recorded. Owner-account execution used the existing packages without installation. Final staging and published controls are separate evidence. None invokes native poker exports, fits scientific weights or changes production.

## What this does not establish

The contexts/public trees and compatible entry law are real preserved inputs, but all-in strengths, board payoffs and physical-visit targets in these tests are invented. Synthetic fit loss and exact restoration do not certify equilibrium, action values, improved AA decisions, agreement with GTO Wizard, multiway behavior, stack-specific opening ranges or generalization accuracy. The existing inherited BTN opening range and restricted preflop tree are not expanded by this integration.

The checkpoint/receipt components cannot authenticate a native process merely from a tree hash. The next work is to connect typed native board and physical/posterior-river workers, retain executable/request/process provenance and insert only postflop physical visits, then profile a representative full round against the hardware/memory/disk reserves. After that qualification, register a genuinely adequate board budget and independent stability/payoff comparison before consuming scientific training/test data.

The read-only drive inventory during preparation showed about 282 GB free on S and 13 GB on T. Future native-board/training artifacts should use S, with reserves rechecked at admission; do not place a large store on the nearly full repository drive or delete preserved failed evidence to make it fit. These are a current inventory observation, not a reserved storage allocation.

The original comparison, failed improvement criterion, models, budgets and failures remain unchanged. Production on 56708 is untouched. No GitHub push or deployment. The broad goal of accurate flexible preflop ranges remains open.
'''
target=OUT/'STACK-CONTEXT-PREFLOP-TRAINING-INTEGRATION-20261002.md'
doc=doc.replace('publish/restored','publish and restore')
with target.open('x',encoding='utf-8',newline='\n') as out:out.write(doc)
inputs[str(OUT/'preflop-expected-training-publication-v1.json')]=sha(OUT/'preflop-expected-training-publication-v1.json')
inputs[str(Path(__file__).resolve())]=sha(__file__)
receipt=OUT/'preflop-expected-training-review-v1.json'
with receipt.open('x',encoding='utf-8') as out:json.dump(dict(passed=True,inputs=inputs,outputs={str(target):sha(target)},
    synthetic_only=True,actual_native_training_worker_qualified=False,accuracy_qualified=False,
    scientific_attempt=False,production_modified=False,push=False,deployment=False),out,indent=2)
journal=OUT/'RIVER-CONTINUATION-RUNNING.md'
tail=f'''\n\n## 2026-10-02 Adelaide - complete all-node training cycles and dense/shared fit controls pass

Previous research goal turn published the typed cumulative preflop policy and native transport adapter (d9831a24); the intervening user question was explanatory. This turn implemented a separate complete-round checkpoint and shared network objective using all supported cumulative preflop targets with original actor mass applied once, explicit stack normalization and fixed context/preflop/postflop loss proportions. Both fits and all context/cumulative/sampler/action/retention states publish together; no partial round or final unplayed model enters the played bank. Saved histories now bind the actual previous played models, and canonical reservoir allocations/public visible inputs are checked without unnecessary full-policy preparation.

Initial synthetic controls passed and are preserved with their exact source snapshots. The initial sandbox NumPy access failure occurred before tests; owner-account runs use existing packages. Strengthened final staging and published controls passed. Published CPU duration {cpu['seconds']:.3f}s covers five fitted depths/two held-out registry depths, both representations/actors, three/one rounds, exact next-round restoration, independent dense/postflop weights/loss/gradients and31refused unsafe/interrupted cases. Published CUDA duration {gpu['seconds']:.3f}s qualifies four actual synthetic fits against independent eager CUDA updates and complete checkpoint restoration; peak allocated tensors {gpu['peak_cuda_allocated_bytes']}bytes. These are controls, not representative speed or poker-accuracy evidence; proportion .25, K2 and four fit steps are test settings only.

Saved training integration notes SHA {sha(target)}; review receipt SHA {sha(receipt)}. Original comparison/findings/AA/expected-component/cumulative/policy evidence pins remain unchanged. No scientific attempt, native invocation, production56708change, push or deployment. Software-control handles88160/78414/32514/19293/71622/33753 all completed successfully and are closed; no scientific worker was started by this work.

Next is genuine typed native board/physical/posterior64 worker integration and authenticated complete runner, representative resource profiling, then prospective registration of sufficient board sampling and independent stability/payoff evaluation. Current components must be used in that real runner rather than remaining unused source. Five-bets, stack-specific openings, multiway/GTO Wizard/full preflop accuracy and production readiness remain unproven. Goal active; current turn made concrete qualified training integration.
'''
with journal.open('ab') as out:out.write(tail.encode('utf-8'))
print(json.dumps(dict(document=str(target),review=str(receipt),inputs=len(inputs),document_sha256=sha(target),review_sha256=sha(receipt))))
