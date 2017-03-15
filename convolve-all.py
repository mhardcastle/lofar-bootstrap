#!/usr/bin/python

# requires module load miriad

import os
import os.path
import glob
from astropy.io import fits

#resolution=160

files=glob.glob('*.fits')

# Work out the resolution we want

resolution=0
for f in files:
    hdulist=fits.open(f)
    bmaj=3600.0*hdulist[0].header['BMAJ']
    if bmaj>resolution:
        resolution=bmaj
    hdulist.close()

resolution*=1.01

print 'Convolving everything with circular beam of',resolution,'arcsec'

rstr=str(resolution)+','+str(resolution)

for f in files:
    if 'conv' not in f:
        outfile=f[:-5]+'_conv.fits'
        if not os.path.exists(outfile):
            print 'Doing',f,'output to',outfile
            os.system('fits op=xyin in='+f+' out=tmp')
            os.system('convol map=tmp fwhm='+rstr+' options=final out=tmp_out')
            os.system('fits op=xyout in=tmp_out out='+outfile)
            os.system('rm -r tmp tmp_out')
