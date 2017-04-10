#!/usr/bin/env python

# Code to bootstrap the LOFAR flux density scale
# This is based heavily on the Tier 1 pipeline code, see
# https://github.com/mhardcastle/ddf-pipeline

import os,sys
import os.path
from auxcodes import report,warn,die
import numpy as np
import shutil
from make_cube import get_freqs_hdus, make_cube
from make_fitting_product import make_catalogue
import fitting_factors
import find_outliers
from astropy.io import fits
from lofar import bdsm

# options needed:
# working directory -- where cube and other outputs are stored
# directory for images
# bootstrap options from ddf-pipeline

def run_bootstrap(o):

    os.chdir(o['wdir'])
    
    if o['imdir'] is None:
        die('Image directory must be specified')
    
    # check the data supplied
    if o['frequencies'] is None or o['catalogues'] is None:
        die('Frequencies and catalogues options must be specified')

    cl=len(o['catalogues'])
    if o['names'] is None:
        o['names']=[os.path.basename(x).replace('.fits','') for x in o['catalogues']]
    if o['radii'] is None:
        o['radii']=[10]*cl
    if o['groups'] is None:
        o['groups']=range(cl)
    if (len(o['frequencies'])!=cl or len(o['radii'])!=cl or
        len(o['names'])!=cl or len(o['groups'])!=cl):
        die('Names, groups, radii and frequencies entries must be the same length as the catalogue list')

    report('Reading the images')
    freqs,hdus=get_freqs_hdus(o['imdir'],o['images'])

    # Clean in cube mode
    if os.path.isfile('cube.fits'):
        warn('Cube exists, skipping cube generation')
    else:
        report('Making the cube')
        make_cube(freqs,hdus,'cube.fits')

    if os.path.isfile('cube.fits.pybdsm.srl'):
        warn('Source list exists, skipping source extraction')
    #Option for using a detection image in PyBDSM   
    elif o['detection_image'] is not None:
        report('Running PyBDSM using a specified detection image, please wait...')
        img=bdsm.process_image('cube.fits',detection_image=o['detection_image'],thresh_pix=5,rms_map=True,atrous_do=True,atrous_jmax=2,group_by_isl=True,rms_box=(80,20), adaptive_rms_box=True, adaptive_thresh=80, rms_box_bright=(35,7),mean_map='zero',spectralindex_do=True,specind_maxchan=1,debug=True,kappa_clip=3,flagchan_rms=False,flagchan_snr=False,incl_chan=True,spline_rank=1)
        # Write out in ASCII to work round bug in pybdsm
        img.write_catalog(catalog_type='srl',format='ascii',incl_chan='true')
        img.export_image(img_type='rms',img_format='fits')   
    else:
        report('Running PyBDSM, please wait...')
        img=bdsm.process_image('cube.fits',thresh_pix=5,rms_map=True,atrous_do=True,atrous_jmax=2,group_by_isl=True,rms_box=(80,20), adaptive_rms_box=True, adaptive_thresh=80, rms_box_bright=(35,7),mean_map='zero',spectralindex_do=True,specind_maxchan=1,debug=True,kappa_clip=3,flagchan_rms=False,flagchan_snr=False,incl_chan=True,spline_rank=1)
        # Write out in ASCII to work round bug in pybdsm
        img.write_catalog(catalog_type='srl',format='ascii',incl_chan='true')
        img.export_image(img_type='rms',img_format='fits')


    # generate the fitting product
    if os.path.isfile('crossmatch-1.fits'):
        warn('Crossmatch table exists, skipping crossmatch')
    else:
        hdu=fits.open('cube.fits')
        ra=hdu[0].header['CRVAL1']
        dec=hdu[0].header['CRVAL2']

        cats=zip(o['catalogues'],o['names'],o['groups'],o['radii'])
        make_catalogue('cube.pybdsm.srl',ra,dec,2.5,cats)
    
    freqlist=open('frequencies.txt','w')
    for n,f in zip(o['names'],o['frequencies']):
        freqlist.write('%f %s_Total_flux %s_E_Total_flux False\n' % (f,n,n))
    for i,f in enumerate(freqs):
        freqlist.write('%f Total_flux_ch%i E_Total_flux_ch%i True\n' % (f,i+1,i+1))
    freqlist.close()

    # Now call the fitting code

    if os.path.isfile('crossmatch-results-1.npy'):
        warn('Results 1 exists, skipping first fit')
    else:
        fitting_factors.run_all(1)

    nreject=-1 # avoid error if we fail somewhere
    if os.path.isfile('crossmatch-2.fits'):
        warn('Second crossmatch exists, skipping outlier rejection')
    else:
        nreject=find_outliers.run_all(1)
    
    if os.path.isfile('crossmatch-results-2.npy'):
        warn('Results 1 exists, skipping second fit')
    else:
        if nreject==0:
            shutil.copyfile('crossmatch-results-1.npy','crossmatch-results-2.npy')
        else:
            fitting_factors.run_all(2)

if __name__=='__main__':
    from options import options,print_options
    if len(sys.argv)<2:
        print 'bootstrap.py needs command-line options and/or a config file'
        print_options()
    else:
        o=options(sys.argv[1:])
        run_bootstrap(o)
