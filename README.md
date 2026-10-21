# 未踏アドバンスト応募プロジェクト

2026年度下期の未踏アドバンスト応募に向けた調査、提案資料、議事録、シミュレーション実験を管理します。現在の状況は [MEMO.md](MEMO.md)、作業時のルールは [AGENTS.md](AGENTS.md) を参照してください。

応募資料、個人の経歴、相談記録を含むため、GitHubでは**非公開**で管理します。共同作業者はリポジトリの Settings → Collaborators から招待してください。

## フォルダー構成

| 場所 | 内容 |
|---|---|
| `MEMO.md` | 現在の状況・判断・未確認事項 |
| `applications/` | 応募資料、下書き、提出済みPDF |
| `minutes/` | 議事録と意思決定の記録 |
| `research/` | 調査資料と参考文献 |
| `experiments/` | シミュレーション、試作コード、保存済みの評価結果・図・動画 |
| `scripts/` | 調査などの補助スクリプト |

## 取得

アクセス権のあるGitHubアカウントで認証してから実行します。

```sh
git clone --recurse-submodules https://github.com/yukiobata1/mitou.git
cd mitou
```

通常のcloneで取得した場合は、次のコマンドでU-FASTを取得します。

```sh
git submodule update --init --recursive
```

`experiments/ufast` は既存の [U-FAST](https://github.com/DaeeunLim/ufast) をサブモジュールとして参照しています。親リポジトリに記録された版を使用し、ライセンスは同ディレクトリの `LICENSE.txt` を参照してください。

## 共同編集

作業開始時に最新の内容を取り込み、作業用ブランチを作ります。

```sh
git pull --ff-only
git submodule update --init --recursive
git switch -c your-topic
```

変更内容を確認し、必要なファイルを指定して登録します。

```sh
git status
git diff
git add <変更したファイル>
git commit -m "変更内容の説明"
git push -u origin HEAD
```

GitHubでPull Requestを作成して変更を共有します。

## ローカルで用意するもの

- `.env` は共有しません。SNS取得機能を使用する場合のみ `.env.example` をコピーし、自分の認証情報を設定します。
- Pythonの仮想環境、キャッシュ、`tmp/`、`.tmp-*/`、実行ログはGit管理の対象外です。元のローカルファイルは保持します。
- U-FAST内の `results/` と `sweep/` はローカル生成データです。サブモジュールの共有内容には含まれません。既存の実験結果の要約・評価JSON・図・動画は `experiments/` に保存しています。
- 実験の詳細は [experiments/README.md](experiments/README.md)、小規模MARL試作は [experiments/marl_poc/README.md](experiments/marl_poc/README.md) を参照してください。U-FASTは上記の手順で取得済みなので、実験README内の再cloneは不要です。
- `sweep/` のSMAT需要表は `experiments/make_smat_fromto.py` で生成できます。`case1` の20倍・40倍需要表は実験READMEの `awk` 例で生成します（Git Bash等を使用し、出力先 `sweep/` を作成してから実行）。

WindowsでU-FASTの環境を用意する例（PowerShell）:

```powershell
cd experiments
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ./ufast
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
```

実験記録の数値・表現は作成当時のものです。構想と実装済みの範囲については、最新のMEMOと議事録を優先してください。
