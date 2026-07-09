# r8-dental-report（令和8年度診療報酬改定サイト・歯科）

公開URL: https://toki-git501.github.io/r8-dental-report/ （GitHub Pages）

## 最重要ルール
- **編集するのは `_src/` のみ**（`_src/index.html` と `_src/gigi_parts/`）
- `index.html`（ルート）と `gigi.html` は**生成・コピーされた成果物であり、直接編集禁止**
  - `index.html` ← `_src/index.html` のコピー
  - `gigi.html` ← `_src/build_gigi.py` による自動生成物
- 更新は `./deploy.sh "変更内容"` で build → cp → commit → push → Pages再ビルドを一括実行

## ファイル構成

```
_src/                   ← ソース（唯一の編集対象）
  index.html            ← メインページのソース
  gigi_parts/           ← gigi.html 固有部分（4ファイル）
  build_gigi.py         ← gigi.html 生成スクリプト
deploy.sh               ← 更新の1コマンド化スクリプト
index.html              ← 生成物（直接編集禁止）
gigi.html               ← 生成物（直接編集禁止）
更新記録.md              ← 業務ログ（手動追記）
```

## 更新手順
1. `_src/index.html` または `_src/gigi_parts/` を編集
2. `./deploy.sh "変更内容の説明"` を実行
3. 公開URLで表示確認: https://toki-git501.github.io/r8-dental-report/
4. `更新記録.md` に履歴を追記

## 疑義解釈の新規発出時
- `_src/gigi_parts/section05_gigi.html` にQ&Aを追記して `./deploy.sh` で反映

## トラブル対応
- Pagesデプロイ失敗時: `gh api -X POST repos/toki-git501/r8-dental-report/pages/builds` で即再ビルド

## Vault について
- 旧ソースフォルダ（Obsidian Vault内）は退役済み。ポインタノートのみ残置
- 以後の編集はすべてこのリポジトリの `_src/` で行う
