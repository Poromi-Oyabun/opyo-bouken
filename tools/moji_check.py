# 再発防止：ゲーム画面の 文字が にじんで 読めない ことを 防ぐ チェック
# キャンバス（176×176）に 小さい 文字を 書くと、スマホで 拡大した ときに ぼやける。
# 日本語の 文章（スタッフロール・せりふ など）は HTMLの 文字（--u 単位）で 出すこと。
# キャンバスに 書いて よいのは 数字や 1文字の 記号（ダメージ・z）だけ。
import re, sys, pathlib
src = pathlib.Path(__file__).resolve().parent.parent.joinpath('index.html').read_text(encoding='utf-8')
ALLOW = {"'z'", 'p.txt'}            # ダメージの 数字・ねむりの z
bad = []
for m in re.finditer(r"fillText\(([^,]+),", src):
    arg = m.group(1).strip()
    if arg in ALLOW: continue
    line = src.count('\n', 0, m.start()) + 1
    bad.append(f'{line}行目 fillText({arg}, …)')
for m in re.finditer(r"\.(?:big|sub|ln|w)\b[^{]*\{[^}]*font-size:calc\(var\(--u\)\*([\d.]+)\)", src):
    if float(m.group(1)) < 7: bad.append(f'{src.count(chr(10),0,m.start())+1}行目 文字が 小さすぎる（{m.group(1)}u）')
if bad:
    print('文字チェック：NG（キャンバスに 文章を 書いている／文字が 小さい）'); print('\n'.join(bad)); sys.exit(1)
print('文字チェック：OK（文章は すべて くっきりした HTMLの 文字）')
