#!/usr/bin/env bash
set -euo pipefail

# deploy.sh — _src/ のソースから index.html / gigi.html を生成し、commit → push → Pages再ビルド
# 使い方: ./deploy.sh "疑義解釈その10を追加"

if [ $# -eq 0 ] || [ -z "$1" ]; then
  echo "ERROR: コミットメッセージを引数で指定してください。"
  echo "使い方: ./deploy.sh \"変更内容の説明\""
  exit 1
fi

MSG="$1"
REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_ROOT"

echo "=== 1/5: gigi.html を生成 ==="
python3 _src/build_gigi.py

echo "=== 2/5: _src/index.html → index.html コピー ==="
cp _src/index.html index.html

echo "=== 3/5: 差分サマリ ==="
git diff --stat

echo "=== 4/5: commit ==="
git add index.html gigi.html _src 更新記録.md
git commit -m "$MSG"

echo "=== 5/5: push & Pages再ビルド ==="
git push
gh api -X POST repos/toki-git501/r8-dental-report/pages/builds

echo ""
echo "公開URL: https://toki-git501.github.io/r8-dental-report/"
echo "※ 更新記録.md への追記を忘れずに"
