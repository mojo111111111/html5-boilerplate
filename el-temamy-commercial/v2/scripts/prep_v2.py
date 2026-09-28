"""v2 assets. Screens are used at native resolution; only crops / lossless re-save are applied."""
from PIL import Image, ImageFilter
import shutil
A = 'assets'; O = 'web2/img'
shutil.copy(f'{A}/v2_rx.jpg', f'{O}/screen_rx.jpg')             # 785x1600, untouched
shutil.copy(f'{A}/v2_loyalty.jpg', f'{O}/screen_loyalty.jpg')   # 798x1600, untouched
Image.open(f'{A}/v2_home.jpg').crop((0, 0, 762, 1597)).save(f'{O}/screen_home.png')  # drop 3 black rows at the bottom
# Categories screen: only supplied as a small store image -> 4x Lanczos, crop the screen below its status bar
cat = Image.open(f'{A}/src_cat.jpg').convert('RGB').resize((273 * 4, 592 * 4), Image.LANCZOS)
cat = cat.crop((111, 760, 981, 2368)).filter(ImageFilter.UnsharpMask(radius=2, percent=40, threshold=2))
cat.save(f'{O}/screen_cat.png')
shutil.copy(f'{A}/logo.jpg', f'{O}/logo_tile.jpg')             # original logo file, untouched
shutil.copy('web/img/logo_white.png', f'{O}/logo_white.png')    # keyed mark (verified identical on orange)
for n in ['screen_rx.jpg', 'screen_loyalty.jpg', 'screen_home.png', 'screen_cat.png', 'logo_tile.jpg', 'logo_white.png']:
    print(n, Image.open(f'{O}/{n}').size)
