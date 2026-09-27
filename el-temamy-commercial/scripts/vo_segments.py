import sherpa_onnx, numpy as np, scipy.io.wavfile as w, json, sys
d="vits-piper-ar_JO-kareem-medium"
def tts(ls):
    return sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(vits=sherpa_onnx.OfflineTtsVitsModelConfig(model=f"{d}/ar_JO-kareem-medium.onnx",tokens=f"{d}/tokens.txt",data_dir=f"{d}/espeak-ng-data",length_scale=ls,noise_scale=0.45,noise_scale_w=0.6),num_threads=4)))
# Script split into timed lines. Diacritics only steer pronunciation; wording is the approved script.
segs=json.load(open(sys.argv[1]))
out={}
cache={}
for k,(text,ls) in segs.items():
    if ls not in cache: cache[ls]=tts(ls)
    a=cache[ls].generate(text,sid=0,speed=1.0); x=np.array(a.samples,dtype=np.float32)
    thr=0.006; idx=np.nonzero(np.abs(x)>thr)[0]; x=x[max(idx[0]-300,0):idx[-1]+2500]
    w.write(f"vo_{k}.wav",a.sample_rate,(x*32767).astype(np.int16)); out[k]=round(len(x)/a.sample_rate,3)
print(out)
