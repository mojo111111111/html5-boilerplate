# EL TEMAMY PHARMACY: v2 (final edit)

The final file is `el-temamy-commercial-v2.mp4`: 1080×1920 (9:16), 60 fps, 20.0 s, H.264 High, AAC 48 kHz. The soundtrack is sound effects only: no voiceover and no music. It measures −17.3 LUFS integrated with peaks at −2.8 dBFS.

## Timeline
| Time | Scene | Headline |
|---|---|---|
| 0.0–2.5 | The original logo file appears as a rounded tile on cream, with slow orange brand shapes | صيدلية في كل بيت |
| 2.5–5.3 | The tile grows into the phone, which shows the real home screen. The real categories row gets a soft highlight and a tap on "الأدوية" | كل اللي تحتاجه في مكان واحد |
| 5.3–8.0 | A native push to the real categories screen, with a slight perspective turn and a still hold | تصفح منتجاتك بسهولة |
| 8.0–10.8 | A top-down wipe with an orange edge reveals the real Loyalty Points screen. The real balance area gets an outline and one gentle pulse | اجمع نقاطك واستفاد بيها |
| 10.8–14.5 | A push to the real prescription screen, a tap on "روشتة جديدة", a slow camera push, and one orange scan line across the prescription card | صوّر روشتتك أو أدويتك |
| 14.5–16.5 | The scan line leaves the phone as an orange path and lands on a white paper bag labelled with the original logo file. The bag settles and a check confirms the order | طلبك بيتجهز |
| 16.5–17.9 | The path draws the ground and a home outline, and the bag travels to the door | توصيل لحد عندك |
| 17.9–20.0 | Warm door light opens into the orange brand frame. It is fully settled at 18.6 s and holds still to the end | صيدلية في كل بيت · اطلب عبر التطبيق |

## Asset integrity
- **Home, prescription and Loyalty Points screens:** the supplied full-resolution screenshots (about 785×1600) are used at native quality and shown slightly *downscaled* in the phone. The only edit is removing 3 black rows at the bottom of the home screenshot. The Loyalty numbers and text are untouched.
- **Categories screen:** this was only supplied inside the small store image (273×592). It is enlarged with Lanczos only (no generative upscaling) and cropped below its status bar. A full-resolution categories screenshot can replace it directly: `web/img/screen_cat.png`.
- **Logo:** the opening tile and the bag label are the original logo JPG with rounded-corner masks. The end frame uses the white mark keyed from that same file, which composites back onto the original background with under 1/255 mean error.
- **Arabic:** each headline is one Cairo text layer, animated only with opacity, position, scale and blur. The approved phrases are the only added Arabic.

## Sound (Foley/SFX only)
Each sound is shaped noise or a short transient, with no oscillators. A spectral check found no tonal peaks (max 2.7 dB above the local floor). There are 17 cues with silence between them: logo air, the phone forming, a tap, screen pushes, a wipe, the points confirmation, a camera tap, the scan, the line whoosh, the paper bag, packaging, the order confirmation, the travel whoosh, the package placement, and a final dry confirmation.

## Rebuild
```
python3 scripts/prep_v2.py
python3 scripts/sfx_v2.py
WEB=web DUR=20 FFMPEG=/path/to/ffmpeg node scripts/render.mjs video video_silent.mp4 60
ffmpeg -i video_silent.mp4 -i sfx_v2.wav -c:v copy -af "volume=10dB,alimiter=limit=0.708:attack=1:release=60:level=disabled" -c:a aac -b:a 192k -shortest el-temamy-commercial-v2.mp4
```
