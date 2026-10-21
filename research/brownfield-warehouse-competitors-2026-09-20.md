# 既設マルチベンダー倉庫フリート調停ランタイム: 競合と差別化の調査

- 調査日: 2026-09-20（以下のURLはすべて同日に WebSearch / WebFetch で確認）
- 用途: 未踏アドバンスト（2026年度下期）申請書「競合と差別化」節の根拠資料
- 表記規則
  - **[確]** = 一次情報（公式サイト・公式文書・公的文書）で記述を確認した事実
  - **[確・二次]** = 報道・プレスリリース転載など二次情報で確認した事実
  - **[推]** = 情報源からの推論（情報源に明記はない）
  - **[未確認]** = 調べたが確認できなかった。推測で埋めていない
- 注意: WebFetch は取得ページを小型モデルで要約して返すため、引用句は「要約モデルが原文として返した文言」である。申請書に直接引用する箇所は、提出前に該当URLを目視で再確認すること。

---

## 0. 申請書転記用の比較表

凡例: ○ = 公式に謳っている / △ = 条件付き・部分的 / × = 公式文書上は対象外 / ？ = 未確認。各セルの根拠区分を [確][推][未確認] で付す。

| 比較対象 | 既設 black-box 機への対応 | ベンダー側実装の要否 | ベンダー横断の交通調停 | 応答特性のオンライン同定 | 導入形態 |
|---|---|---|---|---|---|
| **VDA 5050 (v3.0.0)**（規格） | × 規格は車両とマスタ制御の両端実装が前提 [確]。非対応の既設機の扱いは規格・プレスリリースに記載なし [確] | **要**（車両側とマスタ側の両方）[確] | 規格自体は通信IF。調停は単一マスタ制御が担う前提 [確] | × 記載なし [確]。factsheetで能力を「申告」する方式 [確] | 単一マスタ制御への集約（既設FMの置換または車両のVDA化）[推] |
| **SYNAOS IMP** | △ 手動フォークリフトの位置取得・統合は謳う [確]。非VDAのAGVはVDA化改修の事例（Götting、4週間）[確] | **要**（VDA 5050 native。改修は車両側ベンダーと共同）[確] | ○ 統合交通管理を謳う（VDA 5050で6〜7社の車両を単一制御）[確] | ？ 記載を確認できず [未確認] | 中央プラットフォーム（SaaS）が単一マスタになる [確] |
| **KINEXON Fleet Manager** | ？ 非VDA既設機の扱いは公式記事に記載なし [確]。「API経由の統合」に言及 [確] | **要**（VDA 5050 または API）[確] | ○ 中央集権の交通管理を謳う [確] | ？ [未確認] | 単一の中央フリートマネージャ [確] |
| **NAiSE Fleet Manager** | △ 「legacy systems and manual vehicles」対応を謳うが技術要件は非開示 [確] | **要**（VDA 5050 / MassRobotics / API / 直接IF のいずれか）[確] | ○ 手動車両も含む全交通参加者の統合を謳う [確] | ？ [未確認] | 中央フリートマネージャ + 導入コンサル [確] |
| **Meili FMS** | × ロボット（または中央ROSノード）にエージェントを入れるか VDA 5050 [確・検索要約] | **要**（VDA 5050 実装 or エージェント導入）[確・検索要約] | ○ 交差点調停・低優先度機への startPause/stopPause 送信 [確] | × 記載なし [確]（当該ページの範囲）| 汎用FMS（単一FMSに集約）[確] |
| **InOrbit Space Intelligence / OpenRobOps** | △ 「個別ベンダーシステムの上に載る」「30以上のブランドに接続」と謳う [確・二次]。ただし接続は Agent / Edge / VDA 5050 / MassRobotics / Open-RMF / コネクタ [確] | **要**（コネクタまたは標準IF。ベンダーFMのAPI利用可否は機種依存）[推] | ○ 異種フリート間の traffic management と task deconfliction を謳う [確・二次]。Open-RMF 経由の場合は Full Control アダプタ [確・検索要約] | ？ 「AI-driven analytics でボトルネック特定」はあるが、命令応答の遅延・能力同定の記述は確認できず [確]/[未確認] | 上位オーケストレーション層（クラウド/エッジ）。shadow mode・段階導入の記述なし [確] |
| **WAKU Sense** | ？ 接続方式の技術詳細を公式ページで確認できず [未確認] | ？ [未確認] | △ 「Area Limits」によるゾーン単位の交通ルール（混在フリート向け）[確・検索要約] | ？ [未確認] | ベンダー非依存の control tower（監視・分析中心）[確・検索要約] |
| **Formant** | ？ エージェントにアダプタを配布する方式 [確・検索要約] | **要**（ロボットにFormant agent）[推] | △ 中央交通制御を謳う記述あり（検索要約のみ、一次ページは404）[未確認] | ？ [未確認] | クラウド型の遠隔運用・可観測性基盤 [確・検索要約] |
| **Open-RMF** | △ Read Only / Traffic Light カテゴリが「RMF以前のレガシー」向けに用意されている [確] | **要**（fleet adapter を誰かが書く。ベンダーAPIが前提）[確] | ○ ただし Full Control で最大効率。Read Only は共有空間に最大1フリートまで [確] | × Read Only は運動学パラメータを**設定ファイルで静的に与える** [確]。オンライン同定の記述なし [確] | OSS。各フリートにアダプタ、全体にスケジュール/交渉 [確] |
| **Rapyuta Robotics (rapyuta.io)** | ？ 他社既設機の統合方法は公式ページで確認できず [未確認] | ？ [未確認] | ？ 「マルチロボットのタスク割当・ルートプランニング」の記述のみ [確] | ？ [未確認] | クラウドロボティクス基盤 + 自社AMR/AFL/ASRS [確] |
| **国内WES（YEデジタル MMLogiStation / GROUND GWES）** | △ メーカー別プラグイン（MMLogiStation、2025-01時点で計12製品）[確・二次] | **要**（製品ごとのプラグイン＝ベンダーFMのIF前提）[推] | × 走行レベルの交通調停の記述は確認できず。設備・作業の統合管理が主 [推] | ？ [未確認] | WMSと設備の間のWES層 [確・二次] |
| **日立 ユニバーサルWCS + LogiRiSM** | △ 「既に現場で稼働している他社製のAGVやソーターともシームレスに連携」[確] | ？ 連携IFの詳細は未確認 [未確認] | △ オーダー投入順序・搬送ルートの最適化、GTP/OTP同期 [確]。走行レベルの局所調停かは不明 [未確認] | ？ [未確認] | 上位WCSとして統合制御 [確] |
| **NEC マルチロボットコントローラ** | ？ 対応ロボットは個別対応（第一弾トピー工業）[確・二次] | **要**（対応機種を順次拡大する方式）[推] | ○ 「複数のロボット同士が干渉しない走行」の経路生成 [確・二次] | ？ [未確認] | 集中管制ソフト（2020-02発売）[確・二次]。現行の販売状況は未確認 |
| **BLACK STONE BRAIN（未踏AD 2023）** | × 前提が異なる（後述）[確] | 自社システムとして行動計画を直接指令 [推] | 対象はリフターAGV群の行動計画・タスク割当の最適化 [確] | × 環境は「観察可能・決定論的・静的」と仮定 [確] | AGV群の運用計画最適化ソフト [確] |
| **本提案** | ○ 位置履歴と限定命令（pause/目的地変更）への応答のみを前提 | **不要**（既設FMの公開I/F・既存の操作経路の範囲で動作）| ○ ただし狭路・交差点・充電器などの競合箇所に**限定** | ○ 各fleetの能力・遅延をオンライン同定（本提案の中核）| 既設の上に載せる上位ランタイム。shadow mode から段階導入 |

表の読み方（申請書に添える一文の案）:
> 既存のマルチベンダー製品・規格は、いずれも「標準IFの実装」「エージェントの導入」「ベンダー別コネクタ」など**ベンダー側または車両側の協力を前提**に、単一の上位制御へ集約する。Open-RMF は pause のみ／読み取り専用のフリートを制度として認めているが、その場合の効率低下と同時運用数の制約を公式文書が明記しており、フリートの応答特性は静的な設定値として与える。本提案は、この「協力が得られない既設フリート」を対象に、応答特性を運用中に同定して局所調停に使う点が異なる。

（上の一文のうち「いずれも」は本調査で確認できた範囲に限った言い方である。WAKU・Formant・Rapyuta・日立は接続方式の詳細が未確認のため、申請書では「確認できた範囲では」と限定するのが安全。）

---

## 1. VDA 5050

### 確認済みの事実
- **何を標準化しているか**: 移動ロボットフリートと中央フリート制御の間の通信。MQTT + JSON で、order / instantActions / state / visualization / connection / factsheet などのトピックを定める。GitHubリポジトリの現行版は 3.0.0。GitHubとPDFに差異がある場合はVDAサイトのPDFが正。
  - https://github.com/VDA5050/VDA5050 （確認日 2026-09-20）
- **最新版**: v3.0（3.0.0）。VDA のプレスリリース（URL上の日付 2026-04-21）で公開を告知。発行主体は VDMA Materials Handling and Intralogistics Association と VDA、技術監修は KIT の IFL。
  - 新機能: 自由走行ロボット向けの**ゾーン概念**（進入禁止、一方通行、マスタ制御の明示許可が必要な領域など）、ロボットが自己計画した**経路の共有**（マスタ側の交通管理のため）、ローカライズされたエラーメッセージ、省電力モード。
  - 既存の事前定義軌道・コリドー概念は 3.0 でも残す旨の記述あり（"The existing concepts with predefined trajectories and corridors for obstacle avoidance remain an integral part of the interface in version 3.0"）。
  - 同プレスリリースには、対応ベンダー数やレガシー車両の扱いに関する記述は**ない**。
  - https://www.vda.de/en/press/press-releases/2026/260421_PM_VDA_5050_EN （確認日 2026-09-20）
- **リリース時期の表記ゆれ**: idealworks の記事は「2026-02-17 に VDMA と VDA が 3.0.0 を正式採択、その後に法務確認」と記載。GitHub のパブリックレビューで40件超の変更を反映、長年の曖昧さ（実装の不整合の原因）を解消したとする。
  - https://www.idealworks.com/en/news/vda5050-300-release-march-2026 （確認日 2026-09-20）
- **前版**: v2.1.0 は 2025年1月公開（検索結果の要約による。一次ページは未取得）[確・二次]。
  - https://flowfuse.com/blog/2026/08/connect-agvs-vda-5050-mqtt/ （確認日 2026-09-20、検索要約）
- **実装は両端に必要**: IFR の解説記事（2021年6月時点の内容）に "VDA 5050 will need to be implemented at both ends of this communication channel (i.e., within the fleet manager and within the AGVs themselves) in order to function correctly." とある。
  - https://ifr.org/post/vda-5050-explained （確認日 2026-09-20）
- **非対応既設機のVDA化は「改修プロジェクト」になる**: SYNAOS と Götting の事例では、Linde P250 牽引車を VDA 5050 対応にするのに、SYNAOS の文書提供・ワークショップ込みで約4週間。車両自動化側（Götting）の実装作業が前提。
  - https://www.synaos.com/en/customer-stories/goetting （確認日 2026-09-20）
- **日本での状況（確認できた範囲）**:
  - v2.1.0 の日本語訳が個人のGitHubフォークとして存在する（公式訳ではない）。https://github.com/hijimasa/VDA5050/blob/release/2.1.0-jp/VDA5050_JP.md （確認日 2026-09-20、検索結果で存在を確認。本文は未読）
  - 日本独自の動きとして、NEDO と東芝が 2020-03-30 に **AMR-IF**（自律型移動ロボットと運行管理システムの間の地図情報・走行経路指示・現在位置のプロトコル）の仕様を策定し、準拠GUIのサンプルをOSSで公開。RRI のロボットイノベーションWGで標準化を進めるとした。https://www.nedo.go.jp/news/press/AA5_101303.html （確認日 2026-09-20）
  - 東芝は 2021-09-17 に、運行システムの異なる移動ロボット同士が無線LANマルチホップの**直接通信**で相互回避する協調連携システムを発表（ロボット側への実装が前提）。https://www.global.toshiba/jp/technology/corporate/rdc/rd/topics/21/2109-03.html （確認日 2026-09-20）

### 未確認
- 日本国内の VDA 5050 対応機種数・普及率を示す統計は見つからなかった。国内主要メーカー（ダイフク、村田機械、豊田自動織機、シャープ、明電舎など）の VDA 5050 対応発表も、今回の検索では確認できなかった（「対応していない」ことを確認したわけではない）。
- 経産省の令和5年度報告書（ロボット導入障壁のルール形成戦略）に VDA 5050 への言及があることは検索結果で示されたが、PDF が 403 で取得できず内容は未確認。https://www.meti.go.jp/meti_lib/report/2023FY/000581.pdf
- KIT IFL の「VDA 5050 実装事例一覧」ページは 404 で取得できず。
- AMR-IF のその後の普及・国際標準化の進捗は未確認。
- v3.0 が 2.x と後方互換か（破壊的変更の有無）は、取得できた資料に明記がなかった。

### 情報源からの推論
- VDA 5050 は「これから買う車両を単一マスタに集約する」ための規格であり、**ベンダーが対応版ファームを出さない既設機**には規格自体は解を与えない。既設機のVDA化は車両側の改修事業になる（Götting事例）。[推]
- v3.0 のゾーン概念と経路共有は「自律度の高いAMRをマスタが緩く統制する」方向で、本提案の「局所的な競合箇所だけ調停」と発想は近い。ただし車両側の 3.0 実装が前提である点は変わらない。[推]

---

## 2. マルチベンダー fleet 管理・オーケストレーション製品

### 2.1 InOrbit（InOrbit.AI）
**確認済みの事実**
- 公式概要: "Connect robots from multiple vendors for optimized traffic management and advanced collaboration." 接続手段は InOrbit Agent、InOrbit Edge、および VDA 5050 / MassRobotics AMR Interoperability Standard / Open-RMF。WMS/WES/WCS/ERP など既存業務システムとの接続を謳う。https://www.inorbit.ai/overview （確認日 2026-09-20）
- イントラロジ向けページ: 複数ベンダーのロボットを単一画面で管理、AI分析でボトルネック特定。shadow mode、段階導入、遅延特性に関する記述は**なかった**。https://www.inorbit.ai/intralogistics （確認日 2026-09-20）
- Automate 2026（プレスリリース 2026-06-22）: 8社（Ati Robotics, InOrbit.AI, Kärcher, Neura Robotics, Omron, Peer Robotics, Quasi Robotics, Unitree）のロボットを InOrbit Space Intelligence で統合するデモ。Space Intelligence を「個別ベンダーシステムの上に載るエンタープライズ級オーケストレーション基盤」とし、"real-time spatial awareness, traffic management, and task deconfliction across heterogeneous fleets" を中核機能に挙げる。Connect エコシステムは30以上のロボットブランド。ISO 21423 の初の公開デモと称する。https://www.prweb.com/releases/inorbitai-demonstrates-the-future-of-multi-vendor-robot-orchestration-and-physical-ai-at-automate-2026-302805136.html （確認日 2026-09-20）[確・二次]
- OpenRobOps（2026-09-15 発表）: Apache 2.0 のOSSフリート運用基盤。テレメトリ取込、地図上の追跡と遠隔操作、Configuration as code、異常検知、エッジ-クラウド構成、**Open-RMF とのネイティブ連携（物理/シミュレーションのフリートを Open-RMF のマルチフリート交通系に接続するアダプタ内蔵）**。ISO 21423 の最初のリファレンス実装と称する。brownfield/レガシーに関する明示的記述はなし。https://www.therobotreport.com/inorbit-ai-releases-openrobops-iso-21423-reference-implementation/ （確認日 2026-09-20）[確・二次]
- InOrbit の Open-RMF アダプタは **Full Control** 型（InOrbit REST API 経由）。https://github.com/inorbit-ai/ros_amr_interop （確認日 2026-09-20、検索要約）

**推論**
- InOrbit のベンダー横断交通制御は、(a) コネクタ経由で各ロボットへミッション/経路を指示できること、または (b) Open-RMF Full Control 相当の制御権があること、を前提にしていると読める。pause しか効かない black-box フリートをどう扱うかの公開記述は見つからなかった。[推]
- 位置づけ（「ベンダーシステムの上に載る」「既存設備と共存」）は本提案と最も近い。

### 2.2 Meili Robots（Meili FMS）
**確認済みの事実**
- VDA 5050 ロボット向け交通制御: ノード/エッジのグラフ上で、衝突可能性を検出すると優先度の低いロボットへ instantAction の `startPause` を送り、解消後に `stopPause` を送る。「同一経路に複数台」モードではロボット側に静的障害物回避能力が必要。https://docs.meilirobots.com/docs/tutorials/vda5050/traffic-control-vda/traffic-control-vda/ （確認日 2026-09-20）
- ROS 1/2 と VDA 5050 に対応。ロボット（または中央ROSノード）にエージェントを導入して双方向通信する方式。MiR の MiR Go パートナー製品として掲載。https://meilirobots.com/faqs , https://mobile-industrial-robots.com/products/mir-go/meili-robots-meili-fms （確認日 2026-09-20、検索要約。FAQ本文は WebFetch で取得できず）[確・検索要約]

**推論**
- 調停の手段が pause/resume である点は本提案と同じ。違いは、Meili は VDA 5050 準拠（= pause が即時・確実に効くと仮定できる車両）を前提にし、本提案は pause の効き方自体が未知・ばらつく既設フリートを前提にする点。[推]

### 2.3 SYNAOS
**確認済みの事実**
- "VDA 5050 native"。統合交通管理を謳う。信号機・シャッター・安全設備の統合、既設の手動車両（フォークリフト等）の位置取得と統合に言及。7社のロボットによる異種フリート運用を謳う。https://www.synaos.com/en/partners/connectivity （確認日 2026-09-20）
- VDA 5050 で6社（Safelog, Still, Kuka, Item, Fraunhofer IML, Bluepath Robotics）の車両を単一制御した実績の記述。https://www.synaos.com/en/partners/vda-5050 （確認日 2026-09-20、検索要約）
- 非対応車両は VDA 5050 化の共同改修（Götting事例、前掲）。

### 2.4 KINEXON
**確認済みの事実**
- VDA 5050 または API 連携による中央集権の交通・オーダー管理。"standardized communication protocols such as VDA 5050 or the integration of systems via API enable seamless interoperability and efficient traffic management"。既存のベンダー製フリートマネージャとの上下関係、非対応レガシー機の扱いは記事に記載なし。https://kinexon.com/resources/blog/interview-orchestrate-amr-agv-systems-different-manufacturers （確認日 2026-09-20）

### 2.5 WAKU Robotics（WAKU Sense）
**確認済みの事実**
- ベンダー非依存の robot control tower（アラート、分析、フリート管理、オーダー管理）。「Area Limits」でゾーン単位の交通ルールをドラッグ&ドロップで設定し、混在フリートの渋滞・閉塞を避けるとする。2019年設立、ドイツ。https://waku-robotics.com/en/solutions/waku-sense （確認日 2026-09-20、検索要約）[確・検索要約]

**未確認**
- 接続方式（ベンダーFMのAPI利用か、VDA 5050か）、Area Limits がロボットへ送る命令の種類、対応ベンダー一覧は、公式ページの取得結果に含まれず確認できなかった。

### 2.6 Formant
**確認済みの事実**
- クラウド型の遠隔運用・可観測性基盤（テレオペ、映像、センサ統合）。Formant agent にアダプタをリモート配布する方式。[確・検索要約]
- formant.io は formant.ai へ恒久リダイレクト。該当ブログ記事は 404 で本文未取得。

**未確認**
- ベンダー横断の交通制御を実運用で提供しているか。検索要約には "central traffic control system" の文言があったが、一次ページで確認できていない。

### 2.7 NAiSE（調査依頼外だが関連性が高いため追加）
**確認済みの事実**
- "Integration via VDA 5050, MassRobotics, APIs, or direct interfaces"。異なる VDA 5050 バージョンの同時運用。AGV/AMR に加えフォークリフト・牽引車など手動車両も「全交通参加者」として統合。"Support for legacy systems and manual vehicles"。対応ブランド28以上。https://naise.eu/fleet-manager/ , https://naise.eu/ （確認日 2026-09-20）
- 2026年5月、Linde MH の AGV を VDA 5050 で統合した旨の報道。https://logisticsbusiness.com/materials-handling/new-integration-expands-mixed-fleet-agv-interoperability/ （確認日 2026-09-20、検索要約）

**未確認**
- 「legacy systems」対応の技術的な中身（ベンダーに何を要求するか）は非開示。

### 2.8 Rapyuta Robotics
**確認済みの事実**
- rapyuta.io は、ロボティクスアプリケーションのCI/デプロイから物理ロボット群のリモート管理までを扱うクラウドロボティクス基盤。「マルチロボットシステムのタスク割り当てやルートプランニング」に言及。https://www.rapyuta-robotics.com/ja/rapyuta-io/ （確認日 2026-09-20）
- 技術ページは「複数種類のロボットを組み合わせる必要」を述べるが、他社製既設機の統合方法・交通制御・既設対応の具体記述は取得結果になかった。https://www.rapyuta-robotics.com/ja/technology/ （確認日 2026-09-20）

**未確認**
- 他社の既設 black-box フリートを rapyuta.io の群制御下に入れた事例の有無。

### 2.9 国内のその他
**確認済みの事実**
- **YEデジタル MMLogiStation**（WES）: メーカーを問わず自動化設備と接続するプラグイン方式。2025-01 のプラグイン追加で AGV 等を含め計12製品。Mujin の AGV とも 2022-07 に連携開始。https://www.lnews.jp/2025/01/r0114601.html , https://www.lnews.jp/2022/07/o0708401.html （確認日 2026-09-20、検索要約）[確・二次]
- **GROUND GWES**: 異なるメーカーのハード（マテハン・ロボット）とソフト（WMS・WCS）を連携し、物流施設全体を統合管理・最適化。2021-08-02 提供開始。https://www.groundinc.co.jp/newsroom/pressrelease/20210802 （確認日 2026-09-20、検索要約）[確・二次]。走行・交通レベルの制御を行うかは FAQ ページから確認できず [未確認]。
- **日立 ユニバーサルWCS / LogiRiSM**: AGV・ソーター・ロボット・自動倉庫・コンベヤなど異種・マルチベンダー設備を階層型に連携。オーダー投入順序や搬送ルートを最適化。「既に現場で稼働している他社製のAGVやソーターともシームレスに連携」。2026年3月の Hitachi Physical AI Day 講演に基づくコラム。https://www.hitachi.co.jp/products/infrastructure/product_site/logistics_center/column/logistics-center-autonomy.html （確認日 2026-09-20）
- **NEC マルチロボットコントローラ**: 複数台・複数タイプの自律移動ロボットを集中管制。一方通行・一時停止など現場ルールに適応した経路生成、「複数のロボット同士が干渉しない走行」、WMS/MES連携。2020年2月発売、3年で300拠点の導入を見込むとした。第一弾対応はトピー工業のクローラロボット。https://www.lnews.jp/2019/12/l1213401.html （確認日 2026-09-20）[確・二次]。NEC 公式製品ページは 403 で未取得、現行の販売状況・導入実績は [未確認]。
- **Mujin**: 自社のQRグリッド式AGV（最大100台規模）と MujinController による統合制御。他社AGVを統合制御する記述は確認できず。https://www.mujin.co.jp/solution/mobilerobot/agv/ （確認日 2026-09-20、検索要約）
- **オムロン FLOW Core**: 自社AMRフリート向け。REST / SQL / MQTT の統合ツールキットあり。Automate 2026 の InOrbit デモに Omron が参加。他社機の混在制御は [未確認]。
- **村田機械**: 今回の検索では他社機統合に関する情報を得られず [未確認]。
- **Open-RMF の国内動向**: 富士ソフトがシミュレータ上で ROS/ROS2 実装の多種類ロボットの群制御を確認。「実機」と「ROS未対応ロボットを含む混在環境」は今後の検証予定と明記。https://www.fsi.co.jp/ros/cases/12.html （確認日 2026-09-20、日付記載なし）。アプトポッドは intdash CONTROL CENTER で Open-RMF 連携のマルチベンダー群管理を謳う。https://www.aptpod.co.jp/solutions/control-center/robops/ （検索要約）
- **Octa Robotics LCI**: ロボットとエレベータ・自動ドア等の設備をマルチベンダーで連携する通信サービス。2025年2〜3月、ハクオウロボティクスの自動フォーク AutoFork と東京ロジファクトリー川越物流センターのエレベータ連携で実運用開始。対象はロボット-設備間で、フリート間の交通調停ではない。https://www.octa8.jp/news/20250325/ （確認日 2026-09-20、検索要約）

### 2.10 関連する新規格: ISO 21423
**確認済みの事実**
- 名称: Robotics — Industrial mobile robots — Communications and interoperability。異なるベンダーの産業用AMRシステム（AMR、フリートマネージャ、その他の企業リソース）間の相互運用のための通信プロトコル。MassRobotics Interoperability Standard と VDA 5050 を土台に、約90の参加者で策定。VDA 5050 の単一中央制御モデルに対し、複数のフリートマネージャとロボットが共存・協調する連合型（federated）の構成を想定。https://www.prweb.com/releases/inorbitai-demonstrates-the-future-of-multi-vendor-robot-orchestration-and-physical-ai-at-automate-2026-302805136.html , https://www.agvnetwork.com/agv-technology/iso21423 （確認日 2026-09-20）[確・二次]
- 検索結果に "ISO/FDIS 21423" のカタログページが存在（FDIS段階に達したことを示唆）。https://standards.iteh.ai/catalog/standards/iso/f772b16e-582a-4ed4-9f79-0a80ad376f40/iso-fdis-21423 （検索結果のタイトルのみ確認）

**未確認**
- 正式発行の有無と発行日（ISO 公式ページは 403 で取得できず）。
- 共有ゾーンでの複数フリートマネージャ間の交通調停の具体的な仕組み。agvnetwork の解説記事はこの点を扱っておらず、共通座標系へのマッピングが未解決課題だと指摘している。

---

## 3. Open-RMF

### 確認済みの事実
出典はいずれも公式書籍 "Programming Multiple Robots with ROS 2"。
- フリートアダプタの制御カテゴリは4種。https://osrf.github.io/ros2multirobotbook/rmf-core.html （確認日 2026-09-20）
  - **Full Control**: 各ロボットの経路を RMF が完全に制御。"provides the highest overall efficiency and compliance with RMF, which allows RMF to minimize stoppages and deal with unexpected scenarios gracefully."
  - **Traffic Light**: 状態取得 + 各ロボットの pause/resume のみ。"useful for deconflicting traffic schedules"
  - **Read Only**: 状態更新のみ、制御は一切なし。
  - **No Interface**: RMF と非互換。"other fleets cannot coordinate with it through RMF, and will likely result in deadlocks."
- 協調度と効率の関係: "The more collaborative a fleet is with RMF, the more harmoniously all of the fleets and systems are able to operate together."（同上）
- **Read Only の同時運用制約**: "Any shared space is allowed to have a maximum of just one 'Read Only' fleet in operation"。理由は "any two or more of such fleets will make avoiding deadlock or resource conflict nearly impossible."（同上）
- Read Only は RMF 以前に開発されたレガシーシステム向け。Fleet Driver が `rmf_fleet_msgs/FleetState`（name, location, path）を送る必要がある。Location の時刻フィールドは概ね無視され、アダプタが**起動パラメータで与えた車両特性**（linear_velocity, angular_velocity, linear_acceleration, angular_acceleration, footprint_radius, vicinity_radius）から到達時刻を推定する。https://osrf.github.io/ros2multirobotbook/integration_read-only.html （確認日 2026-09-20）
- Traffic Light 型について、メンテナ（grey）の Discourse での発言（2025-09-21〜23）: 目的は「施設のシステムと既に統合済みで、Open-RMF からは pause/resume しか受け付けないロボットの交通管理」。ドア・リフト連携はこの型では未対応（"it seemed infeasible for us to manage these interactions while not having much control over the robot"）。"I'm not aware of any open source examples of a traffic-light integration since all robot APIs that needed the traffic-light integration were proprietary." 実装は `EasyTrafficLight`。次世代の "Execution Protocols" で一般化を検討。https://discourse.openrobotics.org/t/feature-and-limitation-of-traffic-light-adapter/50134 （確認日 2026-09-20）

### 未確認
- Read Only / Traffic Light フリートでの効率低下を**定量的に**示した公式記述・ベンチマークは見つからなかった。公式文書の記述は定性的（Full Control が最高効率、Read Only は共有空間に1つまで）にとどまる。

### 情報源からの推論
- Open-RMF は本提案と同じ問題設定（pause しか効かない／見るだけの既設フリート）を**認識しカテゴリ化している**が、(1) Read Only は経路意図（path）の提供を要求する、(2) 車両特性は静的パラメータ、(3) Read Only の複数同居は事実上非対応、(4) Traffic Light の公開実装例がない、という状態。ここが本提案の入り込む余地である。[推]
- 逆に言えば、本提案は「Open-RMF の Traffic Light / Read Only アダプタを賢くしたもの」と評価されうる。差別化は、応答特性のオンライン同定と、複数 black-box フリート同居下での局所調停の安全性保証に置く必要がある。[推]

---

## 4. 日本の物流倉庫の状況

### 確認済みの事実
- **2024年問題の輸送能力不足試算**: 経産省・国交省・農水省「持続可能な物流の実現に向けた検討会 最終取りまとめ」（2023年8月）。NX総合研究所の試算として、対策を行わなかった場合、2019年度比で **2024年度に輸送能力の14.2%（4.0億トン相当）**、ドライバー数減少も加味すると **2030年度に34.1%（9.4億トン相当）** が不足する可能性。https://www.mlit.go.jp/seisakutokatsu/freight/content/001626756.pdf （確認日 2026-09-20、PDFをテキスト化して該当箇所を確認）
- **倉庫自動化の公的KPI**: 「総合物流施策大綱（2026年度〜2030年度）」（令和8年=2026年3月31日 閣議決定）のKPI。「無人搬送車の導入その他の措置により庫内作業の自動化に取り組んでいる倉庫事業者の割合」**12%（2025年度）→ 20%（2030年度）**。本文は、倉庫・配送センター等の業務効率化・省人化が「急務」であり、中小の荷主・物流事業者を中心に庫内作業の自動化・機械化機器の導入を推進するとする。WMS・WCS 等の活用による自動荷役機器・自動倉庫の最適運用にも言及。https://www.mlit.go.jp/seisakutokatsu/freight/content/001993236.pdf （確認日 2026-09-20、PDFをテキスト化して確認）。閣議決定の事実: https://www.meti.go.jp/press/2025/03/20260331010/20260331010.html
- **物流ロボティクス市場（矢野経済研究所、2025-03-11 発表）**: 国内の物流ロボティクス市場規模は **2024年度 404億3,000万円（前年度比113.1%）**、2027年度 733億3,000万円、**2030年度 1,238億円** の予測。対象は物流倉庫・物流センター・工場横倉庫の屋内ロボット（AGF、GTP型AGV、ACR、搬送ロボットAGV/AMR等）。海外メーカーの日本進出が活発化との指摘。調査期間 2024年10月〜2025年2月。https://www.yano.co.jp/press-release/show/press_id/3762 （確認日 2026-09-20）
- **次世代物流システム・サービス市場（富士経済、2024-11-14 発表）**: 次世代物流ロボットシステムは 2030年に2023年比7.4倍の317億円、WMS は同57.6%増の457億円、バース管理システムは同5.1倍の163億円。https://www.nikkei.com/article/DGXZRSP682012_U4A111C2000000/ （確認日 2026-09-20）[確・二次（プレスリリース転載）]
  - 全体市場「2024年見込 7,542億円、2030年予測 1兆1,670億円」、および「WES は2030年に2023年比10.0倍」は検索要約・二次記事による。https://toralogi.com/news-fuji-keizai-logistics-dx-investigation-1614/ , https://dxmagazine.jp/news/2411d296/ [確・二次]。富士経済の一次ページは未取得。
- **AGV/AMR 世界市場（矢野経済研究所）**: 2025年の世界出荷台数見込み 286,235台（前年比117.7%）、2030年に約138万台の予測。https://www.nikkei.com/article/DGXZRSP701093_T21C25A2000000/ （確認日 2026-09-20、検索要約）[確・二次]

### 未確認
- **「複数ベンダーのAGV/AMRが同一倉庫に混在している」割合を示す公的統計・調査は見つからなかった。** これは申請書の問題設定の根幹なので、ヒアリングや現場事例で補う必要がある。
- 経産省 令和6年度「中堅・中小企業の物流施設自動化のための課題整理・分析」調査報告書（2025年3月）は、導入率・障壁のアンケートを含むとみられるが、PDF が 403 で取得できず内容未確認。https://www.meti.go.jp/meti_lib/report/2024FY/1000144.pdf
- JILS の物流コスト調査など、JILS 発の自動化投資額データは今回未調査（検索で該当が出なかった）。
- 2024年度の実際の輸送能力不足が試算どおりだったかの事後検証は未調査。

### 情報源からの推論
- 12%→20% のKPIは「自動化に取り組む倉庫事業者がまだ少数」であることを示す。混在問題が顕在化するのは、自動化済みで追加導入の段階にある大手・先進拠点に偏る可能性が高い。市場の初期顧客は狭い。[推]
- 矢野の指摘する「海外メーカーの日本進出の活発化」は、1拠点に複数ベンダーが入る状況を増やす方向に働く。ただし直接の裏付けデータではない。[推]
- WES 市場が10倍成長の予測（二次情報）であることは、「設備をまたぐ上位層」への投資意欲の傍証になる一方、WESベンダーが走行レベルの調停まで降りてくる可能性も示す。[推]

---

## 5. 近接する未踏アドバンスト採択: BLACK STONE BRAIN（2023年度）

### 確認済みの事実
出典: https://www.ipa.go.jp/jinzai/mitou/advanced/2023/gaiyou_hn-1.html （確認日 2026-09-20）
- プロジェクト名: 「組合せ最適化手法を用いたAGV群運用計画最適化システム『BLACK STONE BRAIN』の開発」
- 採択者: 井上亮太郎（東京大学大学院総合文化研究科）、大澤琢真（TRUST SMITH株式会社）、髙田悠太（非公開）、山崎泰貴（TRUST SMITH株式会社）。PM: 平野豊。契約金額 13,608,000円。
- 対象: **リフターAGV**を用いた無人搬送システムの効率向上。製造業・物流業。
- 開発物: 複数台AGVの行動計画に特化した組合せ最適化手法によるソフトウェア。重点は (1) 高精度な行動計画モジュール、(2) 高効率な搬送タスク割当モジュール。
- 前提: 環境は **「状態が観察可能・決定論的・静的」** で、組合せ最適化に適しているとする。
- 採択理由: 既存技術は「他AGVの行動を適切に捉えられていない経路計画」という課題があり、その解決に未踏性。競合は多いが成功時の優位性が大きいと評価。

### 情報源からの推論
- BLACK STONE BRAIN は、**自分が全AGVの行動計画を決められる**（= Full Control 相当、単一種のリフターAGV）ことを前提に、計画の最適性を追求するもの。本提案はその逆で、計画を決める権限がなく、相手の挙動も不確実な既設フリート群を対象にする。「観察可能・決定論的・静的」という仮定を、本提案は「部分観測・応答が確率的・能力が未知」に置き換える。[推]
- 申請書では「同じAGV群制御の領域だが、前提（制御権と環境仮定）が正反対」と一文で切り分けられる。PMが同系統の場合、既視感を持たれる可能性があるため、この対比は冒頭で示すのがよい。[推]

---

## 6. 我々の提案の差別化が崩れるリスク

正直に書く。深刻度の高い順。

### R1. InOrbit が同じ位置取りを既に宣伝しており、OSS も出した（最大の脅威）
- InOrbit Space Intelligence は「個別ベンダーシステムの上に載る」「異種フリート間の traffic management と task deconfliction」を公式に謳い、30以上のブランドのコネクタを持ち、2026-06 に8社混在デモ、2026-09-15 に Apache 2.0 の OpenRobOps（Open-RMF 連携内蔵）を公開した。審査員が「それ InOrbit でできるのでは」と言う可能性が最も高い。
- 残る差分（確認できた範囲）: InOrbit の公開資料には、(a) pause しか効かない／APIを開けない black-box フリートの扱い、(b) 命令応答の遅延・能力のオンライン同定、(c) shadow mode からの導入、の記述が**見つからなかった**。ただし「見つからなかった」だけで、非公開機能や個別案件で実施している可能性は否定できない [未確認]。
- 日本での InOrbit の販売・導入体制は今回未調査 [未確認]。

### R2. Open-RMF の Traffic Light / Read Only と「問題設定が同じ」
- 公式文書がレガシー向けカテゴリを定義済み。本提案は「Open-RMF の Traffic Light アダプタの改良版」と見なされうる。Open-RMF 側が "Execution Protocols" で Traffic Light 型を一般化する計画に言及している（時期未確認）。
- 対抗軸: Read Only の「共有空間に1フリートまで」制約、車両特性の静的設定、Traffic Light の公開実装例ゼロ（メンテナ自身の発言）を根拠に、「制度はあるが実用解がない領域」と位置づける。Open-RMF と競合せず、そのアダプタ層として提供する選択肢もある。

### R3. 「応答特性のオンライン同定」が差別化として弱いと見られる
- 調査した製品・規格のいずれにも同等機能の記述は確認できなかった。これは新規性の根拠になる一方、「需要がないから誰もやっていない」「静的パラメータ+安全マージンで足りる」と解釈される余地がある。
- 同定の有無でスループットや停止回数がどれだけ変わるかの定量根拠が、申請時点で必要。Open-RMF 公式にも定量値はなく [未確認]、自前のシミュレーション結果が最も効く。
- 学術側の先行研究（black-box エージェントの応答同定、multi-fleet の federated coordination）は今回十分に調べていない [未確認]。関連しそうな米国特許 US 12,164,307 "Method for interlinking heterogeneous fleet systems, device and system implementing the same" が検索に出たが、PDFが画像のみで出願人・請求項を確認できなかった [未確認]。提出前に要確認。

### R4. 規格側が前提を崩す（中長期）
- VDA 5050 v3.0（ゾーン概念・経路共有）と ISO 21423（複数フリートマネージャの連合型）が普及すれば、「協力しないフリート」は減る。ISO 21423 は FDIS 段階とみられる（正式発行は未確認）。
- ただし既設機は規格対応ファームが出ない限り対象外で、倉庫設備の更新周期は長い。国内での VDA 5050 普及を示す資料も見つからなかった。5年程度は black-box 既設が残る、という主張は可能だが、裏付けデータは未取得。

### R5. 国内大手が「既設他社機と連携」を既に謳っている
- 日立（ユニバーサルWCS / LogiRiSM）は「既に現場で稼働している他社製のAGVやソーターともシームレスに連携」と明記。YEデジタルはプラグイン12製品。顧客から見れば「上位で束ねる製品」は既にある。
- 確認できた範囲では、これらはオーダー・搬送指示レベルの統合であり、走行レベルの局所調停やブラックボックス同定ではない [推]。ただし日立の連携IFの詳細は未確認で、走行レベルまで踏み込んでいる可能性は残る。

### R6. 問題の存在自体の裏付けが弱い
- 「複数ベンダーのAGV/AMRが同一倉庫で干渉している」ことを示す公的統計は見つからなかった。自動化に取り組む倉庫事業者は2025年度で12%。審査で「その問題は何拠点にあるのか」と問われたときの答えが、現状では現場ヒアリング頼みになる。

### R7. 技術・契約上の実現性
- 既設FMに対する pause/目的地変更の命令経路が、そもそも公開I/Fとして存在しない機種がある。存在しても、第三者ランタイムからの操作が保守契約・安全認証（ISO 3691-4 等）上許されるかは別問題。今回は未調査 [未確認]。shadow mode から始める設計はこのリスクへの妥当な答えだが、制御モードへ移行できる拠点の割合は不明。

---

## 付録: 取得に失敗した情報源（再確認候補）
| URL | 状況 |
|---|---|
| https://www.meti.go.jp/meti_lib/report/2023FY/000581.pdf | 403（VDA 5050 の国内評価を含む可能性）|
| https://www.meti.go.jp/meti_lib/report/2024FY/1000144.pdf | 403（物流施設自動化のアンケート）|
| https://jpn.nec.com/iot/platform/iort/index.html | 403（NEC マルチロボットコントローラ公式）|
| https://www.iso.org/standard/86749.html | 403（ISO 21423 のステージ）|
| https://www.automate.org/robotics/editorials/iso-21423-building-global-consensus-for-mobile-robot-interoperability | 403 |
| https://www.ifl.kit.edu/english/6611.php | 404（VDA 5050 実装事例一覧）|
| https://bluebotics.com/blog/vda-5050 | 404 |
| https://meilirobots.com/faqs | 本文が取得できず（ナビゲーションのみ）|
| https://docs.waku-robotics.com | 未取得（WAKU の接続方式の確認先）|
| https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12164307 | 画像PDFでテキスト抽出不可 |
