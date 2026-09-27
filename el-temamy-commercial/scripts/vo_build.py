import numpy as np, scipy.io.wavfile as w, json, subprocess, sys
sr=22050
def load(k):
    s,x=w.read(f'vo_{k}.wav'); return x.astype(np.float32)/32768
def squeeze(x,maxgap=0.11,keep=0.07):
    """Shorten long internal silences (breaths between words) - keeps speech untouched."""
    f=int(0.01*sr); n=len(x)//f; rms=np.array([np.sqrt(np.mean(x[i*f:(i+1)*f]**2)) for i in range(n)])
    sil=rms<0.008; out=[]; i=0
    while i<n:
        j=i
        while j<n and sil[j]==sil[i]: j+=1
        seg=x[i*f:j*f]
        if sil[i] and (j-i)*0.01>maxgap and i>0 and j<n:
            k=int(keep*sr); seg=np.concatenate([seg[:k//2],seg[-k//2:]])
        out.append(seg); i=j
    out.append(x[n*f:]); return np.concatenate(out)
plan=json.load(open(sys.argv[1]))
T=np.zeros(int(13*sr),np.float32); t=None
for k,start in plan:
    x=squeeze(load(k))
    # 8ms fades to avoid clicks
    fl=int(0.008*sr); x[:fl]*=np.linspace(0,1,fl); x[-fl:]*=np.linspace(1,0,fl)
    if isinstance(start,str): start=t+float(start)
    i=int(start*sr); T[i:i+len(x)]+=x; t=start+len(x)/sr; print(k,round(start,2),round(t,2))
w.write('vo_full.wav',sr,(T*32767).astype(np.int16))
