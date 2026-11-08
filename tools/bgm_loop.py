# Google Flow の 曲を、つなぎ目の 分からない ループ曲に する（v7 で 使った やりかた）
# 使い方: python3 tools/bgm_loop.py 曲.mp3 なまえ  → bgm/なまえ.mp3 を つくり、BGMF に いれる [ループ開始, ループ終わり] を 表示
# 1) 拍ごとの 音の 特徴で「同じ ところ」A（前）と B（後ろ）を さがす
# 2) B の 手前 1.5秒を A の 手前と クロスフェードし、B の あとに A の つづき 0.25秒を つける（つなぎ目の 一致度 0.99 いじょう）
# 3) mp3 128kbps・48kHz・ステレオ（カバー画像は のぞく）。BGMF・BGM_V・MUSN・MUS_NEAR も わすれずに 更新
import sys, json, subprocess, numpy as np, librosa
src,name=sys.argv[1],sys.argv[2];sr=48000
y22,s22=librosa.load(src,sr=22050,mono=True);tempo,beats=librosa.beat.beat_track(y=y22,sr=s22,hop_length=512);bt=librosa.frames_to_time(beats,sr=s22,hop_length=512)
C=librosa.feature.chroma_cqt(y=y22,sr=s22,hop_length=512);M=librosa.power_to_db(librosa.feature.melspectrogram(y=y22,sr=s22,hop_length=512,n_mels=48))
Fb=librosa.util.sync(np.vstack([C*2,(M-M.mean())/(M.std()+1e-6)*0.5]),beats);rb=librosa.util.sync(librosa.feature.rms(y=y22,hop_length=512),beats)[0];med=np.median(rb)
nb=Fb.shape[1];Wn=12;spb=60/float(np.atleast_1d(tempo)[0]);best=None
for b in range(nb-Wn-1,nb//2,-1):
    if rb[min(nb-1,b+Wn)]<med*0.6:continue
    for a in range(Wn,b-int(40/spb)):
        sc=-(np.mean((Fb[:,a:a+Wn]-Fb[:,b:b+Wn])**2)+np.mean((Fb[:,a-Wn:a]-Fb[:,b-Wn:b])**2))
        if best is None or sc>best[0]:best=(sc,a,b)
A,B=bt[best[1]],bt[best[2]]
raw=subprocess.run(['ffmpeg','-v','error','-i',src,'-vn','-ar','48000','-ac','2','-f','f32le','-'],capture_output=True).stdout
y=np.frombuffer(raw,np.float32).reshape(-1,2);ia,ib=int(A*sr),int(B*sr);X=int(1.5*sr);t=np.linspace(0,1,X)[:,None]
body=y[:ib].copy();body[ib-X:ib]=y[ib-X:ib]*np.cos(t*np.pi/2)+y[ia-X:ia]*np.sin(t*np.pi/2);full=np.vstack([body,y[ia:ia+int(0.25*sr)]]).astype(np.float32)
subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar','48000','-ac','2','-i','-','-c:a','libmp3lame','-b:a','128k',f'bgm/{name}.mp3'],input=full.tobytes(),check=True)
z,_=librosa.load(f'bgm/{name}.mp3',sr=sr,mono=True);m=int(0.2*sr);bl=(-2,0)
for lag in range(-3000,3001):
    i=ia+lag;c=np.dot(z[i:i+m],z[ib:ib+m])/(np.linalg.norm(z[i:i+m])*np.linalg.norm(z[ib:ib+m])+1e-9)
    if c>bl[0]:bl=(c,lag)
print(json.dumps({name:[round(A+bl[1]/sr,4),round(B,4)]}),'一致度',round(bl[0],4))
