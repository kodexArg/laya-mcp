#!/usr/bin/env python3
"""Goldens / regression suite for bin/cowsay (stdlib only)."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIN = ROOT / "bin" / "cowsay"

sys.path.insert(0, str(ROOT))
from lib.dialog import MAX_WRAP_COLS  # noqa: E402


def run(
    args: list[str],
    stdin: bytes | str = b"",
    *,
    env: dict[str, str] | None = None,
    use_active_cow: bool = False,
) -> subprocess.CompletedProcess[bytes]:
    """
    Run bin/cowsay.

    By default pins COWSAY_COW=default so a developer's .active-cow (e.g. tux)
    cannot break goldens. Pass use_active_cow=True to exercise --set-cow /
    --show-cow / .active-cow (clears COWSAY_COW unless env sets it).
    """
    data = stdin.encode("utf-8") if isinstance(stdin, str) else stdin
    full_env = os.environ.copy()
    if use_active_cow:
        full_env.pop("COWSAY_COW", None)
    else:
        full_env["COWSAY_COW"] = "default"
    if env:
        full_env.update(env)
    return subprocess.run(
        [str(BIN), *args],
        input=data,
        capture_output=True,
        env=full_env,
        check=False,
    )


class CowsayTests(unittest.TestCase):
    def test_display_width_wide_and_combining(self) -> None:
        sys.path.insert(0, str(ROOT))
        from lib.dialog import display_width, normalize, pad_display

        s = "café ñandú 😀 中文"
        self.assertEqual(len(s), 15)
        self.assertEqual(display_width(s), 18)
        # NFD: combining acute is zero columns
        nfd = "cafe\u0301"
        self.assertEqual(len(nfd), 5)
        self.assertEqual(display_width(nfd), 4)
        self.assertEqual(display_width(normalize(nfd)), 4)
        # pad to columns, not codepoints
        padded = pad_display("中", 4)
        self.assertEqual(display_width(padded), 4)
        self.assertTrue(padded.startswith("中"))

    def test_box_aligned_with_wide_chars(self) -> None:
        """Wide / fullwidth glyphs must not blow past the right border."""
        sys.path.insert(0, str(ROOT))
        from lib.dialog import display_width

        sample = "café ñandú 😀 中文"
        r = run(["-W", "40"], sample)
        self.assertEqual(r.returncode, 0, r.stderr)
        lines = r.stdout.decode().splitlines()
        box = []
        for L in lines:
            if L[:1] in "╭│╰":
                box.append(L)
            elif box:
                break
        self.assertGreaterEqual(len(box), 5)  # top + 3 body + bot
        cols = display_width(box[0])
        for L in box:
            self.assertEqual(display_width(L), cols, msg=repr(L))
        # content row contains the sample and stays inside the box
        self.assertTrue(any(sample in L or "café" in L for L in box))

    def test_moo_width_40(self) -> None:
        r = run(["-W", "40"], "moo")
        self.assertEqual(r.returncode, 0, r.stderr)
        out = r.stdout.decode()
        self.assertIn("│ moo ", out)
        self.assertIn("╭", out)
        self.assertIn("╰", out)
        self.assertIn("(oo)", out)
        self.assertTrue(out.endswith("\n"))

    def test_wrap_width_3(self) -> None:
        r = run(["-W", "3"], "a b c")
        self.assertEqual(r.returncode, 0, r.stderr)
        lines = r.stdout.decode().splitlines()
        # default cow art is 28 cols → content_w >= 24, box 28; min 3 text rows
        self.assertEqual(lines[0][0], "╭")
        self.assertEqual(lines[0][-1], "╮")
        self.assertTrue(lines[1].startswith("│ a b "))
        self.assertTrue(lines[2].startswith("│ c   "))
        self.assertEqual(lines[3], "│" + " " * (len(lines[0]) - 2) + "│")
        self.assertEqual(lines[4][0], "╰")
        self.assertEqual(len(lines[0]), 28)  # matches cow tail span

    def test_deterministic(self) -> None:
        a = run(["-W", "40"], "x")
        b = run(["-W", "40"], "x")
        self.assertEqual(a.returncode, 0)
        self.assertEqual(a.stdout, b.stdout)

    def test_think(self) -> None:
        r = run(["-W", "20", "--think"], "hmm")
        self.assertEqual(r.returncode, 0, r.stderr)
        out = r.stdout.decode()
        self.assertIn("│ hmm ", out)
        self.assertIn("╭", out)
        # original two-line thought stems
        self.assertIn("\n        o   ", out)
        self.assertIn("\n         o  ", out)

    def test_dead_face(self) -> None:
        r = run(["-W", "20", "-d"], "x")
        self.assertEqual(r.returncode, 0, r.stderr)
        out = r.stdout.decode()
        self.assertIn("(xx)", out)
        self.assertIn("U ", out)

    def test_moose_eyes_substituted(self) -> None:
        r = run(["-W", "20", "-f", "moose", "-e", "XX"], "x")
        self.assertEqual(r.returncode, 0, r.stderr)
        out = r.stdout.decode()
        self.assertIn("(XX)", out)
        self.assertNotIn("(oo)", out)

    def test_moose_dead_eyes(self) -> None:
        r = run(["-W", "20", "-f", "moose", "-d"], "x")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("(xx)", r.stdout.decode())

    def test_layers_exist_and_separated(self) -> None:
        """dialog.py has no cow paths; art.py has no balloon glyphs."""
        dialog = (ROOT / "lib" / "dialog.py").read_text(encoding="utf-8")
        art = (ROOT / "lib" / "art.py").read_text(encoding="utf-8")
        self.assertNotIn("cows/", dialog)
        self.assertNotIn(".cow", dialog)
        self.assertNotIn("╭", art)
        self.assertNotIn("def balloon", art)
        self.assertIn("load_cow", art)
        self.assertIn("def balloon", dialog)

    def test_swap_cow_resource_without_dialog_change(self) -> None:
        """New .cow on COWPATH works; dialog still rounded."""
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "blob.cow").write_text(
                "  $thoughts\n  [$eyes]\n  $tongue~~\n", encoding="utf-8"
            )
            r = run(["-f", "blob", "-W", "20"], "hi", env={"COWPATH": tmp})
            self.assertEqual(r.returncode, 0, r.stderr)
            out = r.stdout.decode()
            self.assertIn("╭", out)
            self.assertIn("[oo]", out)
            self.assertIn("~~", out)

    def test_missing_cow(self) -> None:
        r = run(["-f", "no-such-cow", "-W", "20"], "x")
        self.assertEqual(r.returncode, 2)
        self.assertIn(b"cowfile not found", r.stderr)

    def test_refuse_non_cow_path(self) -> None:
        r = run(["-f", "/etc/passwd", "-W", "20"], "x")
        self.assertEqual(r.returncode, 2)
        self.assertIn(b"refusing non-.cow path", r.stderr)
        self.assertNotIn(b"root:", r.stdout)

    def test_explicit_cow_path_ok(self) -> None:
        cow = ROOT / "cows" / "tux.cow"
        r = run(["-f", str(cow), "-W", "20"], "hi")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(b"o_o", r.stdout)

    def test_invalid_utf8_stdin(self) -> None:
        r = run(["-W", "20"], b"\xff\xfe")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(r.stderr, b"cowsay: invalid UTF-8 on stdin\n")
        self.assertEqual(r.stdout, b"")

    def test_list_cows(self) -> None:
        r = run(["-l"])
        self.assertEqual(r.returncode, 0, r.stderr)
        names = r.stdout.decode().strip().split()
        self.assertEqual(names, ["default", "moose", "tux"])

    def test_cowpath_keeps_bundled_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            custom = Path(tmp) / "x.cow"
            custom.write_text("  $thoughts X\n  ($eyes)\n  $tongue\n", encoding="utf-8")
            r = run(["-W", "10"], "z", env={"COWPATH": tmp})
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn(b"(oo)", r.stdout)  # bundled default still resolves
            r2 = run(["-f", "x", "-W", "10"], "z", env={"COWPATH": tmp})
            self.assertEqual(r2.returncode, 0, r2.stderr)
            self.assertIn(b"X", r2.stdout)

    def test_version(self) -> None:
        r = run(["-V"])
        self.assertEqual(r.returncode, 0)
        self.assertIn(b"1.0.5", r.stdout)
        self.assertIn(b"kodexArg", r.stdout)

    def test_hard_wrap_n(self) -> None:
        r = run(["-n", "-W", "5"], "no wrap please\nsecond")
        self.assertEqual(r.returncode, 0, r.stderr)
        out = r.stdout.decode()
        self.assertIn("no wrap please", out)
        self.assertIn("second", out)

    def test_empty_stdin(self) -> None:
        r = run(["-W", "40"], "")
        self.assertEqual(r.returncode, 0, r.stderr)
        out = r.stdout.decode()
        lines = out.splitlines()
        self.assertEqual(lines[0][0], "╭")
        # short/empty text → floor to cow silhouette (28), not full -W
        self.assertEqual(len(lines[0]), 28)
        self.assertTrue(all(lines[i].startswith("│") for i in (1, 2, 3)))
        self.assertIn("(oo)", out)
        self.assertTrue(out.endswith("\n"))

    def test_moo_default_golden(self) -> None:
        """Min-3 box hugs text; floor cow tail; +1 blank; original art."""
        r = run(["-W", "40"], "moo")
        self.assertEqual(r.returncode, 0, r.stderr)
        # text 3+1=4 < cow floor 24 → content 24, box 28
        self.assertEqual(
            r.stdout.decode(),
            "╭──────────────────────────╮\n"
            "│ moo                      │\n"
            "│                          │\n"
            "│                          │\n"
            "╰──────────────────────────╯\n"
            "        \\   ^__^\n"
            "         \\  (oo)\\_______\n"
            "            (__)\\       )\\/\\\n"
            "                ||----w |\n"
            "                ||     ||\n",
        )

    def test_dialog_min_height_and_cow_width(self) -> None:
        # short text + wide -W → still floor to cow (28), not max -W
        r = run(["-W", "60"], "x")
        self.assertEqual(r.returncode, 0, r.stderr)
        lines = r.stdout.decode().splitlines()
        box_w = len(lines[0])
        self.assertEqual(box_w, 28)
        self.assertEqual(sum(1 for L in lines if L.startswith("│")), 3)
        cow_w = max(len(L) for L in lines if not L.startswith(("╭", "╰", "│")))
        self.assertEqual(box_w, cow_w)

    def test_dialog_grows_with_long_text_not_bare_W(self) -> None:
        """Long line grows box to text+1; -W only wraps, does not pad short lines."""
        r = run(["-W", "60"], "hi")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(len(r.stdout.decode().splitlines()[0]), 28)  # short → cow floor
        # one long unwrapped-enough line: 30 chars → content 31, box 35 (> cow 28)
        r2 = run(["-W", "60", "-n"], "x" * 30)
        self.assertEqual(r2.returncode, 0, r2.stderr)
        self.assertEqual(len(r2.stdout.decode().splitlines()[0]), 35)

    def test_wrap_limit_from_W_not_box_pad(self) -> None:
        """-W / COWSAY_WIDTH limit wrap; short message does not inflate box."""
        r = run([], "hi", env={"COWSAY_WIDTH": "50", "COLUMNS": "20"})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(len(r.stdout.decode().splitlines()[0]), 28)

    def test_wrap_capped_at_max_cols(self) -> None:
        """Wide -W and wide terminals both cap at MAX_WRAP_COLS; COWSAY_WIDTH does not."""
        long_word = "x" * 200
        box_w = MAX_WRAP_COLS + 5  # 2 borders + 2 pad + the balloon's +1 hug column

        capped_flag = run(["-W", "200"], long_word)
        self.assertEqual(capped_flag.returncode, 0, capped_flag.stderr)
        self.assertEqual(len(capped_flag.stdout.decode().splitlines()[0]), box_w)

        capped_env = run([], long_word, env={"COLUMNS": "200"})
        self.assertEqual(capped_env.returncode, 0, capped_env.stderr)
        self.assertEqual(len(capped_env.stdout.decode().splitlines()[0]), box_w)

        uncapped = run([], long_word, env={"COWSAY_WIDTH": "120"})
        self.assertEqual(uncapped.returncode, 0, uncapped.stderr)
        self.assertEqual(len(uncapped.stdout.decode().splitlines()[0]), 125)

    def test_original_default_stems(self) -> None:
        r = run(["-W", "20"], "x")
        self.assertEqual(r.returncode, 0, r.stderr)
        lines = r.stdout.decode().splitlines()
        # two original diagonal stems before the body
        self.assertTrue(any("^__^" in L and "\\" in L for L in lines))
        self.assertTrue(any("(oo)\\_______" in L for L in lines))

    def test_symlink_cow_escape_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evil = Path(tmp) / "evil.cow"
            evil.symlink_to("/etc/passwd")
            r = run(["-f", str(evil), "-W", "10"], "x")
            self.assertEqual(r.returncode, 2)
            self.assertIn(b"refusing cowfile outside COWPATH", r.stderr)
            self.assertNotIn(b"root:", r.stdout)
            r2 = run(["-f", "evil", "-W", "10"], "x", env={"COWPATH": tmp})
            self.assertEqual(r2.returncode, 2)
            self.assertNotIn(b"root:", r2.stdout)
            # Must not appear in -l either
            r3 = run(["-l"], env={"COWPATH": tmp})
            self.assertEqual(r3.returncode, 0, r3.stderr)
            self.assertNotIn("evil", r3.stdout.decode().split())

    def test_cow_outside_cowpath_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            outside = Path(tmp) / "lone.cow"
            outside.write_text("  $thoughts X\n  ($eyes)\n", encoding="utf-8")
            r = run(["-f", str(outside), "-W", "10"], "x")
            self.assertEqual(r.returncode, 2)
            self.assertIn(b"refusing cowfile outside COWPATH", r.stderr)
            # Allowed once its directory is on COWPATH
            r2 = run(["-f", str(outside), "-W", "10"], "x", env={"COWPATH": tmp})
            self.assertEqual(r2.returncode, 0, r2.stderr)
            self.assertIn(b"X", r2.stdout)

    def test_symlink_into_bundled_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / "alias.cow"
            link.symlink_to(ROOT / "cows" / "default.cow")
            r = run(["-f", str(link), "-W", "10"], "z", env={"COWPATH": tmp})
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn(b"(oo)", r.stdout)

    def test_set_and_show_active_cow(self) -> None:
        active = ROOT / ".active-cow"
        backup = active.read_text(encoding="utf-8") if active.is_file() else None
        try:
            if active.is_file():
                active.unlink()
            r = run(["--show-cow"], use_active_cow=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(r.stdout.decode().strip(), "default")
            r2 = run(["--set-cow", "tux"], use_active_cow=True)
            self.assertEqual(r2.returncode, 0, r2.stderr)
            self.assertEqual(r2.stdout.decode().strip(), "tux")
            self.assertEqual(active.read_text(encoding="utf-8").strip(), "tux")
            r3 = run(["--show-cow"], use_active_cow=True)
            self.assertEqual(r3.stdout.decode().strip(), "tux")
            # no -f → uses active art (tux has o_o)
            r4 = run(["-W", "20"], "hi", use_active_cow=True)
            self.assertEqual(r4.returncode, 0, r4.stderr)
            self.assertIn(b"o_o", r4.stdout)
            r5 = run(["--set-cow", "nope"], use_active_cow=True)
            self.assertEqual(r5.returncode, 2)
        finally:
            if backup is None:
                if active.is_file():
                    active.unlink()
            else:
                active.write_text(backup, encoding="utf-8")

    def test_cowsay_cow_env_beats_active_file(self) -> None:
        active = ROOT / ".active-cow"
        backup = active.read_text(encoding="utf-8") if active.is_file() else None
        try:
            run(["--set-cow", "tux"], use_active_cow=True)
            r = run(["-W", "20"], "x", env={"COWSAY_COW": "moose"})
            self.assertEqual(r.returncode, 0, r.stderr)
            # moose antlers marker
            self.assertIn(b"_/_/", r.stdout)
        finally:
            if backup is None:
                if active.is_file():
                    active.unlink()
            else:
                active.write_text(backup, encoding="utf-8")


if __name__ == "__main__":
    if not BIN.is_file():
        sys.stderr.write(f"missing binary: {BIN}\n")
        raise SystemExit(2)
    raise SystemExit(unittest.main(verbosity=2))
