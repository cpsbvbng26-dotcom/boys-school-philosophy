#!/usr/bin/env python3
"""Copies that must stay byte-for-byte the same as their canonical files, and the licences.

1. SECURITY.md, .github/ISSUE_TEMPLATE/error-report.yml, .github/workflows/empty-issue.yml,
   .github/checked-intake/verify.js and .github/workflows/checked-intake.yml are copies of the canonical files in
   cpsbvbng26-dotcom, made on 2026-11-23. Their SHA-256 at the time of copying is recorded here. When the canonical
   files change, the copies and these hashes change together; the cross-repository comparison is made from
   cpsbvbng26-dotcom. The error report form promises the checked intake from 2026-12-01, so the intake's tool and
   workflow are here too. Its .github/checked-intake/config.json is this repository's own; `verify.js --check` reads it.
2. LICENSE is the CC BY 4.0 legal code (the same bytes as in golden-window-resolution); LICENSE-CODE is the MIT
   licence in the author's name.
3. When cpsbvbng26-dotcom is a sibling directory, the copies are also compared with it directly.
4. .zenodo.json (2026-11-25), which Zenodo's GitHub integration reads at a release: its title begins with the title in
   CITATION.cff, its upload type is that of the CITATION.cff type, its one creator is Takuya Nemoto with the ORCID iD and
   no affiliation, its licence is that of LICENSE, its keywords are those of CITATION.cff in the same order, its notes
   carry the disclosure ("Claude is not an author.") and say what the licence field covers, and it holds no DOI: the
   paper has none yet (CLAUDE.md, rule 3), so none is written.

  python3 verification/check_copies.py           # the check
  python3 verification/check_copies.py --break   # each change made in memory must fail
"""
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COPIES = {
    "SECURITY.md": "973a9630e16e0e5f91efa9ebb870ed3bfb51cd4a2e53693c94e68e321187785d",
    ".github/ISSUE_TEMPLATE/error-report.yml": "804c65aaf92d2032cd63d9bd36cc5bd4cbaf7edf97de74faf8bdb76f03a04c96",
    ".github/workflows/empty-issue.yml": "8a5ce275946c4e9258d2775be2cccd0ee39d8c54bf16baf97885a1aef4d3b072",
    ".github/checked-intake/verify.js": "640a886749427c3a92ddde825ad93b9f616541b14c47ca1f49a3adcf3cb1ab8c",
    ".github/workflows/checked-intake.yml": "66a93337e8a56c3ab35a4045764fe54350b165ba97c0139ce5d9ed6b9f669a5d",
    "LICENSE": "d557539df68e771cc1eedcc91d13f70fca930e508d11eedcafa4b15db49e3744",
}
LICENCE_CODE_LINES = ["MIT License", "Copyright (c) 2026 Takuya Nemoto"]
CANON = os.path.join(os.path.dirname(ROOT), "cpsbvbng26-dotcom")


def sha(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def text(rel):
    p = os.path.join(ROOT, rel)
    return open(p, encoding="utf-8").read() if os.path.exists(p) else None


def zenodo_problems(ztext, cff, licence):
    if ztext is None:
        return [".zenodo.json: missing"]
    try:
        z = json.loads(ztext)
    except ValueError:
        return [".zenodo.json: cannot be read"]
    cff = cff or ""
    errs = []
    title = re.search(r'^title:\s*"([^"]+)"', cff, re.M)
    if not title or not z.get("title", "").startswith(title.group(1) + ":"):
        errs.append(".zenodo.json: the title does not begin with the title in CITATION.cff")
    kind = re.search(r"^type:\s*(\S+)", cff, re.M)
    if not kind or z.get("upload_type") != {"software": "software", "dataset": "dataset"}.get(kind.group(1)):
        errs.append(".zenodo.json: the upload type is not that of the CITATION.cff type")
    if z.get("creators") != [{"name": "Nemoto, Takuya", "orcid": "0009-0000-1406-0547"}]:
        errs.append(".zenodo.json: the creator (one, with the ORCID iD, no affiliation)")
    if z.get("license") != ("cc-by-4.0" if (licence or "").startswith("Creative Commons Attribution 4.0") else "?"):
        errs.append(".zenodo.json: the licence is not that of LICENSE")
    block = cff.split("\nkeywords:\n", 1)[1] if "\nkeywords:\n" in cff else ""
    words = re.findall(r"^  - (.+)$", block.split("\n\S", 1)[0] if block else "", re.M)
    if not words or z.get("keywords") != words:
        errs.append(".zenodo.json: the keywords are not those of CITATION.cff in the same order")
    notes = z.get("notes", "")
    if "Claude is not an author." not in notes or not re.search(r"The licence field of this record covers .+? only\.", notes):
        errs.append(".zenodo.json: the notes lack the disclosure or the sentence on the licence field")
    if re.search(r"\b10\.\d{4,9}/", ztext) or "related_identifiers" in z:
        errs.append(".zenodo.json: a DOI or a related identifier, though the paper has no DOI yet")
    return errs


def state():
    return {"hashes": {rel: sha(os.path.join(ROOT, rel)) for rel in COPIES},
            "zenodo": text(".zenodo.json"), "cff": text("CITATION.cff"), "licence": text("LICENSE"),
            "canon": {rel: sha(os.path.join(CANON, rel)) for rel in COPIES if rel != "LICENSE"} if os.path.isdir(CANON) else {},
            "code": open(os.path.join(ROOT, "LICENSE-CODE"), encoding="utf-8").read() if os.path.exists(os.path.join(ROOT, "LICENSE-CODE")) else ""}


def problems(s):
    bad = []
    for rel, want in COPIES.items():
        got = s["hashes"].get(rel)
        if got is None:
            bad.append(f"{rel}: missing")
        elif got != want:
            bad.append(f"{rel}: sha256 {got} is not the recorded {want}")
        c = s["canon"].get(rel)
        if c is not None and got is not None and c != got:
            bad.append(f"{rel}: differs from the canonical file in the sibling cpsbvbng26-dotcom (that file changed; copy it and update the hash)")
    lines = [line.strip() for line in s["code"].splitlines() if line.strip()]
    if lines[:2] != LICENCE_CODE_LINES:
        bad.append("LICENSE-CODE: not the MIT licence in the author's name")
    bad += zenodo_problems(s["zenodo"], s["cff"], s["licence"])
    return bad


def main(argv):
    s = state()
    if "--break" in argv:
        if problems(s):
            print("break test: the unbroken state already fails")
            return 1
        cases = [
            ("a copy changed by one byte", dict(s, hashes=dict(s["hashes"], **{"SECURITY.md": "0" * 64}))),
            ("the intake's workflow missing", dict(s, hashes=dict(s["hashes"], **{".github/workflows/checked-intake.yml": None}))),
            ("the licence of the text changed", dict(s, hashes=dict(s["hashes"], LICENSE="1" * 64))),
            ("the licence of the code changed", dict(s, code=s["code"].replace("MIT License", "Apache License", 1))),
            (".zenodo.json missing", dict(s, zenodo=None)),
            ("the disclosure in .zenodo.json", dict(s, zenodo=s["zenodo"].replace("Claude is not an author.", "Claude helped."))),
            ("an affiliation in .zenodo.json", dict(s, zenodo=s["zenodo"].replace('"orcid": "0009-0000-1406-0547"', '"orcid": "0009-0000-1406-0547", "affiliation": "x"'))),
            ("the licence in .zenodo.json", dict(s, zenodo=s["zenodo"].replace('"license": "cc-by-4.0"', '"license": "mit"'))),
            ("the title in .zenodo.json", dict(s, zenodo=s["zenodo"].replace('"title": "The Value of Public', '"title": "On the Value of Public'))),
            ("the upload type in .zenodo.json", dict(s, zenodo=s["zenodo"].replace('"upload_type": "software"', '"upload_type": "publication"'))),
            ("a keyword of .zenodo.json dropped", dict(s, zenodo=s["zenodo"].replace('"peer effects",\n', ''))),
            ("the sentence on the licence field in .zenodo.json", dict(s, zenodo=s["zenodo"].replace("The licence field of this record covers", "The licence field of this record applies to"))),
            ("a guessed DOI in .zenodo.json", dict(s, zenodo=s["zenodo"].replace('"access_right": "open",', '"access_right": "open",\n  "doi": "10.2139/ssrn.0000000",'))),
        ]
        missed = 0
        for what, y in cases:
            caught = bool(problems(y))
            print(f"  {'caught' if caught else 'MISSED'}: {what}")
            missed += not caught
        print("break test: " + ("every change made the check fail, as it should" if not missed else f"{missed} missed"))
        return 1 if missed else 0
    bad = problems(s)
    print(f"copies and licences: {len(COPIES)} files, {'compared with the sibling cpsbvbng26-dotcom' if s['canon'] else 'no sibling cpsbvbng26-dotcom'}, {len(bad)} problems")
    for b in bad:
        print("  " + b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
