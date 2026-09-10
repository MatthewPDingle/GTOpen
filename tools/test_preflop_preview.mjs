import assert from 'node:assert/strict';
import { publishedIteration, publicationKey, publicationLabel, solveCompletionLabel } from '../web/js/preflop_preview.js';
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
console.log('preflop preview publication tests passed');
