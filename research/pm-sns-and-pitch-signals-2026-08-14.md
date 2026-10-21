# 2026年度下期 未踏アドバンストPM 公開SNS調査と訴求シグナル

- 調査日: 2026-08-14（日本時間）
- 対象: 統括PM 2名、PM 9名の計11名
- 基準リスト: [IPA「2026年度下期 未踏アドバンスト事業プロジェクトマネージャー・ビジネスアドバイザー」](https://www.ipa.go.jp/jinzai/mitou/advanced/2026second/pm.html)（2026-07-16公開）
- 取得範囲: 本人性を確認できた公開プロフィール、公開投稿、本人執筆記事、所属組織・研究室の発信
- 取得方法: 公開ページの目視確認、検索、X API・GitHub REST API・RSSで継続取得できるソースの特定

## 0. 結論

**確認済みの事実**

- Xの本人アカウントを確認できたのは、夏野剛、石黒浩、漆原茂、首藤一幸、吉崎航の5名。
- LinkedInの本人プロフィールを確認できたのは、竹内郁雄、夏野剛、石黒浩、漆原茂、梶田真実、首藤一幸、平野豊、藤井彰人の8名。ただし直近の自著投稿が見えるのは漆原氏が中心で、他は休眠または投稿が疎である。
- Facebookの本人プロフィールを確認できたのは夏野氏、漆原氏。梶田氏、吉崎氏は本人への過去リンクを確認したが、2026-08-14時点ではページが利用不能または非公開だった。
- 首藤氏は本人GitHubを確認できた。竹内氏・石黒氏・吉崎氏には、本人執筆または所属組織のnoteも補助情報として存在する。
- 原田達也氏は、本人性を確定できる個人X、LinkedIn、Facebook、Instagramを確認できなかった。公式研究室サイト・本人執筆の研究室記事を代替情報源とする。
- 「SNSが見つからない」ことと「SNSが存在しない」ことは同義ではない。本資料は、公開情報で本人性を確認できた範囲を記録しており、同名アカウントを推測で採用していない。

**情報源からの推論**

- PMの公開発信は、IPAが明文化した追加審査基準ではない。提案内容を相手の専門に合わせて翻訳するための補助材料として使う。
- 現在1位の `Voice Safety Kernel for Physical AI` は、吉崎PMには「実機・Sim2Real・停止訂正」、首藤PMには「ランタイムと行為契約」、石黒PMには「人間の割り込みと主体性」、漆原PMには「模倣困難な深い技術」として説明を変えるとよい。
- 現在2位の `エッジ音声デバイス・コンパイラ` は、漆原PM、首藤PM、平野PM、藤井PMに対し、それぞれアーキテクチャ、システム抽象化、モデルベース実機検証、端末・ネットワーク・クラウド規模の観点で翻訳できる。

**チームの仮説**

- PM別に題材を変えるのではなく、同一の技術核について「何が新しいか」「何を実機で証明するか」「誰の行動や事業が変わるか」の強調順を変える。
- SNSの短期的話題へ迎合するより、複数年の発信に共通する専門的関心と、公式PMメッセージが一致する部分を重視する。

## 1. 公開SNS・発信源の一覧

`本人` は本人プロフィール、`所属` は所属組織・研究室、`過去` は外部リンクで本人性を確認できたが現在取得できないものを表す。

| 区分 | 氏名 | 確認できたSNS・公開発信 | 2026-08-14時点の取得状態 |
|---|---|---|---|
| 統括PM | 竹内郁雄 | [LinkedIn](https://www.linkedin.com/in/ikuo-takeuchi-4b145694/)（本人）、[情報処理学会note寄稿](https://note.com/ipsj/n/n1036cbfab26e)（本人執筆） | LinkedInはプロフィールのみ、直近投稿なし。寄稿本文は取得可 |
| 統括PM | 夏野剛 | [X @tnatsu](https://x.com/tnatsu)（本人）、[LinkedIn](https://www.linkedin.com/in/takeshi-natsuno-ab3778342/)（本人）、[Facebook](https://www.facebook.com/tnatsu)（本人）、[ニコニコチャンネル](https://ch.nicovideo.jp/natsuno)（本人） | X公開投稿を取得可。Facebook本文はログイン制限あり |
| PM | 石黒浩 | [X @hiroshiishiguro](https://x.com/hiroshiishiguro)（本人）、[LinkedIn](https://www.linkedin.com/in/hiroshi-ishiguro-7b30072b/)（本人）、[AVITA note](https://note.com/avita)（所属） | X公開投稿を取得可。LinkedInは直近投稿なし。noteはRSS可 |
| PM | 漆原茂 | [X @urucrunch](https://x.com/urucrunch)（本人）、[LinkedIn](https://www.linkedin.com/in/shigeru-urushibara/)（本人）、[Facebook](https://www.facebook.com/shigeru.urushibara)（本人） | X・LinkedInとも最近の発信あり。Facebookは一部のみ公開 |
| PM | 梶田真実 | [LinkedIn](https://www.linkedin.com/in/mamikajita/)（本人）、[Wantedly](https://www.wantedly.com/id/mami_kajita)（本人）、[Facebook](https://www.facebook.com/mami.kajitapp/)（過去） | LinkedIn・Wantedlyはプロフィールのみ。Facebookは取得不能 |
| PM | 首藤一幸 | [X @shudo](https://x.com/shudo)（本人）、[LinkedIn](https://www.linkedin.com/in/shudo/)（本人）、[GitHub](https://github.com/shudo)（本人）、[研究室Facebook](https://www.facebook.com/shudolab)（所属） | Xが活発。GitHub公開イベントはAPI取得可。LinkedInは直近投稿なし |
| PM | 原田達也 | [研究室サイト](https://www.mi.t.u-tokyo.ac.jp/harada/)（所属）、[研究室ブログの本人記事](https://www.mi.t.u-tokyo.ac.jp/blog/research/statement/) | 本人と確定できる個人SNSは未確認。研究室発信を代替利用 |
| PM | 平野豊 | [LinkedIn](https://www.linkedin.com/in/yutaka-hirano-6617451b7/)（本人） | 詳細プロフィールは取得可。直近投稿なし |
| PM | 藤井彰人 | [LinkedIn](https://www.linkedin.com/in/akihitofujii/)（本人） | プロフィール・反応・短いコメント中心。自著投稿は疎 |
| PM | 三木寛文 | [Wantedly](https://www.wantedly.com/id/hirofumi_miki)（本人）、[MIRAI CROSSプロフィール](https://portal.mirai-cross.ventures/advisory/hirofumimiki/)（本人） | Wantedlyにストーリーなし。後者はSNSではなく職務情報の補助 |
| PM | 吉崎航 | [X @W_Yoshizaki](https://x.com/W_Yoshizaki)（本人）、[Facebook](https://www.facebook.com/wataru.yoshizaki)（過去）、[アスラテックnote](https://note.com/asratec)（所属） | Xが非常に活発。Facebookは取得不能。noteはRSS可 |

完全な機械可読台帳は [pm-social-sources.json](pm-social-sources.json)、日次の取得状態は [pm-sns-monitor-status.md](pm-sns-monitor-status.md) に置く。

## 2. PM別の発信内容と「刺さる」説明

### 2.1 竹内郁雄 統括PM

**確認済みの事実**

- [LinkedIn](https://www.linkedin.com/in/ikuo-takeuchi-4b145694/)は未踏統括PM、一般社団法人未踏代表理事、東京大学名誉教授等の経歴と一致する。2026-08-14取得時、最近の投稿は表示されなかった。
- 2025-02-17の[情報処理学会note寄稿「環境，大事です」](https://note.com/ipsj/n/n1036cbfab26e)では、女性・地域によるIT人材機会の偏りと、才能が育つ環境の重要性を論じている。
- IPA公式では、独創的技術を事業化・社会実装・国際デファクト標準化へ展開する未踏アドの役割を説明する。

**情報源からの推論**

- 目先の流行より、尖った個人が長期に育ち、技術が社会の基盤になる筋道を重視する。
- 小さな改善ではなく、「このチームだから発見できた異質な技術」と「8か月後の成果」を両立させる説明が合う。

**刺さる形への翻訳**

> 音声AIの一製品ではなく、物理AIが人間の割り込みを安全に解釈する共通ランタイムと評価規格を日本から作る。8か月で実機・SDK・公開ベンチマークまで残す。

確度: 中。最近の個人SNS投稿がないため、公式メッセージと本人寄稿を中心にした推論。

### 2.2 夏野剛 統括PM

**確認済みの事実**

- [X @tnatsu](https://x.com/tnatsu)はKADOKAWA・ドワンゴ、近畿大学の本人プロフィールと一致し、2026-08-14時点で約40.7万フォロワー。
- [2025-12-15のX投稿](https://x.com/tnatsu/status/2000363624356102193)では、少子化・労働力不足、女性のキャリア継続に対するフルリモート雇用の有効性を取り上げた。
- 2024-06-28の投稿では、クラシック音楽とデジタル技術、Vtuberを融合したリアルタイム演奏体験を紹介した。
- IPA公式では「平均値の向上はもう要らない」「世界で通用するソフト」「世界で例のないビジネスモデル」「想像を上回るサービス」を求める。

**情報源からの推論**

- 技術の改善率より、デジタル技術で既存カテゴリや働き方を変え、大規模に普及する可能性を見せる方がよい。
- 30秒で誰でも差を理解できるデモと、世界規模の利用像を先に示すべきである。

**刺さる形への翻訳**

> 人が「止めて」と言い終わる前に物理AIが安全停止し、同じ会話の中で訂正後の行為へ復帰する。従来の音声UIでは不可能だった制御体験を30秒で見せ、複数産業へ共通提供する。

確度: 中〜高。X本人投稿と公式メッセージの方向が一致。

### 2.3 石黒浩PM

**確認済みの事実**

- [X @hiroshiishiguro](https://x.com/hiroshiishiguro)は本人の肩書・AVITAとの関係が一致する。2026-02-21には、AVITAをPhysical AI領域へ拡大し、ヒューマノイド開発人材を募集すると発信した。
- AVITA公式noteの本人執筆記事[「アバターで人類を進化させる」](https://note.com/avita/n/n0ac438c822ac)では、富そのものではなく人類の進化・発展を目的とし、技術で人間と社会の新しい可能性を探ると述べる。
- LinkedInは本人プロフィールだが、2026-08-14取得時に最近の投稿はなかった。
- IPA公式では、人間の性質を深く理解し、ソフトウェア、VR、AI、ロボットで「人に親和的なシステム」を作る挑戦を求める。

**情報源からの推論**

- レイテンシや安全性を機械の性能だけで語らず、人が相手の主体性をどう感じ、いつ発話を「停止命令」と解釈するかという人間理解へ接続する必要がある。
- アバターからヒューマノイドへ関心領域を広げているため、身体を持つAIでの新しい人間関係を見せると強い。

**刺さる形への翻訳**

> 重複発話・言い直し・ためらいから、人間が行為を委ねたのか撤回したのかを逐次推定する。安全停止だけでなく、人が主導権を保っていると感じる条件を被験者実験で定量化する。

確度: 高。2026年の本人X、本人執筆、公式メッセージが相互に補強。

### 2.4 漆原茂PM

**確認済みの事実**

- [X @urucrunch](https://x.com/urucrunch)は、ソフトウェアエンジニア、Database/OS、cloud native、scalable architecture、生成AI、startup等をプロフィールに掲げる。
- 2026-08-02のXでは、AI駆動開発が人月モデルと人材育成を変え、育成できる企業が競争力を持つと発信。2026-08-01には、AI時代にも若手エンジニアを人が育てる重要性を述べた。
- [LinkedIn](https://www.linkedin.com/in/shigeru-urushibara/)では、AI駆動開発、顧客価値との共創、Spring Boot 4、Java、技術者コミュニティに関する投稿が確認できる。
- [Facebook](https://www.facebook.com/shigeru.urushibara)は本人プロフィール・所属を確認でき、公開範囲では企業決算への投稿も見えた。
- IPA公式では「他では真似できない技術」を明示的に問う。

**情報源からの推論**

- 新技術そのものだけでなく、深いソフトウェア設計が企業の作り方・顧客価値・人材へ与える変化に関心がある。
- APIの組み合わせではなく、自作ランタイム、データ構造、検証系、開発ツールとして残る技術を示すべきである。

**刺さる形への翻訳**

> 音声認識APIのラッパーではなく、音声・意味・行為の投機実行を管理するカーネル、制約記述、HILテストランナーを自作する。1社の受託案件で終わらず、物理AI開発の検証工程そのものを変える。

確度: 高。X・LinkedInの最近の本人発信が豊富。

### 2.5 梶田真実PM

**確認済みの事実**

- [LinkedIn](https://www.linkedin.com/in/mamikajita/)と[Wantedly](https://www.wantedly.com/id/mami_kajita)は、Singular Perturbations CEO、理論物理学・犯罪予測システム開発の経歴が一致する。2026-08-14取得時、最近の投稿・ストーリーはなかった。
- 外部の本人紹介からリンクされた[Facebook](https://www.facebook.com/mami.kajitapp/)は、2026-08-14時点で利用できなかった。
- 東京大学公式インタビュー[「Physicist’s crime prediction system」](https://www.u-tokyo.ac.jp/focus/en/features/entrepreneurs23.html)では、研究を犯罪予測へ転用し、警察・自治体で実証し、データの少ない地域へのtransfer learningを扱う。
- [Disrupting Japanの本人インタビュー](https://www.disruptingjapan.com/how-the-police-use-proven-ai-to-predict-future-crime/)では、A/Bテスト、人間の判断を置換しない運用、行政営業、研究から起業への移行を語る。

**情報源からの推論**

- 理論・アルゴリズムを、現場で責任ある意思決定と定量効果へ変換する道筋が重要。
- 技術デモだけでなく、誰と、何を比較し、誤作動をどう扱うかを事前に示すとよい。

**刺さる形への翻訳**

> 停止見逃し率、誤停止率、停止距離、復帰成功率を事前登録し、既存VAD/STT制御との同条件比較を行う。AIが人を置換するのではなく、人間が物理AIの主導権を保つ安全補助として実証する。

確度: 中。SNSは休眠だが、本人インタビューの情報量と公式メッセージは強い。

### 2.6 首藤一幸PM

**確認済みの事実**

- [X @shudo](https://x.com/shudo)は、本人サイト、京都大学、IPAの経歴と一致し、2026-08-14時点で約3,760フォロワー。
- 2026年8月のXでは、ソフトウェア工学を単なる「ソフトウェアを作ること」と同一視しない定義、半導体設計教育と設計価値、論文査読・研究者キャリア等を扱う。
- テンソル形状をコンパイル時に検査する仕組み、プログラミング言語処理等の技術発信も共有している。
- [GitHub](https://github.com/shudo)ではOverlay Weaver、shuJIT、SimBlock等のシステム研究・実装を公開している。LinkedInは本人だが最近の投稿なし。
- IPA公式では「世の中をこうしてやりたい」という思いを求める。

**情報源からの推論**

- 流行語より、ソフトウェアを成立させる抽象化、原理、実装、再現可能な評価に反応しやすい。
- ひとつの正確なシステムプリミティブをコードとベンチマークで見せる方が、広い構想図より強い。

**刺さる形への翻訳**

> 行為を `prepare / commit / abort / repair` へ分ける音声行為契約と、低遅延経路・高知能経路を並行実行するランタイムを作る。停止・訂正の意味論、参照実装、再現ベンチマークを公開する。

確度: 非常に高い。活発な本人X、GitHub、公式メッセージが一貫。

### 2.7 原田達也PM

**確認済みの事実**

- 本人と確定できる個人SNSは、2026-08-14までの公開検索で確認できなかった。
- [研究室サイト](https://www.mi.t.u-tokyo.ac.jp/harada/)は論文採択や研究成果を継続更新している。
- 本人執筆の研究室記事[「“機械ならでは”の知能」](https://www.mi.t.u-tokyo.ac.jp/blog/research/statement/)では、人間知能の模倣だけでなく、機械に特有の知能を実現する方向を示す。
- IPA公式では、流行に流されず冬の時代にも可能性を信じる「骨太のチャレンジ」を求める。

**情報源からの推論**

- 既存音声モデルの統合では弱い。新しい表現、学習目的、データ、評価方法のうち何が研究コミュニティに残るかを説明する必要がある。
- 人間会話の模倣だけでなく、機械が並列推論・投機実行できるからこその安全知能を定義すると独自性が出る。

**刺さる形への翻訳**

> 人間の会話模倣ではなく、機械だけが可能な複数行為候補の並列準備と、安全境界内での逐次commitを学習する。新しいストリーミング表現と評価タスクを論文水準で切り出す。

確度: 中。個人SNSではなく、本人執筆・研究室・IPA公式に基づく。

### 2.8 平野豊PM

**確認済みの事実**

- [LinkedIn](https://www.linkedin.com/in/yutaka-hirano-6617451b7/)は本人のHIRANO Research Lab、未踏PM、Toyota/Wovenの経歴と一致する。2026-08-14取得時、最近の投稿はなかった。
- プロフィールでは、車両運動制御、HEV/EVのモデルベース開発、ロボティクス、AI/ML、人間特性、脳科学、新規事業、自動運転・スマートシティのプラットフォームアーキテクチャを挙げる。
- Modelica/FMI等のモデルベース開発・相互運用標準にも関わる。
- IPA公式では、社会課題・生活課題を新技術で解き、新事業と創業者精神へつなげることを求める。

**情報源からの推論**

- 単体AI精度より、モデル、制御、実機、安全、標準インターフェース、事業がつながる全体設計が重要。
- Model-in-the-loop、Hardware-in-the-loop、実機の順に検証可能な構成が合う。

**刺さる形への翻訳**

> 音声行為契約をFMI等で制御系へ接続し、シミュレーション、HIL、実ロボットで同じ停止・訂正シナリオを再生する。安全KPIと導入先の業務KPIを一つの検証工程へ統合する。

確度: 中。LinkedInの詳細経歴は強いが、最近の投稿がない。

### 2.9 藤井彰人PM

**確認済みの事実**

- [LinkedIn](https://www.linkedin.com/in/akihitofujii/)はKDDI・IPAの経歴と一致し、2026-08-14時点で約1,307フォロワー。
- 直近の表示は短い祝意コメントやリアクションが中心で、本人の長文投稿は疎だった。
- IPA公式では、スマートデバイス、IoT、クラウド、AIの転換を機会とし、新価値を将来の大きな事業へつなげることを求める。
- KDDI公式の過去発言では、5Gと他社資産を組み合わせたB-to-B-to-Xの共創、新市場・社会課題解決を述べる。

**情報源からの推論**

- SNSから強い個人嗜好を推定するのは避け、端末・エッジ・ネットワーク・クラウド・事業規模という職務上のレンズを使う。
- 2026年度上期の「エージェンティック音声入力」との非重複を最初に明示する必要がある。

**刺さる形への翻訳**

> 端末内の即時Safety Monitorとクラウドの高知能推論を分離し、ジッタ・通信断・費用を含む配置最適化を行う。入力支援ではなく、物理行為のcommit/abortを保証する新しい制御層である。

確度: 中〜低。本人SNSの自著投稿が少ないため、公式メッセージと職務情報が中心。

### 2.10 三木寛文PM

**確認済みの事実**

- [Wantedly](https://www.wantedly.com/id/hirofumi_miki)はMKマネジメント代表の経歴と一致するが、2026-08-14時点でストーリー投稿はなかった。
- [MIRAI CROSSプロフィール](https://portal.mirai-cross.ventures/advisory/hirofumimiki/)では、GREE初期のモバイル・SNS事業、提携、広告、ゲームプラットフォーム、中国事業、国内外約50社・VCへの支援、AI・SaaS・産業DX等の投資・助言経験を挙げる。
- IPA公式では、前人未到のアイデア・技術・起業家と、日本の産業競争力・エコシステム強化を求める。

**情報源からの推論**

- 技術だけでなく、最初の顧客、販売経路、パートナー、海外展開、資金・人員の伸ばし方まで一体にするとよい。
- 汎用市場を語る前に、狭いbeachheadと実証先を特定する必要がある。

**刺さる形への翻訳**

> まず協働ロボットの音声停止・訂正へ限定し、設計パートナー2社、SDK販売、機器メーカー組込みの順で展開する。8か月後の技術完成だけでなく、終了後18か月の販売・提携・海外展開を示す。

確度: 中〜低。活発な個人SNSがなく、職務プロフィールと公式メッセージに基づく。

### 2.11 吉崎航PM

**確認済みの事実**

- [X @W_Yoshizaki](https://x.com/W_Yoshizaki)はV-Sido開発、実物大ガンダム、変形マクロス、クラタス等の経歴と一致し、2026-08-14時点で約1.9万フォロワー、約8,835投稿。
- 2026-06-17には、Isaac Labで学習した結果を実機へ載せたSim2Real、シミュレータと実機の一致、歩容の増加、サーボの実装知見を発信した。
- 2026-08-11には、二足・四足・六足等の複数ロボット案件を並行していることと、徹夜を含む実機製作の楽しさを発信した。
- 固定投稿では、V-Sido Simulatorを構造・動作・モデル検証、VR、映像、実ロボット、展示に一貫利用した例を示す。
- IPA公式では、Physical AIは未成熟で方法論が未確立な「未踏要素の宝庫」と述べる。

**情報源からの推論**

- スライド上の構想より、ロボットが実際に動き、壊れ方・ズレ・材料・サーボ・遅延まで扱う提案が強い。
- 一種類のヒューマノイド専用ではなく、複数形態で同じ制御原理が通用することを見せると方法論として評価しやすい。

**刺さる形への翻訳**

> 実ロボットが動作中、重複発話の「待って、右じゃなく左」で安全停止し、訂正後に復帰する。二足と車輪型の2機種で同じ行為契約を使い、Sim、HIL、実機の停止距離と失敗動画をすべて公開する。

確度: 非常に高い。最近の本人Xが豊富で、IPA公式メッセージとも直接一致。

## 3. 現在案への訴求マップ

| PM | Voice Safety Kernelで先頭に置く証拠 | エッジ音声デバイス・コンパイラで先頭に置く証拠 |
|---|---|---|
| 竹内 | 共通ランタイム・公開評価規格・日本発標準化 | 設計知を広く開く開発環境と長期的波及 |
| 夏野 | 30秒でカテゴリの違いが伝わる実機デモ | 非専門家が実機を完成させる劇的な体験差 |
| 石黒 | 主体性・割り込み・人間評価 | 人に親和的な身体・音声インタラクション |
| 漆原 | 行為契約・投機実行・HIL基盤の自作 | クロスレイヤIR、制約充足、自己検証という堀 |
| 梶田 | 事前登録した安全KPIと現場比較試験 | 研究仮説から顧客実証・製品化までの一本道 |
| 首藤 | ランタイム意味論、コード、ベンチマーク | モデル非依存のIR・コンパイラ・検証系 |
| 原田 | 新しいストリーミング表現・学習目的 | 制約を学習・探索する新規手法と評価データ |
| 平野 | Model/HIL/実機を通す安全アーキテクチャ | モデルベース開発と現場・標準インターフェース |
| 藤井 | エッジ即時系＋クラウド高知能系、通信断 | 端末・ネットワーク・クラウドの配置最適化と規模 |
| 三木 | 最初の産業、設計パートナー、販売経路 | 限定市場から機器メーカー・海外へ伸ばす経路 |
| 吉崎 | 2機種の実ロボット、Sim2Real、失敗動画 | 生成物が実機で動き、計測から自己修正する閉ループ |

### 3.1 X API初回取得で新たに強まった判断

2026-08-14に5名の本人Xから、リプライとリポストを除く直近計116投稿を取得した。各人最大25件のスナップショットであり、本人の全関心や審査基準を代表するものではない。

**確認済みの事実**

- 石黒PMは2026-08-03に、ジェミノイドとの対話だけでなく、参加者同士が友人になる「ジェミノイドサロン」を告知した。[本人投稿](https://x.com/hiroshiishiguro/status/2084175914561339709)
- 漆原PMはAI駆動開発による人月モデルの変化を語る一方、若手を人が育てる環境と、AIを使いこなす技術者を育成する企業の競争力を繰り返し述べた。[2026-08-02の本人投稿](https://x.com/urucrunch/status/2083871182781358461)、[2026-03-05の本人投稿](https://x.com/urucrunch/status/2029418050341224528)
- 首藤PMは2026-06-10に「〇〇に役立つ」という説明を `nice to have` と判断して確認対象から外す旨を投稿した。また、実用的な言語モデル開発とNVIDIA独占を緩和する研究開発、実機前のドローンシミュレーションにも言及した。[「役立つ」への本人投稿](https://x.com/shudo/status/2064533959468601758)、[言語モデル・GPUへの本人投稿](https://x.com/shudo/status/2076200660798947808)、[ドローンシミュレーションへの本人投稿](https://x.com/shudo/status/2062549608811917638)
- 吉崎PMはPhysical AIコンテストについて「無難な正解はいらない」と紹介し、人間はAIに依存しないという解決策を早期に諦めるべきとも述べた。さらに、揚げ油に入れられる3Dプリント製ロボットハンドや企業との実機検証を紹介した。[コンテストへの本人投稿](https://x.com/W_Yoshizaki/status/2067018101477286387)、[AI依存への本人投稿](https://x.com/W_Yoshizaki/status/2030213888223195553)、[ロボットハンドへの本人投稿](https://x.com/W_Yoshizaki/status/2064312493946905056)
- 夏野統括PMは取得25件のうち最新が2025-12-15、その前が2024-06-28であり、現在のX投稿頻度は低い。最新投稿では少子化・労働力不足・女性のキャリア継続に対するリモートワークの有効性を述べた。[本人投稿](https://x.com/tnatsu/status/2000363624356102193)

**情報源からの推論**

- Physical AIという分野名だけでは差別化にならない。石黒PMと吉崎PMの双方が現在進行形で扱っているため、人間関係をどう変えるか、どの未解決制御問題を解くか、どの過酷条件で実証したかまで必要である。
- `Voice Safety Kernel` は「AIへ依存しないための安全装置」ではなく、「AIへの依存が進む前提で、人間が委任・撤回・訂正できる制御プリミティブ」と説明する方が、吉崎PMの発信と石黒PMの人間中心の関心に整合する。
- 首藤PMへは「役に立つ」「社会課題を解く」を先頭に置かず、停止・訂正の意味論、ランタイム、モデル非依存性、再現ベンチマークを先に示す必要がある。
- 漆原PMへは省人化を主価値にせず、開発者が安全なPhysical AIを作り、失敗から学び、能力を高められる開発基盤として示す方がよい。
- 夏野統括PMの現在嗜好をXだけから更新する確度は低く、IPA公式メッセージと職務・事業発信を優先する。

**チームの仮説**

- 現在案の順位を逆転させる材料はない。一方、本命デモは「2種類の実機」「重複発話による停止・訂正・復帰」「失敗動画」「人が主導権を感じる評価」を一つにまとめるべきである。
- 提案の一文は「役立つ音声AI」ではなく、「身体を持つAIへの委任を、実行中でも撤回・訂正できる共通ランタイム」とすると、今回のX差分を最も一貫して反映できる。

## 4. 継続更新の実装

2026-08-14に、このリポジトリへ次を追加した。

- ソース台帳: [pm-social-sources.json](pm-social-sources.json)
- 取得器: [update-pm-social.ps1](../scripts/update-pm-social.ps1)
- 日次タスク登録器: [install-pm-social-task.ps1](../scripts/install-pm-social-task.ps1)
- Xトークンの非表示入力: [set-x-bearer-token.ps1](../scripts/set-x-bearer-token.ps1)
- 現在状態: [pm-sns-monitor-status.md](pm-sns-monitor-status.md)
- 最新スナップショット: [data/pm-social/latest.json](data/pm-social/latest.json)
- 追記専用の差分履歴: [data/pm-social/events.ndjson](data/pm-social/events.ndjson)

Windowsタスク `MitouPMSocialDailyUpdate` を毎日07:00（ローカル時刻）で登録済み。次回予定は2026-08-15 07:00。PCが予定時刻に停止中なら、次回利用可能時に実行する設定である。

取得器は以下の方針で動く。

1. Xは初回に `username -> user_id` を解決し、以後そのIDを保存する。
2. X投稿は前回の `since_id` より新しいものだけを取得する。
3. GitHub公開イベント、note RSS、研究室ページを取得する。
4. `events.ndjson` の `event_key` で既取得項目を重複保存しない。
5. LinkedIn、Facebook、WantedlyはAPI制約により自動取得せず、台帳に手動確認状態を残す。
6. APIトークンは環境変数だけから読み、リポジトリへ保存しない。

## 5. 必要なAPI・認証情報

| 媒体 | 使用する公式手段 | 認証 | 今回必要か | 制約・費用 |
|---|---|---|---|---|
| X | `GET /2/users/by/username/:username`、`GET /2/users/:id/tweets` | `X_BEARER_TOKEN` | **必要** | [X APIは従量課金](https://docs.x.com/x-api/getting-started/pricing)。2026-08-14確認時はUser Read $0.010/件、Post Read $0.005/件。価格はDeveloper Consoleで再確認する |
| LinkedIn | [Posts API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api) | OAuth、`r_member_social` | 不要・実用不可 | `r_member_social`は承認済み利用者限定。2026-05-15更新の[Community Management概要](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/community-management-overview)では新規申請を受け付けていない。任意の第三者個人投稿を汎用トークンで取得できない |
| Facebook | Graph API Page feed | Page access token、Page権限、審査 | 不要 | 本人個人プロフィールを第三者として横断取得する用途には使えない。Pages向け権限と個人プロフィールを混同しない |
| Instagram | Instagram API | Professional accountの認可、必要に応じAdvanced Access | 不要 | Meta公式PostmanコレクションではBusiness/Creatorが対象で、consumer accountは取得不可。今回本人確認済みInstagramなし |
| GitHub | `GET /users/{username}/events/public` | 無認証可。`GITHUB_TOKEN`は任意 | 不要 | [無認証60 req/h、認証済み5,000 req/h](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api)。首藤氏1名の日次取得は無認証で十分 |
| note | `https://note.com/{creator}/rss` | 不要 | 不要 | 公開RSSを実地確認。正式な汎用開発者APIとしては扱わない。所属組織フィードなので氏名・V-Sido等で絞る |
| YouTube | `channels.list`、`playlistItems.list` | 公開情報はAPI key | 任意 | IPA公式動画メッセージの更新監視には利用可能。[playlistItems.listは1 call=1 quota unit](https://developers.google.com/youtube/v3/docs/playlistItems/list)。個人SNSの取得には現時点で不要 |
| Wantedly / ニコニコ | 今回の用途に適した公開公式APIを確認できず | — | 不要 | 公開ページの手動確認に留める |

### X APIについてユーザーにお願いするもの

`X_BEARER_TOKEN` のみ。対象は次の5ハンドル。

- `tnatsu`
- `hiroshiishiguro`
- `urucrunch`
- `shudo`
- `W_Yoshizaki`

[X公式のGetting Access](https://docs.x.com/x-api/getting-started/getting-access)に従い、Developer ConsoleでProject/App、クレジット、Bearer Tokenを用意する。トークンはチャットやMarkdownへ貼らず、このWindowsユーザーの環境変数 `X_BEARER_TOKEN` に設定する。

ローカルでは次を実行すると、入力内容を画面に表示せずユーザー環境変数へ保存できる。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\set-x-bearer-token.ps1
```

初回を最大25投稿/人とすると、最大でUser Read 5件＋Post Read 125件、2026-08-14の公表単価では概算上限 $0.675。実際の返却件数が少なければ下がる。以後は `since_id` により新規投稿だけを取得する。

## 6. 解釈上の注意

- 公開SNSは本人の全活動・全関心を代表しない。投稿頻度が低い人ほど推論の確度を下げた。
- 「いいね」「短いコメント」「リポスト」は、本人の継続的な評価基準として強く扱わない。
- 所属組織note、研究室ブログ、研究室Facebookは本人SNSではない。本人執筆・本人登場・組織一般の発信を区別する。
- 個人の職歴・経歴は本人申告または公開プロフィールとして扱い、応募資料へ転記する場合も必要最小限にする。
- PM向け最適化は、公式の未踏性、事業・社会的意義、実現性を弱めてはならない。

## 7. 主な一次情報

- [IPA 2026年度下期 PM・BA紹介](https://www.ipa.go.jp/jinzai/mitou/advanced/2026second/pm.html)
- [X User Lookup](https://docs.x.com/x-api/users/lookup/introduction)
- [X Timelines](https://docs.x.com/x-api/posts/timelines/introduction)
- [X API Pricing](https://docs.x.com/x-api/getting-started/pricing)
- [LinkedIn Posts API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api)
- [LinkedIn Community Management Overview](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/community-management-overview)
- [GitHub public events endpoint](https://docs.github.com/en/rest/activity/events#list-public-events-for-a-user)
- [GitHub REST API rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api)
- [YouTube Data API playlistItems.list](https://developers.google.com/youtube/v3/docs/playlistItems/list)
- [東京大学 梶田真実氏インタビュー](https://www.u-tokyo.ac.jp/focus/en/features/entrepreneurs23.html)
- [原田研究室「“機械ならでは”の知能」](https://www.mi.t.u-tokyo.ac.jp/blog/research/statement/)
- [AVITA 石黒浩氏本人記事](https://note.com/avita/n/n0ac438c822ac)
