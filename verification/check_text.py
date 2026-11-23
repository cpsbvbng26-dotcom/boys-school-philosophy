#!/usr/bin/env python3
"""Text checks over every text file in the repository and over the text of the PDF.

1. Words not to use (the owner's rules 6 and 10, and the golden-window-resolution list): self-assigned titles, the
   excluded titles and activities, and the name of a particular university as an affiliation. The terms are assembled
   from code points, so that this file does not itself contain them.
2. No living person beyond the cited authors (rule 10). (a) No word for a single relative of the author, in English or
   Japanese. (b) No name of the school the author attended or of the other schools named in the author's own account,
   and no named high school at all: no "<name> High School" and no Japanese school name ending in a word for a high
   school, except the generic forms in GENERIC_SCHOOL. (c) A closed vocabulary for the paper: every capitalised word in
   the body of the LaTeX source is in CAPITALISED or is the family name of an author in a stored Crossref record. A new
   name therefore fails until it is reviewed and added.
3. No link to the creative works (Nusquama, quiet-wizard): the research series is never linked to them. Every URL in a
   text file has an allowed host and path (URL_ALLOWED).
4. No organisation names in the paper (the user's rule of 2026-11-23, "自分が創設したもの以外つまり団体名は一切かかないでね"):
   the LaTeX source and the PDF text contain none of the names in ORGANISATIONS, none of the publishers of the stored
   Crossref records, and no capitalised word followed by an organisational suffix. URLs and DOIs are removed first,
   since they identify sources. The author's own projects in OWN are allowed.

  python3 verification/check_text.py           # the check
  python3 verification/check_text.py --break   # each change made in memory must fail
"""
import glob
import json
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paperlib import ROOT, TEX, read, body  # noqa: E402


def u(*cps):
    return "".join(chr(c) for c in cps)


SKIP_DIRS = {".git", "__pycache__"}
TEXT_EXT = {".md", ".tex", ".py", ".yml", ".yaml", ".cff", ".txt", ".json", ".js", ".lua", ".sh", ""}

Z = "z" + "en"
DAI = u(0x5927, 0x5b66)
WORDS = [
    (re.compile(Z + r"[\s\-_." + u(0x30fb) + "]*(" + DAI + "|univ)"), "affiliation (a university name)"),
    (re.compile(u(0x30bc, 0x30f3) + r"[\s" + u(0x30fb) + "]*" + DAI), "affiliation (a university name, katakana)"),
    (re.compile(u(0x72ec, 0x7acb, 0x7814, 0x7a76, 0x8005)), "self-assigned title"),
    (re.compile("independent" + r"\s+" + "researcher"), "self-assigned title"),
    (re.compile("consult" + "ant|" + u(0x30b3, 0x30f3, 0x30b5, 0x30eb, 0x30bf, 0x30f3, 0x30c8)), "excluded title (rule 10)"),
    (re.compile("(" + u(0x30e9, 0x30a4, 0x30d6, 0x914d, 0x4fe1) + "|live)" + r"[\s-]*" + "stream"), "excluded activity (rule 10)"),
    (re.compile("sea" + "land|" + u(0x30b7, 0x30fc, 0x30e9, 0x30f3, 0x30c9)), "excluded title (rule 10, the principality)"),
]

PARTICLE = "(?:" + "|".join(u(c) for c in (0x304c, 0x306e, 0x306f, 0x3092, 0x3082, 0x306b, 0x3068, 0x3078)) + ")"
KIN = [
    re.compile(r"\b(?:my|the author['\u2019]s|his) (?:father|mother|grandfather|grandmother|brother|sister|uncle|aunt|spouse|wife|husband)\b", re.I),
    re.compile(r"\bthe author['\u2019]s parents\b", re.I),
    re.compile("(?<![" + u(0x7956, 0x66fe, 0x66fd, 0x4f2f, 0x53d4, 0x7fa9, 0x5206) + "])(?:" + u(0x7236) + "|" + u(0x6bcd) + ")" + PARTICLE
               + "|" + u(0x7236, 0x89aa) + "|" + u(0x6bcd, 0x89aa)),
    re.compile(u(0x5148, 0x751f) + "|" + u(0x6559, 0x8aed) + "|" + u(0x540c, 0x7d1a, 0x751f) + "|" + u(0x6821, 0x9577) + "|" + u(0x62c5, 0x4efb)),
]
SCHOOL_NAMES = [u(0x6803, 0x6728), u(0x6803, 0x9ad8), u(0x4f5c, 0x65b0), u(0x5b87, 0x77ed, 0x9644), u(0x5b87, 0x90fd, 0x5bae),
                u(0x99ff, 0x53f0), "to" + "chigi", "utsu" + "nomiya", "sun" + "dai", "saku" + "shin"]
HIGH = "(?:" + u(0x9ad8, 0x7b49, 0x5b66, 0x6821) + "|" + u(0x9ad8, 0x6821) + "|" + u(0x4e2d, 0x5b66, 0x6821) + ")"
GENERIC_SCHOOL = {u(0x7537, 0x5b50), u(0x5973, 0x5b50), u(0x516c, 0x7acb), u(0x79c1, 0x7acb), u(0x5225, 0x5b66), u(0x5171, 0x5b66),
                  u(0x516c, 0x7acb, 0x306e, 0x7537, 0x5b50)}
NAMED_SCHOOL = re.compile(r"\b[A-Z][a-z]+(?: [A-Z][a-z]+)* (?:High School|Boys['\u2019] (?:High )?School|Grammar School|Senior High)\b")
JA_SCHOOL = re.compile(r"([\u30a0-\u30ff\u4e00-\u9fff]{1,8})" + HIGH)

PLAY = re.compile(r"nusquama|quiet[\s_-]*wizard|qw-draft", re.I)
URL = re.compile(r"https?://[^\s)\"'<>\]}`,]+")
URL_ALLOWED = [r"https://doi\.org/", r"https?://dx\.doi\.org/", r"https://orcid\.org/(?:0009-0000-1406-0547)?$",
               r"https://creativecommons\.org/licenses/(?:by/4\.0/)?$", r"https://api\.crossref\.org/works",
               r"https://api\.openalex\.org/works", r"https://openalex\.org/W\d+",
               r"https://github\.com/cpsbvbng26-dotcom/(?:boys-school-philosophy|cpsbvbng26-dotcom|golden-window-resolution)\b",
               r"https://api\.github\.com/repos/$", r"https://github\.com$", r"https://claude\.(?:ai|com)/"]

ORGANISATIONS = [
    "Crossref", "DataCite", "OpenAlex", "SSRN", "arXiv", "PhilPapers", "PhilArchive", "Zenodo", "Figshare", "GitHub", "ORCID",
    "Anthropic", "OpenAI", "Google", "Microsoft", "Vercel", "Elsevier", "JSTOR", "Springer", "Routledge", "Wiley", "SAGE",
    "Informa", "Taylor & Francis", "De Gruyter", "Creative Commons", "Personal Information Protection Commission",
    "Supreme Court", "Board of Education", "OECD", "PISA", "UNESCO", "World Bank", "RIETI", "MEXT", "AERA", "AAAS", "APA",
    "MIT", "IPA", "HAL", "researchmap", "J-STAGE", "CiNii", "NII", "Wikidata", "OSF", "Harvard", "Yale", "Princeton",
    "Oxford", "Cambridge", "Duke", "Stanford",
    u(0x6587, 0x90e8, 0x79d1, 0x5b66, 0x7701), u(0x6559, 0x80b2, 0x59d4, 0x54e1, 0x4f1a), u(0x7d4c, 0x6e08, 0x7523, 0x696d, 0x7814, 0x7a76, 0x6240),
    DAI,
]
SUFFIX = re.compile(r"\b[A-Z][A-Za-z&.-]*(?: [A-Z][A-Za-z&.-]*)* (?:University|Institute|Association|Society|Press|Foundation|Council|Ministry|Agency|Commission|Corporation|Inc\.?|Ltd\.?|LLC|Bureau)\b"
                    r"|\bUniversity of [A-Z]")
OWN = ["Sophaxis"]
# Byte-for-byte copies of the canonical files in cpsbvbng26-dotcom (check_copies.py). Their URLs are the canonical
# file's; every other check still applies to them.
COPIES = {"SECURITY.md", ".github/ISSUE_TEMPLATE/error-report.yml", ".github/workflows/empty-issue.yml",
          ".github/checked-intake/verify.js", ".github/workflows/checked-intake.yml"}

CAPITALISED = set("""A Absence Abstracts Access Achievement Admission An Another Any Attitudes BY Bibliographic But CC Changing
Claims Claude Code Comparing Competing Conclusion Conversions Critics DOI Debates Defenders Designs Disclosure Distribution
Each England English Estimating Ethics Even Every Evidence External Family Fifth First For Fourth Gendered Graduates Here
Heterogeneity How If In Inertia Institutional Introduction It Item Its Japan Japanese Keywords Labour Legal Licence Limitations
Literature Many Measurement Mechanism Mechanisms Most Much Networks No None November Objections Of On One Only Other Outcomes
Peer Persistence Pre Prediction Public Pupils Question Quotations Random Read Real Reproduction School Searches Second Section
Sections Selection Separate Several Social Some Sorting Spillovers States Stating Status Studies Studying Subject Such Suggested
Table Terms That The Their There These They Third This Those Three Two United Used Value Variation Wellbeing What When Where
Whether Why Within Yet""".split())


def norm(text):
    return unicodedata.normalize("NFKC", text)


def files():
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for fn in fns:
            yield os.path.join(dp, fn)


def strip_ids(text):
    """Removes URLs, DOIs and LaTeX link commands, which identify sources and are not names in prose."""
    t = re.sub(r"\\(?:url|doi|nolinkurl)\{[^{}]*\}|\\href\{[^{}]*\}", " ", text)
    t = URL.sub(" ", t)
    return re.sub(r"\b(?:doi:)?10\.\d{4,9}/\S+", " ", t)


def scan(name, text, paper=False, families=(), publishers=(), urls=True):
    hits = []
    t = norm(text)
    low = t.casefold()

    def at(pos):
        return t.count("\n", 0, pos) + 1
    for pat, what in WORDS:
        hits += [f"{name}:{at(m.start())}: {what}" for m in pat.finditer(low)]
    for pat in KIN:
        hits += [f"{name}:{at(m.start())}: a word for a single relative or a person of the author's school ({m.group(0)})" for m in pat.finditer(t)]
    for s in SCHOOL_NAMES:
        for m in re.finditer(re.escape(s.casefold()), low):
            hits.append(f"{name}:{at(m.start())}: the name of a school or its place")
    hits += [f"{name}:{at(m.start())}: a named school ({m.group(0)})" for m in NAMED_SCHOOL.finditer(t)]
    for m in JA_SCHOOL.finditer(t):
        if m.group(1) not in GENERIC_SCHOOL:
            hits.append(f"{name}:{at(m.start())}: a named school ({m.group(0)})")
    hits += [f"{name}:{at(m.start())}: a link to or name of a creative work ({m.group(0)})" for m in PLAY.finditer(t)]
    for m in (URL.finditer(t) if urls else []):
        if not any(re.match(a, m.group(0)) for a in URL_ALLOWED):
            hits.append(f"{name}:{at(m.start())}: a URL outside the allowed list ({m.group(0)})")
    if paper:
        s = strip_ids(t)
        for o in ORGANISATIONS + list(publishers):
            if o in OWN:
                continue
            flags = 0 if (o.isupper() or len(o) <= 4) else re.I
            for m in re.finditer(r"(?<![A-Za-z])" + re.escape(o) + r"(?![A-Za-z])", s, flags):
                hits.append(f"{name}:{at(m.start())}: an organisation name ({m.group(0)})")
        hits += [f"{name}: an organisation name ({m.group(0)})" for m in SUFFIX.finditer(s) if m.group(0) not in OWN]
    return hits


def vocabulary(tex, families):
    b = body(tex)
    b = re.sub(r"\\(?:cite[tp]?|ref|label|doi|url)\{[^{}]*\}", " ", b)
    b = re.sub(r"\\srcq\{[^{}]*\}\{[^{}]*\}", " ", b)  # quotations are checked against their sources
    b = re.sub(r"\\[a-zA-Z]+\*?", " ", b)
    return sorted({w for w in re.findall(r"\b([A-Z][A-Za-z]*)", b) if w not in CAPITALISED and w not in families})


def context():
    fams, pubs = set(), set()
    for p in glob.glob(os.path.join(ROOT, "literature", "crossref", "*.json")):
        r = json.load(open(p, encoding="utf-8"))
        for a in r.get("author", []) + r.get("editor", []):
            for part in re.findall(r"[A-Z][A-Za-z]+", a.get("family", "") or ""):
                fams.add(part)
        if r.get("publisher"):
            pubs.add(r["publisher"])
            pubs.update(re.findall(r"\(([A-Z]{2,})\)", r["publisher"]))
            pubs.add(re.sub(r"\s*\([^)]*\)", "", r["publisher"]).strip())
    return fams, pubs


def pdf_text():
    import pypdf
    r = pypdf.PdfReader(os.path.join(ROOT, "paper", "boys-school-philosophy.pdf"))
    meta = " ".join(str(v) for v in (r.metadata or {}).values())
    return meta + "\n" + "\n".join(p.extract_text() or "" for p in r.pages)


def run():
    fams, pubs = context()
    hits, n = [], 0
    for path in files():
        rel = os.path.relpath(path, ROOT)
        if rel.startswith("literature" + os.sep):
            continue  # stored records of other works: their words are not this repository's prose
        if rel == os.path.join("verification", "check_text.py"):
            continue
        ext = os.path.splitext(path)[1].lower()
        if ext == ".pdf":
            hits += scan(rel, pdf_text(), paper=True, families=fams, publishers=pubs)
            n += 1
        elif ext in TEXT_EXT:
            try:
                t = open(path, encoding="utf-8").read()
            except UnicodeDecodeError:
                continue
            hits += scan(rel, t, paper=(rel == TEX), families=fams, publishers=pubs, urls=rel.replace(os.sep, "/") not in COPIES)
    for w in vocabulary(read(TEX), fams):
        hits.append(f"{TEX}: a capitalised word outside the closed vocabulary ({w}); a name must be reviewed")
    return hits, n


def break_test():
    fams, pubs = context()
    tex = read(TEX)
    clean = "The school is not named. Public boys' schools, coeducational schools, and the parents of pupils.\n"
    bad = 0
    if scan("clean", clean, paper=True, families=fams, publishers=pubs) or vocabulary(tex, fams):
        print("break test: the unbroken state already fails")
        return 1
    cases = [
        ("a self-assigned title", "Takuya Nemoto, " + "Independent " + "Researcher", False),
        ("a self-assigned title in Japanese", u(0x72ec, 0x7acb, 0x7814, 0x7a76, 0x8005), False),
        ("an affiliation", "Takuya Nemoto, " + Z.upper() + " " + "University", False),
        ("an excluded title", "a " + "consult" + "ant", False),
        ("a relative of the author", "The author's " + "father attended such a school.", False),
        ("a relative of the author in Japanese", u(0x7236) + u(0x304c) + u(0x5352, 0x696d, 0x3057, 0x305f), False),
        ("a teacher in Japanese", u(0x62c5, 0x4efb, 0x306e, 0x5148, 0x751f), False),
        ("the name of the school's place", "a school in " + "To" + "chigi", False),
        ("the school's short name in Japanese", u(0x6803, 0x9ad8), False),
        ("a named Japanese high school", u(0x6771, 0x4eac) + u(0x9ad8, 0x6821), False),
        ("a named high school in English", "Springfield " + "High School", False),
        ("a link to a creative work", "https://" + "nusquama" + ".example/", False),
        ("a URL outside the list", "https://example.com/page", False),
        ("an organisation in the paper", "This paper was prepared for " + "SS" + "RN.", True),
        ("the vendor of the tool in the paper", "Claude Code (" + "Anthro" + "pic) was used.", True),
        ("a publisher of a source in the paper", "Published by " + sorted(pubs)[0] + ".", True),
        ("an organisation by its suffix", "A survey by the Example " + "Institute.", True),
        ("a ministry in Japanese", u(0x6587, 0x90e8, 0x79d1, 0x5b66, 0x7701) + u(0x306e, 0x8abf, 0x67fb), True),
    ]
    for what, text, paper in cases:
        caught = bool(scan("injected", text + "\n", paper=paper, families=fams, publishers=pubs))
        print(f"  {'caught' if caught else 'MISSED'}: {what}")
        bad += not caught
    anchor = "A critic may say that the schools exclude"
    assert anchor in tex, anchor
    caught = bool(vocabulary(tex.replace(anchor, "Tanaka may say that the schools exclude", 1), fams))
    print(f"  {'caught' if caught else 'MISSED'}: a new name in the paper's prose")
    bad += not caught
    caught = bool(scan("injected", "https://orcid.org/0009-0000-1406-0547 Sophaxis\n", paper=True, families=fams, publishers=pubs))
    print(f"  {'false positive' if caught else 'passed, as it should'}: the author's ORCID URL and an own project")
    bad += caught
    print("break test: " + ("every change made the check fail, as it should" if not bad else f"{bad} problems"))
    return 1 if bad else 0



def main(argv):
    if "--break" in argv:
        return break_test()
    hits, n = run()
    print(f"text check: {n} PDF and all text files scanned, {len(hits)} problems")
    for h in hits:
        print("  " + h)
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
