import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import scipy.stats

parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str, required=True, help="input dat file")
parser.add_argument('-o', type=str, required=True, help="figure outdir")
parser.add_argument('-t', type=str, required=True, help="centroids, OR volumes")
args = parser.parse_args()

if not os.path.exists(args.o):
    os.makedirs(args.o)

# Sample "Hippocamus", "Cortex", "Thalamus", "Hypothalamus", "Midbrain", "Brain stem"
data    = np.loadtxt(args.i, skiprows=1, usecols=(1,2,3,4,5,6))
headers = np.loadtxt(args.i, skiprows=1, usecols=(0), dtype=str)
print(data)

dx=3.26*1.e-3
dz=3.00*1.e-3
regions = ["Hippocamus", "Cortex", "Thalamus", "Hypothalamus", "Midbrain", "Brain stem"]

if args.t == "centroids":
    vp = 1
elif args.t == "volumes":
    vp = dx*dx*dz


Nc = np.shape(data)[1]
x_pos = np.arange(len(regions))

my_cmap = plt.cm.get_cmap('plasma')

#group1=["Brain9","Brain6","Brain10","Brain7","Brain12","Brain1","Brain16","Brain2"]
group1=["Brain7","Brain12","Brain1","Brain16"]
group2=["Brain13","Brain4","Brain14","Brain5","Brain3","Brain11","Brain15"]


# Compute mean/std of segmented volume per group
g1 = []
for i,s in enumerate(group1):
    idx1 = np.where(headers==s)[0]
    o = data[idx1,:][0] * vp
    g1.append( o )
means1 = np.mean(g1, axis=0)
stads1 = np.std( g1, axis=0)
print(g1)
print(means1)
print(stads1)

g2 = []
for i,s in enumerate(group2):
    idx1 = np.where(headers==s)[0]
    o = data[idx1,:][0] * vp
    g2.append( o )
means2 = np.mean(g2, axis=0)
stads2 = np.std( g2, axis=0)

# Plot
fig, ax = plt.subplots(figsize=(9,5))
ax.bar(x_pos-0.25, means1, yerr=stads1, align='edge', width=0.2, capsize=7, edgecolor='k', linewidth=0.5, color='m', label="Adrb1")
ax.bar(x_pos,      means2, yerr=stads2, align='edge', width=0.2, capsize=7, edgecolor='k', linewidth=0.5, color='c', label="Dnmt1")
for i,s in enumerate(group1):
    idx1 = np.where(headers==s)[0]
    o = data[idx1,:][0] * vp
    ax.scatter(x_pos-0.25+0.1, o, color='k', alpha=0.5, s=20)
for i,s in enumerate(group2):
    idx1 = np.where(headers==s)[0]
    o = data[idx1,:][0] * vp
    ax.scatter(x_pos+0.1, o, color='k', alpha=0.5, s=20)
 
if args.t == "centroids":
    ax.set_ylabel(r'Counts', fontsize=13)
elif args.t == "volumes":
    ax.set_ylabel(r'Total volume ($mm^3$)', fontsize=13)
ax.set_xticks(x_pos)
ax.set_xticklabels(regions, fontsize=13)
ax.tick_params(axis='y', which='major', labelsize=13)
ax.set_ylim(bottom=0)
plt.legend(prop={'size': 11})
plt.savefig("%s/figure_per_region_%s.png"% (args.o, args.t), transparent=False)


if 0:
    # Compute 2-sided t-test
    from scipy.stats import ttest_ind_from_stats
    
    tCL = ttest_ind_from_stats(mean1=means2, std1=stads2, nobs1=3,   mean2=means1, std2=stads1, nobs2=3)
    print("T-test", tCL)
    
    
    print(np.shape(g1))
    print(np.shape(regions))
    print(np.shape(means1))
    
    # Dump data in CSV
    fw = open("pvalues_SELECTED_regions.csv", 'w')
    
    fw.write("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s\n " % ("Region name", "vol P1", "vol P2", "vol P3", "avg_P",  "vol LD1", "vol LD2", "vol LD3", "avg_LD",  "vol HD1", "vol HD2", "vol HD3", "avg HD",  "st LD", "pv LD", "st HD", "pv HD") )
    
    for i in range(len(means1)):
        fw.write("%s, %g, %g, %g, %g, %g, %g, %g, %g, %g, %g, %g, %g, %g, %g, %g, %g\n " % (regions[i].replace(',', ''), g1[0][i+1], g1[1][i+1], g1[2][i+1], means1[i], g2[0][i+1], g2[1][i+1], g2[2][i+1], means2[i], g3[0][i+1], g3[1][i+1], g3[2][i+1], means3[i], tCL.statistic[i], tCL.pvalue[i], tCH.statistic[i], tCH.pvalue[i] ) )
    
    fw.close()


