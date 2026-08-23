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

---

# 修正→デプロイ 標準手順（2026-07-27 確立）

## 0. 環境（必読・ハマりどころ）
`xcode-select` が Xcode.app を指しており **Xcode ライセンス未同意で git / gh / brew が全て失敗する**。
sudo パスワードが不明なため `sudo xcodebuild -license` は使えない。**回避策**:

```bash
export DEVELOPER_DIR=/Library/Developer/CommandLineTools
```

これを付ければ `/usr/bin/git`（2.50.1）がそのまま動く。`deploy.sh` を叩く時も同じシェルで export しておくこと。
恒久化するなら `~/.zshrc` に上記1行を追記（未実施）。

## 1. 点数の検証手順（数値を触る前に必ず実施）
根拠PDF: `_reference/`（旧: Vault `85_Scripts/092_開発/令和8年度診療報酬改定サイト/参考資料/`）

```bash
cd ~/Projects/r8-dental-report
pdftotext -layout "_reference/別表第二 歯科診療報酬点数表.pdf" /tmp/r8_tensu.txt          # 告示＝点数の正
pdftotext -layout "_reference/別添２ 歯科診療報酬点数表に関する事項.pdf" /tmp/r8_tsuchi.txt  # 通知＝算定要件の正
grep -n "区分番号" /tmp/r8_tensu.txt
```

- **点数は告示（別表第二）が正**、**算定要件・施設基準は通知（別添２）が正**。疑義解釈は補足。
- 区分番号（C000、B000-4-2、I011-2、M017-2 等）で引くのが最速。項目名は表記ゆれがある。
- ⚠️ **R6（改定前）の点数は手元PDFでは検証不能**。「旧→新」の差分表を直すときは新点数のみ根拠付きで直し、旧点数は断定しない。
- 全文チェックは1回では終わらない。`_src/index.html` は306KB・点数言及471箇所あるため、
  行範囲を分けて `general-purpose` サブエージェント2体に並列で照合させると速い。

## 2. 修正
- 編集対象は `_src/` のみ（ルートの index.html / gigi.html は生成物）。
- 表のセル内補足は既存パターンに合わせる（`cell-note` 等の独自classはCSSが無いので使わない）:
  ```html
  <td style="text-align:right;">361点<br><small style="color:var(--text-sub);">2〜9人</small></td>
  ```
- `gigi_parts/*.js` を触ったら `node --check` で構文確認。
- ⚠️ **`.reveal` は `opacity:0` で IntersectionObserver 待ち**。検索・フィルタで `display` を戻すだけでは
  画面外の要素が透明のままになる。表示する要素には必ず `el.classList.add("visible")` を付ける
  （2026-07-27 の疑義解釈検索バグの原因）。

## 3. デプロイ
```bash
export DEVELOPER_DIR=/Library/Developer/CommandLineTools
./deploy.sh "変更内容の説明"
```
⚠️ `deploy.sh` の git add 対象は `index.html gigi.html _src 更新記録.md` **のみ**。
**新規のルートPDF（疑義解釈PDF等）と sitemap.xml は拾わない** → デプロイ後に必ず:
```bash
git status --short   # 空であることを確認。残っていれば手動 add → commit → push
```

## 4. 公開反映の確認（_src を直しただけでは公開に反映されない）
```bash
gh api repos/toki-git501/r8-dental-report/pages/builds/latest --jq '.status'   # built を待つ
curl -s https://toki-git501.github.io/r8-dental-report/ | grep -c "検証したい文字列"
```
直したはずの旧文言が0件、新文言が1件以上あることを両方チェックする。

## 5. 記録
`更新記録.md` の末尾に日付・修正内容・**根拠（区分番号と告示/通知の別）**・保留事項を追記。

## 6. ChatGPTによるクロスチェック（2026-08-23〜運用開始）
デプロイ前後どちらでもよいが、内容を大きく変更した場合は公開URL（`https://toki-git501.github.io/r8-dental-report/`）をChatGPT（GPT-5.6 Sol）に渡し、告示・通知内容との整合性・表現の精度をチェックさせる。
- **手順は `gpt-crosscheck` スキルに切り出し済み**（`~/.claude/skills/gpt-crosscheck/SKILL.md`）。`codex exec` CLI（ChatGPTアカウント認証済み・model=gpt-5.6-sol）で非対話的に呼び出す方法が確立済みで、ブラウザ操作より速く確実
- 依頼文には必ず「今この瞬間の最新版を再取得してから読んでください」と明記する（古いキャッシュを前提に回答されるのを防ぐため）
- **ChatGPTの指摘は鵜呑みにしない**。「回答は必ずしも正しいとは限らない」を前提に、`_reference/` の一次資料PDF・厚労省公式サイト（WebFetch等）で1件ずつ裏取りしてから反映する
- 実績: 2026-08-23、この手順で疑義解釈その6の日付誤り（5/21→正式には5/22）と、回復期等口腔機能管理計画策定料/管理料をR8新設と誤記していた点（実際はR6ですでに存在）を発見・是正した

## トラブル対応
- Pagesデプロイ失敗時: `gh api -X POST repos/toki-git501/r8-dental-report/pages/builds` で即再ビルド
- git が "You have not agreed to the Xcode license" → 上記 §0 の DEVELOPER_DIR

## Vault について
- 旧ソースフォルダ（Obsidian Vault内）は退役済み。ポインタノートのみ残置
- 以後の編集はすべてこのリポジトリの `_src/` で行う
