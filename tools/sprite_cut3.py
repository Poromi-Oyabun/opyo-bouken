# ChatGPTの 絵（白い 背景・2×2）から、こうがしつ（3ばい）の 絵を きりだす。画面は 176×176 を 3ばいで かいて いるので、
# 「ゲームの 中での 大きさ（論理サイズ）」の 3ばいの 画素で 保存する。EI に 入れる とき i.hd=3 を つける
# 使い方: python3 cut3.py 絵.png 出力.json よこ たて なまえ1 [なまえ2 なまえ3 なまえ4] [--L よこ たて]
#   例（なかま）: python3 cut3.py a4.png out.json 26 28 haru hiro yuu kayobe --L 84 92   → haru（マップ用）と haru_L（会話用）
#   例（てき）  : python3 cut3.py d4.png out.json 58 42 karno parasauro iguano ovi
import sys, json, base64, io, numpy as np
from PIL import Image
from scipy import ndimage
R=3;av=sys.argv[1:];L=None
if '--L' in av:i=av.index('--L');L=(int(av[i+1]),int(av[i+2]));av=av[:i]
src,outp,mw,mh=av[0],av[1],int(av[2]),int(av[3]);names=av[4:8]
a=np.array(Image.open(src).convert('RGB'));H,W=a.shape[:2];rgb=a.astype(int)
white=(rgb.min(2)>232)&((rgb.max(2)-rgb.min(2))<22);lab,n=ndimage.label(white)
edge=set(np.unique(np.r_[lab[0],lab[-1],lab[:,0],lab[:,-1]]))-{0};fg=ndimage.binary_opening(~np.isin(lab,list(edge)),iterations=1)
labg,ng=ndimage.label(ndimage.binary_dilation(fg,iterations=5));sizes=ndimage.sum(fg,labg,range(1,ng+1));cms=ndimage.center_of_mass(fg,labg,range(1,ng+1))
def shrink(crop,w,h,cols):
    s=min(w*R/crop.width,h*R/crop.height,1.0);tw,th=max(1,round(crop.width*s)),max(1,round(crop.height*s))
    pm=np.array(crop).astype(float);pm[:,:,:3]*=pm[:,:,3:4]/255
    r=np.array(Image.fromarray(pm.astype(np.uint8)).resize((tw,th),Image.LANCZOS)).astype(float);al=r[:,:,3]
    col=np.where(al[:,:,None]>0,r[:,:,:3]*255/np.maximum(al[:,:,None],1),0)
    q=Image.fromarray(np.clip(col,0,255).astype(np.uint8)).quantize(colors=cols,method=Image.MEDIANCUT,dither=Image.NONE).convert('RGB')
    al=np.where(al<24,0,np.where(al>230,255,al)).astype(np.uint8)
    return Image.fromarray(np.dstack([np.array(q),al]),'RGBA')
def uri(im):
    b=io.BytesIO();im.save(b,'PNG',optimize=True);return 'data:image/png;base64,'+base64.b64encode(b.getvalue()).decode()
out={};rep=[]
for qi,nm in enumerate(names):
    x0=(qi%2)*W//2;y0=(qi//2)*H//2
    mine=[i+1 for i,(cy,cx) in enumerate(cms) if x0<=cx<x0+W//2 and y0<=cy<y0+H//2];big=max(sizes[i-1] for i in mine)
    m=np.isin(labg,[i for i in mine if sizes[i-1]>big*0.02])&fg;m=ndimage.binary_fill_holes(m)|m;ys,xs=np.nonzero(m)
    by0,by1,bx0,bx1=ys.min(),ys.max()+1,xs.min(),xs.max()+1
    soft=ndimage.gaussian_filter(m.astype(float),0.8)[by0:by1,bx0:bx1]
    rgba=np.zeros((by1-by0,bx1-bx0,4),np.uint8);rgba[:,:,:3]=a[by0:by1,bx0:bx1];rgba[:,:,3]=np.clip(soft*2-0.5,0,1)*255
    crop=Image.fromarray(rgba)
    S=shrink(crop,mw,mh,96);S.save(nm+'_3x.png');out[nm]=uri(S)
    if L:B=shrink(crop,L[0],L[1],128);B.save(nm+'_L3x.png');out[nm+'_L']=uri(B)
    rep.append((nm,S.size,'EDGE!' if bx0<=1 or by0<=1 or bx1>=W-1 or by1>=H-1 else 'ok'))
json.dump(out,open(outp,'w'));print(rep,sum(len(v) for v in out.values())//1024,'KB')
