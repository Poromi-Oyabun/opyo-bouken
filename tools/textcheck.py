# 誤字脱字チェック担当（レンダリングや公開の前に かならず通す）
#  1) CMテロップ：元の漢字の読み と 画面の ひらがな が 一致するか（janome で読みを出す）
#  2) ゲーム本文・テロップ共通：よくある 読みまちがい辞書、カッコの対応、同じ語の重なり
# 使い方: python3 textcheck.py [game.html ...]   → まちがいが あれば 終了コード1
import re, sys, os
D=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,D)

# よくある 読みまちがい（まちがい → ただしい）。見つけたら ここに たして 再発防止する
MISREAD={
 'だいがた':'おおがた（大型）','だいはば':'おおはば（大幅）','だいぜい':'おおぜい（大勢）',
 'ふいんき':'ふんいき（雰囲気）','こんにちわ':'こんにちは','こんばんわ':'こんばんは',
 'たいくかん':'たいいくかん（体育館）','いちにんで':'ひとりで（一人で）','せいいっぱつ':'せいいっぱい（精一杯）',
 'いっしょうけんめい':None,'ぜんぜんいい':None,
}
MISREAD={k:v for k,v in MISREAD.items() if v}
PAIRS=['「」','『』','（）','【】','()']

def kata2hira(s):return ''.join(chr(ord(c)-0x60) if 'ァ'<=c<='ヶ' else c for c in s)
def norm(s):return re.sub(r'[\s　]','',kata2hira(s))

_tk=None
def reading(src):
    global _tk
    from janome.tokenizer import Tokenizer
    if _tk is None:_tk=Tokenizer()
    out=[];pos=0
    for m in re.finditer(r'([^\[\]\s　]+?)\[([^\]]+)\]',src):
        pre=src[pos:m.start()]
        # 指定よみの 直前の 漢字列だけを 置きかえる
        km=re.search(r'[一-龯々]+$',m.group(1))
        head=m.group(1)[:km.start()] if km else m.group(1)
        out.append(_auto(pre+head));out.append(m.group(2));pos=m.end()
    out.append(_auto(src[pos:]));return norm(''.join(out))
def _auto(s):
    if not s:return ''
    return ''.join(t.reading if t.reading not in ('*','') else t.surface for t in _tk.tokenize(s))

def common(label,s,errs,warns,brackets=True,space=True):
    h=norm(s)
    for k,v in MISREAD.items():
        if norm(k) in h:errs.append(f'{label}: 「{k}」は まちがい → {v}  ／ {s!r}')
    for p in (PAIRS if brackets else []):
        if s.count(p[0])!=s.count(p[1]):errs.append(f'{label}: カッコ{p}の 数が あわない ／ {s!r}')
    for m in re.finditer(r'(?<!\S)(\S{2,}) \1(?!\S)',s):warns.append(f'{label}: 「{m.group(1)}」が つづけて 2回 ／ {s!r}')
    if re.search(r'([ぁ-ん])\1\1',s):warns.append(f'{label}: 同じ字が 3つ つづく ／ {s!r}')
    if space and re.search(r'\s$|^\s',s.replace('\n','')):warns.append(f'{label}: 前後に よけいな空白 ／ {s!r}')

def check_captions():
    from captions import CAP
    errs=[];warns=[]
    for k,(src,disp) in CAP.items():
        r=reading(src);d=norm(disp)
        if r!=d:errs.append(f'テロップ[{k}]: 読みが ちがう  元「{src}」→ {r} ／ 画面 {d}')
        common(f'テロップ[{k}]',disp,errs,warns)
    return errs,warns

def check_game(path):
    # ゲームは 1つの せりふが 何こかの 文字列に わかれていることが あるので
    # カッコの対応は 「同じ行の 文字列を つないだもの」で みる
    errs=[];warns=[];h=open(path,encoding='utf-8').read();byline={}
    for m in re.finditer(r"'((?:[^'\\\n]|\\.)*[ぁ-ん](?:[^'\\\n]|\\.)*)'",h):
        s=m.group(1).replace('\\n','\n');line=h.count('\n',0,m.start())+1
        if '${' in s or '<' in s:continue
        common(f'{os.path.basename(path)}:{line}',s,errs,warns,brackets=False,space=False)
        byline.setdefault(line,[]).append(s)
    for line,ss in byline.items():
        j=''.join(ss)
        for p in PAIRS[:4]:
            if j.count(p[0])!=j.count(p[1]):warns.append(f'{os.path.basename(path)}:{line}: カッコ{p}の 数が あわない（つなぎ文字列かも）／ {j[:60]!r}')
    return errs,warns

def main(args):
    E=[];W=[]
    if not args or '--captions' in args:
        e,w=check_captions();E+=e;W+=w
    for a in args:
        if a.endswith('.html'):e,w=check_game(a);E+=e;W+=w
    for w in W:print('［ちゅうい］',w)
    for e in E:print('［まちがい］',e)
    print(f'誤字脱字チェック：まちがい {len(E)}件 ／ ちゅうい {len(W)}件')
    return 1 if E else 0
if __name__=='__main__':sys.exit(main(sys.argv[1:]))
