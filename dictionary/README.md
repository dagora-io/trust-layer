# Shared consulting dictionary

This is the public word list for how projects talk about advice.

It is not an engine. It is not a decision API. It does not say what anyone is allowed to do.

Projects may adopt or narrow these terms in a later project file. This folder is the shared set only.

## Closed terms

| Term | Meaning |
|---|---|
| `statement` | What is being asserted this time |
| `confidence` | How sure the speaker claims to be — a word, not a permission |
| `grounds` | What the statement rests on |
| `source` | Who said it, in which run, at what time |
| `brief` | What was asked this time |
| `you_keep_the_call` | The human retains the decision |

No other term is in the shared set. A project overlay may add local aliases later; it may not add an action key.

## Check

`python3 tools/check.py` also loads `dictionary/shared.json`. Extra keys, action keys, and a short banned-word list fail. A lawful envelope in `examples/` still passes.

## Status

v0.1 dictionary. The v0.1 envelope in `spec/` is unchanged in this drop.
