# ChatGPTで つくった 2×2 の 絵（白い 背景）から、ゲーム用の ドット絵を きりだす
# 使い方: python3 tools/sprite_cut.py 絵.png なまえ1 なまえ2 なまえ3 なまえ4 [--boss なまえ,...] > out.json
#   ふつうの てき 58×42 いない、ボス 78×46 いない。出力は {なまえ: data:image/png;base64,...}
#   index.html の「v7 の 絵」の D に たして つかう（i.hd=1 で 等倍表示）
#   となりの 絵と つながって しまう ときは、BOX で きりだす はんいを してい する（v7 の クロノドンで 使った）
import sys, json, base64, io, numpy as np
from PIL import Image
from scipy import ndimage
args=[a for a in sys.argv[1:] if not a.startswith('--')]
boss=set(sys.argv[sys.argv.index('--boss')+1].split(',')) if '--boss' in sys.argv else set()
src,names=args[0],[a for a in args[1:] if a not in boss or True][:4]
a=np.array(Image.open(src).convert('RGB'));H,W=a.shape[:2];rgb=a.astype(int)
white=(rgb.min(2)>232)&((rgb.max(2)-rgb.min(2))<22);lab,n=ndimage.label(white)
edge=set(np.unique(np.r_[lab[0],lab[-1],lab[:,0],lab[:,-1]]))-{0};fg=ndimage.binary_opening(~np.isin(lab,list(edge)),iterations=1)
labg,ng=ndimage.label(ndimage.binary_dilation(fg,iterations=5));sizes=ndimage.sum(fg,labg,range(1,ng+1));cms=ndimage.center_of_mass(fg,labg,range(1,ng+1))
out={}
for qi,nm in enumerate(names):
    x0=(qi%2)*W//2;y0=(qi//2)*H//2
    mine=[i+1 for i,(cy,cx) in enumerate(cms) if x0<=cx<x0+W//2 and y0<=cy<y0+H//2];big=max(sizes[i-1] for i in mine)
    m=np.isin(labg,[i for i in mine if sizes[i-1]>big*0.06])&fg;ys,xs=np.nonzero(m)
    by0,by1,bx0,bx1=ys.min(),ys.max()+1,xs.min(),xs.max()+1
    rgba=np.zeros((by1-by0,bx1-bx0,4),np.uint8);rgba[:,:,:3]=a[by0:by1,bx0:bx1];rgba[:,:,3]=m[by0:by1,bx0:bx1]*255
    crop=Image.fromarray(rgba);mw,mh=(78,46) if nm in boss else (58,42);s=min(mw/crop.width,mh/crop.height)
    tw,th=max(1,round(crop.width*s)),max(1,round(crop.height*s));pm=np.array(crop).astype(float);pm[:,:,:3]*=pm[:,:,3:4]/255
    r=np.array(Image.fromarray(pm.astype(np.uint8)).resize((tw,th),Image.BOX)).astype(float);al=r[:,:,3]
    col=np.where(al[:,:,None]>0,r[:,:,:3]*255/np.maximum(al[:,:,None],1),0);alpha=(al>110).astype(np.uint8)*255
    q=Image.fromarray(np.clip(col,0,255).astype(np.uint8)).quantize(colors=48,method=Image.MEDIANCUT,dither=Image.NONE).convert('RGB')
    im=Image.fromarray(np.dstack([np.array(q),alpha]),'RGBA');im.save(nm+'.png');b=io.BytesIO();im.save(b,'PNG',optimize=True)
    out[nm]='data:image/png;base64,'+base64.b64encode(b.getvalue()).decode()
print(json.dumps(out))
