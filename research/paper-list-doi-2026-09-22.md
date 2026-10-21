# 必要論文のDOI一覧

- 作成: 2026-09-22。DOIはCrossref APIで確認（「未取得」はCrossref検索で見つからなかったもの）
- 区分: ★必読（手法の本体）／◎差別化の相手／○背景・数値の出典／△補助

| 区分 | 著者・年 | 題名 | 誌名 | DOI／URL | 入手 | 用途 |
|---|---|---|---|---|---|---|
| ★ | Hwang & Jang, 2020 | Q(λ) learning-based dynamic route guidance algorithm for overhead hoist transport systems in semiconductor fabs | Int. J. Production Research 58(4), 1199–1221 | https://doi.org/10.1080/00207543.2019.1614692 | **オープンアクセス**。読了、読解メモあり | DAIMの手法の本体。B4, B5, B6a, B6b, B6c |
| ★ | Hong, Hwang & Jang, 2022 | Practical Q-Learning-Based Route-Guidance and Vehicle Assignment for OHT Systems in Semiconductor Fabs | IEEE Trans. Semiconductor Manufacturing 35(3), 385–396 | https://doi.org/10.1109/TSM.2022.3168702 | 有料。東大アカウント | 割当を加えた版。報酬・更新式に外部性が入っていないかの確認 |
| ★ | Hwang, Cho, Hong, Lee, Kim & Jang, 2020 | Q-learning-based route-guidance and vehicle assignment for OHT systems in semiconductor fabs | SEMI ASMC 2020（6ページ） | https://doi.org/10.1109/ASMC49169.2020.9185357 | 有料（IEEE）。**小幡が取得、読了**。読解メモ5章 | TSM 2022の会議版。割当の仕組みと著者の限界を確認済み。TSM版は必須でなくなった |
| ○ | Hong, Hwang, Hwang & Jang, 2022 | Industry Case: Semiconductor Fab OHT Management System and Digital Twin for OHT Operation | Winter Simulation Conference 2022 | 未取得（IEEE Xplore）。PDF: https://www.informs-sim.org/wsc22papers/337.pdf | 無料 | 商用化、1,000台超、デジタルツイン。N1 |
| ○ | Jang, Kim & Hong, 2024 | Digital Twin for Virtual Learning – Industry Case | SMMSO 2024（3ページ） | DOIなし。PDF: https://www.smmso2024.it/papers/23.pdf | 無料。読了 | 実導入の数値（1,000→800台、1,600万ドル）。B5 |
| ○ | Japhne & Jang, 2024 | Digital Twin Based Dynamic Routing for Overhead Hoist Transport Systems in Semiconductor Fab | Winter Simulation Conference 2024（2ページ） | 未取得。PDF: https://informs-sim.org/wsc24papers/cea151.pdf | 無料。読了 | レイアウト変更時の再学習をデジタルツインで先回り。B6b |
| ◎ | Koo, Kim, Choi, Jun & Shin, 2026 | Alleviation of OHT vehicle congestion in semiconductor FAB with dynamic link weight control: A reinforcement learning approach | Int. J. Production Research | https://doi.org/10.1080/00207543.2026.2656773 | 有料。東大アカウント | 区間の重みを強化学習で動かす。最も近い先行。C3, U5 |
| ◎ | Gu et al., 2026 | Trajectory-Initialized Neural Double Q-Routing for Large-Scale Overhead Hoist Transport Systems | arXiv 2608.30512 | https://doi.org/10.48550/arXiv.2608.30512 | 無料。読了 | 表形式Q-routingの弱点、改善0.8〜8.8%。L5 |
| ◎ | Yin et al., 2026 | （MCS層の渋滞考慮経路スケジューリング。実MCSログ51,700件） | arXiv 2608.30520 | https://doi.org/10.48550/arXiv.2608.30520 | 無料。読了 | MCS層での代替案。平均−16.4%、スループット不変 |
| ◎ | Kang et al., 2019 | Dynamic Vehicle Traffic Control Using Deep Reinforcement Learning in Automated Material Handling System | AAAI 2019 | https://doi.org/10.1609/aaai.v33i01.33019949 | 無料（AAAI） | 経路コストを深層RLで動的調整。Kooの原型 |
| ○ | Bartlett et al., 2014 | Congestion-aware dynamic routing in automated material handling systems | Computers & Industrial Engineering 70 | https://doi.org/10.1016/j.cie.2014.02.002 | 有料 | IJPR 2020のベンチマーク（PU/IU）。「5%改善」の原文確認用 |
| ○ | Ahn, Lee, Yeon & Park, 2022 | Congestion-aware dynamic routing for an overhead hoist transporter system using a graph convolutional gated recurrent unit | IISE Transactions 54(8) | https://doi.org/10.1080/24725854.2021.2000680 | 有料 | KAIST以外（KAIST Park研）の渋滞予測→経路。競合の網羅性 |
| ○ | 2025 | Multiagent reinforcement learning-based dispatching model for overhead hoist transfer in automated material handling system | Computers & Industrial Engineering | https://doi.org/10.1016/j.cie.2025.111109 | 有料 | MARLの割当。「MARLは少ない」と書くなら反例として押さえる |
| ○ | 吉田正義, 2007 | 半導体工場向け搬送装置におけるシミュレーションを用いた経路探索 | 日本機械学会誌 110(1069), p.958 | DOIなし。PDF: https://www.jsme.or.jp/publish/kaisi/071204t.pdf | 無料。読了 | 「過度の増車は逆に搬送能力を低下させる」。B4 |
| △ | Lee & Jang, 2022 | The Graph Neural Network–Based Dynamic Routing ... | ISMI 2022 | DOIなし。PDF: https://www.conf.tw/site/userdata/1449/ISMI_paper/ISMI2022_paper_5130.pdf | 無料 | 「数千台」「デッドロック」の引用元。B1 |
| △ | Choi et al., 2024 | Visualization system to identify structurally vulnerable links in OHT railway network in semiconductor FAB using betweenness centrality | PLOS ONE | https://doi.org/10.1371/journal.pone.0307059 | 無料 | 「1日平均20km走行」「渋滞とデッドロックで生産性低下」 |
| △ | Bang, Kim & Kim, 2023 | （グリッド型AGVの経路とディスパッチ） | Int. J. Industrial Engineering 30(2) | 未取得。PDF: https://ijietap.com/index.php/ijie/article/download/8657/1345/49887 | 無料 | 「ディスパッチの方が効く」という反論への備え |

## 読む優先順位（小幡のChromeで開く順）

1. IJPR 2026 Koo et al.（DOI 10.1080/00207543.2026.2656773）: 重みをどう決めているか、報酬は何か、比較対象と改善率。**残る唯一の必須**
2. IEEE TSM 2022（DOI 10.1109/TSM.2022.3168702）: 会議版で割当を確認済みなので、時間があれば
3. Bartlett 2014: 「5%」の条件（申請書に数値を使うなら）

小幡は本文を読まない（9/22決定）。取得したPDFをDownloadsに置けば、Claudeが読んで要点を渡す

## 注意

- WSC 2022とWSC 2024はIEEE Xploreに収録されているはずだが、Crossref検索では該当しなかった。引用するときはinforms-simのPDFのURLで足りる
- IIJPR 2020のCrossrefの発行年は2019（オンライン公開）。誌面は58(4), 2020
