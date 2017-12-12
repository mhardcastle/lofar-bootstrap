#!/usr/bin/python
from astropy.io import fits
import numpy as np
import glob
import sys

# Utility functions for making the cube

def get_freqs_hdus(directory,filenames):
    hdus=[]
    freqs=[]
    g=glob.glob(directory+'/'+filenames)
    for f in g:
        if f==(directory+'/cube.fits'): continue
        hdus.append(fits.open(f))
        header=hdus[-1][0].header
        if header['CUNIT3']=='Hz':
            freqs.append(header['CRVAL3'])
        else:
            freqs.append(header['RESTFRQ'])
        print f,freqs[-1]

    freqs,hdus = (list(x) for x in zip(*sorted(zip(freqs, hdus), key=lambda pair: pair[0])))
    return freqs,hdus
    
def make_cube(freqs,hdus,outfile):

    stokes,chan,y,x=hdus[0][0].data.shape
    print stokes,chan,y,x

    newdata=np.zeros((stokes,len(hdus),y,x),dtype=np.float32)
    print newdata.shape
    for i,h in enumerate(hdus):
        newdata[0,i,:,:]=h[0].data

    ohdu=hdus[0]
    ohdu[0].data=newdata
    ohdu[0].header['NAXIS3']=len(hdus)
    ohdu[0].header['CTYPE3']='FREQ'
    ohdu[0].header['CUNIT3']='Hz'
    ohdu[0].header['CRPIX3']=1
    ohdu[0].header['CRVAL3']=freqs[0]
    ohdu[0].header['CDELT3']=freqs[1]-freqs[0]
    if 'BPA' not in ohdu[0].header.keys():
        ohdu[0].header['BPA']=0
    hdus[0].writeto(outfile,clobber=True)

if __name__=='__main__':
    directory=sys.argv[1]
    outfile=sys.argv[2]
    make_cube(directory,'*-wsclean-mfs-*-image-pb.fits',outfile)
    
