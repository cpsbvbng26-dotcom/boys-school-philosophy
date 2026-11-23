# boys-school-philosophy

The Value of Public Boys' Schools: A Social-Scientific Perspective（公立男子校の価値：社会科学的観点から）の LaTeX の原稿・組んだ PDF・検査を置いています。

[English](README.en.md)

## 稿について

SSRN に出すための稿です。査読を経ていません。
本文は英語で、日本語の要旨を付けています。
SSRN への投稿は、運営者のアカウントで行うものです。
このリポジトリからは行えません。
DOI はまだありません。
受け取るまで、番号は書きません。

稿の PDF は `paper/boys-school-philosophy.pdf` です。
PDF は 16 頁です。
SHA-256 は `308ac06cbbbd8450806333b73eb572b5ea9b47083f0c99ef81a694c7caf03ffc` です。
本文は 7,367 語です。
数えたのは、PDF の文字のうち「1 Introduction」の見出しから言語モデルの開示の見出しの手前までです。
数え方は `verification/paperlib.py` の `word_count` にあります。

この主題は、学部一年次の独学の系列（autonomy-and-self-cultivation の三篇）には足していません。
新しい主題として、SSRN にプレプリントとして出すものです。
SSRN は投稿にも閲覧にも費用を取らない場として選びました。
SSRN の今の規程は、作業の環境から SSRN に届かないため、確かめていません。

## 稿の主張

公立男子校の価値は、多くの点で開かれた実証の問いです。
価値を生みうる仕組みはありますが、ここで読んだ効果の研究（要旨だけ）は結果が分かれ、選抜制の公立男子校という型そのものや日本を扱うものはありません。
入学の機会については、平等の観点からの批判は、公の制度が性別で締め出しているという構造上の事実に立っています。
男子への効果をどう見積もっても、その事実は消えません。
証拠にできるのは、締め出される側にとっての代償を測ることです。
稿は、この種の学校を残すべきだとも、廃すべきだとも主張していません。

稿の組み立ては次のとおりです。
価値の仕組み（仲間の構成、入学試験による選抜、学費の壁がないこと、学校の文化と帰属意識、人のつながりと地位）を仮説として立てます。
平等の観点からの批判を、実証で答えられる問いの形に分けます。
読んだ研究の要旨を引いて、何が分かっていて何が分かっていないかを示します。
最後に、どちらの仮説が正しいかを決めるための研究の設計を示します。

## キーワードと分類の目安

キーワード：single-sex schooling; public education; selective admission; peer effects; educational stratification; gender norms; causal inference; research design.

分類の目安：主に教育（education）です。
副に、教育社会学と教育の階層化（sociology of education, educational stratification）を置きます。
ジェンダー研究（gender studies）の読者にも関わります。
SSRN の網（network）の水準では、Education Research Network と、社会学の網と、ジェンダー研究の網が当たると考えています。
SSRN の網と eJournal の今の名前は、作業の環境から SSRN に届かないため、確かめていません。
そのため、eJournal の名前は挙げていません。
紙面には、決めごと 2（団体名を書かない）に従って、SSRN の名前も網の名前も書いていません。

## 決めごと

このリポジトリの決めごとは [CLAUDE.md](CLAUDE.md) にあります。
2026-11-23 に利用者が決めたことが二つあります。
一つは、社会科学の観点から書くことです（「公立男子校は社会科学的観点からでお願い」）。
もう一つは、著者が創設したもののほかは、団体の名前を紙面に一切書かないことです（「自分が創設したもの以外つまり団体名は一切かかないでね」）。
紙面の文献の欄は、著者・年・題・DOI だけを書いています。
言語モデルの開示は、道具の名前「Claude Code」だけを書き、作った会社の名前は書いていません。

## 文献の読み方

文献を探して読んだのは 2026-11-23 です。
引いた文献は 17 件です。
書誌の記録は、すべて Crossref の API で確かめました。
Crossref の記録の要旨で読んだものが 12 件、OpenAlex の要旨で読んだものが 4 件、記録だけを読んだものが 1 件です。
全文を読んだものはありません。
要旨からの引用は 37 か所です。
`verification/check_sources.py` が、引用の一つずつを保存した要旨と照らしています。
保存した記録は `literature/` にあります。
`literature/sources.json` が、文献ごとの読み方と使い道を持っています。

日本語の研究の記録も、OpenAlex で見つかりました。
どれも要旨も全文も読めず、Crossref に記録が無かったので、引いていません。
稿は、日本についての実証の主張をしていません。

## 著者の立場の開示

著者は公立の男子高校に合格して入学し、半年ほどで退学しています。
稿の「Disclosure of the author's position」の節にそう書いています。
これは利益相反と立場の開示であって、論証の根拠ではありません。
学校の名前は、稿にもこのリポジトリにも書いていません。
実在の学校を描いたり評価したりする文はありません。

## 中身

| 場所 | 中身 |
| --- | --- |
| `paper/boys-school-philosophy.tex` | LaTeX の原稿 |
| `paper/boys-school-philosophy.pdf` | 組んだ PDF |
| `paper/ja.lua` | 日本語の行を、日本語の TeX の包みを使わずに折り返すための小さな関数 |
| `build.sh` | PDF を組む台本 |
| `literature/` | 文献の記録と要旨、読み方 |
| `verification/` | 検査 |
| `CLAUDE.md` | このリポジトリの決めごと |

## 組み方

```
./build.sh
```

LuaLaTeX で三回組みます。
PDF の日付は `SOURCE_DATE_EPOCH` で稿の日付（2026-11-23）に固定しています。
PDF の ID も原稿の中で固定しています。
同じ TeX と同じ字体なら、同じバイトの PDF になります。
組んだのは、LuaHBTeX 1.17.0（TeX Live 2023、Debian の包み）と、Debian の包み fonts-ipafont-gothic の字体です。
この環境で二度組み、同じ SHA-256 になることを確かめました。
CI は PDF を組み直さず、記録した SHA-256 と頁数を確かめます。

## 検査

```
python3 -m pip install -r requirements.txt
python3 verification/check_paper.py      # 稿の著者・開示・題・PDF の頁数と SHA-256 と語数・散文の数・README の数
python3 verification/check_sources.py    # 引いた文献の記録・読み方・引用と要旨の照合（--online で Crossref と照らし直す）
python3 verification/check_text.py       # 使わない語・存命の人・学校の名・創作の場へのリンク・紙面の団体名
python3 verification/check_copies.py     # 正本の写しとライセンス
node .github/checked-intake/verify.js --check
```

どの検査も `--break` を付けると、壊した形を一つずつ作って、落ちることを確かめます。
壊して確かめる型は、四つの検査で合わせて 56 通りです。
この数は `check_paper.py` が、四つの検査を `--break` で走らせて数え直しています。

## 言語モデルの利用

Claude Code（Anthropic）を使いました。
文献の記録を探して要旨を読むこと、文章の下書き、検査の台本、偏り・言い過ぎ・確かめていない事実を探す読み直しに使っています。
内容の責任は著者が負います。
Claude は著者ではありません。

## 誤りの知らせと個人の情報

誤りは、issue の様式「誤りの知らせ」で受けます。
2026-12-01 から、その issue は突き合わせの受付で確かめます。
受付の道具とワークフロー（`.github/checked-intake/verify.js`、`.github/workflows/checked-intake.yml`）は、運営者のほかのリポジトリと一字一句同じ写しです。
issue で届いた個人の情報の扱いと、開示・訂正・利用の停止・消去の求め方は、運営者の[免責事項](https://github.com/cpsbvbng26-dotcom/cpsbvbng26-dotcom/blob/main/DISCLAIMER.md)の「情報の扱い」の節にあります。
題と本文を言語モデルに渡すときの扱いは、同じ免責事項の「issue の中身と言語モデル」の節にあります。

`SECURITY.md` も、運営者のほかのリポジトリと一字一句同じ写しです。
その中の「免責事項」は、上の免責事項のことです。
その中の「2026-11-12 に確かめました」は、写しのもとのリポジトリで確かめた日です。
このリポジトリは 2026-11-23 に作りました。
このリポジトリでも GitHub の非公開の脆弱性報告が有効でないことを、2026-11-23 に GitHub の API で確かめました。

## ライセンス

稿と散文は CC BY 4.0（`LICENSE`）、台本と検査は MIT（`LICENSE-CODE`）です。
稿が引く他の著者の要旨の文は、CC BY 4.0 でも MIT でも許諾しておらず、それぞれの権利者のものです。
