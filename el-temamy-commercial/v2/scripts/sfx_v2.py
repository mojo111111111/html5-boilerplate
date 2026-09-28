"""v2 soundtrack: Foley/SFX only. No voice, no music. Every sound is shaped noise or a short
transient (no oscillators, no pitch, no rhythm). Clicks are low-passed to avoid harsh highs."""
import numpy as np, scipy.io.wavfile as w
from scipy.signal import butter, sosfilt, stft, istft
SR = 48000; DUR = 20.0
rng = np.random.default_rng(11)
track = np.zeros(int(SR * DUR) + SR)

def bp(x, lo, hi, o=4): return sosfilt(butter(o, [lo, hi], 'bandpass', fs=SR, output='sos'), x)
def lp(x, f, o=4): return sosfilt(butter(o, f, 'lowpass', fs=SR, output='sos'), x)
def hp(x, f, o=4): return sosfilt(butter(o, f, 'highpass', fs=SR, output='sos'), x)
def norm(y): return y / (np.abs(y).max() + 1e-9)
def add(x, t, g):
    i = int(t * SR); n = min(len(x), len(track) - i); track[i:i + n] += x[:n] * g
def env(n, att, rel):
    t = np.linspace(0, 1, n)
    a = np.clip(t / max(att, 1e-4), 0, 1); r = np.clip((1 - t) / max(rel, 1e-4), 0, 1)
    return (np.sin(a * np.pi / 2) ** 2) * (np.sin(r * np.pi / 2) ** 2)

def whoosh(dur, f0, f1, att=.5, rel=.5, width=.9):
    n = int(dur * SR); x = rng.standard_normal(n)
    f, tt, Z = stft(x, SR, nperseg=1024)
    fc = f0 * (f1 / f0) ** np.clip(tt / dur, 0, 1)
    M = np.exp(-(np.log2(np.maximum(f[:, None], 1) / fc[None, :]) ** 2) / (2 * width ** 2))
    _, y = istft(Z * M, SR, nperseg=1024); y = y[:n] * env(n, att, rel); return norm(lp(y, 9000))

def tap():
    n = int(.09 * SR); t = np.arange(n) / SR
    y = lp(hp(rng.standard_normal(n), 1200), 5000) * np.exp(-t / .0025) * .55 + lp(rng.standard_normal(n), 300) * np.exp(-t / .016) * 1.6
    return norm(y)

def soft_click(decay=.0028, lo=1500, hi=4800):
    n = int(.05 * SR); t = np.arange(n) / SR
    return norm(bp(rng.standard_normal(n), lo, hi) * np.exp(-t / decay))

def confirm():            # dry two-part click, second slightly softer (no pitch)
    y = np.zeros(int(.12 * SR)); a = soft_click(); b = soft_click()
    y[:len(a)] += a; o = int(.048 * SR); y[o:o + len(b)] += b * .6; return norm(y)

def shutter():            # soft mechanical camera tap: two muffled transients
    y = np.zeros(int(.14 * SR)); a = soft_click(.004, 700, 3800); b = soft_click(.006, 500, 3000)
    y[:len(a)] += a; o = int(.07 * SR); y[o:o + len(b)] += b * .8; return norm(y + np.pad(tap(), (0, len(y) - len(tap()))) * .5)

def crinkle(dur, density=240, lo=1000, hi=6500, att=.15, rel=.5):
    n = int(dur * SR); y = np.zeros(n)
    for pos in rng.integers(0, n - 400, int(density * dur)):
        L = rng.integers(60, 360); y[pos:pos + L] += rng.standard_normal(L) * np.exp(-np.arange(L) / (L / 4)) * rng.uniform(.2, 1) ** 2
    y = bp(y, lo, hi) + bp(rng.standard_normal(n), lo, hi) * .05
    return norm(y * env(n, att, rel))

def thud(dur=.18, f=200):
    n = int(dur * SR); t = np.arange(n) / SR
    return norm(lp(rng.standard_normal(n), f) * np.exp(-t / .035) + bp(rng.standard_normal(n), 400, 1400) * np.exp(-t / .012) * .25)

def scan(dur):             # soft electronic sweep: band-limited air rising, no hum or tone
    return norm(whoosh(dur, 1800, 4200, .2, .3, .55) + crinkle(dur, 60, 2500, 7000, .2, .3) * .2)

E = [  # (sound, time s, gain)
    (whoosh(1.0, 300, 1300, .55, .45), 0.15, .12),       # logo reveal: soft air
    (whoosh(1.0, 180, 800, .5, .5), 2.3, .12),           # tile becomes the phone
    (tap(), 4.72, .26),                                  # tap on a category
    (whoosh(.34, 1500, 4000, .25, .6), 4.95, .08),       # screen push
    (whoosh(.5, 1200, 3200, .35, .6), 7.6, .07),         # wipe to loyalty
    (confirm(), 9.33, .16),                              # points emphasis
    (whoosh(.34, 1500, 4000, .25, .6), 10.5, .08),       # screen push
    (shutter(), 11.75, .24),                             # camera / new-prescription tap
    (scan(1.15), 12.52, .075),                           # scan line
    (whoosh(.95, 600, 2200, .35, .55), 14.3, .09),       # line leaves the phone
    (crinkle(.55, 300, att=.1, rel=.6), 14.85, .13),     # paper bag
    (thud(), 15.42, .10), (crinkle(.3, 380, att=.05, rel=.7), 15.4, .08),   # bag settles
    (confirm(), 15.95, .16),                             # order confirmed
    (whoosh(1.0, 300, 1300, .45, .5), 16.55, .07),       # travel to the home
    (thud(.2, 170), 17.82, .09),                         # package placed at the door
    (whoosh(.7, 250, 900, .5, .5), 17.85, .08),          # light opens into brand frame
    (np.concatenate([soft_click(.004, 900, 3500), np.zeros(10)]) + 0, 18.56, .12),  # final dry confirmation
    (thud(.22, 140), 18.56, .06),
]
for x, t, g in E: add(x, t, g)
mix = track[:int(SR * DUR)]
fade = int(.3 * SR); mix[-fade:] *= 0
mix = norm(mix) * .5
w.write('sfx_v2.wav', SR, (np.stack([mix, mix], 1) * 32767).astype(np.int16))
print('ok')
