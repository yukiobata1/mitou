# 半導体AMHSのbrownfield性と横断調停ランタイムの成立性調査

- 調査日・全URLの確認日: 2026-09-20
- 目的: 未踏アドバンスト（2026年度下期）応募書類「①背景」「競合」節の根拠集め
- 対象提案: 内部を変更できない複数ベンダーの既設搬送システム（OHT、AGV/AMR、ストッカ、各社の搬送制御/fleet manager）の上に載り、位置履歴と限定された命令への応答から能力・遅延をオンライン同定し、競合箇所だけを局所調停する上位ランタイム

## 0. この文書の読み方（信頼度ラベル）

| ラベル | 意味 |
|---|---|
| **[事実・原文確認]** | ページ/PDFの生テキストを自分で取得し、該当文言を目視確認した |
| **[事実・要約経由]** | URLは取得できたが、内容は自動要約ツール経由で読んだ。数値は一致確認済みだが、申請書に引用する前に原文を人間の目で再確認すること |
| **[事実・検索スニペットのみ]** | 本文が403等で取得できず、検索結果の抜粋でしか見ていない。引用前に必ず原文確認が必要 |
| **[推論]** | 上記情報源から筆者（調査エージェント）が導いた解釈。事実ではない |
| **[未確認]** | 調べたが裏が取れなかった。推測で埋めていない |

注意: 今回、自動要約ツールが論文タイトルを誤って生成する事例が1件あった（OHTを"Oversize and Heavy Transportation"と誤読）。このため、重要な数値はできる限り生テキストで再確認した。再確認できなかったものはラベルで区別している。

---

## 1. 申請書「①背景」へ転記できる事実（要点）

1. **工程数は微細化とともに増え続けている。** マスク層数は28nmで40〜50層、14/10nmで約60層、7nmで80〜85層、5nmで約100層。fabサイクルタイムは28nmの約40日から5nmで約100日へ。先端ロジックは600〜1,000工程以上（UC Berkeley Robert Leachman教授の発言として Semiconductor Engineering, 2017-02-16 が報道）。工程数の分だけ装置間搬送が発生する。 https://semiengineering.com/battling-fab-cycle-times/ [事実・要約経由]
2. **大規模fabはOHTを数千台規模で走らせており、渋滞がサイクルタイムを直接押し上げる。** 「most large-scale semiconductor fabs operate thousands of OHT vehicles on a track simultaneously」「This congestion increases OHT vehicle travel time, thereby highly increasing the overall cycle time of a product. In worst-case situations, a deadlock occurs」（KAIST Lee & Jang, ISMI 2022）。1,000台超を強化学習で制御する商用システム（DAIM Research OMS）が既に存在する（WSC 2022 Industry Case）。 [事実・原文確認]
3. **SEMI規格は「上位から見た搬送装置のインタフェース」を標準化しているが、交通管理は標準化していない。** SEMI E82（IBSEM）の公開要旨は「Several topics require additional activity that are within the scope of this Standard: traffic management characteristics (queuing), ... transport system controller architecture, ...」と明記。すなわち渋滞・待ち行列の扱いと搬送コントローラの内部構造は現行規格で未規定のまま、各ベンダーの実装に委ねられている。 https://store-us.semi.org/products/e08200-semi-e82-specification-for-interbay-intrabay-amhs-sem-ibsem （E82-1106, Reapproved 0523）[事実・要約経由、該当文は逐語取得を指示して取得]
4. **実fabのAMHSは複数ベンダー混在で、上位（MCS）からは内部状態が部分的にしか見えない。** 2026-08-31投稿のarXiv論文（実稼働MCSのログ51,700件を使用）が「A fab AMHS may contain equipment from several vendors, with different interfaces and local control logic, while some internal device queues are only partly observable」「vendor-specific relay equipment whose internal queues are only partly reported, so the relevant state must be inferred from event logs」と記述。 https://arxiv.org/abs/2608.30520 [事実・原文確認]
5. **搬送制御の改善幅は「数%〜十数%」の帯で報告されている。** (a) OHT経路制御: 100/150/200台のシミュレーションで平均完了時間 0.8〜8.8%短縮（対 表形式Double Q-routing、arXiv 2608.30512, 2026）。(b) MCS経路スケジューリング: 較正済み閉ループシミュレータで平均搬送時間16.4%短縮（対 静的最短経路、arXiv 2608.30520, 2026）。(c) 実生産ライン設計向けAGVシミュレーション: 経路制御単独でリードタイム2.1〜4.5%短縮、ディスパッチ変更で27.8〜28.8%短縮（POSTECH + Samsung Display, IJIE 2023）。いずれもシミュレーション値であり、実fab実測ではない。 [事実・原文確認]
6. **レガシーfabは消えず、むしろ増えている。かつ止められない。** SEMIは200mm fab能力が2023〜2026年に14%増え、2026年に過去最高の月産770万枚超、新規量産fab 12棟と予測（SEMIプレスリリース, 2023-09）。レガシーfab自動化ベンダーFabmaticsは稼働中fabへの後付けを「open heart surgeries」と呼び、「limited ceiling height, narrow aisles, and mixed equipment generations」を制約として挙げる。 [200mm数値: 事実・検索スニペットのみ（semi.orgは403）/ Fabmatics: 事実・原文確認]
7. **後工程は自動化が遅れており、標準化そのものが進行中。** 半導体後工程自動化・標準化技術研究組合（SATAS）が2024-04-16設立、2028年実用化目標。事業内容に「完全自動化に必要な装置・システム間の標準化」「頭上と地上の両方を組み合わせた自動搬送システムが補完的な役割を担う」を掲げる。組合員にダイフク、村田機械、インテル、オムロン、平田機工、ローツェ等（2026年4月末現在38組織）。 https://satas-cip.jp/organization-2/ , https://monoist.itmedia.co.jp/mn/articles/2405/08/news078.html [事実・要約経由]
8. **日本国内で兆円単位のfab投資が同時進行している。** Rapidus: 2026-04-11に2026年度6,315億円の追加支援発表、政府支援累計2兆3,540億円、2027年度後半に2nm量産開始予定。JASM: 第1・第2工場へ最大1兆2,080億円補助、第2工場は2026-02-05に3nm導入を表明。Micron広島: 1.5兆円投資・最大5,360億円支援、2026-07-04起工。（出典は6章）[事実・要約経由]

---

## 2. 半導体AMHSの構造

### 2.1 確認済みの事実

- **階層**: MESが搬送要求を出し、MCS（Material Control System）がそれを実行可能な搬送コマンドに変換して経路（中継リソースの列）を決め、その下に各搬送装置のコントローラ（OHTコントローラ、ストッカコントローラ等）がある。「the Material Control System (MCS) converts transport requests from the Manufacturing Execution System (MES) into executable commands and schedules a relay route for each command online. ... Unlike the local controller of a single device, the MCS coordinates heterogeneous transport and relay resources.」 https://arxiv.org/abs/2608.30520 （2026）[事実・原文確認]
- **村田機械のMCS**: 「Total control system for AMHS for overall control of all transport equipment such as OHS, OHT, AGV, RGV and Stocker」。他社機器対応の記述は同ページに無い。 https://www.muratec.com/cfa/products/mcs.html [事実・要約経由]。村田機械クリーンFA事業ページには「MCS（Material Control System）、MDS（MCS Dispatching System）」の記載あり。 https://www.muratec.jp/corp/division/cleanfa.html [事実・要約経由]
- **SEMI規格が標準化している範囲**（いずれもSEMI公式ストアの公開要旨、規格本文は有償で未読）:
  - **E82 (IBSEM)**: 工程間/工程内搬送装置（OHT, OHS, RGV, AGV等）を「SECS-IIホストから見た」モデルとして規定。搬送コマンド・搬送システムコントローラ・ビークル・キャリアの状態モデル、収集イベント、アラーム、リモートコマンド。現行版 E82-1106 (Reapproved 0523)。交通管理（queuing）とコントローラアーキテクチャは「追加作業が必要な項目」。 [事実・要約経由]
  - **E88 (Stocker SEM)**: 保管装置（ストッカ）の同様のホスト視点モデル。ストッカコントローラ、搬送コマンド、キャリア、クレーンの状態モデル。E88-0307 (Reapproved 0523)。「defines the view of the equipment through the SECS communication link」であり内部動作は対象外。 https://store-us.semi.org/products/e08800-semi-e88-specification-for-amhs-storage-sem-stocker-sem [事実・要約経由]
  - **E84**: 搬送装置（AGV, RGV, OHT）と受け側装置（製造装置、ストッカ）の間のキャリア受け渡しパラレルI/O信号、ハンドオフシーケンス、エラー検出・復旧。E84-0823。「ハンドオフ動作そのもの」だけを規定し、工場レベルのホスト管理機能は対象外。 https://store-us.semi.org/products/e08400-semi-e84-specification-for-enhanced-carrier-handoff-parallel-i-o-interface [事実・要約経由]
  - **E87**: キャリア管理（Carrier Management Specification）。装置側ロードポートでのキャリアID確認・スロットマップ等。 [事実・検索スニペットのみ]
  - **E153 (AMHS SEM)**: 搬送と保管を統合したモデル。ストア上のステータスは **Inactive**（E153-0310, Reapproved 0517）。E82と同じく交通管理を「追加作業が必要」と記載。 https://store-us.semi.org/products/e15300-semi-e153-specification-for-amhs-sem-amhs-sem [事実・要約経由]
  - **E187/E188**: fab装置およびAMHSのサイバーセキュリティ要件（E187-0122、12要件）と、導入前のマルウェア・脆弱性スキャン（E188）。E187は「semiconductor manufacturing equipment and automated material handling systems (AMHS)」に適用。 https://www.pdf.com/standards/semi-e187/ 他 [事実・検索スニペットのみ]
- **主要ベンダーの事業規模**（公式開示）:
  - 村田機械: 2025年3月期 連結売上高5,260億円（前期比+6%、初の5,000億円超）、うちクリーンFA 2,362億円（+19%、全体の約45%）。 https://kikai-news.net/2025/06/09/ （2025-06-09）[事実・要約経由。村田機械公式PDF https://www.muratec.jp/company/asset/pdf/2503_FOA.pdf で売上高4,974→5,260億円、営業利益791→931億円は原文確認。セグメント別数値はPDFの文字化けにより原文未確認]
  - ダイフク: 2025年12月期 売上高6,607億円、受注高6,726億円、営業利益1,008億円。業種別でエレクトロニクス向け売上2,510億円（構成比38.0%）、受注2,398億円（35.7%）。決算説明資料に「生成AI向け先端半導体投資の強い需要が継続」。 https://azcms.ir-service.net/DATA/6383/ir/140120260212556155.pdf （2026-02-12）[事実・原文確認。ただし「エレクトロニクス」は半導体とFPDの合算で、半導体単独の数値は未確認]
  - ダイフクは2026年4月に滋賀事業所のクリーンルーム事業新工場棟を竣工、生産能力1.3倍。 [事実・検索スニペットのみ]

### 2.2 未確認

- **世界シェア**: 市場調査会社の公開要約は相互に矛盾している（「ダイフク約50%、次いで村田機械」とするものと、「ダイフク28%、村田機械21%」とするもの）。一次情報（両社IR、SEMI）でシェアを明示したものは見つけられなかった。**申請書にシェア数値を書くのは避け、「日本の2社（ダイフク、村田機械）が世界の主要サプライヤー」という定性表現に留めるのが安全。** [未確認]
- AMHS市場規模も調査会社により幅がある（例: SNS Insiderは2025年26.6億ドル→2035年54.2億ドル、Precedenceは2034年62億ドル）。いずれも二次情報。 [事実・検索スニペットのみ、信頼度低]
- E82が定義するリモートコマンドの具体的一覧（TRANSFER / CANCEL / ABORT / PAUSE / RESUME 等）は規格本文が有償のため未確認。**提案の「限定された命令」が実際に何を指せるかはここに依存するため、ムラタシステムへの追加ヒアリング事項として重要。** [未確認]

### 2.3 情報源からの推論

- SEMI規格が統一しているのは「MCS⇔各搬送装置コントローラ」の縦のメッセージ形式と「搬送車⇔ロードポート」の受け渡し信号であり、「ある合流点で誰を先に通すか」という横の交通制御は規格の外にある。ここは各ベンダーのコントローラ内部に閉じている。 [推論]
- したがって、既存の「ベンダー横断レイヤ」はMCSであり、その粒度は搬送コマンド単位（どのストッカ・どのリフタを経由するか）。車両単位の合流調停ではない。 [推論]

---

## 3. 搬送効率が生産に与える影響の定量的根拠

### 3.1 確認済みの事実

| # | 出典（年） | 条件 | 数値 | ラベル |
|---|---|---|---|---|
| A | Gu et al., arXiv 2608.30512 (2026-08-31) https://arxiv.org/abs/2608.30512 | 単一fabレイアウトのシミュレータ、OHT 100/150/200台 × 到着率3水準の9設定。比較対象は表形式Double Q-routing | 平均完了時間 0.8〜8.8%短縮。150台・200台の6設定では全手法中最良。**100台の3設定ではDijkstra（静的最短経路）が最良**。立ち上げ時はオフライン初期化で完了タスク数最大+23%、裾の完了時間最大-15% | 事実・原文確認 |
| B | Yin et al., arXiv 2608.30520 (2026-08-31) https://arxiv.org/abs/2608.30520 | 半導体ディスプレイfabの実稼働MCSログ51,700件で学習、ノード762・有向辺1,549。評価は較正済み閉ループシミュレータ、1runあたり500コマンド×5反復、目標稼働率0.70。比較対象は静的最短経路 | 平均総時間 -16.40%、P95 -10.33%、内部待ち時間 -22.59%、スループットほぼ不変。著者自身が「段階的で監視付きの導入を推奨」と明記 | 事実・原文確認 |
| C | Bang, Kim, Kim (POSTECH, Samsung Display), Int. J. Industrial Engineering 30(2), 2023 https://ijietap.com/index.php/ijie/article/download/8657/1345/49887 | 実生産ライン向けに設計されたグリッド型AGVシステムのシミュレーション | 経路制御（advanced dynamic A*）単独でリードタイム2.1〜4.5%短縮（高負荷3600 loadsでは4.9〜7.8%）。ディスパッチ（HABOR）で27.8〜28.8%短縮。併用で30.4%短縮（475.4s→331.1s）。結論: 「dispatching methods showed a more significant impact」 | 事実・原文確認 |
| D | Fabmatics（ベンダーFAQ、年不明・2026-09-20閲覧） https://www.fabmatics.com/lp/automating-legacy-fabs/ | レガシーfab自動化の「rule of thumb」 | 「automation can reduce cycle time by 10 - 30%, with an additional 5 - 10% improvement through advanced scheduling. WIP turns increase from 3 - 4 (manual fabs) to 5 - 6 with AMHS.」 | 事実・原文確認（ただしベンダーの経験則で、測定条件なし） |
| E | Applied Materials SmartFactory ブログ（公開日不明） https://appliedsmartfactory.com/semiconductor-blog/scheduling/smartfactory-dispatching-solutions/ | 同社ディスパッチ製品の顧客実績として | 「improve throughput by 5-10%」「increase productivity by another 3-5% by integrating these solutions」。最適化ベースはヒューリスティック比で追加3〜5% | 事実・要約経由（ベンダー主張、条件不明。搬送ではなくロット・ディスパッチの話） |
| F | Koo et al., Int. J. Production Research (2026) https://www.tandfonline.com/doi/abs/10.1080/00207543.2026.2656773 | 大規模fab、レイアウトを領域分割しRLでリンク重みを動的制御 | ルールベース比でスループット・リードタイムともに改善（数値は未取得） | 事実・検索スニペットのみ |
| G | Bartlett et al., Computers & Industrial Engineering 70, 2014 https://www.sciencedirect.com/science/article/abs/pii/S0360835214000357 | 渋滞考慮の動的経路制御 | 「定常状態で5%の性能改善、重度渋滞の発生を解消」 | **事実・検索スニペットのみ。本文403。5%という数値を申請書に使うなら原文確認必須** |
| H | 「Integration of lot dispatching and AMHS control in a 300mm wafer FAB」IEEE (2005) https://ieeexplore.ieee.org/document/1438808/ | ロットディスパッチとAMHS制御の統合 | 搬送時間4.4%短縮、1日あたり総待ち時間37.35時間短縮 | 事実・検索スニペットのみ。要原文確認 |

定性的な因果の記述:
- 「Material-handling delays directly increase cycle time and work-in-process, while prolonged queueing at intermediate storage can cause queue-time (Q-time) violations and threaten yield」「Transport times therefore have a pronounced upper tail, with a small fraction of severely delayed commands causing disproportionate operational disruption and Q-time risk.」（arXiv 2608.30520）[事実・原文確認]
- 「frequent congestion and deadlocks in the FAB lead to diminished productivity」、OHTは「numbering in the hundreds within a FAB, travel an average of 20 kilometers per day」（Choi et al., PLOS ONE, 2024-07-12） https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0307059 [事実・要約経由]

### 3.2 未確認

- 「搬送時間がサイクルタイムの何%を占めるか」の公開一次データは見つけられなかった。 [未確認]
- 実fabでの搬送制御変更による装置稼働率・スループットの実測改善値（論文・ベンダー事例とも）は見つけられなかった。DAIM ResearchのOMSは「has improved OHT operation significantly」とのみ記述し数値非開示。 [未確認]
- 「5%前後」の一次根拠として最も近いのはG（Bartlett 2014）だが原文未確認。

### 3.3 情報源からの推論

- 公開されている改善幅は、経路制御単独では「数%」、ディスパッチや上位の経路選択まで含めると「10〜30%」という二層構造になっている。提案が触れるのが合流・交差の局所調停（経路制御寄り）だけなら、期待できるのは数%帯と見るのが誠実。 [推論]
- A論文で「100台ではDijkstraが最良」という結果は、混雑していない系では学習型制御の上積みがほぼ無いことを示す。提案の価値は混雑度に強く依存する。 [推論]
- 平均値より裾（P95、Q-time違反）のほうが現場の痛みに近い可能性がある。評価指標を平均搬送時間でなくテール遅延に置くほうが説得力が出る。 [推論]

---

## 4. 微細化・工程数増加と搬送の複雑化

### 4.1 確認済みの事実

- マスク層数とサイクルタイム（1章の1と同じ、Leachman / Semiconductor Engineering 2017-02-16）。SAQPの1フローだけで「60 operations」（Coventor CTO David Fried）。 [事実・要約経由]
- 「The process of forming modern semiconductor wafers consists of numerous steps with re-entrance performed by hundreds of machines. Bundles of 25 wafers are loaded into a ... FOUP for transport via an OHT system to the machine that performs each step.」（Lee & Jang, ISMI 2022） https://www.conf.tw/site/userdata/1449/ISMI_paper/ISMI2022_paper_5130.pdf [事実・原文確認]
- 「Due to recent increases in production, most semiconductor fabs now operate thousands of OHT vehicles」（Hong et al., WSC 2022） https://www.informs-sim.org/wsc22papers/337.pdf [事実・原文確認]
- レイアウトは固定ではない: 「modifications to the existing OHT vehicle track, such as removal or addition, may be necessary due to scheduled preventive maintenance, the introduction of new machines, resource expansion, changes in layout」（Japhne & Jang, WSC 2024） https://informs-sim.org/wsc24papers/cea151.pdf [事実・原文確認]
- TSMCは12インチGIGAFABを6拠点運営、AMHSを公式に「silver highway」と紹介。 [事実・検索スニペットのみ]

### 4.2 未確認

- 1ウェハ（1ロット）あたりの搬送回数、fab内総走行距離、軌道総延長、1日あたり搬送回数の公開一次データ（TSMC、Samsung、Intel等）は見つけられなかった。各社とも非開示と思われる。 [未確認]
- 2017年以降（3nm、2nm）のマスク層数・工程数の一次データは未確認。1章の数値は2017年時点の予測を含む（5nmの「100層」は当時の見込み）。 [未確認]

### 4.3 情報源からの推論

- 工程数600〜1,000は、各工程間で少なくとも1回のFOUP搬送を伴うため、1ロットあたり数百〜千回規模の搬送に相当すると推定できる。ただしこれは推定であり、公開データではない。申請書に書く場合は「工程数と同程度の回数の搬送が発生する」と推定である旨を明示すること。 [推論]

---

## 5. brownfield性

### 5.1 確認済みの事実

- **200mm能力は拡大中**: SEMI「Global 200mm Fabs to Reach Record High Capacity by 2026」（2023-09）。2023〜2026年に14%増、月産770万枚超、新規量産fab 12棟。車載・パワー向けが34%増。 https://www.semi.org/en/news-media-press-releases/semi-press-releases/global-200-mm-fabs-to-reach-record-high-capacity-by-2026-semi-reports [事実・検索スニペットのみ、本文403]
- **レガシーfabの制約**（Fabmatics、原文確認）: 「Legacy fabs often suffer from space constraints and non-linear layouts」「No two legacy fabs are alike」「Legacy IT environments are often fragmented and difficult to extend (island solutions, mixed generation software)」。キャリア種別も open cassette / SMIF pod / FOUP が混在。稼働中の後付けは可能で、自社では「open heart surgeries」と呼ぶ。 https://www.fabmatics.com/lp/automating-legacy-fabs/
- **手搬送からの段階的自動化の実例**: Bosch Reutlingen 200mm fabは元は手動運用で、孤立した自動化から始めて、固定ロボットセル、レール式ロボット、コンベヤへ段階拡張（Fabmatics, 2016-07-26）。 https://www.fabmatics.com/news-2/new-video-material-handling-automation-in-200mm-semiconductor-fab-bosch/ [事実・要約経由]
- **200mm fabでのAMR後付け実証**: Fabmatics と Infineon Technologies Dresden が欧州研究プロジェクトAIMS 5.0の一環で、AMR「HERO Scout」を200mm fabの実生産環境で評価（レチクルSMIFポッドと200mmキャリア、リソ工程。ダミー材料を使用）。2026-07-30発表。MES/MCS/fleet managerとの統合方法の詳細は記事に無い。 https://www.fabmatics.com/news-2/future-of-lithography-logistics-hero-scout-proven-in-real-world-cleanroom-operations/ [事実・要約経由]
- **複数ベンダー混在は少なくとも2007年から公知の課題**: TSMC特許 US7684888B2「Extendable MES for Cross-AMHS Transportation」（出願2007-05-08、登録2010-03-23）。背景に「typical MES and MCS systems are limited to a single fab and cannot process cross-fab and/or cross-AMHS transportation requests」「different fabs may have different AMHS vendors and communication protocols」。解決策は複数MCS・複数AMHSをブリッジで接続し統合制御ユニットで調整するもので、「the flexibility to choose an AMHS vendor ... and not be tied to a single vendor」を利点に挙げる。 https://patents.google.com/patent/US7684888B2/en [事実・要約経由]
- **装置ソフトを変更できず生産も止められない、という制約の言語化**: Focussia（fab装置ソフトのアップグレード企業）「Production is not stopped. Automation is not disrupted. Existing software is not modified.」、レガシー装置にSECS/GEMとE84を後付け。 https://www.focussia.com/smart-manufacturing/ [事実・要約経由]
- **後工程**:
  - ダイフクはSEMICON Japan 2025で、OHT「CLW-08K」と協力企業Gyro Systemsの搭載型AMRを組み合わせたデモを展示。Youibot Robotics等とも協業。後工程は「前工程ほど標準化できていない」。大規模OHTは低コスト化にハードル（MONOist, 2025-12-24）。 https://monoist.itmedia.co.jp/mn/articles/2512/24/news032.html [事実・要約経由]
  - 「前工程に比べ人手による作業が多かった後工程も今後、自動化が進むと見込まれる」。600mm角の大型インターポーザーは約100kgでOHT搬送が難しく、シンフォニアテクノロジーが最大可搬100kgのパネル搬送AMRシステムを開発中（電波新聞, 2025-01-06）。 https://dempa-digital.com/article/621359 [事実・要約経由]
  - SATAS（1章の7）。

### 5.2 未確認

- 200mm/150mm fabのうち手搬送主体のものの割合、AMR/AGV後付け済みの割合を示す統計は見つけられなかった。 [未確認]
- 日本国内のレガシーfab数とその自動化率。「日本は工場数で世界1位」という記述は東京エレクトロンの解説記事にあるが、口径別・自動化水準別の内訳は未確認。 [未確認]
- 同一fab内で複数ベンダーのOHTが同じ軌道網を共有している事例の有無。 [未確認]（→ 8章のリスク2に直結）

### 5.3 情報源からの推論

- 公開情報から読み取れる「複数ベンダー混在」は、(i) fab棟ごと・フェーズごとにAMHSベンダーが違う（TSMC特許）、(ii) OHT＋ストッカ＋リフタ＋AMRなど装置種別ごとにベンダーが違う（arXiv 2608.30520、ダイフク×Gyro Systems）、の2形態。同じレール上で他社車両が混走する形態は確認できていない。つまり、半導体fabでベンダー間の競合が起きる場所は「合流・交差」よりも「受け渡し点（ストッカ入出庫口、リフタ、ロードポート、OHT⇔AMRドッキング）」である可能性が高い。 [推論]
- 後工程と200mmは、OHT一社支配が成立しておらず、床上AMRと天井搬送の混在が今まさに設計されている領域。提案の入り口としては300mm前工程より現実的に見える。 [推論]

---

## 6. 日本の半導体投資の追い風

### 6.1 確認済みの事実

| 案件 | 内容 | 出典（発表年月） | ラベル |
|---|---|---|---|
| Rapidus 追加支援 | 赤沢経産相が2026-04-11、2026年度の研究開発委託費として6,315億円の追加支援を発表。政府支援累計2兆3,540億円。別枠で政府出資が2025・2026年度で2,500億円。2027年度後半の量産化へ | ITmedia NEWS（産経）2026-04-13 https://www.itmedia.co.jp/news/articles/2604/13/news067.html | 事実・要約経由 |
| Rapidus 中期計画 | 2027年度後半に2nm量産開始、2029年度後半1.4nm、2031年度後半1.0nm、2031年度頃に上場を目指す | EE Times Japan 2025-11-21 https://eetimes.itmedia.co.jp/ee/articles/2511/21/news147.html | 事実・要約経由 |
| Rapidus 出資 | IPAが1,000億円出資、民間32社が1,676億円出資（2026年2月下旬） | 検索結果抜粋（テレ東BIZ/産経系） | 事実・検索スニペットのみ。**検索結果の抜粋には「内閣人事局(IPA)」という明らかな誤記があり、金額も原文確認が必要** |
| Rapidus 試作ライン | 2025-04-01、千歳IIMで2nm試作ライン稼働開始。2025年度最大8,025億円の追加支援で当時累計1兆7,225億円 | 検索結果抜粋 | 事実・検索スニペットのみ |
| JASM 第1・第2工場 | 第2工場総投資約1兆6,900億円（当初計画）、第1と合わせ約3兆円。補助は第1に最大4,760億円、第2に最大7,320億円、計最大1兆2,080億円。第1工場は22/28nm、12/16nmを量産中 | 地方経済総合研究所 2025-10-20 https://www.reri.or.jp/report-and-news/tsmc-kumamoto-second-factory/ | 事実・要約経由 |
| JASM 第2工場 3nm転換 | TSMC C.C. Wei CEOが2026-02-05に第2工場での3nm導入を表明 | EE Times Japan 2026-02-05 https://eetimes.itmedia.co.jp/ee/articles/2602/06/news047.html | 事実・要約経由 |
| 同 台湾当局承認 | 台湾経済部投資審査委員会が計画変更を承認。2028年量産開始予定、月産1万5,000枚規模 | マイナビTECH+ 2026-04-01 https://news.mynavi.jp/techplus/article/20260401-4284892/ | 事実・要約経由 |
| 同 投資額 | 122億ドル→170億ドルへ拡大見通し | 検索結果抜粋（複数の二次メディア） | 事実・検索スニペットのみ。**抜粋間で円換算が約2.6兆円と約2.7兆円に割れている** |
| Micron 広島 | 新製造棟を2026-07-04起工。総額約1兆5,000億円投資、経産省が最大5,360億円支援。2028年下半期に量産開始予定 | EE Times Japan 2026-07-05 https://eetimes.itmedia.co.jp/ee/articles/2607/06/news047.html | 事実・要約経由 |
| ダイフク | 2026年12月期は受注7,800〜8,200億円を予想、「先端半導体需要の拡大といった構造的トレンドを追い風に」 | ダイフク決算説明資料 2026-02-12 | 事実・原文確認 |

### 6.2 未確認

- 経産省の一次資料（半導体・デジタル産業戦略、次世代半導体等小委員会 第8回 2026-04-03 資料3、情報処理促進法に基づく実施計画概要）は meti.go.jp が403を返し、直接読めなかった。上表は報道経由。**申請書で金額を引用する際は経産省PDFの該当ページを人間が確認すること。** [未確認]
  - https://www.meti.go.jp/shingikai/sankoshin/shomu_ryutsu/next_generation_semiconductor/pdf/008_03_00.pdf
  - https://www.meti.go.jp/policy/mono_info_service/joho/laws/josokuho/josokuho_jisshikeikaku.pdf
- JASM第2工場の稼働時期は報道間で不一致（EE Times 2026-02-05は「2027年の本格稼働開始を目指す」、マイナビ2026-04-01は「2028年に量産開始」）。 [未確認]
- キオクシア、ソニー、ローム、ルネサス等の個別増強計画は今回未調査。 [未確認]

### 6.3 情報源からの推論

- 国内の大型案件（Rapidus、JASM第2、Micron広島新棟）はいずれも新設（greenfield）で、AMHSは単一ベンダー一括導入になる公算が高い。「国内投資の追い風」は市場の熱量の根拠にはなるが、brownfield向けの本提案の直接の顧客根拠としては弱い。追い風として使うなら、「新設fabに技術者・装置が集中し、既存レガシーfabの省人化圧力が高まる」という間接経路で述べるべきで、その裏付け（人手不足データ）は今回未取得。 [推論]

---

## 7. 先行研究（OHT/AMHS交通制御へのRL・MARL・最適化、2020年以降）

### 7.1 確認済みの事実

| 研究 | 手法 | 規模・評価 | 備考 | ラベル |
|---|---|---|---|---|
| Hwang & Jang, IJPR 58(4), 2020 https://www.tandfonline.com/doi/full/10.1080/00207543.2019.1614692 | Q(λ)学習による動的経路誘導（QLBWR(λ)）、Boltzmann方策 | 実fabレイアウトのシミュレーション、数百台をリアルタイム処理。静的・動的ベンチマークを上回る（数値未取得） | 後にDAIM ResearchのOMSとして商用化 | 事実・検索スニペットのみ |
| Hong, Hwang, Jang, IEEE Trans. Semiconductor Manufacturing, 2022 https://ieeexplore.ieee.org/document/9759491/ | Q学習ベースの経路誘導＋車両割当 | 数百台の実用環境 | 同上 | 事実・検索スニペットのみ |
| Hong et al., WSC 2022 Industry Case | OMSの商用化とデジタルツイン（車両エミュレータ、OMSコネクタ、仮想工場） | 1,000台超。「used by major semiconductor fab manufacturers」 | 産業パートナーと共同開発 | 事実・原文確認 |
| Lee & Jang, ISMI 2022 | GNNで辺の通過時間を先読みする active Q routing | 制御された小規模ケースで平均移動時間短縮。実fab検証は今後 | Q-routingの「遅れた適応」問題を指摘 | 事実・原文確認 |
| Ahn et al., IISE Transactions 54(8), 2022 https://www.tandfonline.com/doi/abs/10.1080/24725854.2021.2000680 | Graph convolutional GRUで渋滞予測→動的経路 | 未取得 | | 事実・検索スニペットのみ |
| Japhne & Jang, WSC 2024 | デジタルツイン＋Q(λ)で軌道変更を事前に織り込む | 20ベイ、OHT 40台 | | 事実・原文確認 |
| Choi et al., PLOS ONE, 2024 | 媒介中心性でOHT軌道網の脆弱リンクを可視化 | | 制御ではなく診断 | 事実・要約経由 |
| 「Multiagent reinforcement learning-based dispatching model for OHT in AMHS」Computers & Industrial Engineering, 2025 https://www.sciencedirect.com/science/article/abs/pii/S0360835225002554 | MAIPPO＋注意機構、各ベイをエージェントとする部分観測マルコフゲーム | ファウンドリのAMHSシミュレーション、古典ルールを上回る | MARLだが単一AMHS内 | 事実・検索スニペットのみ |
| Koo et al., IJPR, 2026 | RLによる動的リンク重み制御（DLWC）、領域分割 | 大規模fabシミュレーション | 車両を直接制御せず、経路コストを操作する間接制御 | 事実・検索スニペットのみ |
| Gu et al., arXiv 2608.30512, 2026 | Neural Double Q-routing、軌跡回帰で初期化 | 100〜200台 | 限界として「not validated on a physical OHT system」「controller interfaces」の施設別検証が必要と自認 | 事実・原文確認（抄録）、限界の記述は要約経由 |
| Yin et al., arXiv 2608.30520, 2026 | MCS層での渋滞考慮経路スケジューリング（LightGBM＋リスク制約付き選択） | 実MCSログ51,700件 | **複数ベンダー・部分観測を明示的に前提にした唯一の確認例。ただし操作対象は経路選択のみ** | 事実・原文確認 |
| 「Heterogeneous multi-agent fleet control system for material handling in a Software-Defined Factory」J. Manufacturing Systems, 2026 https://www.sciencedirect.com/science/article/abs/pii/S0278612526000166 | 集中型、通信・自己位置推定・ナビゲーション・タスク割当を一括管理 | 縮小スケールの半導体製造フロアでOHTとAGVを協調動作 | 「among the first works to address intra-MAR heterogeneity (multi-vendor fleet of AMRs) and inter-MAR heterogeneity (OHT vehicles and floor operating AGVs) in a unified system-level framework」 | 事実・検索スニペットのみ、本文403 |
| Kang et al., AAAI 2019 https://mlanthology.org/aaai/2019/kang2019aaai-dynamic/ | 深層RLで高交通領域の経路コストを動的調整 | | 2020年以前だが動的コスト操作の原型 | 事実・要約経由 |

### 7.2 未確認

- 「内部を変更できないベンダー製コントローラ複数をブラックボックスとして扱い、その応答特性をオンライン同定したうえで境界の競合だけを調停する」研究は、今回の検索では見つからなかった。ただし網羅的な文献調査ではなく、「存在しない」とは言えない。 [未確認]
- J. Manufacturing Systems 2026論文が、ベンダーの既設fleet managerを残したまま上に載るのか、それを置き換えて車両を直接制御するのかは、抄録からは断定できない。 [未確認]

### 7.3 情報源からの推論

- 先行研究のほぼ全ては「単一のOHT系を、内部状態が見え、経路やディスパッチを自由に書き換えられる」前提で最適化している。評価もほぼシミュレーション。 [推論]
- J. Manufacturing Systems 2026論文は抄録で「localization, navigation」まで自前で管理すると述べており、ベンダーのコントローラを置き換える（あるいは車両を直接叩く）構成と読める。既設コントローラを残す本提案とは前提が逆。ただし「複数ベンダー・OHT＋AGV横断」という問題設定そのものは先に取られている。 [推論]
- arXiv 2608.30520は本提案の問題意識（複数ベンダー、部分観測、ログからの状態推定）を最も強く裏付けると同時に、「それはMCS層で解ける」という反論の根拠にもなる。 [推論]
- 未解決として主張できそうなのは、(i) 実機・実fabでの検証、(ii) ブラックボックス制御器の応答同定、(iii) 限定的な操作権限しかない状況での調停、(iv) 安全性保証。ただし(iii)は「操作権限が本当に存在するか」の確認が先。 [推論]

---

## 8. 競合・近接製品

### 8.1 確認済みの事実

| 製品・企業 | 何をするか | 他社搬送をまたぐか | 出典 | ラベル |
|---|---|---|---|---|
| Applied Materials SmartFactory Material Control（CLASS MCS 5、旧Brooks系） | ウェハ・レチクル・パネルの搬送と保管を調整するリアルタイムMCS | **「With over 250 deployments worldwide ... the market leading MCS solution」「Integrate with any AMHS solution or multiple AMHS providers without interruption」**。「advanced scheduling algorithms」で最適経路選択、「Reduce AMHS device transport times」 | https://appliedsmartfactory.com/productivity-solutions/material-control/ | 250件は原文確認。複数AMHSプロバイダの文言は要約経由＋検索スニペットで一致 |
| 村田機械 MCS / MDS | OHS, OHT, AGV, RGV, ストッカの全体制御 | 自社ページに他社機器対応の記載なし | https://www.muratec.com/cfa/products/mcs.html | 事実・要約経由 |
| Samsung SDS Nexplant AMHS（MCS含む） | 工場全体の統合制御 | 「supports standard interfaces for integration with third party controller and hardware」 | https://www.samsungsds.com/en/amhs/nexplant-amhs.html | 事実・要約経由 |
| Mirle MCS | MESから搬送コマンドを受け、搬送・保管・バッファ装置を統合スケジューリング、最適経路選択 | 記載未確認 | https://www.mirle.com.tw/en/solution-detail/214/ | 事実・検索スニペットのみ |
| DAIM Research OMS / xMS（KAISTスピンオフ） | RL（Q-routing）でOHT 1,000台超の割当と経路誘導。xMSは「brand-agnostic」でOHT, AGV, AMRに適用可能と主張。顧客にPOSCO DX、Samsung Electronics、LG Energy Solution、SK On。MX RoboticsとOHT市場でMOU | 主張上はまたぐ。既設他社コントローラの上に載るのか置き換えるのかは記事から不明 | https://www.informs-sim.org/wsc22papers/337.pdf , https://www.venturesquare.net/en/1094912/ , https://www.automateshow.com/prior-exhibitors/daim-technology | WSC: 原文確認 / 他: 要約経由・スニペット |
| Applied Materials RTD / AutoSched | ロットのリアルタイム・ディスパッチ、スケジューリング | 搬送ではなく「どのロットをどの装置へ」の層 | https://appliedsmartfactory.com/semiconductor/productivity-solutions/rtd/ | 事実・検索スニペットのみ |
| camLine（Elisa IndustrIQ傘下） | LineWorks MES、Line Controller。「Integrates natively with MES, AMHS, and SPC」 | AMHSとは連携する側。製品群（RACE Suite）にMaterial Control Systemの名が挙がるが範囲は不明 | https://www.elisaindustriq.com/camline/industries/semiconductor-backend | 事実・要約経由。**チームはcamLineにインタビュー済みなので、MCS相当機能の範囲は直接確認するのが早い** |
| Critical Manufacturing MES | Material Logisticsモジュール（資材要求、補充、ロケーション間移動） | 搬送車の交通制御ではない | https://www.criticalmanufacturing.com/industries/semiconductor-manufacturing/ | 事実・検索スニペットのみ |
| Fabmatics（HERO Fab AGV、HERO Scout AMR、ストッカ、Fleet Manager） | レガシーfab向けの搬送・ハンドリング一式。既存MESとSECS/GEM、HSMSで統合する「software framework」、自社Fleet Manager | 自社機器の統合が中心。他社搬送との横断調停の記載は見当たらない | https://www.fabmatics.com/lp/automating-legacy-fabs/ | 事実・原文確認 |
| ダイフク × Gyro Systems / Youibot | OHTとAMRの自動ドッキング連携（後工程向け） | ダイフクが主導して協力企業のAMRを自社系に組み込む形 | MONOist 2025-12-24 | 事実・要約経由 |
| TSMC特許 US7684888B2 | MES拡張で複数MCS・複数AMHS（異ベンダー）間の搬送を統合制御 | またぐ（搬送要求の粒度で） | Google Patents | 事実・要約経由 |
| VDA 5050（物流側の標準） | 上位制御とAGV/AMR間の通信インタフェース標準。注文の渡し方、状態報告、位置データ | 通信は統一するが、業界ブログは「Traffic arbitration ... is still largely vendor-specific under the hood」「not every vendor's native fleet manager is willing to fully cede that authority to an external master controller」と指摘 | https://www.mesengineer.com/2026/08/08/vda-5050-is-everywhere-in-amr-rfps-now-heres-what-it-actually-federates/ | **事実・検索スニペットのみ（本文502）。個人ブログ級の二次情報で、申請書の根拠には弱い** |
| マルチフリート・オーケストレーション（物流） | Interact Analysisが新興セグメントとして定義。倉庫ソフト市場全体より高成長と予測。Kinexon、SYNAOS等がベンダー非依存のfleet managementを提供 | またぐ（物流側では既に製品カテゴリが存在） | https://interactanalysis.com/insight/amr-multi-fleet-orchestration-software/ | 事実・検索スニペットのみ |

### 8.2 未確認

- レクザム（Rexxam）のfab向けAMRと上位統合方法: 日本語・英語とも検索でヒットせず。 [未確認]
- 村田機械・ダイフクのMCSが他社製OHT/ストッカを実際に制御した事例の有無。 [未確認]（ムラタシステムに直接聞くべき）
- Applied Material Controlが車両単位の交通制御に介入するか。公開ページの表現は搬送コマンド・経路選択の粒度に留まる。 [未確認]

### 8.3 情報源からの推論

- 「他社の既設搬送をまたぐ調整」は、搬送コマンドの粒度では既にMCSという製品カテゴリで行われており、250件超の導入実績を持つ既存プレイヤーがいる。ここを新規性として主張すると崩れる。 [推論]
- 公開情報の範囲で空いているように見えるのは、(a) MCSより下・各社コントローラより上の「境界での局所的な順序調停」、(b) ブラックボックス応答のオンライン同定、の2点。ただし(a)が空いているのは、技術的に未解決だからではなく、各社コントローラが外部にその操作権限を開けていないから、という可能性がある。 [推論]
- 物流倉庫側はVDA 5050とマルチフリート・オーケストレーション製品が既に存在し、半導体より競合が多い。一方で「交通調停はベンダー依存のまま」という指摘（二次情報）が正しければ、提案の核はむしろ物流側で素直に刺さる。 [推論]

---

## 9. この提案が半導体fabで成立しない可能性（正直な評価）

以下は情報源からの推論であり、事実ではない。ただし各項目の根拠となる事実は上の章に示した。

### リスク1: 「ベンダー横断レイヤ」は既に存在し、強い既存プレイヤーがいる（重大）
MCSがまさにその層で、Applied Materialsは250件超の導入と「any AMHS solution or multiple AMHS providers」を公言している。Samsung SDSも第三者コントローラとの標準インタフェース統合を謳う。TSMCは2007年に異ベンダーAMHS間搬送の特許を出願している。さらに2026年8月には、実MCSログで「複数ベンダー・部分観測」を前提にした学習型経路スケジューリングの論文が出ている。審査員や業界人から「それはMCSの仕事では」と言われたとき、搬送コマンド粒度の話をしている限り反論できない。

### リスク2: 操作権限が無い可能性（最大のリスク）
提案は「限定された命令への応答」を前提にするが、SEMI E82が上位に公開するのは搬送コマンド単位の操作（搬送指示、取消、中断等と推定。規格本文未確認）で、特定の車両を合流手前で待たせるような車両単位の操作は、公開要旨を見る限り規格の対象外。交通管理は「追加作業が必要」とされたまま各社コントローラの内部にある。そして300mm前工程のOHT軌道網は、確認できた範囲では単一ベンダーで完結しており、合流・交差の調停はそのベンダーのコントローラが既にやっている。つまり、半導体fabで「複数ベンダーにまたがる合流・交差」という競合箇所がそもそも存在しない可能性がある。存在するのは受け渡し点（ストッカ口、リフタ、ロードポート、OHT⇔AMRドッキング）で、そこはE84のハンドシェイクとMCSの経路選択が既にカバーしている。
→ ムラタシステムへの確認事項: (1) 上位から出せるコマンドの実際の一覧、(2) 他社機器との境界で実際に起きている待ち・詰まりの具体例、(3) その境界の制御を外部ソフトに渡す余地があるか。

### リスク3: 改善幅が小さく、導入コストに見合わない可能性
公開されている経路制御単独の改善幅はシミュレーションで数%（0.8〜8.8%、2.1〜4.5%）。混雑していない条件では静的最短経路が最良という結果すらある。提案は内部を変えられない分、これらの研究より操作の自由度が低いので、上積みはさらに小さいと見るのが自然。一方でディスパッチ層は10〜30%帯の改善が報告されており、fabが投資するならそちらが先になる。

### リスク4: fabは外部ソフトを搬送制御ループに入れない
搬送の誤動作はFOUP落下・衝突・ライン停止に直結し、1ロットの価値が高い。SEMI E187/E188はAMHSを含むfab装置にサイバーセキュリティ要件と導入前スキャンを課している。fab内ネットワークは外部から隔離されているのが通例で、スタートアップのソフトが既設AMHSの制御ループに入るには、AMHSベンダーの保証範囲、fabのIT審査、長い認定期間を越える必要がある。学術側ですら実機検証に到達していない（arXiv 2608.30512は「not validated on a physical OHT system」と自認、2608.30520は「staged, monitored rollout」を推奨）。未踏の期間内に実fabで動かすのは現実的でない可能性が高い。

### リスク5: ベンダーロックインは「課題」ではなく「ビジネスモデル」
ダイフクと村田機械にとって、自社MCSと自社搬送機の一体提供は収益の源泉。他社の上位ランタイムに位置履歴と操作口を開く動機が無い。ダイフクの後工程戦略も、協力企業のAMRを自社系に取り込む方向（Gyro Systems、Youibot）で、中立レイヤを歓迎する動きではない。村田機械グループにインタビューできていること自体は強みだが、協力が得られるかは別問題。

### リスク6: 安全とクリーン度
調停によって車両の停止・再加速が増えれば、振動とパーティクル発生、ウェハへのストレスが増える方向に働く。Q-time（工程間の時間制約）違反は歩留まりに直結するため、「局所最適の調停が別の場所でQ-time違反を生む」ことを否定できなければ採用されない。衝突防止などの安全機能は各社コントローラ側に残るとしても、上位からの介入がその安全ロジックとどう干渉するかを検証する手段（実機またはベンダー提供のエミュレータ）が無い。

### リスク7: 国内投資の追い風が提案の顧客に直結しない
Rapidus、JASM第2、Micron広島新棟はいずれも新設で、AMHSは単一ベンダー一括導入が自然。brownfieldの痛みを持つのは既存の200mm/後工程だが、そこの市場規模・自動化率・支払い意思を示す一次データは今回取得できなかった。

### それでも成立しうる道筋（推論）
- 入り口を300mm前工程のOHTではなく、**後工程・200mm・OHT＋AMR混在領域**に置く。ここは標準化自体が進行中（SATAS、2028年目標）で、単一ベンダー支配が無く、床上AMRは物流系の操作口（VDA 5050等）を持つ可能性がある。
- 最初は制御ループに入らず、**位置履歴とイベントログから各社システムの応答特性と境界での待ちを同定・可視化する診断ツール**として入る。これなら操作権限もfabの安全審査も要らず、arXiv 2608.30520が示した「内部キューは部分的にしか報告されず、ログから推定するしかない」という実需に直接応える。調停は、診断で詰まりの所在と大きさが示せた後の第二段階にする。
- 評価指標を平均搬送時間ではなく、**テール遅延とQ-timeリスク**に置く。
- 「物流倉庫が展開先」ではなく、物流を同格の第一市場として扱う選択肢も検討に値する。操作口の開放度は物流のほうが高い。

---

## 10. 追加で確認すべき事項（優先順）

1. ムラタシステム: E82/E88経由で上位が出せるコマンドの実際、他社機器との境界で起きている詰まりの実例、外部ソフトに境界制御を渡す余地。
2. camLine: 顧客fabで複数ベンダーAMHSが混在する頻度と形態（棟別か、装置種別か、同一軌道か）。RACE SuiteのMCS機能の範囲。
3. Bartlett et al. 2014（5%改善）と IEEE 2005（搬送時間4.4%短縮）の原文確認。
4. 経産省PDF（第8回次世代半導体等小委員会 資料3）でRapidus累計額を確認。
5. J. Manufacturing Systems 2026（DAIM/KAIST系と推定される異種フリート制御論文）の本文入手。既設fleet managerを残す構成か否か。
6. SEMI 200mm Fab Outlook の原文（2023-09プレスリリース以降の更新版があるか）。

---

## 11. 追補（2026-09-21）：増車では渋滞が解けないというメーカー側の記述

### 確認済みの事実

- 吉田正義（アシストテクノロジーズジャパン（株））「半導体工場向け搬送装置におけるシミュレーションを用いた経路探索」日本機械学会誌 2007年12月 Vol.110 No.1069, p.958。 https://www.jsme.or.jp/publish/kaisi/071204t.pdf [事実・原文確認（PDFから本文抽出）]
  - 「2007年現在…搬送量に応じてOHTを数十台〜300台程度投入している．今後はより高い搬送能力を求められ，500台以上のOHTビークルを投入する必要があると考えられる．」
  - 「大量のビークルを投入すると，特定箇所で慢性的な渋滞が発生したり，断続的に渋滞が発生したりして，ビークルの増車だけでは搬送能力を向上させることが難しく，過度の増車は逆に搬送能力を低下させてしまうケースもある．」「OHTシステムの渋滞は重要な課題であり」
  - 対策は他車との干渉を考慮した経路探索（全ビークルの動きをシミュレーションしながら経路を決定）。600台程度、散発的に渋滞するレイアウトの搬送シミュレータで、最大搬送量が従来手法（最短経路）比で15%程度増加。計算時間20〜30ms。実機ではなくシミュレーション。
- Koo et al., IJPR 2026 の要旨（検索スニペット）: 「In large-scale FAB environments characterised by dense track networks, frequent congestion often leads to bottlenecks, decreasing overall productivity」「traditional static routing approaches for each OHT fail to effectively manage real-time congestion」。 https://www.tandfonline.com/doi/abs/10.1080/00207543.2026.2656773 [事実・検索スニペットのみ]

### 情報源からの推論

- 著者は搬送メーカー側の技術者であり、渋滞が約20年前から現場側で認識された課題であること、かつ「台車を買い足す」では解けないことの裏づけになる。
- 一方で、対策は車両の経路制御（短距離〜中距離の下半分）であり、メーカー自身が長年取り組んでいる領域である。外部の第三者が入れるのは、搬送需要の出し方（投入タイミング、中継先の選択、集中の平準化）という上位側に限られる、という整理は変わらない。
- アシストテクノロジーズジャパンはその後、村田機械に買収されたと記憶しているが未確認。 [未確認]

---

## 12. 追補（2026-09-21）：DAIM Research（韓国、KAIST発）の詳細

### 確認済みの事実

- 設立と体制: 2020年2月5日、KAIST 産業及びシステム工学科のJang Young Jae（張榮宰）教授と教え子4名が設立。従業員50名強（修士・博士10名以上）。 https://zdnet.co.kr/view/?no=20250903084245 （2025-09-03、要約経由）、検索要約
- 資金: 初期にNaver D2SF等、2022年シリーズA 100億ウォン、シリーズB 約200億ウォンの調達を開始。売上は「前年比8倍を見込む」「上半期で前年通年の5倍」。金額は非開示。（同上）
- 導入: 「現在50工場にソフトウェアを供給、うち90%が大企業」。業種は半導体、二次電池、自動車。プロジェクト実績としてSamsung Electronics、POSCO DX、LG Energy Solution、SK On。（同上、venturesquare）
- 製品: OHT Management System（OMS）。Q-routing（強化学習）で車両の搬送ジョブへの割当と、渋滞を避ける動的な経路誘導を行い、1,000台超を運用。検証用のデジタルツイン（OMS-DT: 車両エミュレータ、OMS接続部、仮想工場）。後継のxMSは「brand-agnostic」でOHT・AGV・AMRに適用可能と主張。Hong et al., WSC 2022 Industry Case https://www.informs-sim.org/wsc22papers/337.pdf [原文確認]
- 開発の経緯: 「KAISTのチーム、DAIM Research、半導体業界の産業パートナーが協働してOMSを開発し商用化した」（WSC 2022、原文）。検索要約では、Jang研究室が半導体自動化企業と研究センターを設立し1,000台超の搬送システムを開発、とある（企業名は検索要約のみで未確認）。
- 2025年、OHTハードウェアのMX RoboticsとMOU。ハードはMX、AI制御はDAIM。狙いは半導体の工程物流（HBM等の先端パッケージング）。市場は「日本などの少数のグローバル企業が支配してきた」。 https://www.venturesquare.net/en/1094912/ [要約経由]
- 価格の参考: 同種の外国製ソフトは「2億ウォンを超える」（ZDNet Korea、文脈は中小企業向け無償配布構想の説明）。
- 元論文: Hwang & Jang, IJPR 58(4), 2020（Q(λ)学習による動的経路誘導）、Hong, Hwang & Jang, IEEE Trans. Semiconductor Manufacturing, 2022（Q学習ベースの経路誘導と車両割当。被引用19）。後者の要旨（OpenAlex経由で全文取得）は、数百台規模、従来の割当方式との比較、実用的な大規模設定で十分高速、と述べるが、改善率の数値は要旨に無い。

### 未確認

- 実工場での改善の数値（搬送時間、台数削減、稼働率等）。WSC 2022、ZDNet Korea、ロボット新聞、KAISTニュース、論文要旨のいずれにも数値は無かった。論文本文（IJPR 2020、IEEE TSM 2022）は有料で未読。
- 同社のソフトが既設メーカーのコントローラを置き換えるのか、上に載るのか。

### 情報源からの推論

- 同社が前面に出す価値は「何%速い」ではなく、(a) 1,000台超を渋滞で破綻させずに運用できること、(b) 実機につなぐ前にデジタルツインで検証でき導入工程が短くなること、(c) 日本メーカー支配の市場での国産化、の3つである。
- 手法は車両ごとに自分の到着時間を最小化するQ-routing系である。2026年8月のarXiv 2608.30512は、表形式Q-routingの弱点（行き先・ノード・行動ごとに独立に学習し情報共有が弱い、立ち上がりが不安定）を指摘し、ニューラル化しても平均完了時間の改善は0.8〜8.8%、100台規模ではDijkstraが最良と報告している。
- 各車両が自分の時間を最小化する経路選択は、交通工学でいう利用者均衡に収束し、全体最適とは一致しない（混雑ゲームにおける均衡と社会的最適の乖離）。この差を、限界費用に相当する項を報酬に入れて埋めるという方向は、ゲーム理論を道具でなく核として使える候補である。【チームの仮説。白石氏の検証が必要】

### 12-2. 追補（2026-09-21 夜）：DAIM／KAISTの実導入の数値を確認

- Jang, Kim（KAIST）, Hong（DAIM Research）「Digital Twin for Virtual Learning - Industry Case」, 14th Conference on Stochastic Models of Manufacturing and Service Operations（SMMSO 2024）。 https://www.smmso2024.it/papers/23.pdf [事実・原文確認（PDFから本文抽出、全3ページ）]
  - 導入先は「a Korean memory chip manufacturer」。1,000台のOHTを運用する映像つき。
  - 「The implementation of the RL and DT-VL solution markedly improved robot efficiency with delivery times and capacity improving by 32% and 20%, respectively. This efficiency allowed the factory to reduce its robot fleet to 800, saving USD 16 million based on the cost of each robot.」
  - 要旨: 「enabling the facility to operate efficiently with fewer robots and achieve substantial cost savings」
  - 手法の記述: ノードごとにQ関数（ノード間の推定移動時間）を持ち、行き先dに向かうロボットはノードiで Q_i(d,j) と Q_i(d,k) を比べ、推定移動時間が短い方の辺を選ぶ。割当も、空き車両のうち min_k Q_i(d,k) が最小のものを選ぶ。
  - デジタルツイン（DT-VL）の必要性: 「Factories are dynamic entities... As machines are upgraded and new products launched, both the factory layout and the flow of parts change, requiring robots' paths to be adjusted.」レイアウト変更のたびに、仮想環境でQテーブルを先に学習し直してから実機へ反映する。
- 情報源からの推論:
  - 200台の削減で1,600万ドルなので、OHT1台あたり約8万ドルという単価が逆算できる。【推論。論文は単価を明示していない】
  - 比較対象（何に対して32%か）、測定期間、実測かシミュレーションかの別は本文に明記がない。「deployment demonstrated」とあるが、3ページの産業事例報告であり査読の程度は不明。ベンダー側の自己申告として扱う。
  - 経路選択は各ロボットが自分の推定移動時間を最小化する形であり、他車への影響を明示的に扱う記述はない。表形式のQテーブルは行き先×ノード×辺ごとに値を持つため、レイアウトが変わるたびに学習し直しが要る（だからデジタルツインが製品の中核になっている）。
