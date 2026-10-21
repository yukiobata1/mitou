# 読解メモ: Hwang & Jang, IJPR 58(4), 2020（DAIMの手法の元論文）

- 読んだ日: 2026-09-22（Claudeが本文を読んだ。**オープンアクセス**で、Taylor & Francisのページに「Open access」表示あり。購読契約の制約は受けない）
- 書誌: Illhoe Hwang, Young Jae Jang, "Q(λ) learning-based dynamic route guidance algorithm for overhead hoist transport systems in semiconductor fabs", International Journal of Production Research 58(4), pp.1199–1221, 2020. https://doi.org/10.1080/00207543.2019.1614692
- 手法名: QLBWR(λ)（論文中の表記は QLWBR(λ) と揺れている）
- 動画: https://www.youtube.com/watch?v=r-WUwqYMD-M （シミュレーションのアニメーション）
- 記法: 「原文」= 論文の記述 / 「読み」= こちらの解釈

## 1. 手法の構造（原文）

- **エージェントは車両ではなくノード**（分岐点）。「Instead of modelling each vehicle as an agent, we model the node points at which the vehicles make routing decisions as agents」。著者自身が「single agent reinforcement learning with multiple decision points」と分類。車両ごとのマルチエージェントは学習時間が膨大で5〜10台にしか使えない、として退けている（3.3節）
- **Q値の定義**: Q[(d,i),j] = 行き先dの車両がノードiでノードjを選んだときの、dまでの推定総移動時間
- **報酬**: R[(d,i),j] = t(i,j) + ρ·F[(d,i),j]
  - t(i,j) = その車両が辺(i,j)を通過するのに実際にかかった時間
  - F = γφ(d,j) − φ(d,i)。φは無交通時の決定論的最短移動時間（ポテンシャルにもとづく報酬整形。Ng, Harada, Russell 1999により最適方策を変えない）
- **更新**: Q(λ)学習（多段TD誤差＋適格度トレース）。式(2)〜(5)
- **方策**: Boltzmann softmax。Q値の差が小さいときは意図的にばらけさせる。貪欲方策だと「渋滞は消えずに振動する」と明記（4.3節）
- **初期化**: 無交通時の辺通過時間で価値反復
- **割当**: 最も近い待機車を割り当てる（nearest-first）。学習の対象外
- 計算量は車両数に依存せず、ノード数だけで決まる
- ノード同士は直接通信しない。直接通信を小規模で試したが、学習時間と安定性が悪化したので不採用（結論）

## 2. 数値結果（原文）

### ケースI（文献のレイアウト、20ポート、37〜43台）

- 生産量 10,000 / 10,500 / 11,000 / 11,500 枚/週 に対して 37 / 39 / 41 / 43台。11手法を比較、各20回反復
- 10,500以下では静的経路（NU）を含む全手法が同程度。11,000で従来法（NU, PU(10), PU(60), IU）がRL系に劣り、**11,500で安定を保ったのはQLBWR(λ)だけ**
- ε-greedy系は全条件で悪い。「渋滞が移動するだけで消えない」

### ケースII（実工場データ、160m×80m、装置群325、STB 112、ストッカ9、最大170台）— 表8

| 搬送要求（件/日） | 静的経路: 必要台数 | 静的: 平均配送時間 | QLBWR(λ): 必要台数 | QLBWR(λ): 平均配送時間 |
|---|---|---|---|---|
| 88,056 | 130 | 80.56 | 120 | 85.58 |
| 94,344 | 150 | 82.79 | 140 | 80.59 |
| 100,632 | 不可 | 不可 | 160 | 82.93 |
| 106,920 | 不可 | 不可 | 170 | 105.14 |

- 原文: 「the minimum required number of OHTs is smaller when the proposed QLWBR(λ) algorithm is applied ... the same service level can be achieved with a smaller number of OHTs」
- 原文: 「when the lot movement volume increases above 100,000/day, the conventional method cannot satisfy all of the transportation requests, even with a high number of OHTs. The conventional method cannot add more OHTs to the tracks, because it fails to resolve increased traffic congestion」
- 単位は本文に明記なし（秒と読むのが自然。要確認）

## 3. 著者自身が挙げる限界（原文、結論）

1. 割当は最近接ルールのまま。割当と経路の統合は将来課題（→ Hong et al., IEEE TSM 2022で扱われた）
2. ホットロット（優先度）を扱っていない
3. **レール区間の収容台数制限を扱っていない**。非接触給電のため区間あたりの台数に上限があり、実際にはこれで停止・遅延が起きる
4. α, λ, γ は文献の標準値を使い、探索していない

## 4. 申請書の主張への含意（読み）

- **B4（増車は効かない）の裏付けが査読論文で得られた。** 表8の10万件/日以上の行: 静的経路は台数を増やしても要求を満たせない。2007年のJSME記事と合わせて2出典になる
- **B5（台数削減）の裏付けが査読論文で得られた。** 同じ搬送量を130→120台、150→140台（7〜8%減）でこなした。SMMSO 2024の「1,000→800台（20%）」は実導入の自己申告なので、申請書では「論文のシミュレーションで7〜8%、実導入の報告で20%」と両方を出典つきで書ける
- **B6a（各車両の自分の時間だけを縮める）は原文で確認できた。ただし言い方を直す。** エージェントは車両ではなくノードなので「利己的な車両」は誤り。正しくは: 「Q値はその車両自身の残り移動時間の推定であり、その車両が他の車両に与える遅れ（外部性）は報酬にも更新式にも入っていない。渋滞の回避はBoltzmann方策のランダム化で間接的に得ているだけで、著者も貪欲方策では渋滞が振動すると述べている」。→ 差別化Aの「他の車に与える影響を値付けする」は、原文の構造に対して正面から立つ
- **B6b（表形式で再学習）も原文で確認。** Q[(d,i),j]の表で持ち、レイアウト変更時の再学習をWSC 2024（Japhne & Jang）がデジタルツインで先回りする構成にしている
- 著者の限界3（区間の収容制限）は、混雑ゲームで扱う「容量」そのもの。差別化Aの入口として使える
- 注意: 表8で台数が減った行では平均配送時間が長くなっている（88,056の行: 80.56→85.58）。「台数を減らすと配送時間は少し延びる」というトレードオフを、目標G2の指標定義に織り込むこと（同じ配送時間で台数何%減、と条件を固定する）

## 5. 割当を加えた版: Hwang, Cho, Hong, Lee, Kim & Jang, SEMI ASMC 2020（小幡が東大アカウントで取得、6ページ）

- DOI: 10.1109/ASMC49169.2020.9185357。IEEE TSM 2022 "Practical Q-Learning-Based..." の会議版。TSM版は未読
- 構造: 原文「We take a node-based control approach where each node point is an agent」。報酬と更新式は「More details ... are provided in [6]」（[6] = IJPR 2020）。同じ
- **割当**: 原文「The Q-learning-based vehicle assignment algorithm allocates each job (vehicle) to the vehicle (job) with the closest Q value」。つまり割当も、その車両の推定到着時間が最小の車両を選ぶだけ。他の車両への影響は入っていない
- **著者自身の限界**（結論）: 「Our state definition of Q-learning does not include additional traffic information such as the positions of other vehicles and the tasks they are performing. Therefore, our next step will be to incorporate traffic information into the current state definition」→ B6aを著者が認めている
- **B4の出典**（要旨）: 「The algorithm most commonly used in industry, a mathematical optimization-based algorithm that constantly seeks the shortest routes, has been proven ineffective in dealing with fabs operating around 1,000 vehicles or more」
- 数値: 24ベイ、250台、160m×80m、装置群325、STB 112、ストッカ9。生産量4水準（124,170 / 130,968 / 140,037 / 151,764 件/日）、各5反復。最高負荷では最短経路型（Dijkstra + STDF割当）が要求をさばけず、提案手法（QQ）はさばいた。配送時間の差は負荷とともに拡大。改善率の数値は図のみで本文に無い
- 工場の物流容量の目安（原文）: 「When the average delivery time was over 160 s and the average utilization of vehicles was over 85–90%, the fabs could not transport requests on time」→ 予備実験の指標の目安に使える
- レイアウト頑健性: 6ベイ模型で近道を22→12本に減らしても、提案手法の平均配送時間の標準偏差は0.696（Dijkstraは3.961）。高速道路0本のQ学習が高速道路6本のDijkstraより良い
- 計算時間: Dijkstraより大幅に低い（図8）

## 6. 未読・未確認

- 表6（ケースIの各手法の数値）は未取得。必要なら同じ手順（showPopup, id=T0006）で取れる
- IEEE TSM 35(3), 2022（会議版の拡張）は未読。会議版で割当の仕組みが確認できたので、必須ではない
