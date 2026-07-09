#!/usr/bin/env python3
"""gigi.html をソースHTML（_src/index.html）+ gigi_parts/ から生成するビルドスクリプト。

使い方:
    python3 _src/build_gigi.py          # リポジトリルートから
    ./deploy.sh "変更内容"               # 推奨: build→cp→commit→push を一括実行

- ソース: _src/index.html（唯一の編集対象。日付リネーム方式は廃止済み）
- gigi固有部分: _src/gigi_parts/ 配下の4ファイル
    head_meta.html        … <title>とmeta description
    gigi_css.html         … gigiページ専用CSS（</style>直前に追記）
    section05_gigi.html   … 疑義解釈Q&A全文セクション
    gigi_search_js.html   … 検索・フィルタJS（</body>直前に追記）
- 出力: リポジトリルートの gigi.html（直接編集禁止の生成物）

アンカーが見つからない場合は即エラーで停止する（サイレントなドリフト防止）。
"""
import sys
from pathlib import Path

BASE = Path(__file__).parent
PARTS = BASE / 'gigi_parts'
SOURCE = BASE / 'index.html'
OUTPUT = BASE.parent / 'gigi.html'


def part(name):
    return (PARTS / name).read_text(encoding='utf-8')


def replace_once(html, old, new, label):
    n = html.count(old)
    if n != 1:
        sys.exit(f'ERROR [{label}]: アンカーが {n} 件（1件のはず）。ソースHTMLの変更に合わせて build_gigi.py を修正してください。\n  anchor: {old[:80]!r}')
    return html.replace(old, new)


def replace_between(html, start, end, new, label, keep_end=True):
    """start〜end の間（startを含み、endは keep_end=True なら残す）を new に置換。"""
    if html.count(start) != 1 or html.count(end, html.index(start)) < 1:
        sys.exit(f'ERROR [{label}]: 範囲アンカーが見つかりません。\n  start: {start[:80]!r}\n  end: {end[:80]!r}')
    i = html.index(start)
    j = html.index(end, i)
    return html[:i] + new + (html[j:] if keep_end else html[j + len(end):])


def main():
    print(f'ソース: {SOURCE.name}')
    html = SOURCE.read_text(encoding='utf-8')

    # 0. 生成ファイルであることの明示
    html = replace_once(
        html,
        '<!DOCTYPE html>\n',
        '<!DOCTYPE html>\n<!-- このファイルは build_gigi.py により自動生成されます。直接編集せず、ソースHTMLと gigi_parts/ を編集して再生成してください。 -->\n',
        'generated banner')

    # 1. head: title〜twitterメタを gigi 用に差し替え（faviconリンク以降は共通）
    html = replace_between(html, '<title>', '<link rel="icon"', part('head_meta.html'), 'head meta')

    # 2. gigi専用CSSを </style> 直前に追記
    html = replace_once(html, '\n</style>', '\n\n' + part('gigi_css.html') + '</style>', 'gigi css')

    # 3. body クラス
    html = replace_once(html, '<body>', '<body class="gigi-page">', 'body class')

    # 4. ナビロゴをトップへのリンクに変更
    html = replace_once(
        html,
        '''    <div class="nav-logo">
      R6 vs R8 歯科改定
      <span class="badge">2026</span>
    </div>''',
        '''    <a href="index.html" class="nav-logo">
      R6 vs R8 歯科改定
      <span class="badge">2026</span>
    </a>''',
        'nav logo')

    # 5. ナビメニューをトップページ各セクションへのリンクに差し替え
    html = replace_between(
        html,
        '<ul class="nav-links">',
        '</ul>',
        '''<ul class="nav-links">
      <li><a href="index.html#summary">改定ポイント9</a></li>
      <li><a href="index.html#premise">前提条件の比較</a></li>
      <li><a href="index.html#compare">これまでの改定経緯</a></li>
      <li><a href="index.html#points">主要点数の新旧比較</a></li>
      <li><a href="index.html#gigi">疑義解釈</a></li>
      <li><a href="index.html#forecast">歯科業界の未来予測</a></li>
      <li><a href="index.html#checklist">実施チェックリスト</a></li>
      <li><a href="index.html#references">参照ソース一覧</a></li>
    ''',
        'nav links')

    # 6. TOC・サイドメニューの 05 リンクをページ内アンカーへ
    html = replace_once(html, '<a href="gigi.html" class="toc-item">', '<a href="#gigi" class="toc-item">', 'toc link')
    html = replace_once(html, '<a href="gigi.html" class="side-menu-link">', '<a href="#gigi" class="side-menu-link">', 'side-menu link')

    # 7. SECTION 05 を疑義解釈Q&A全文に差し替え（SECTION 06 コメントの手前まで）
    html = replace_between(html, '<!-- ===== SECTION 05', '<!-- ===== SECTION 06', part('section05_gigi.html'), 'section 05')

    # 8. Back to Top: gigiページはヒーロー直下からQ&Aのため閾値を下げ、初期表示も判定
    html = replace_once(
        html,
        '''window.addEventListener('scroll', () => {
  if (!backToTopBtn) return;
  backToTopBtn.classList.toggle('visible', window.scrollY > 420);
}, { passive: true });''',
        '''function updateBackToTopVisibility() {
  if (!backToTopBtn) return;
  backToTopBtn.classList.toggle('visible', window.scrollY > 120);
}
window.addEventListener('scroll', updateBackToTopVisibility, { passive: true });
updateBackToTopVisibility();''',
        'back-to-top')

    # 9. 検索・フィルタJSを </body> 直前に追加
    html = replace_once(html, '</body>', part('gigi_search_js.html') + '</body>', 'gigi search js')

    OUTPUT.write_text(html, encoding='utf-8')

    # 検証
    checks = {
        'div balance': html.count('<div') - html.count('</div>'),
        'section balance': html.count('<section') - html.count('</section>'),
    }
    ok = all(v == 0 for v in checks.values())
    for k, v in checks.items():
        print(f'  {k}: {v}' + ('' if v == 0 else '  ← NG!'))
    if not ok:
        sys.exit('ERROR: タグバランス不一致。生成結果を確認してください。')
    print(f'OK: {OUTPUT.name} を生成しました（{len(html):,} 文字）')


if __name__ == '__main__':
    main()
