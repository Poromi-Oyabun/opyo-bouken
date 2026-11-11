import numpy as np,json
from PIL import Image
from scipy import ndimage
src=open('hdfit_b.py').read().split("meta={};rep=[]")[0];exec(src)
J=[('5c866ffc',1,2,0,'kinkabuto'),('a5090b1a',2,2,0,'kuwa'),('a5090b1a',2,2,2,'ari'),('a5090b1a',2,2,3,'kabuto'),('3e1018ed',2,2,3,'kamemushi'),('5ccfac02',1,1,0,'semi'),('0c3ef7a3',2,2,3,'hachi'),('deaae29d',1,1,0,'kabuking'),('a9530fd3',1,1,0,'okama')]
sheet=[];meta={}
for f,rows,cols,i,k in J:
    a=np.array(Image.open(U+f+'-image.png').convert('RGB'));H,W=a.shape[:2];fg=seg(a);r,c=divmod(i,cols)
    labg,ng=ndimage.label(ndimage.binary_dilation(fg,iterations=5));sizes=ndimage.sum(fg,labg,range(1,ng+1));cms=ndimage.center_of_mass(fg,labg,range(1,ng+1))
    x0,x1,y0,y1=c*W//cols,(c+1)*W//cols,r*H//rows,(r+1)*H//rows
    mine=[j+1 for j,(cy,cx) in enumerate(cms) if x0<=cx<x1 and y0<=cy<y1 and sizes[j]>0];big=max(sizes[j-1] for j in mine)
    frac=0.5 if k in('kinkabuto','kamemushi') else 0.06     # きらきら・におい の かざりは 今の 絵にも ないので はずす
    m=np.isin(labg,[j for j in mine if sizes[j-1]>big*frac])&fg;m=ndimage.binary_fill_holes(m)|m;ys,xs=np.nonzero(m);bx0,bx1,by0,by1=xs.min(),xs.max()+1,ys.min(),ys.max()+1
    soft=ndimage.gaussian_filter(m.astype(float),0.8)[by0:by1,bx0:bx1];o=np.zeros((by1-by0,bx1-bx0,4),np.uint8);o[:,:,:3]=a[by0:by1,bx0:bx1];o[:,:,3]=np.clip(soft*2-0.5,0,1)*255
    e=EX[k];h,w=e.shape[:2];asp=(bx1-bx0)/(by1-by0);ga=w/h
    # わくの 中に たてよこ比を たもって 入れる（下そろえ・よこは まん中）。meta は わくに 対する はみ出し（マイナス＝内がわ）
    if asp>ga:tw=w;th=w/asp
    else:th=h;tw=h*asp
    l=-(w-tw)/2/w;t=-(h-th)/h;meta[k]=[round(l,4),round(t,4),round(l,4),0]
    pm=o.astype(float);pm[:,:,:3]*=pm[:,:,3:4]/255;rr=np.array(Image.fromarray(pm.astype(np.uint8)).resize((round(tw*3),round(th*3)),Image.LANCZOS)).astype(float);al=rr[:,:,3]
    col=np.where(al[:,:,None]>0,rr[:,:,:3]*255/np.maximum(al[:,:,None],1),0);al=np.where(al<24,0,np.where(al>230,255,al))
    hi=Image.fromarray(np.dstack([np.clip(col,0,255),al]).astype(np.uint8),'RGBA');hi.save(k+'.webp','WEBP',quality=86,method=6,alpha_quality=92)
    print(k,(w,h),round(ga,2),round(asp,2),meta[k],hi.size);sheet.append((k,hi,e))
json.dump(meta,open('meta_bbox.json','w'))
Wd=Image.new('RGB',(9*300,150),(70,60,110))
for i,(k,hi,e) in enumerate(sheet):
    h,w=e.shape[:2];x=i*300+4;ei=Image.fromarray(e.astype(np.uint8),'RGBA').resize((w*2,h*2),Image.NEAREST);Wd.paste(ei,(x,10),ei)
    l,t,r,b=meta[k];h2=hi.resize((round(w*2*(1+l+r)),round(h*2*(1+t+b))),Image.LANCZOS);Wd.paste(h2,(x+150-round(l*w*2),10-round(t*h*2)),h2)
Wd.save('fit_bbox.png')
