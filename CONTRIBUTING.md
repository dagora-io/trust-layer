# Contributing

Change the standard in the open. Do not send engine source, model weights, or private run logs.

1. Open an issue describing the gap (missing field, ambiguous sentence, checker hole).
2. Keep examples in `examples/` paired: one valid, one invalid, for each rule you touch.
3. Run `python3 tools/check.py` before you ask for review.

Editorial changes that make a sentence shorter without changing the rule are welcome. New claim grades are not in scope for v0.1.
