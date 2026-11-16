import sys,json; sys.path.insert(0,'.')
from fit import *
img=np.array(Image.open('/home/user/PofBC/public/identity-collected/south-fraser-health-region/south-fraser-health-region-horizontal-tagline-2001-raster.png').convert('L')).astype(float)
mask=np.clip((235-img)/120,0,1)
regions={'symbol':(0,0,142,142),'line1':(198,9,555,62),'line2':(196,74,606,139),'rule':(195,158,294,161),'tag1':(196,188,445,217),'tag2':(196,222,482,252)}
r=fit_groups(mask,regions)
json.dump(r,open('fit_colour2001.json','w'),indent=1)
