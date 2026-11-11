# ChatGPTの 絵（白い 背景）から、マップ用（小）と 会話用（大）の 2つの 大きさで きりだす
# 使い方: python3 cut2.py 絵.png なまえ1 なまえ2 [なまえ3 なまえ4]  → out_<絵>.json {なまえ:小, なまえ_L:大}
import sys, json, base64, io, numpy as np
from PIL import Image
from scipy import ndimage
src,names=sys.argv[1],sys.argv[2:6]
a=np.array(Image.open(src).convert('RGB'));H,W=a.shape[:2];rgb=a.astype(int)
white=(rgb.min(2)>232)&((rgb.max(2)-rgb.min(2))<22);lab,n=ndimage.label(white)
edge=set(np.unique(np.r_[lab[0],lab[-1],lab[:,0],lab[:,-1]]))-{0};fg=ndimage.binary_opening(~np.isin(lab,list(edge)),iterations=1)
labg,ng=ndimage.label(ndimage.binary_dilation(fg,iterations=5));sizes=ndimage.sum(fg,labg,range(1,ng+1));cms=ndimage.center_of_mass(fg,labg,range(1,ng+1))
def shrink(crop,mw,mh,cols,thr):
    s=min(mw/crop.width,mh/crop.height);tw,th=max(1,round(crop.width*s)),max(1,round(crop.height*s))
    pm=np.array(crop).astype(float);pm[:,:,:3]*=pm[:,:,3:4]/255
    r=np.array(Image.fromarray(pm.astype(np.uint8)).resize((tw,th),Image.BOX)).astype(float);al=r[:,:,3]
    col=np.where(al[:,:,None]>0,r[:,:,:3]*255/np.maximum(al[:,:,None],1),0);alpha=(al>thr).astype(np.uint8)*255
    q=Image.fromarray(np.clip(col,0,255).astype(np.uint8)).quantize(colors=cols,method=Image.MEDIANCUT,dither=Image.NONE).convert('RGB')
    return Image.fromarray(np.dstack([np.array(q),alpha]),'RGBA')
def outline(im):
    a=np.array(im);al=a[:,:,3]>0;p=np.pad(al,1);a2=np.zeros((a.shape[0]+2,a.shape[1]+2,4),np.uint8);a2[1:-1,1:-1]=a
    nb=ndimage.binary_dilation(p,structure=np.array([[0,1,0],[1,1,1],[0,1,0]]))&~p;a2[nb]=(42,26,18,255);return Image.fromarray(a2,'RGBA')
def uri(im):
    b=io.BytesIO();im.save(b,'PNG',optimize=True);return 'data:image/png;base64,'+base64.b64encode(b.getvalue()).decode()
out={};rep=[]
for qi,nm in enumerate(names):
    x0=(qi%2)*W//2;y0=(qi//2)*H//2
    mine=[i+1 for i,(cy,cx) in enumerate(cms) if x0<=cx<x0+W//2 and y0<=cy<y0+H//2];big=max(sizes[i-1] for i in mine)
    m=np.isin(labg,[i for i in mine if sizes[i-1]>big*0.02])&fg;ys,xs=np.nonzero(m)
    by0,by1,bx0,bx1=ys.min(),ys.max()+1,xs.min(),xs.max()+1
    rep.append((nm,int(bx0),int(by0),int(bx1),int(by1),'EDGE!' if bx0<=1 or by0<=1 or bx1>=W-1 or by1>=H-1 else 'ok'))
    rgba=np.zeros((by1-by0,bx1-bx0,4),np.uint8);rgba[:,:,:3]=a[by0:by1,bx0:bx1];rgba[:,:,3]=m[by0:by1,bx0:bx1]*255
    crop=Image.fromarray(rgba);crop.save(nm+'_full.png')
    S=outline(shrink(crop,26,28,28,120));L=shrink(crop,66,70,56,110);S.save(nm+'.png');L.save(nm+'_L.png');out[nm]=uri(S);out[nm+'_L']=uri(L)
json.dump(out,open('out_'+src.split('.')[0]+'.json','w'));print(rep,{k:len(v) for k,v in out.items()})
