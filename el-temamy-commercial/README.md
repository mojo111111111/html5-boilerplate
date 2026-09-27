# EL TEMAMY PHARMACY: 12 s vertical commercial

The final file is `el-temamy-commercial.mp4`: 1080×1920 (9:16), 60 fps, 12.0 s, H.264 High, AAC stereo 48 kHz, loudness normalized to −14 LUFS.

## Storyboard (one continuous shot)

| Time | Scene | On-screen Arabic |
|---|---|---|
| 0.0–2.0 | An orange point expands into a phone that shows the real home screen, with a slow push-in | صيدلية في كل بيت |
| 2.0–4.0 | The phone turns slightly toward the camera. Real UI pieces (offer banner, categories, product cards) lift off the screen. A tap on the real upload button pushes to the prescription screen | اطلب عبر التطبيق |
| 4.0–6.0 | The camera locks onto the prescription. The real prescription card lifts forward and an orange scan line passes over it | صوّر روشتتك أو أدويتك |
| 6.0–7.7 | The scan line peels off into a motion path and lands on an orange paper bag. The two real product cards drop into the bag and an order check appears | طلبك بيتجهز |
| 7.7–9.5 | The path draws the ground and a simple home outline. The bag travels to the door and warm light opens | توصيل لحد عندك |
| 9.5–12.0 | The door light expands into the brand frame: original logo, headline, and app call to action. The frame is fully settled at 10.4 s and holds for 1.6 s | صيدلية في كل بيت · اطلب عبر التطبيق |

## Asset handling
- **Logo:** the supplied logo is used as-is. The white mark was separated from its orange background with an alpha key only; its colors and geometry are unchanged. Recompositing it onto the original background gives a mean error below 1/255.
- **Screenshots:** the real screens were cut out of the supplied store images using crops, uniform scaling and rounded-corner masks. The home-screen phone is tilted 9.93° in the source, so that screen was straightened with a pure rotation. No UI was redrawn or invented, and no text inside the screenshots was changed.
- **Product imagery:** only the two real product cards from the home screen appear. There is no invented packaging.
- **Arabic copy:** only the five approved phrases appear. The "صيدليات التمامي" line under the logo is part of the logo itself. The headlines are set in Cairo (Google Fonts) and rendered by Chromium, so the shaping is correct right-to-left.

## Audio
- **No music of any kind.** Every effect is filtered noise or a short transient: whooshes, a finger tap, a swipe, paper rustle, a scanner, bag and package movement, and a double click for the order notification. A spectral check confirms there are no sustained pitched components.
- **Voiceover:** the approved script is read by an offline neural Arabic male voice (Piper `ar_JO-kareem`) through sherpa-onnx. It is timed so that "صيدلية في كل بيت" lands with the end-frame headline. Diacritics in `scripts/segs_final.json` only guide pronunciation; the words are the script. I checked intelligibility by running the audio back through Whisper-small.

## Rebuild
```
python3 scripts/prep_assets.py               # screens, UI pieces, keyed logo -> web/img
python3 scripts/vo_segments.py scripts/segs_final.json && python3 scripts/vo_build.py scripts/plan.json
python3 scripts/sfx_mix.py                   # -> mix.wav
FFMPEG=/path/to/ffmpeg node scripts/render.mjs video video_silent.mp4 60
ffmpeg -i video_silent.mp4 -i mix.wav -c:v copy -af loudnorm=I=-14:TP=-1.5 -c:a aac -b:a 192k -shortest el-temamy-commercial.mp4
```
The voice steps need the sherpa-onnx models `vits-piper-ar_JO-kareem-medium` and `sherpa-onnx-whisper-small` (the latter only for QC) in the working directory. The whole animation is `web/index.html`, driven frame by frame through `renderAt(t)`.
