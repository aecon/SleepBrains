import nrrd
import argparse
import skimage.io
import numpy as np
from numpy.ma import masked_array
import matplotlib.pyplot as plt
from matplotlib import cm


parser = argparse.ArgumentParser()
parser.add_argument('-b',  type=str, required=True, help="aligned brain, nrrd")
parser.add_argument('-a', type=str, required=True, help="atlas reference hemisphere, nrrd")
parser.add_argument('-o', type=str, required=True, help="path to output directory")
parser.add_argument('-s', type=str, required=True, help="sample ID")
args = parser.parse_args()
print(args)


# paths
fatlas=args.a
fcells=args.b


# load
#atlas  = skimage.io.imread(fatlas,  plugin='tifffile').T   # for tif file
#cells  = skimage.io.imread(fcells, plugin='simpleitk')     # for mhd file
atlas, _  = nrrd.read(fatlas)  # for nrrd file
cells, _  = nrrd.read(fcells)  # for nrrd file
print(np.shape(atlas))
print(np.shape(cells))


# visuals (adjusted from auto in Fiji)
Vmin=50
Vmax=800
atlas[atlas<20] = 0
atlas[atlas>250] = 250


# plot coronal view
Nc=9
Nr=1
fig,ax = plt.subplots(Nr,Nc, figsize=(36,4), constrained_layout=True)
slices = [50, 100, 150, 200, 250, 300, 350, 400, 450]
for ic in range(9):
    k = int(ic)
    i = int(slices[k])
    print(i)
    pa = ax[ic].imshow(cells[:,i,:],interpolation='nearest',cmap=cm.gray, vmin=Vmin, vmax=Vmax)
    pb = ax[ic].contour(np.log10(atlas[:,i,:]+1), levels=10, linewidths=0.5, linestyles='-', colors='m')
    #pb = ax[ic].contour(atlas[:,i,:], levels=3, linewidths=0.5, linestyles='-', colors='m')
    print(np.min(atlas[:,i,:]), np.mean(atlas[:,i,:]), np.max(atlas[:,i,:]))

    ax[ic].set_axis_off()

plt.subplots_adjust(wspace=0, hspace=0)
#plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=None)

plt.savefig("%s/%s_alignment.png" % (args.o, args.s), transparent=True, pad_inches=0)
#plt.savefig("%s/%s_alignment.png" % (args.o, args.s))
plt.close()

