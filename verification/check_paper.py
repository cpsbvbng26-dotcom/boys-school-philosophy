#!/usr/bin/env python3
"""The paper, its PDF and the numbers written about them.

1. The LaTeX source names Takuya Nemoto as the only author, with the ORCID iD, and has the title in English and
   Japanese. It has the disclosure of the author's position (the school is not named; the experience is not evidence),
   the disclosure of the use of a language model ("Claude Code", "Claude is not an author.") and the licence section
   (CC BY 4.0). The PDF text has the same headings and sentences, and its metadata title is the title.
2. The PDF is the recorded one: its page count, SHA-256 and body word count (paperlib.word_count) are the ones that
   README.md and README.en.md state. CITATION.cff has the title.
3. Prose numbers in the paper. Every number word from two to twenty and every numeral in the body of the LaTeX
   source, outside quotations (which check_sources.py compares with their abstracts), URLs and layout commands, is
   covered by a rule in NUMBER_RULES that recounts it: "three features" must be followed by First, Second and Third in
   its block, and so on. A number with no rule fails. The Japanese abstract has no count words at all.
4. Prose numbers in the READMEs. The number of cited items and of each read mode (literature/sources.json), of
   quotations (the \\srcq in the source), and of break cases (counted by running every check with --break) are the
   ones the READMEs state. Any other "<number> 件 / 通り / 項目 / か所" or "<number> items / cases" in a README fails.

  python3 verification/check_paper.py           # the check
  python3 verification/check_paper.py --break   # each change made in memory must fail
"""
import hashlib
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paperlib import ROOT, TEX, PDF, AUTHOR, ORCID, read, body, srcq, uncomment, word_count  # noqa: E402

TITLE = "The Value of Public Boys' Schools: A Social-Scientific Perspective"
TITLE_JA = "公立男子校の価値：社会科学的観点から"
CHECKS = ["check_paper.py", "check_sources.py", "check_text.py", "check_copies.py"]
WORDS = {w: i for i, w in enumerate("two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty".split(), start=2)}
ORD = ["First", "Second", "Third", "Fourth", "Fifth", "Sixth"]


def prose(tex):
    """The body with quotations, references, URLs and layout removed."""
    b = body(tex)
    b = re.sub(r"\\srcq\{[^{}]*\}\{[^{}]*\}", " QUOTE ", b)
    b = re.sub(r"\\(?:cite[tp]?|ref|label|doi|url|nolinkurl)\{[^{}]*\}", " ", b)
    b = re.sub(r"\\href\{[^{}]*\}", " ", b)
    b = re.sub(r"https?://\S+", " ", b)
    b = re.sub(r"[pm]\{\d+(?:\.\d+)?cm\}", " ", b)
    b = re.sub(r"\\ja\{[^{}]*\}", " ", b)
    return b


def block_after(text, pos):
    ends = [m.start() for m in re.finditer(r"\\(?:sub)?section\*?\{|\\mech\{|\\eqq\{|\\paragraph\{", text) if m.start() > pos]
    return text[pos:min(ends) if ends else len(text)]


def ordinals(block):
    """The largest k such that First..k-th (or The first..the k-th) begin sentences of the block, in order."""
    k = 0
    for i, w in enumerate(ORD):
        if re.search(r"(?:^|[.?:]\s+|\n\s*)(?:" + w + r",|The " + w.lower() + r"\b)", block):
            k = i + 1
        else:
            break
    return k


def ordinal_rule(phrase):
    def f(x, m):
        return ordinals(block_after(x["prose"], m.end()))
    return (re.compile(r"\b" + phrase + r"\b"), f)


NUMBER_RULES = [
    ordinal_rule(r"(?:a school with )?three features"),
    ordinal_rule(r"three questions"),
    ordinal_rule(r"Two commitments"),
    ordinal_rule(r"Three gaps"),
]
DATE_RULE = re.compile(r"\b(\d{1,2}) November (\d{4})\b")
LICENCE_RULE = re.compile(r"CC BY (\d\.\d)")


def number_problems(x):
    bad = []
    p = x["prose"]
    used = []
    for pat, f in NUMBER_RULES:
        for m in pat.finditer(p):
            said = WORDS[re.search(r"two|three|four|five|six", m.group(0), re.I).group(0).lower()]
            got = f(x, m)
            if got != said:
                bad.append(f"'{m.group(0)}': the text that follows enumerates {got}")
            used.append((m.start(), m.end()))
    for m in DATE_RULE.finditer(p):
        if f"{m.group(2)}-11-{int(m.group(1)):02d}" != x["sources"]["retrieved"]:
            bad.append(f"'{m.group(0)}': literature/sources.json records the search on {x['sources']['retrieved']}")
        used.append((m.start(), m.end()))
    for m in LICENCE_RULE.finditer(p):
        if f"Attribution {m.group(1)} International" not in x["licence"]:
            bad.append(f"'{m.group(0)}': LICENSE is not that version")
        used.append((m.start(), m.end()))
    for m in re.finditer(r"\b(?:" + "|".join(WORDS) + r")\b|\d+(?:[.,]\d+)*", p, re.I):
        if not any(a <= m.start() < b for a, b in used):
            bad.append(f"a number with no rule: '{p[max(0, m.start() - 30):m.end() + 30].strip()}'")
    ja = "".join(re.findall(r"\\ja\{([^{}]*)\}", uncomment(x["tex"])))
    for m in re.finditer(r"[二三四五六七八九十百千]+(?:つ|件|項目|通り|人|校)|[0-9０-９]+", ja):
        bad.append(f"a count in the Japanese text: {m.group(0)}")
    return bad


def paper_problems(x):
    bad = []
    t = " ".join(uncomment(x["tex"]).split())
    authors = re.findall(r"\\author\{([^\\}]*)", t)
    if authors != [AUTHOR]:
        bad.append(f"the author line is not exactly {AUTHOR}: {authors}")
    if "https://orcid.org/" + ORCID not in t:
        bad.append("the ORCID iD is missing")
    if "pdftitle={" + TITLE + "}" not in t or TITLE_JA not in t:
        bad.append("the title (English, in the PDF metadata, or Japanese) is missing or changed")
    need = [r"\section{Disclosure of the author's position}", "The school is not named in this paper",
            "The experience is not used as evidence for any claim made here.", "attended it for about half a year, and withdrew",
            r"\section*{Disclosure of the use of a language model}", "Claude Code was used", "Claude is not an author.",
            r"\section*{Licence}", "CC BY 4.0"]
    for s in need:
        if s not in t:
            bad.append(f"the source lacks '{s}'")
    pdf = " ".join(x["pdf_text"].split())
    for s in ["Disclosure of the author's position", "The school is not named in this paper",
              "Disclosure of the use of a language model", "Claude is not an author.", "Licence"]:
        if s.replace("'", "\u2019") not in pdf and s not in pdf:
            bad.append(f"the PDF text lacks '{s}'")
    if x["pdf_title"] != TITLE:
        bad.append(f"the PDF metadata title is {x['pdf_title']!r}")
    if TITLE not in x["citation"]:
        bad.append("CITATION.cff lacks the title")
    return bad


README_RULES = {
    "README.md": {
        "pages": r"PDF は (\d+) 頁です", "sha": r"SHA-256 は `([0-9a-f]{64})` です", "words": r"本文は ([\d,]+) 語です",
        "items": r"引いた文献は (\d+) 件です", "abstract-crossref": r"Crossref の記録の要旨で読んだものが (\d+) 件",
        "abstract-openalex": r"OpenAlex の要旨で読んだものが (\d+) 件", "record": r"記録だけを読んだものが (\d+) 件",
        "quotes": r"要旨からの引用は (\d+) か所です", "breaks": r"壊して確かめる型は、四つの検査で合わせて (\d+) 通りです",
        "loose": r"(\d+) ?(?:件|通り|項目|か所)"},
    "README.en.md": {
        "pages": r"The PDF has (\d+) pages", "sha": r"its SHA-256 is `([0-9a-f]{64})`", "words": r"The body has ([\d,]+) words",
        "items": r"The paper cites (\d+) items", "abstract-crossref": r"(\d+) were read as the abstract in their Crossref record",
        "abstract-openalex": r"(\d+) as the abstract in OpenAlex", "record": r"(\d+) as a record only",
        "quotes": r"(\d+) quotations from abstracts", "breaks": r"(\d+) break cases across the four checks",
        "loose": r"(\d+) (?:items|cases|quotations)"},
}


def readme_problems(x):
    bad = []
    modes = {}
    for it in x["sources"]["items"]:
        modes[it["read"]] = modes.get(it["read"], 0) + 1
    actual = {"pages": x["pages"], "sha": x["sha"], "words": x["words"], "items": len(x["sources"]["items"]),
              "quotes": len(srcq(x["tex"])), "breaks": x["breaks"], **{k: modes.get(k, 0) for k in ("abstract-crossref", "abstract-openalex", "record")}}
    for rel, rules in README_RULES.items():
        t = x["readme"][rel]
        used = []
        for key, pat in rules.items():
            if key == "loose":
                continue
            m = re.search(pat, t)
            if not m:
                bad.append(f"{rel}: no sentence for {key}")
                continue
            got = m.group(1) if key == "sha" else int(m.group(1).replace(",", ""))
            if got != actual[key]:
                bad.append(f"{rel}: states {key} {got}, the actual value is {actual[key]}")
            used.append(m.start(1))
        for m in re.finditer(rules["loose"], t):
            if m.start(1) not in used:
                bad.append(f"{rel}: a count with no rule: '{t[max(0, m.start() - 20):m.end() + 5].strip()}'")
    return bad


def count_breaks():
    n = 0
    for c in CHECKS:
        out = subprocess.run([sys.executable, os.path.join(ROOT, "verification", c), "--break", "--count-only"],
                             capture_output=True, text=True).stdout
        n += sum(1 for line in out.splitlines() if re.match(r"\s+(caught|MISSED|case|passed, as it should|false positive)\b", line))
    return n


def load(with_breaks=True):
    import pypdf
    tex = read(TEX)
    r = pypdf.PdfReader(os.path.join(ROOT, PDF))
    text = "\n".join(p.extract_text() or "" for p in r.pages)
    with open(os.path.join(ROOT, PDF), "rb") as fh:
        sha = hashlib.sha256(fh.read()).hexdigest()
    return {"tex": tex, "prose": prose(tex), "pdf_text": text, "pdf_title": str((r.metadata or {}).get("/Title", "")),
            "pages": len(r.pages), "sha": sha, "words": word_count(text), "citation": read("CITATION.cff"),
            "licence": read("LICENSE"), "sources": json.loads(read("literature/sources.json")),
            "readme": {k: read(k) for k in README_RULES}, "breaks": count_breaks() if with_breaks else None}


def problems(x):
    return paper_problems(x) + number_problems(x) + readme_problems(x)


def breaks(x):
    def tex(a, b):
        assert a in x["tex"], a
        t = x["tex"].replace(a, b, 1)
        return dict(x, tex=t, prose=prose(t))

    def readme(rel, a, b):
        assert a in x["readme"][rel], a
        return dict(x, readme=dict(x["readme"], **{rel: x["readme"][rel].replace(a, b, 1)}))
    return [
        ("Claude added as an author", tex(r"\author{Takuya Nemoto", r"\author{Takuya Nemoto and Claude")),
        ("the disclosure sentence removed", tex("Claude is not an author.", "")),
        ("the disclosure of the author's position removed", tex(r"\section{Disclosure of the author's position}", r"\section{Background}")),
        ("the sentence that the experience is not evidence removed", tex("The experience is not used as evidence for any claim made here. ", "")),
        ("the licence changed", tex("licence CC BY 4.0 (", "licence CC BY-NC 4.0 (")),
        ("the PDF's page count changed", dict(x, pages=x["pages"] + 1)),
        ("the PDF's hash changed", dict(x, sha="0" * 64)),
        ("the PDF's word count changed", dict(x, words=x["words"] + 1)),
        ("the PDF loses the disclosure heading", dict(x, pdf_text=x["pdf_text"].replace("Disclosure of the use of a language model", "Notes"))),
        ("a count word changed", tex("is a school with three features", "is a school with four features")),
        ("an enumeration shortened", tex("Third, it admits boys only.", "It admits boys only.")),
        ("a number with no rule", tex("Some public authorities maintain", "Some 12 public authorities maintain")),
        ("a count word with no rule", tex("Debates about whether such schools", "Two debates about whether such schools")),
        ("the search date changed", tex("read on 23 November 2026", "read on 22 November 2026")),
        ("a count in the Japanese abstract", tex("仕組みを示す。", "五つの仕組みを示す。")),
        ("a README's item count changed", readme("README.md", "引いた文献は 17 件です", "引いた文献は 18 件です")),
        ("a README's page count changed", readme("README.en.md", "The PDF has 16 pages", "The PDF has 15 pages")),
        ("a README's break count changed", dict(x, breaks=(x["breaks"] or 0) + 1)),
        ("a count with no rule in a README", readme("README.md", "## 検査", "## 検査\n\n検査は 5 件あります。")),
    ]


def main(argv):
    if "--break" in argv:
        x = load(with_breaks="--count-only" not in argv)
        if "--count-only" in argv:
            x["breaks"] = 0
            for what, _ in breaks(x):
                print(f"  case: {what}")
            return 0
        if problems(x):
            print("break test: the unbroken state already fails")
            for p in problems(x):
                print("  " + p)
            return 1
        missed = 0
        for what, y in breaks(x):
            caught = bool(problems(y))
            print(f"  {'caught' if caught else 'MISSED'}: {what}")
            missed += not caught
        print("break test: " + ("every change made the check fail, as it should" if not missed else f"{missed} missed"))
        return 1 if missed else 0
    x = load()
    bad = problems(x)
    print(f"paper: {x['pages']} pages, {x['words']} words, sha256 {x['sha']}, {x['breaks']} break cases, {len(bad)} problems")
    for b in bad:
        print("  " + b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
