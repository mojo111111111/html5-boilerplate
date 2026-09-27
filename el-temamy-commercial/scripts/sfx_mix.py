"""Non-musical sound design: every effect is shaped/filtered noise or short transients (no oscillators,
no pitched tones, no rhythm). VO is placed on top with gentle ducking."""
import numpy as np, scipy.io.wavfile as w
from scipy.signal import butter, sosfilt, resample_poly, stft, istft
SR = 48000; DUR = 12.0
rng = np.random.default_rng(7)
track = np.zeros(int(SR * DUR) + SR)

def bp(x, lo, hi, order=4):
    return sosfilt(butter(order, [lo, hi], 'bandpass', fs=SR, output='sos'), x)
def lp(x, f, order=4): return sosfilt(butter(order, f, 'lowpass', fs=SR, output='sos'), x)
def hp(x, f, order=4): return sosfilt(butter(order, f, 'highpass', fs=SR, output='sos'), x)
def add(x, t, g):
    i = int(t * SR); n = min(len(x), len(track) - i); track[i:i + n] += x[:n] * g

def env(n, att, rel, shape='sin'):
    t = np.linspace(0, 1, n)
    a = np.clip(t / max(att, 1e-4), 0, 1); r = np.clip((1 - t) / max(rel, 1e-4), 0, 1)
    return (np.sin(a * np.pi / 2) ** 2) * (np.sin(r * np.pi / 2) ** 2)

def whoosh(dur, f0, f1, att=0.5, rel=0.5, width=0.9):
    """Air whoosh: white noise through a band that sweeps f0 -> f1 (STFT mask)."""
    n = int(dur * SR); x = rng.standard_normal(n)
    f, tt, Z = stft(x, SR, nperseg=1024)
    prog = np.clip(tt / dur, 0, 1); fc = f0 * (f1 / f0) ** prog
    M = np.exp(-(np.log2(np.maximum(f[:, None], 1) / fc[None, :]) ** 2) / (2 * width ** 2))
    _, y = istft(Z * M, SR, nperseg=1024); y = y[:n]
    y *= env(n, att, rel); return y / (np.abs(y).max() + 1e-9)

def tap():
    n = int(0.09 * SR); t = np.arange(n) / SR
    click = hp(rng.standard_normal(n), 1800) * np.exp(-t / 0.0025)
    body = lp(rng.standard_normal(n), 320) * np.exp(-t / 0.018)
    y = click * 0.6 + body * 1.6; return y / np.abs(y).max()

def crinkle(dur, density=260, lo=1200, hi=7500, att=0.15, rel=0.5):
    """Paper rustle: random micro-transients (irregular, non-rhythmic) + a soft noise bed."""
    n = int(dur * SR); y = np.zeros(n)
    k = int(density * dur)
    for pos in rng.integers(0, n - 400, k):
        L = rng.integers(60, 380); a = rng.uniform(.2, 1) ** 2
        y[pos:pos + L] += rng.standard_normal(L) * np.exp(-np.arange(L) / (L / 4)) * a
    y = bp(y, lo, hi) + bp(rng.standard_normal(n), lo, hi) * 0.05
    y *= env(n, att, rel); return y / (np.abs(y).max() + 1e-9)

def thud(dur=0.16):
    n = int(dur * SR); t = np.arange(n) / SR
    y = lp(rng.standard_normal(n), 220) * np.exp(-t / 0.035) + bp(rng.standard_normal(n), 400, 1500) * np.exp(-t / 0.012) * 0.3
    return y / np.abs(y).max()

def notif_click():
    n = int(0.12 * SR); y = np.zeros(n); t = np.arange(900) / SR
    for off, g in [(0, 1.0), (int(0.055 * SR), 0.7)]:
        y[off:off + 900] += bp(rng.standard_normal(900), 2500, 7000) * np.exp(-t / 0.0022) * g
    return y / np.abs(y).max()

def scan(dur):
    """Scanner: soft band-limited air that brightens as the line moves (no hum, no tone)."""
    y = whoosh(dur, 2600, 5200, att=0.25, rel=0.3, width=0.6)
    grit = crinkle(dur, density=90, lo=3000, hi=9000, att=0.2, rel=0.3) * 0.25
    return y + grit

# ---------- events (seconds, gain) ----------
add(whoosh(0.35, 1800, 3000, .3, .7), 0.06, 0.05)            # point appears
add(whoosh(0.9, 250, 1400, .55, .45), 0.38, 0.14)             # point expands into the phone
add(thud(0.14), 1.16, 0.05)                                    # phone settles
add(whoosh(0.95, 500, 2200, .5, .5), 2.02, 0.10)              # UI pieces lift off
add(whoosh(0.4, 2500, 1200, .3, .6), 3.05, 0.05)              # pieces clear
add(tap(), 3.27, 0.30)                                         # finger tap on upload button
add(whoosh(0.32, 1800, 5000, .25, .6), 3.5, 0.11)             # screen swipe/push
add(crinkle(0.5, 180), 4.58, 0.13)                             # prescription paper lifts
add(scan(0.72), 4.96, 0.07)                                    # scanning
add(whoosh(0.9, 700, 2600, .35, .55), 5.7, 0.10)              # scan line peels into motion path
add(crinkle(0.55, 320, att=.1, rel=.6), 6.26, 0.15)            # paper bag opens/appears
add(whoosh(0.4, 900, 2400, .4, .6), 6.44, 0.04)
add(crinkle(0.3, 400, att=.05, rel=.7), 6.98, 0.12); add(thud(), 7.2, 0.10)    # item into bag
add(crinkle(0.3, 400, att=.05, rel=.7), 7.13, 0.11); add(thud(), 7.36, 0.09)   # second item
add(notif_click(), 7.44, 0.20)                                 # order confirmed click
add(crinkle(0.45, 150), 7.72, 0.06)                            # bag moves
add(whoosh(1.15, 350, 1500, .45, .5), 7.84, 0.07)             # path draws ground + home
add(crinkle(0.9, 70, att=.3, rel=.4), 8.4, 0.05)               # bag travelling
add(thud(0.18), 9.28, 0.05)                                    # arrives at the door
add(whoosh(1.0, 200, 900, .6, .5), 9.4, 0.14)                 # warm light opens into brand frame
add(whoosh(0.8, 900, 300, .2, .8), 10.2, 0.04)                # settle

sfx = track[:int(SR * DUR)]
# ---------- voice ----------
sr, vo = w.read('vo_full.wav'); vo = vo.astype(np.float64) / 32768
vo = resample_poly(vo, 320, 147)[:len(sfx)]; vo = np.pad(vo, (0, len(sfx) - len(vo)))
vo = hp(vo, 85, 2)
# gentle presence lift (~+2.5 dB around 2-5 kHz) and light compression for a warm, clear read
vo = vo + bp(vo, 2000, 5000, 2) * 0.33
e = np.sqrt(lp(vo ** 2, 12, 2).clip(0)); thr = 0.08
g = np.where(e > thr, (thr + (e - thr) / 2.5) / np.maximum(e, 1e-9), 1.0); vo = vo * g
vo /= np.abs(vo).max(); vo *= 0.85
# ducking: sfx dip under the voice
venv = np.sqrt(lp(vo ** 2, 6, 2).clip(0)); venv /= venv.max()
mix = vo + sfx * (1 - 0.45 * np.clip(venv * 3, 0, 1))
fade = int(0.25 * SR); mix[-fade:] *= np.linspace(1, 0, fade) ** 2
mix /= np.abs(mix).max(); mix *= 0.89
w.write('mix.wav', SR, (np.stack([mix, mix], 1) * 32767).astype(np.int16))
w.write('sfx_only.wav', SR, (sfx / np.abs(sfx).max() * 0.8 * 32767).astype(np.int16))
print('ok', len(mix) / SR)
