# AGENTS.md — cowsay (kodexArg)

## Identity

| | |
|---|---|
| Author | kodexArg |
| License | MIT |
| Skill | **cowsay** |
| Scope | This tree only |

## Layers (keep separate)

| Path | Role |
|------|------|
| `bin/cowsay` | CLI compose |
| `lib/dialog.py` | dialog box only |
| `lib/art.py` | cowfile load / faces only |
| `cows/*.cow` | ASCII resources (persistent; swap without touching dialog) |

## Contract

```bash
W=$(( ${COLUMNS:-80} - 4 ))
./bin/cowsay -W "$W" <<'COWEOF'
$TEXT
COWEOF
```

Same text + same flags + same width env → same bytes.

## Rules

1. Do not write outside this path unless ordered.
2. Do not `apt install cowsay`.
3. Do not freehand cow/dialog ASCII; run the binary.
4. Do not put balloon logic in `.cow` files; do not put cow geometry in `dialog.py`.
5. After changes: `python3 tests/test_cowsay.py`.

## Layout note

This skill lives at `skills/cowsay/` (skills.sh package convention). Repo root
keeps `README.md` + `LICENSE` only. Do not put `SKILL.md` at repo root.

## Verify

```bash
# from skills/cowsay/
python3 tests/test_cowsay.py
printf '%s' 'moo' | ./bin/cowsay -W 40
printf '%s' 'x' | ./bin/cowsay -W 40 | cmp - <(printf '%s' 'x' | ./bin/cowsay -W 40)
```
