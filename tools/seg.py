import numpy as np
from PIL import Image
from scipy import ndimage as nd
im = np.asarray(Image.open('/home/sara/Kuvat/spruce.jpeg').convert('RGB')).astype(np.float32)
mx = im.max(2)
print('bg stats', np.percentile(mx[:5,:].ravel(), [50, 99]))
fg = mx > 28
fg = nd.binary_closing(fg, iterations=2)
lab, n = nd.label(nd.binary_dilation(fg, iterations=3))
objs = nd.find_objects(lab)
boxes = []
for i, sl in enumerate(objs):
    y0, y1, x0, x1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
    area = (lab[sl] == i + 1).sum()
    if area < 60: continue
    boxes.append((y0, x0, y1, x1, area))
boxes.sort(key=lambda b: (b[0] // 60, b[1]))
print(len(boxes))
for b in boxes: print(b)
from PIL import ImageDraw
img = Image.open('/home/sara/Kuvat/spruce.jpeg').convert('RGB')
d = ImageDraw.Draw(img)
for i,(y0,x0,y1,x1,a) in enumerate(boxes):
    d.rectangle([x0,y0,x1-1,y1-1], outline=(255,0,0))
    d.text((x0+2,y0+1), str(i), fill=(255,255,0))
img.save('boxes.png')
import json; json.dump([list(map(int,b)) for b in boxes], open('boxes.json','w'))
