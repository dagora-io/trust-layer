# Project overlay

A project file says which shared consulting terms this repository uses.

It may adopt a subset (narrow). It may not add a term that is not in `dictionary/shared.json` (widen).

The shared term keys are pinned at commit `a1c45cb53132bcd476309fcc7f107012e2401a5d`.

## Shape

```text
schema   dagora.trust-layer.project/0.1
adopt    list of shared term keys this project uses
drop     optional list of unused shared keys; must not overlap adopt
aliases  optional local name → shared term key
```

No action keys. Alias targets must be keys from the pinned shared set.

## Check

`python3 tools/check.py` loads `projects/example/project.json` and the project examples. A widen file must fail.
