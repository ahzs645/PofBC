import sys,json; sys.path.insert(0,'.')
from fit import *
img=np.array(Image.open('/home/user/PofBC/public/identity-collected/south-fraser-health-region/south-fraser-health-region-horizontal-1998.png').convert('L')).astype(float)
mask=np.zeros_like(img)
mask[28:318,16:1222]=np.clip((img[28:318,16:1222]-60)/140,0,1)
regions={'symbol':(47,36,333,306),'line1':(428,58,1137,157),'line2':(375,183,1179,306)}
r=fit_groups(mask,regions,blur=2.0)
json.dump(r,open('fit_h1998.json','w'),indent=1)
