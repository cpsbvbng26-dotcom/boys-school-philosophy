# boys-school-philosophy

The LaTeX source, the built PDF and the checks of "The Value of Public Boys' Schools: A Social-Scientific Perspective" (公立男子校の価値：社会科学的観点から).

[日本語](README.md)

## The paper

The paper is a preprint prepared for SSRN. It has not been peer-reviewed.
The body is in English, with an abstract in Japanese.
Submission to SSRN is made from the operator's account and cannot be made from this repository.
There is no DOI yet, and none will be written here until one is received.

The PDF is `paper/boys-school-philosophy.pdf`.
The PDF has 16 pages, and its SHA-256 is `308ac06cbbbd8450806333b73eb572b5ea9b47083f0c99ef81a694c7caf03ffc`.
The body has 7,367 words, counted in the text of the PDF from the heading "1 Introduction" to the heading of the disclosure of the use of a language model (`word_count` in `verification/paperlib.py`).

The subject is not added to the self-study series of the first undergraduate year (the three papers in autonomy-and-self-cultivation). It goes out as a new subject, as a preprint on SSRN.
SSRN was chosen as a venue that charges neither authors nor readers. Its current terms were not checked, because SSRN cannot be reached from the environment in which the work was done.

## The Zenodo record settings

`.zenodo.json` holds the settings that Zenodo reads when a GitHub release is published. It was added on 2026-11-25.
Its title, creator, licence and keywords agree with `CITATION.cff`. The paper has no DOI yet, so no related identifier is given.
This repository has no GitHub release and no tag, as checked with the GitHub API on 2026-11-25. The archiving from GitHub to Zenodo has therefore never run.
`verification/check_copies.py` compares `.zenodo.json` with `CITATION.cff` and `LICENSE`.

## What the paper argues

The value of public boys' schools is, on most points, an open empirical question.
There are plausible mechanisms of value, but the studies of effects read here (abstracts only) are mixed, and none concerns the selective public boys' school as an institutional type or concerns Japan.
On access, the equality critique rests on a structural fact, exclusion by sex from a public institution, that no estimate of the school's effect on boys removes. Evidence can measure what the exclusion costs those it excludes.
The paper argues neither for keeping such schools nor for closing them.

It sets out the mechanisms of value (peer composition, selection by examination, the absence of a fee barrier, school culture and identity, networks and status) as hypotheses; breaks the equality critique into questions that evidence can address; reports what the abstracts of the studies read show and do not show; and ends with a research design that could decide between the hypotheses.

## Keywords and suggested classification

Keywords: single-sex schooling; public education; selective admission; peer effects; educational stratification; gender norms; causal inference; research design.

Suggested classification: education (primary); sociology of education and educational stratification; gender studies.
At the level of SSRN's networks, the Education Research Network, together with the networks for sociology and for gender studies, appear to fit.
The current names of SSRN's networks and eJournals were not checked, because SSRN cannot be reached from the environment in which the work was done, and no eJournal is named for that reason.
Following rule 2 of this repository (no organisation names), the paper itself names neither SSRN nor any network.

## Rules

The rules of this repository are in [CLAUDE.md](CLAUDE.md) (in Japanese).
Two were set by the user on 2026-11-23: to write from a social-science perspective ("公立男子校は社会科学的観点からでお願い"), and to name no organisation in the paper except those the author founded ("自分が創設したもの以外つまり団体名は一切かかないでね").
The paper's references therefore give only authors, year, title and DOI, and the disclosure of the use of a language model names the tool, Claude Code, without its vendor.

## Literature, and how it was read

The literature was searched and read on 2026-11-23.
The paper cites 17 items. Every bibliographic record was checked with the Crossref API.
Of the items, 12 were read as the abstract in their Crossref record, 4 as the abstract in OpenAlex, and 1 as a record only. No full text was read.
The paper has 37 quotations from abstracts, and `verification/check_sources.py` compares each with the stored abstract.
The stored records are in `literature/`; `literature/sources.json` gives each item's read mode and use.

Records of Japanese-language studies were found in OpenAlex. None could be read as an abstract or in full, and none had a Crossref record, so none is cited. The paper makes no empirical claim about Japan.

## Disclosure of the author's position

The author was admitted to a public boys' high school, attended it for about half a year, and withdrew.
The paper says so in the section "Disclosure of the author's position". It is a statement of position and possible conflict of interest, not evidence for the argument.
The school is not named in the paper or in this repository, and no sentence describes or evaluates any real school.

## Contents

| Path | Contents |
| --- | --- |
| `paper/boys-school-philosophy.tex` | the LaTeX source |
| `paper/boys-school-philosophy.pdf` | the built PDF |
| `paper/ja.lua` | a small function that breaks Japanese lines without a Japanese TeX package |
| `build.sh` | the build script |
| `literature/` | the records and abstracts of the cited items, and how each was read |
| `verification/` | the checks |
| `CLAUDE.md` | the rules of this repository |

## Building

```
./build.sh
```

The script typesets the paper three times with LuaLaTeX. The dates in the PDF are fixed to the date of the paper (2026-11-23) by `SOURCE_DATE_EPOCH`, and the PDF's ID is fixed in the source, so the same TeX and fonts give the same bytes.
The PDF was built with LuaHBTeX 1.17.0 (TeX Live 2023, Debian packages) and the font of the Debian package fonts-ipafont-gothic. Two builds in that environment gave the same SHA-256.
CI does not rebuild the PDF; it checks the recorded SHA-256 and page count.

## Checks

```
python3 -m pip install -r requirements.txt
python3 verification/check_paper.py      # author, disclosures, title, the PDF's pages, SHA-256 and words, prose numbers, README numbers
python3 verification/check_sources.py    # records, read modes, quotations against abstracts (--online: compare with Crossref again)
python3 verification/check_text.py       # words not to use, living persons, school names, links to creative works, organisation names in the paper
python3 verification/check_copies.py     # canonical copies, licences and .zenodo.json
node .github/checked-intake/verify.js --check
```

With `--break`, each check builds broken variants one by one and confirms that each fails.
There are 65 break cases across the four checks; `check_paper.py` recounts them by running every check with `--break`.

## Use of a language model

Claude Code (Anthropic) was used: to search the bibliographic records and read the abstracts, to draft the text, to write the checks, and to reread the draft for one-sidedness, overclaiming and unverified statements of fact.
The author is responsible for the content. Claude is not an author.

## Error reports and personal information

Errors are received through the issue form "Error report". From 2026-12-01, such issues are checked by the checked intake, whose tool and workflow (`.github/checked-intake/verify.js`, `.github/workflows/checked-intake.yml`) are word-for-word copies of those in the operator's other repositories.
How personal information received in issues is handled, and how to ask for its disclosure, correction, suspension of use or deletion, is set out in the section "Information" of the operator's [disclaimer](https://github.com/cpsbvbng26-dotcom/cpsbvbng26-dotcom/blob/main/DISCLAIMER.en.md). How the title and text of an issue are given to a language model is set out in the section "Issues and the language model" of the same page.

`SECURITY.md` is also a word-for-word copy. The "disclaimer" in it is the page above, and its "checked on 2026-11-12" is the date checked in the repository it was copied from. This repository was created on 2026-11-23. That GitHub's private vulnerability reporting is not enabled for this repository either was checked with the GitHub API on 2026-11-23.

## Licence

The paper and the prose are under CC BY 4.0 (`LICENSE`); the scripts and checks are under MIT (`LICENSE-CODE`).
Sentences from the abstracts of other authors' works quoted in the paper are licensed under neither and belong to their rights holders.
