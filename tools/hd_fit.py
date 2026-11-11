# 元の 大きい 絵から、今 ゲームに 入って いる 小さい 絵と ぴったり 重なる 3ばいの 絵を つくる（位置あわせつき）
# 1) 小さい 絵が 元の 絵の どこを どの 倍率で 切った ものかを さがす（FFT の 相関）
# 2) その まわりの 絵を 3ばいの こまかさで 保存（hd/<なまえ>.webp）。小さい 絵の わくから はみ出す 分は meta の [左,上,右,下]（わくに 対する 割合）
import sys,re,json,base64,io,numpy as np
from PIL import Image
from scipy import ndimage
from scipy.signal import fftconvolve
R=3;U='/mnt/user-data/uploads/'
MAP={'09377183':(3,3,['nekodai','inoshishi','gorira','wani','nezuking','ookami','owashi','lion','tora']),
 'dcd72fda':(2,7,['noraneko','hato','araiguma','tanuki','saru','hebi','kinneko','nezumi','kaeru','itachi','fukurou','kuma','harinezumi','inko']),
 '08013a65':(2,2,['kurono','jikubat','golem','bannin']),'410d8769':(2,2,['anmo','meganeura','pureshio','konpuso']),
 '772bf745':(2,2,['anki','burakio','pakike','dirofo']),'b0d3bb60':(1,1,['insekiArt']),'477209a0':(2,2,['allo','toriko','brachio','nestArt']),
 '67a85bd5':(2,2,['dimetro','ramfo','mosa','diaanmo']),'f8dffb44':(2,2,['karno','parasauro','iguano','ovi']),
 'b29f5bfa':(2,2,['ketsu','magma','trex','swordArt']),'966af301':(2,2,['kintama','nijipute','rapboss','spino']),'d578d0f6':(2,2,['torike','sutego','raptor','putera'])}
html=open('/home/claude/work/committed_base.html',encoding='utf-8').read();EX={}
for m in re.finditer(r'[\"\']?([A-Za-z0-9_]+)[\"\']?\s*:\s*[\"\']data:image/png;base64,([A-Za-z0-9+/=]+)',html):
    if m.group(1) not in EX:EX[m.group(1)]=np.array(Image.open(io.BytesIO(base64.b64decode(m.group(2)))).convert('RGBA')).astype(float)
def seg(a):
    rgb=a.astype(int);bg=np.median(np.r_[rgb[:4].reshape(-1,3),rgb[-4:].reshape(-1,3)],0);d=np.abs(rgb-bg).max(2);tol=26 if bg.min()>200 else 34
    lab,n=ndimage.label(d<tol);edge=set(np.unique(np.r_[lab[0],lab[-1],lab[:,0],lab[:,-1]]))-{0};return ndimage.binary_opening(~np.isin(lab,list(edge)),iterations=1)
def match(reg,e,s):
    h,w=e.shape[:2];W=max(1,round(reg.shape[1]/s));H=max(1,round(reg.shape[0]/s))
    if W<w or H<h:return None
    I=np.array(Image.fromarray(reg).resize((W,H),Image.BOX)).astype(float);m=(e[:,:,3]>0).astype(float);n=m.sum();tot=np.zeros((H-h+1,W-w+1))
    mf=m[::-1,::-1]
    for c in range(3):
        ec=e[:,:,c]*m;tot+=fftconvolve(I[:,:,c]**2,mf,'valid')-2*fftconvolve(I[:,:,c],ec[::-1,::-1],'valid')+(ec**2).sum()
    j=np.unravel_index(np.argmin(tot),tot.shape);return (max(tot[j],0)/(3*n))**0.5,j[1],j[0]
meta={};rep=[];sheet=[]
only=sys.argv[1:]
for f,(rows,cols,keys) in MAP.items():
    a=np.array(Image.open(U+f+'-image.png').convert('RGB'));H,W=a.shape[:2];fg=seg(a)
    for i,k in enumerate(keys):
        if only and k not in only:continue
        e=EX[k];h,w=e.shape[:2];r,c=divmod(i,cols);cw,ch=W/cols,H/rows
        x0=int(max(0,c*cw-cw*0.3));x1=int(min(W,(c+1)*cw+cw*0.3));y0=int(max(0,r*ch-ch*0.3));y1=int(min(H,(r+1)*ch+ch*0.3));reg=a[y0:y1,x0:x1]
        best=None
        for s in np.arange(0.3*ch/h,1.25*ch/h,0.012*ch/h):
            q=match(reg,e,s)
            if q and(best is None or q[0]<best[0]):best=(q[0],s,q[1],q[2])
        s0=best[1]
        for s in np.arange(s0*0.975,s0*1.025,s0*0.0025):
            q=match(reg,e,s)
            if q and q[0]<best[0]:best=(q[0],s,q[1],q[2])
        sc,s,bx,by=best;X0=x0+bx*s;Y0=y0+by*s;X1=X0+w*s;Y1=Y0+h*s   # 小さい 絵の わく（元の 絵の 座標）
        ex=0.06;ax0=int(max(0,X0-ex*w*s));ay0=int(max(0,Y0-ex*h*s));ax1=int(min(W,X1+ex*w*s));ay1=int(min(H,Y1+ex*h*s))
        sub=fg[ay0:ay1,ax0:ax1];al=Image.fromarray(((e[:,:,3]>0)*255).astype(np.uint8)).resize((max(1,round(w*s)),max(1,round(h*s))),Image.NEAREST)
        allow=np.zeros_like(sub);iy0,ix0=int(round(Y0-ay0)),int(round(X0-ax0));A=np.array(al)>0;hh=min(A.shape[0],sub.shape[0]-iy0);ww=min(A.shape[1],sub.shape[1]-ix0);allow[iy0:iy0+hh,ix0:ix0+ww]=A[:hh,:ww]
        allow=ndimage.binary_dilation(allow,iterations=max(3,int(0.035*h*s)))
        m=sub&allow;m=ndimage.binary_fill_holes(m)|m;ys,xs=np.nonzero(m);bx0,bx1,by0,by1=xs.min()+ax0,xs.max()+1+ax0,ys.min()+ay0,ys.max()+1+ay0
        soft=ndimage.gaussian_filter(m.astype(float),0.8)[by0-ay0:by1-ay0,bx0-ax0:bx1-ax0]
        o=np.zeros((by1-by0,bx1-bx0,4),np.uint8);o[:,:,:3]=a[by0:by1,bx0:bx1];o[:,:,3]=np.clip(soft*2-0.5,0,1)*255
        k3=min(R/s,1.0)*1.0;tw,th=max(1,round((bx1-bx0)*R/s)),max(1,round((by1-by0)*R/s))
        pm=o.astype(float);pm[:,:,:3]*=pm[:,:,3:4]/255;rr=np.array(Image.fromarray(pm.astype(np.uint8)).resize((tw,th),Image.LANCZOS)).astype(float);al=rr[:,:,3]
        col=np.where(al[:,:,None]>0,rr[:,:,:3]*255/np.maximum(al[:,:,None],1),0);al=np.where(al<24,0,np.where(al>230,255,al))
        hi=Image.fromarray(np.dstack([np.clip(col,0,255),al]).astype(np.uint8),'RGBA');hi.save(k+'.webp','WEBP',quality=86,method=6,alpha_quality=92)
        meta[k]=[round((X0-bx0)/(w*s),4),round((Y0-by0)/(h*s),4),round((bx1-X1)/(w*s),4),round((by1-Y1)/(h*s),4)]
        rep.append((k,round(sc,1),round(s,2),meta[k],hi.size));sheet.append((k,hi,e))
        print(rep[-1],flush=True)
if not only:json.dump(meta,open('meta.json','w'))
else:
    M=json.load(open('meta.json'));M.update(meta);json.dump(M,open('meta.json','w'))
# 見くらべ用：左＝今の 絵（3ばいに のばした もの）、右＝新しい 絵を 同じ わくに かさねた もの
cw=260;Wd=Image.new('RGB',(cw*6,170*((len(sheet)+5)//6)),(70,60,110))
for i,(k,hi,e) in enumerate(sheet):
    h,w=e.shape[:2];x=(i%6)*cw+4;y=(i//6)*170+14;l,t,r,b=meta[k]
    ei=Image.fromarray(e.astype(np.uint8),'RGBA').resize((w*2,h*2),Image.NEAREST);Wd.paste(ei,(x,y+10),ei)
    h2=hi.resize((max(1,round(w*2*(1+l+r))),max(1,round(h*2*(1+t+b)))),Image.LANCZOS);Wd.paste(h2,(x+122-round(l*w*2)+8,y+10-round(t*h*2)),h2)
Wd.save('fit_'+(only[0] if only else 'all')+'.png')
