# lofar-bootstrap
Standalone code to bootstrap LOFAR flux densities

## Prerequisites and installation
The code requires astropy, emcee and pybdsm (LOFAR software) to be on
the path.

Because it makes use of routines from ddf-pipeline, ddf-pipeline must
also be installed. Clone it from
https://github.com/mhardcastle/ddf-pipeline and then ensure that the
ddf-pipeline directory is on the PYTHONPATH.

The convolution routines use Miriad and so that must also be installed
if the maps will be made with non-matched resolutions. 

## Operation

The code will determine scaling ('bootstrap') factors from a set of
LOFAR maps which must be of matched resolution. (If they are not
matched in resolution, the script ``convolve_all.py`` may be of some
use.)

These maps are first assembled into a cube, then PyBDSM is used
to extract a catalogue with per-channel fluxes, the catalogue is
matched with suitable catalogues from other surveys and finally
scaling factors that can be applied to the data are found. The factors
are saved to a numpy file and printed to the screen.

## Running the code

``bootstrap.py`` takes parameters from one or more parameter files or
the command line. An example parameter file showing the setup for
specifying catalogues to use is in ``bootstrap.cfg``.

If ``bootstrap.py`` is run without any arguments a full list of
possible options will be printed to the screen.

The expected usage mode is that some parameters will be fixed and will
be specified in a config file, while some will vary from run to run
and may be specified on the command line. So a typical command line
might be

``bootstrap.py bootstrap.cfg --data-imdir=. --data-images="*conv*fits"
--data-wdir=.``
