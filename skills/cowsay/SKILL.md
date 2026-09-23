---
name: cowsay
description: >
  Deterministic cowsay for AI agents (kodexArg). Renders replies through a
  bundled Python stdlib bin/cowsay with terminal-aware wrap and swappable
  ASCII art. Use when the user runs /cowsay, asks for cowsay mode, cowthink,
  modo vaca, change the cow, or switches art with /cowsay tux (or any stem
  from cowsay -l). Apply persistent switches with --set-cow. Replies are
  written in English unless the user explicitly asks for another language;
  Spanish trigger phrases are recognized as input, not as a language request.
license: MIT
compatibility: >
  Requires Python 3. Uses only the Python standard library. Bundled
  bin/cowsay under this skill folder — do not apt-install system cowsay.
metadata:
  author: kodexArg
  version: "1.0.5"
  homepage: https://github.com/kodexArg/cowsay
---

# cowsay

```
╭─────────────────────────────────────────────────────╮
│ Thanks: original cowsay — Tony Monroe / cowsay-org  │
│ https://github.com/cowsay-org/cowsay                │
│                                                     │
│ npx skills add kodexArg/cowsay                      │
│                                                     │
│ /cowsay tux                                         │
│ /cowsay moose                                       │
│ /cowsay default                                     │
│ /cowsay <text>                                      │
╰─────────────────────────────────────────────────────╯
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
```

Deterministic cowsay for AI agents. Python 3 **stdlib only**. **MIT**.
Page: https://skills.sh/kodexArg/cowsay/cowsay

Skill root after install: wherever the agent placed it (e.g.
`~/.agents/skills/cowsay`). Binary: `$SKILL_ROOT/bin/cowsay`.

## Prerequisites

```bash
python3 --version          # 3.x
test -x "$SKILL_ROOT/bin/cowsay"
"$SKILL_ROOT/bin/cowsay" -l
"$SKILL_ROOT/bin/cowsay" -V
```

No network, no extra packages, no system `cowsay`.

## How to use (chat)

| User says | What happens |
|-----------|----------------|
| `/cowsay` | Enter cowsay mode until “normal mode” / “exit cowsay” / “enough cow” (ES: “basta vaca” / “salí de cowsay”) |
| `/cowsay tux` | **Switch art** to Tux (persist with `--set-cow tux`) |
| `/cowsay moose` | Switch art to moose |
| `/cowsay default` | Switch art to default cow |
| `/cowsay <stem>` | Switch art if `stem` is listed by `cowsay -l` |
| `/cowsay <text>` | One-shot: render that text if `text` is **not** a loaded stem |
| “change the cow” (no name) (ES: “cambiar la vaca”) | List every stem from `-l`, wait for pick, then `--set-cow` |
| “cowthink” / “think it” (ES: “pensá”) | Render with `--think` |
| “just this once” + a stem (ES: “solo esta vez”) | One-shot art via `-f <stem>` (do not persist) |

### Example — TUX

```text
/cowsay tux
```

1. Confirm stem is loaded: `"$SKILL_ROOT/bin/cowsay" -l`
2. Persist: `"$SKILL_ROOT/bin/cowsay" --set-cow tux`
3. Confirm by rendering through the binary (Tux art, not freehand ASCII)

**Other cows:** whatever `./bin/cowsay -l` returns (bundled set is typically
`default`, `moose`, `tux`; plus any extra `.cow` under `cows/` or `COWPATH`).

## CLI (local / agent shell)

```bash
printf '%s' 'moo' | "$SKILL_ROOT/bin/cowsay"
printf '%s' 'hi'  | "$SKILL_ROOT/bin/cowsay" -W 40
printf '%s' 'hi'  | "$SKILL_ROOT/bin/cowsay" -W 20 -f tux
printf '%s' 'hmm' | "$SKILL_ROOT/bin/cowsay" -W 40 --think
"$SKILL_ROOT/bin/cowsay" -l
"$SKILL_ROOT/bin/cowsay" --set-cow tux
"$SKILL_ROOT/bin/cowsay" --show-cow
python3 "$SKILL_ROOT/tests/test_cowsay.py"
```

Prefer a **quoted heredoc** for multi-line answers:

```bash
"$SKILL_ROOT/bin/cowsay" <<'COWEOF'
Your full answer here.
COWEOF
```

### Flags (common)

| Flag | Effect |
|------|--------|
| `-W N` | Wrap width (display columns), clamped to the 72-column max. Prefer omitting it |
| `-f <stem>` | One-shot cow (does not write `.active-cow`) |
| `--set-cow <stem>` | Persist active cow to `.active-cow` |
| `--show-cow` | Print active stem |
| `-l` | List loaded stems |
| `--think` | Thought bubbles instead of speech |
| `-d` / faces | Classic face flags when asked |

### Environment

| Env | Effect |
|-----|--------|
| `COLUMNS` | Terminal width when `-W` omitted (still capped at 72) |
| `COWSAY_WIDTH` | Pin wrap width, uncapped (tests/CI; beats `COLUMNS`) |
| `COWSAY_COW` | Force active cow stem (beats `.active-cow`) |
| `COWPATH` | Extra directories of `.cow` files |

### Active cow priority

`-f` → `COWSAY_COW` → `.active-cow` → `default`

## Agent instructions

**Renderer is law.** Never freehand the dialog box or the ASCII animal. Always
run `$SKILL_ROOT/bin/cowsay` and show only its stdout (one fenced code block).

### 1. Width: omit `-W`

The binary resolves it (`COLUMNS` → terminal size → 80, minus 4) and caps every
result at **72** content columns — a 77-column box, which fits an 80-column
terminal even with the chat client's code-block gutter. Do not hardcode a width
and do not shell out to `stty`/`tput` first: `-W N` is clamped to the same
ceiling, so a bigger number cannot widen the box. `COWSAY_WIDTH` is the only
uncapped path and exists for tests/CI.

### 2. Switch cow when the user names a stem

```bash
"$SKILL_ROOT/bin/cowsay" -l
"$SKILL_ROOT/bin/cowsay" --set-cow <stem>
"$SKILL_ROOT/bin/cowsay" <<'COWEOF'
Done: active cow = <stem>
COWEOF
```

Do not invent stem names. Source of truth is `-l`.

### 3. Every final reply in cowsay mode

1. Write the full answer in **English**, regardless of the language the user
   wrote in. Switch languages only on an explicit request (“answer in
   Spanish”); a Spanish trigger phrase is not such a request.
2. Pipe it through the binary (heredoc above).
3. User-visible output = that stdout only.

### 4. Failure

If the binary exits non-zero, report stderr and exit code in **plain text**.
Do not invent art.

### 5. Confinement

Only operate inside `$SKILL_ROOT`. After code changes:
`python3 "$SKILL_ROOT/tests/test_cowsay.py"`.

## Layout

```text
skills/cowsay/
  SKILL.md          this file (Agent Skills format)
  bin/cowsay        CLI compose only
  lib/dialog.py     balloon, wrap, terminal width
  lib/art.py        COWPATH, load .cow, faces, active cow
  cows/*.cow        ASCII resources ($thoughts $eyes $tongue)
  tests/            goldens
```

Dialog and art are separate layers so figures can change without rewriting the
balloon.

## License

**MIT** — Copyright (c) 2026 kodexArg (Gabriel Cavedal) / kodexarg.com.

Full text: repository root `LICENSE`.
