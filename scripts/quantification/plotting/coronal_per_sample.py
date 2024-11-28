import os
import sys
import nrrd
import argparse
import matplotlib.pyplot as plt
import numpy as np
import skimage.io
import skimage.filters
from numpy.ma import masked_array
from matplotlib import cm

def coronal(ax, Nc, slices, cells, normal, cmap, Vmax, Vmin, outfile):

    # load atlas
    fatlas = "/media/user/SSD1/Athena/SOURCE/SleepBrains/scripts/alignment/atlas/ABA_25um_reference_hemisphere_noBulb.nrrd"
    atlas0, _ = nrrd.read(fatlas)
    atlas = np.zeros(np.shape(cells))
    atlas[:,:,:] = atlas0[:, :, 0:np.shape(cells)[2]]

    fannatlas = "/media/user/SSD1/Athena/SOURCE/SleepBrains/scripts/alignment/atlas/ABA_25um_annotation_hemisphere_noBulb.nrrd"
    anatlas0, _ = nrrd.read(fannatlas)
    anatlas = np.zeros(np.shape(cells))
    anatlas[:,:,:] = anatlas0[:, :, 0:np.shape(cells)[2]]

    # plot coronal slices
    for ic in range(Nc):
        i = slices[ic]
        pa   = ax[ic].imshow(atlas[:,i,:],    interpolation='nearest', cmap=cm.gray)

        #pan = ax[ic].contour(anatlas[:,i,:], colors='w', levels=[0,np.max(anatlas[:,i,:])]) # outline
        pan = ax[ic].contour(anatlas[:,i,:], colors='w', levels=[0], linewidths=0.5) # outline
        pan = ax[ic].contour(anatlas[:,i,:], colors='#E6E6E6', levels=np.linspace(50,2001,10), linewidths=0.5, alpha=0.3) # outline

        cells_slice = skimage.filters.gaussian(cells[:,i,:], sigma=2, preserve_range=True)
        cells_slice = masked_array(cells_slice,((cells_slice<0.01) + (anatlas[:,i,:]==0)))
        if normal !=0:
            alphas = cells_slice/normal; alphas[alphas<0.1]=0.1; alphas[alphas>1]=1
        else:
            alphas = 1
        pb = ax[ic].imshow(cells_slice, interpolation='nearest', cmap=cmap, alpha=alphas, vmin=Vmin, vmax=Vmax)

        ax[ic].set_axis_off()
        ax[ic].set_facecolor("white")

#        if ic==0:
#            ax[ic].annotate(text="%s"%args.s, xy=(16, 36), xycoords='data', color='w', fontsize=8)

    plt.subplots_adjust(wspace=0, hspace=0)
    plt.savefig(outfile, bbox_inches='tight', pad_inches=0, transparent=False)
    plt.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', type=str, required=True, help="input: counts on atlas grid, nrrd")
    parser.add_argument('-o', type=str, required=True, help="output folder")
    parser.add_argument('-s', type=str, required=True, help="sample ID")
    parser.add_argument('-n', type=float, required=True, help="normalization factor")
    args = parser.parse_args()


    sample = args.s
    print(sample)
    color = 'm'
    vmin=-2e6; vmax=-1e6
    cmap = cm.cool

    # load
    cells, _ = nrrd.read(args.i)

    # plot
    Nc=8
    Nr=1
    slices = [50, 100, 150, 200, 250, 300, 350, 400]
    fig,ax = plt.subplots(Nr,Nc, figsize=(16,3), facecolor='black')
    outfile = "%s/pic_density_coronal_%s.pdf" % (args.o, sample)
    normal = args.n
    coronal(ax, Nc, slices, cells, normal, cmap, vmax, vmin, outfile)

