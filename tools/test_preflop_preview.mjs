import assert from 'node:assert/strict';
import { publishedIteration, publicationKey, publicationLabel, solveCompletionLabel, supportsEarlyPreview, earlyPreviewRequest, exportPublicationLabel } from '../web/js/preflop_preview.js';
assert.equal(publishedIteration({iteration:49,published_iteration:2}),2);
assert.equal(publishedIteration({iteration:74}),74); // older-server fallback
assert.equal(publicationKey({iteration:11,published_iteration:10}),publicationKey({iteration:19,published_iteration:10}));
assert.notEqual(publicationKey({published_iteration:50}),publicationKey({published_iteration:50,accuracy_iteration:50}));
assert.match(publicationLabel({published_iteration:2,accuracy_iteration:null}),/Preview.*accuracy not measured/);
assert.match(publicationLabel({published_iteration:60,accuracy_iteration:50,gap_total:.02}),/iteration 60.*measured at iteration 50/);
assert.match(publicationLabel({published_iteration:1}),/Preparing/);
assert.doesNotMatch(publicationLabel({published_iteration:1}),/Target reached/);
assert.match(publicationLabel({published_iteration:50,converged:true}),/Target reached.*approximation/);
assert.match(solveCompletionLabel({state:'done',stop_reason:'iteration_limit'}),/target not reached/);
assert.match(solveCompletionLabel({state:'done',stop_reason:'target_reached'}),/Target gap reached/);
assert.doesNotMatch(solveCompletionLabel({state:'done'}),/Target gap reached/);
// Same seam the Lab uses: unsupported servers never receive an unknown field.
const base = Object.freeze({iterations:2000,check_every:50,target_gap:0.005});
for (const caps of [undefined,null,{}, {early_preview_v1:false}, {early_preview_v1:1}, {early_preview_v1:'true'}]) {
  assert.equal(supportsEarlyPreview(caps),false);
  assert.deepEqual(earlyPreviewRequest(base,true,supportsEarlyPreview(caps)),base);
}
assert.equal(supportsEarlyPreview({early_preview_v1:true}),true);
assert.deepEqual(earlyPreviewRequest(base,true,true),{...base,early_preview:true});
assert.deepEqual(earlyPreviewRequest(base,false,true),base);
assert.deepEqual(earlyPreviewRequest({...base,early_preview:true},true,false),base);
assert.equal('early_preview' in base,false);
assert.equal(exportPublicationLabel(undefined),'');
const imported = exportPublicationLabel({published_iteration:2,accuracy_iteration:null});
assert.match(imported,/Preflop source: Preview.*iteration 2.*accuracy not measured/);
assert.match(imported,/imported ranges stay fixed while Preflop Lab continues/);
assert.doesNotMatch(imported,/Target reached/);
assert.match(exportPublicationLabel({published_iteration:50,converged:true}),/preflop approximation/);
console.log('preflop publication, capability compatibility and export provenance tests passed');
