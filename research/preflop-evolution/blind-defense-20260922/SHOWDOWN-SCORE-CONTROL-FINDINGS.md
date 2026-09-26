# Isolated showdown scoring control

The research-only `hu_board_outcomes_v1` example returns twice BB's showdown share (0=loss, 1=tie, 2=win) for supplied nine-card deals. It accepts at most 65,536 deals, rejects out-of-deck and repeated cards, refuses an existing output file, and retains its exact input text in its output. It does not build a game, fit a model, use the GPU or change the production server.

Four example tests passed: pocket aces versus kings and the role-swapped result, a shared royal-flush tie, a wheel versus a pair, and invalid-card rejection. The four existing evaluator unit tests also passed, including its randomized reference comparison. Other integration tests were filtered out by that focused command; this was not a full integration-suite run.

A separate Python scorer compares all 21 five-card subsets using explicit categories and kickers. Its fixtures cover all nine hand categories, kicker ordering, wins, losses and ties. It agreed with the native scorer on all 64 previously inspected control deals, including the complementary outcome after swapping the two private hands. The input, native output, source identities and result are retained in `showdown-score-control-v1-*`.

The archived diagnostic will additionally compare the native and independent scores for every one of its 65,536 supplied deals. Exact expected showdown shares come from authenticated archived private-pair counts, with integer totals equal to all 1,712,304 possible five-card boards. This avoids a new full-board enumeration. Correct scoring establishes neither variance reduction nor better strategic play; those remain separate questions.
