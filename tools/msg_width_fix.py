# メッセージの まどは 1行に 全角 19文字（空白・数字は 0.5）、4行まで。こえる 行だけを 空白の ところで 2つに 分ける。
# それで 4行を こえる ときだけ、文ぜんたいを 組み直す。話し手の 名前（「 の 前）は 分けない。ノート・てきの 定義・えらぶ 項目は さわらない
import re,sys,unicodedata
LIM=19.0;NB='\u0001'
def w(t):return sum(1 if unicodedata.east_asian_width(c) in'WFA' else 0.5 for c in t.replace(NB,' '))
def split_line(l):
    out=[]
    while w(l)>LIM:
        cands=[i for i,c in enumerate(l) if c==' ' and w(l[:i])<=LIM]
        if not cands:return None
        rest_ok=[i for i in cands if w(l[i+1:])<=LIM]
        i=cands[-1]
        out.append(l[:i]);l=l[i+1:]
    out.append(l);return out
def greedy(text):
    words=[x for x in re.split(r'[ ]|\\n',text) if x!=''];lines=[];cur=''
    for wd in words:
        t=wd if not cur else cur+' '+wd
        if w(t)<=LIM:cur=t
        else:
            if cur:lines.append(cur)
            cur=wd
    if cur:lines.append(cur)
    return lines
def fix(t):
    k=t.find('「');p=t.replace('ホーキド はかせ','ホーキド'+NB+'はかせ')
    t=p
    if 0<k<12 and '\\n' not in t[:k]:p=t[:k].replace(' ',NB)+t[k:]
    ls=p.split('\\n');out=[];carry=None
    for l in ls:
        if carry is not None:        # 前の 行から こぼれた 分は、つぎの 行と つなげられるなら つなぐ
            if w(carry+' '+l)<=LIM:l=carry+' '+l
            else:out.append(carry)
            carry=None
        if w(l)<=LIM:out.append(l);continue
        r=split_line(l)
        if r is None:return None
        out+=r[:-1];carry=r[-1]
    if carry is not None:out.append(carry)
    g2=greedy(p)
    if len(g2)<len(out) and all(w(l)<=LIM for l in g2):out=g2
    if len(out)>4 or any(w(l)>LIM for l in out):return None
    return '\\n'.join(out).replace(NB,' ')
apply='--apply' in sys.argv;bad=[]
for f in [a for a in sys.argv[1:] if not a.startswith('--')]:
    s=open(f,encoding='utf-8').read();out=[];pos=0;n=0
    spans=[(m.start(),m.end()) for m in re.finditer(r'Object\.assign\(NOTES9,\{.*?\}\}\);',s,re.S)]+[(m.start(),m.end()) for m in re.finditer(r'NOTES9=\{.*?\}\};',s,re.S)]
    spans+=[(m.start(),m.end()) for m in re.finditer(r'Object\.assign\(EN,\{.*?\}\)\}\);',s,re.S)]+[(m.start(),m.end()) for m in re.finditer(r'choose\(\[.*?\]',s)]
    for m in re.finditer(r"'((?:[^'\\\n]|\\.)*)'",s):
        if any(a<=m.start()<b for a,b in spans):continue
        t=m.group(1)
        if not re.search(r'[ぁ-ん]',t) or all(w(l)<=LIM for l in t.split('\\n')):continue
        r=fix(t)
        if r is None:bad.append((f,t));continue
        out.append(s[pos:m.start(1)]);out.append(r);pos=m.end(1);n+=1
    out.append(s[pos:])
    if apply:open(f,'w',encoding='utf-8').write(''.join(out))
    print(f,'fixed',n)
print('needs hand fix:',len(bad))
for f,t in bad:print(' ',f,t)
