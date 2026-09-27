import sherpa_onnx, scipy.io.wavfile as w, numpy as np, sys
from scipy.signal import resample_poly
d='sherpa-onnx-whisper-small'
r=sherpa_onnx.OfflineRecognizer.from_whisper(encoder=f'{d}/small-encoder.int8.onnx',decoder=f'{d}/small-decoder.int8.onnx',tokens=f'{d}/small-tokens.txt',language='ar',task='transcribe',num_threads=4)
for f in sys.argv[1:]:
    sr,x=w.read(f); x=x.astype(np.float32)/32768
    if x.ndim>1: x=x.mean(1)
    if sr!=16000: x=resample_poly(x,16000,sr).astype(np.float32)
    s=r.create_stream(); s.accept_waveform(16000,x); r.decode_stream(s); print(f, '->', s.result.text)
