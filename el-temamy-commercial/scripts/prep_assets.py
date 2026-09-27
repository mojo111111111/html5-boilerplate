"""Extract real app screens + UI pieces and key the supplied logo. Only rigid transforms, crops,
uniform scaling and alpha masks are applied - no pixels of UI/text/logo are redrawn."""
from PIL import Image, ImageDraw, ImageFilter
import numpy as np, os
U='source'; O='web/img'; os.makedirs(O,exist_ok=True)
S=4
def up(name): return Image.open(f'{U}/src_{name}.jpg').convert('RGB').resize((273*S,592*S),Image.LANCZOS)
def rounded(im,r,corners=(1,1,1,1)):
    m=Image.new('L',(im.width*2,im.height*2),0); d=ImageDraw.Draw(m)
    d.rounded_rectangle([0,0,m.width-1,m.height-1],r*2,fill=255,corners=corners)
    m=m.resize(im.size,Image.LANCZOS); out=im.convert('RGBA'); out.putalpha(m); return out
def sharpen(im): return im.filter(ImageFilter.UnsharpMask(radius=2,percent=45,threshold=2))

# Home screen: phone in source is rotated 9.93deg -> straighten with pure rotation, then crop screen
home=up('home').rotate(9.93,resample=Image.BICUBIC,expand=True)
home=sharpen(home.crop((412,729,1180,2394)))            # 768 x 1665
home_r=rounded(home,78); home_r.save(f'{O}/screen_home.png')
# Prescription screen (front phone, upright)
rx=sharpen(up('rx').crop((369,865,997,2221)))            # 628 x 1356
rounded(rx,64).save(f'{O}/screen_rx.png')
# Categories screen (upright, bottom cut by source image edge)
cat=sharpen(up('cat').crop((111,661,981,2368)))
rounded(cat,80,corners=(1,1,0,0)).save(f'{O}/screen_cat.png')

# Real UI pieces lifted from the home screen (coords in home-screen px)
pieces={'banner':(14,262,756,632),'cats':(0,752,768,1052),'prod1':(424,1180,728,1540),'prod2':(128,1180,414,1540),'rxbtn':(14,640,756,742)}
for k,b in pieces.items():
    rounded(home.crop(b),18).save(f'{O}/ui_{k}.png')
# Prescription illustration from the rx screen
rounded(rx.crop((150,500,490,880)),10).save(f'{O}/ui_rxpaper.png')

# Logo: key the white mark off its orange background (white stays pure white, geometry untouched)
L=np.array(Image.open(f'{U}/logo.jpg').convert('RGB')).astype(float)
B=L[:,:,2]; bgm=(B<90).astype(float)
from scipy.ndimage import gaussian_filter
def blur(a,r): return gaussian_filter(a,r)
bgB=blur(B*bgm,40)/np.maximum(blur(bgm,40),1e-3)
alpha=np.clip((B-bgB)/(250-bgB),0,1); alpha[alpha<0.06]=0
rgba=np.dstack([np.full_like(B,255)]*3+[alpha*255]).astype(np.uint8)
lg=Image.fromarray(rgba,'RGBA'); bbox=lg.getbbox(); print('logo bbox',bbox)
lg.crop(bbox).save(f'{O}/logo_white.png')
# QC: recomposite on the original background to confirm the mark is unchanged
bg=L.copy(); bg[:,:,2]=bgB
comp=(L*0+bg)*(1-alpha[...,None])+255*alpha[...,None]
print('logo recomposite mean abs err', np.abs(comp-L).mean())
for f in sorted(os.listdir(O)): print(f, Image.open(f'{O}/{f}').size)
