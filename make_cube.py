#!/usr/bin/python
from astropy.io import fits
import numpy as np
import glob
import sys

def make_cube(directory,filenames,outfile):
    hdus=[]
    freqs=[]
    g=glob.glob(directory+'/'+filenames)
    for f in g:
        hdus.append(fits.open(f))
        freqs.append(hdus[-1][0].header['CRVAL3'])
        print f,freqs[-1]

    freqs,hdus = (list(x) for x in zip(*sorted(zip(freqs, hdus), key=lambda pair: pair[0])))

    print freqs

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
    ohdu[0].header['CRPIX3']=0
    ohdu[0].header['CRVAL3']=freqs[0]
    ohdu[0].header['CDELT3']=freqs[1]-freqs[0]
    hdus[0].writeto(outfile,clobber=True)

if __name__=='__main__':
    directory=sys.argv[1]
    outfile=sys.argv[2]
    make_cube(directory,'*-wsclean-mfs-robust-0.7-000*-image-pb.fits',outfile)
    
