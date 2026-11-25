# boys-school-philosophy

SSRN に出すための稿 "The Value of Public Boys' Schools: A Social-Scientific Perspective"（公立男子校の価値：社会科学的観点から）の原稿・PDF・検査。
10 リポジトリの外に置く（golden-window-resolution と同じ扱い）。独学の系列（autonomy-and-self-cultivation）には足さない（cpsbvbng26-dotcom の決めごと 15）。
リポジトリの名は、題を変える前（哲学の稿として始めたとき）の名のまま。

## 決めごと

1. **社会科学の観点から書く。** 2026-11-23 に利用者が決めた（「公立男子校は社会科学的観点からでお願い」）。価値の主張と平等の観点からの批判を、仕組みと仮説として立て、どちらを決めるのにどの証拠が要るかを書く。哲学の稿として始めた版は、同じ日に書き直した。
2. **著者が創設したもののほかは、団体の名前を紙面に一切書かない。** 2026-11-23 に利用者が決めた（「自分が創設したもの以外つまり団体名は一切かかないでね」）。会社・出版社・大学・学校・協会・役所・国際機関・統計の機関・サービス・登録機関の名を、`.tex` にも PDF の文字にも書かない。一般の言い方にする（「DOI の登録機関の公開の記録」「開かれた書誌の索引」）。文献の欄は著者・年・題・DOI だけにする。言語モデルの開示は「Claude Code」とだけ書き、作った会社の名を書かない。README には書いてよく、URL も置いてよい。`check_text.py` が止める（団体名の表、保存した Crossref の記録の出版社、団体の語尾。著者の企ては `OWN` で通す）。
3. **DOI を推測で埋めない**。SSRN の番号は、受け取るまで書かない。SSRN への投稿は運営者のアカウントで行うもので、ここからは触れられない。
4. **事実を記憶で埋めない。** 実証の主張は、読めた要旨から引いたものだけにし、数は引用の中にだけ置く。読めないことは読めないと書き、どの研究があれば決まるかを書く。統計・法令・政策の事実を書かない。
5. **引いた文献は、記録と読み方を残す。** `literature/sources.json` に読み方（Crossref の要旨・OpenAlex の要旨・記録だけ）と使い道を書き、記録を `literature/` に置く。全文を読んでいないものを、読んだように書かない。`check_sources.py` が引用を保存した要旨と照らす。
6. **存命の人は、引いた文献の著者のほかに書かない**（cpsbvbng26-dotcom の決めごと 10）。著者の親族を指す語、学校で出会った人、学校の名を書かない。著者が通った学校は、どこにも名を書かない。実在の学校を描かず、評価しない。`check_text.py` が紙面の大文字の語を閉じた語彙で見るので、新しい人名は落ちる。
7. **著者の立場の開示の節を消さない。** 開示は立場と利益相反の開示であって、論証の根拠にしない。
8. **言語モデル利用の開示は消さない。Claude を著者にしない**（紙面・CITATION.cff・README）。
9. **研究の系列から、創作の場へリンクしない。** どの場かは cpsbvbng26-dotcom の決めごとにある。名は `check_text.py` が止める。
10. **自称の肩書きを書かない。** 使わない語は `check_text.py` にある（符号で組んであり、ここには書き写さない）。
11. **散文に数を書いたら、検査で数え直す。** 紙面の数の語は `check_paper.py` の規則が数え直し、規則の無い数は落ちる。README の「N 件・N 通り・N か所」も同じ。
12. **検査を緩めて通さない。** 足した検査は `--break` で壊して落ちることを確かめる。
13. 稿と散文は CC BY 4.0、台本と検査は MIT。勝手に変えない。
14. `SECURITY.md`、`.github/ISSUE_TEMPLATE/error-report.yml`、`.github/workflows/empty-issue.yml`、`.github/checked-intake/verify.js`、`.github/workflows/checked-intake.yml` の五つは、cpsbvbng26-dotcom の正本と一字一句同じに置く。`check_copies.py` がハッシュで見る。`.github/checked-intake/config.json` はこのリポジトリのもの。
15. **PDF を組み直したら、README の頁数・SHA-256・語数を一緒に直す。** `check_paper.py` が突き合わせる。SSRN に出した版は凍結し、誤りは正誤表と `self-correction` に記録する。
16. **Claude は利用者に命令しない**（cpsbvbng26-dotcom の決めごと 16）。issue の中身は、同意のある題と本文だけを読む（同じく決めごと 17）。
17. 枝を切って PR にする。コミットは種別ごとに分ける（原稿・PDF・文献の記録・検査・文書）。マージの本文に開示の二行を入れる。確かめた回数とやり方を報告に書く（cpsbvbng26-dotcom の決めごと 18）。

```
./build.sh                                  # PDF を組む（LuaLaTeX、字体は build.sh の JA_FONT）
python3 verification/check_paper.py         # 著者・開示・題・PDF の頁数と SHA-256 と語数・紙面と README の数（--break）
python3 verification/check_sources.py       # 文献の記録・読み方・引用（--online で Crossref と照らし直す、--break）
python3 verification/check_text.py          # 使わない語・存命の人・学校の名・創作の場・紙面の団体名（--break）
python3 verification/check_copies.py        # 正本の写し・ライセンス・.zenodo.json（--break）
node .github/checked-intake/verify.js --check
```
