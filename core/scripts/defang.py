#!/usr/bin/env python3
"""Defang fetched text so it is safe to write into repo artifacts and render.

Fetched content is untrusted data (trust boundary: extract, never obey).
Before any fetched string lands in a ledger, report, matrix, or manifest,
this module neutralizes the constructs that could fire at render time —
markdown images (network beacons), links, raw HTML, bare URLs — by wrapping
them in inert code spans and defusing URL schemes (http -> hxxp). Control
and invisible characters (bidi overrides, zero-width) are stripped first so
they cannot smuggle or split live markup.

Pure function, stdlib only, no I/O. Imported by the mining pass, the adapter
generator, and both watcher skills; never re-implemented.

Guarantees (each asserted in the self-test):
- No live markdown image/link, HTML tag, or scheme-bearing URL survives
  outside a code region.
- Benign fenced code blocks are left byte-identical (a renderer already
  shows them inert).
- Idempotent: defang(defang(x)) == defang(x).
- Fail-safe segmentation: anything a renderer might treat as live text is
  treated as text here (unclosed fences and unclosed backtick runs are
  neutralized, not skipped; inline code spans never cross blank lines,
  matching CommonMark). Backtick runs that failed to form a span are
  rendered literally by markdown anyway, so they are replaced with
  apostrophes to keep the output stable under re-processing.

Usage:
    from defang import defang
    safe = defang(fetched_text)

Self-test (no pytest needed; core/scripts/tests/ does not exist until U4):
    python3 core/scripts/defang.py

Doctest examples:

>>> defang("see ![](http://attacker/pixel?x=1) here")
'see `![](hxxp://attacker/pixel?x=1)` here'
>>> defang("a [link](http://x) b")
'a `[link](hxxp://x)` b'
>>> defang("bad\\x07bell and \\u202eevil")
'badbell and evil'
>>> defang("`code stays`")
'`code stays`'
"""
import re

# --- character hygiene -------------------------------------------------------
# C0 controls except \t and \n, DEL, C1 controls.
_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f\x80-\x9f]")
# Zero-width, bidi-override, and word-joiner characters used for spoofing or
# for splitting tokens so pattern matches miss them.
_INVISIBLE = re.compile("[​-‏‪-‮⁠-⁤⁦-⁩﻿]")

# --- live-construct patterns (applied only outside code regions) -------------
# Link text / image alt: tolerate one level of bracket nesting so linked
# badges ([![alt](img)](target)) match as a whole.
_BRACKETED = r"\[(?:[^\[\]]|\[[^\]]*\])*\]"
_MD_IMAGE = rf"!{_BRACKETED}\([^)]*\)|!{_BRACKETED}{_BRACKETED}"
_MD_LINK = rf"{_BRACKETED}\([^)]*\)|{_BRACKETED}{_BRACKETED}"
# Reference definition lines: [ref]: http://...
_MD_REFDEF = r"^[ \t]{0,3}\[[^\]]+\]:[ \t]*\S[^\n]*$"
# Anything tag-shaped, including comments, autolinks, and multi-line tags.
_HTML_TAG = r"<[A-Za-z/!?][^>]{0,2000}>"
# Scheme-bearing URLs are the backstop: every live fetch needs a scheme.
# GFM also autolinks scheme-less `www.` hostnames into live links, so those
# are matched too.
_BARE_URL = (
    r"\b(?:https?|ftp)://[^\s<>`]+"
    r"|\b(?:data|javascript|vbscript):[^\s<>`]{1,500}"
    r"|\bwww\.[a-z0-9-]+(?:\.[a-z0-9-]+)+[^\s<>`]*"
)
_DANGEROUS = re.compile(
    "(" + "|".join([_MD_IMAGE, _MD_LINK, _MD_REFDEF, _HTML_TAG, _BARE_URL]) + ")",
    re.MULTILINE | re.DOTALL | re.IGNORECASE,  # IGNORECASE: catch HTTP://, HtTp://
)

_SCHEME = re.compile(r"\b(https|http|ftp|data|javascript|vbscript)(:)", re.IGNORECASE)
_SCHEME_MAP = {
    "https": "hxxps",
    "http": "hxxp",
    "ftp": "fxp",
    "data": "data-defanged",
    "javascript": "js-defanged",
    "vbscript": "vbs-defanged",
}
# Scheme-less GFM autolink hosts (www.) are defused by breaking the leading
# label so no renderer linkifies them.
_WWW = re.compile(r"\bwww(\.)", re.IGNORECASE)

_FENCE_OPEN = re.compile(r"^ {0,3}(`{3,}|~{3,})")
_TICKS = re.compile(r"`+")
_BLANK_LINE = re.compile(r"\n[ \t]*\n")

# Block-level interrupters: a CommonMark paragraph (and therefore any inline
# code span inside it) ends when one of these begins a line. A backtick run
# that "closes" only after crossing such a line is NOT a real span — the
# renderer shows the content live — so we must treat the region as text and
# neutralize it. Being conservative here over-neutralizes at worst (safe
# direction); it never lets live markup through.
_SPAN_BREAKERS = (
    re.compile(r"^ {0,3}#{1,6}(?:\s|$)"),               # ATX heading
    re.compile(r"^ {0,3}([-*_])(?:[ \t]*\1){2,}[ \t]*$"),  # thematic break
    re.compile(r"^ {0,3}>"),                             # blockquote
    # List markers that interrupt a paragraph: any bullet, but an ordered
    # marker only when it starts at 1 (CommonMark) — narrower than before so
    # a genuine `a\n2. b` span isn't needlessly mangled, while still breaking
    # every marker that actually ends a paragraph.
    re.compile(r"^ {0,3}(?:[-+*]|1[.)])(?:\s|$)"),
    re.compile(r"^ {0,3}(?:`{3,}|~{3,})"),              # fenced code open
    re.compile(r"^ {0,3}(?:=+|-+)[ \t]*$"),             # setext underline
    # HTML block start (CommonMark types 1-7): a line beginning with a tag,
    # comment, declaration, or processing instruction interrupts a paragraph,
    # so raw HTML after it renders live. Broad on purpose (safe direction).
    re.compile(r"^ {0,3}<(?:[A-Za-z/!?])"),
    # GFM table: a delimiter row (`|---|:--:|`) or any pipe-bearing row
    # breaks the paragraph, so a backtick region crossing a table is not a
    # code span and its cells (which may hold ![]() beacons) render live.
    re.compile(r"^ {0,3}\|?[ \t]*:?-{1,}:?[ \t]*(?:\|[ \t]*:?-{1,}:?[ \t]*)*\|?[ \t]*$"),
    re.compile(r"^ {0,3}\|.*\|[ \t]*$"),
)


def _crosses_block_interrupter(region: str) -> bool:
    """True if any line after the first in `region` begins a new block —
    which means an enclosing code span cannot survive across it."""
    lines = region.split("\n")
    for line in lines[1:]:
        if any(p.match(line) for p in _SPAN_BREAKERS):
            return True
    return False


def _defuse_schemes(text: str) -> str:
    text = _SCHEME.sub(lambda m: _SCHEME_MAP[m.group(1).lower()] + m.group(2), text)
    return _WWW.sub(r"www[.]", text)


def _neutralize_match(m: re.Match) -> str:
    return "`" + _defuse_schemes(m.group(0)) + "`"


def _neutralize_text(chunk: str) -> str:
    """Neutralize live constructs in a region known to be outside code spans.

    Any backtick run in such a region failed to form a valid span (unclosed,
    or crossing a blank line); markdown renders those literally, so replace
    them with apostrophes. This also guarantees the code-span wrappers added
    below are unambiguous, making the whole function idempotent.
    """
    chunk = chunk.replace("`", "'")
    return _DANGEROUS.sub(_neutralize_match, chunk)


def _split_inline(text: str):
    """Split text into (is_code, chunk) pairs by CommonMark-style code spans.

    A span opens with a backtick run and closes at the next run of the same
    length; it may cross newlines but never a blank line NOR a block-level
    interrupter (heading, blockquote, list marker, thematic break, fenced
    code, setext underline). Once a run cannot be closed, the remainder is
    literal text (fail-safe: it gets neutralized).
    """
    parts, pos = [], 0
    while pos < len(text):
        open_m = _TICKS.search(text, pos)
        if not open_m:
            parts.append((False, text[pos:]))
            break
        run = open_m.group(0)
        close = None
        search_from = open_m.end()
        while True:
            close_m = _TICKS.search(text, search_from)
            if not close_m:
                break
            if len(close_m.group(0)) == len(run):
                close = close_m
                break
            search_from = close_m.end()
        region = text[open_m.start():close.end()] if close else ""
        if close and not _BLANK_LINE.search(text, open_m.start(), close.end()) \
                and not _crosses_block_interrupter(region):
            parts.append((False, text[pos:open_m.start()]))
            parts.append((True, region))
            pos = close.end()
        else:
            parts.append((False, text[pos:]))
            break
    return parts


def defang(text: str) -> str:
    """Return `text` with control chars stripped and live markup neutralized."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _CONTROL.sub("", text)
    text = _INVISIBLE.sub("", text)

    lines = text.split("\n")
    out, buf = [], []

    def flush_text():
        if not buf:
            return
        chunk = "\n".join(buf)
        del buf[:]
        out.append("".join(
            part if is_code else _neutralize_text(part)
            for is_code, part in _split_inline(chunk)
        ))

    def is_closing(line: str, open_run: str) -> bool:
        m = _FENCE_OPEN.match(line)
        return bool(
            m and m.group(1)[0] == open_run[0]
            and len(m.group(1)) >= len(open_run)
            and line.strip() == m.group(1)
        )

    in_fence, fence = False, ""
    for i, line in enumerate(lines):
        if in_fence:
            out.append(line)
            if is_closing(line, fence):
                in_fence = False
            continue
        m = _FENCE_OPEN.match(line)
        # Only trust a fence that actually closes; an unclosed fence may be
        # rendered as text, so it is neutralized instead of skipped.
        if m and any(is_closing(later, m.group(1)) for later in lines[i + 1:]):
            flush_text()
            out.append(line)
            in_fence, fence = True, m.group(1)
        else:
            buf.append(line)
    flush_text()
    return "\n".join(out)


def _selftest() -> None:
    # Beacons, tags, and links render inert; surrounding prose preserved.
    assert defang("see ![](http://attacker/pixel?x=1) here") == \
        "see `![](hxxp://attacker/pixel?x=1)` here"
    assert defang('x <img src="http://evil/p.png"> y') == \
        'x `<img src="hxxp://evil/p.png">` y'
    assert defang("a [link](http://x) b") == "a `[link](hxxp://x)` b"
    # No live scheme or unwrapped construct survives.
    for evil in [
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
    ]:
        d = defang(evil)
        assert "http://" not in d and "https://" not in d and "data:" not in d \
            and "javascript:" not in d, d
    # Control and invisible characters are stripped.
    assert defang("bad\x07bell and ‮evil​") == "badbell and evil"
    # Benign fenced code blocks stay byte-identical and readable.
    block = "before\n```python\nprint('<img> stays literal')\n```\nafter"
    assert defang(block) == block
    # Inline code spans are already inert and left alone.
    assert defang("use `<img>` carefully") == "use `<img>` carefully"
    # Case-insensitive: uppercase/mixed-case bare URL schemes are defused too
    # (host text is preserved inert; only the live scheme is neutralized).
    for u in ("HTTP://EVIL/X", "HtTpS://evil/x", "bare FTP://evil/x"):
        low = defang(u).lower()
        assert "http://" not in low and "https://" not in low \
            and "ftp://" not in low, defang(u)
    # Unclosed fence or backtick run is text, not code: still neutralized.
    assert "hxxp" in defang("```\n<img src=http://evil/unclosed.png>")
    assert "hxxp" in defang("` <img src=http://evil/tick.png>")
    # A backtick "span" crossing a blank line is not a span (CommonMark):
    # renderers would show the content live, so it must be neutralized.
    assert "hxxp" in defang("`a\n\n<img src=http://evil/blank.png> b`")
    # Idempotent on everything above and on mixed documents.
    samples = [
        "see ![](http://attacker/pixel?x=1) here",
        block,
        "a [link](http://x) b `code` <b>bold</b> https://e.example/x",
        "` <img src=http://evil/tick.png>",
        "`a\n\n<img src=http://evil/blank.png> b`",
        "[![badge](https://img.shields.io/x)](https://ci.example)",
        "```\n<img src=http://evil/unclosed.png>",
    ]
    for s in samples:
        once = defang(s)
        assert defang(once) == once, once
    print("defang: all self-tests passed")


if __name__ == "__main__":
    import doctest

    failures, _ = doctest.testmod()
    if failures:
        raise SystemExit(1)
    _selftest()
