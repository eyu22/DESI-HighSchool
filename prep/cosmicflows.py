import glob
import astropy
import numpy               as     np
import pandas              as     pd
import pylab               as     pl
import matplotlib.pyplot   as     plt
import astropy.io.fits     as     fits

from   astropy.table       import Table, join, vstack
from   desitarget.cmx      import cmx_targetmask
from   astropy.coordinates import SkyCoord
from   astropy             import units as u

pd.set_option('display.max_rows', None)


cflows      = pd.read_csv('../dat/CosmicFlows3.txt', comment='#')
cflows      = cflows[['Name', 'Dist', 'RAJ', 'DeJ']]

print(cflows)

names       = set(cflows['Name'])
names       = list(names)

ngc         = [x for x in names if type(x) == type('string')]
ngc         = [x for x in ngc   if x[:3] == 'NGC']

isin        = np.isin(cflows['Name'], ngc)

ngc         = cflows[isin]

sign        = np.sign(ngc['DeJ'])

ngc['_']    = np.array(ngc['DeJ']).astype(np.str)
ngc['_']    = np.array([x.replace('-', '') for x in ngc['_']])
ngc['_']    = np.array([x.zfill(6)         for x in ngc['_']])

ngc['DEC']  = np.array([x[-2:]   for x in np.array(ngc['_']).astype(np.str).tolist()]).astype(np.float) / 3600.
ngc['DEC'] += np.array([x[-4:-2] for x in np.array(ngc['_']).astype(np.str).tolist()]).astype(np.float) / 60.
ngc['DEC'] += np.array([x[-6:-4] for x in np.array(ngc['_']).astype(np.str).tolist()]).astype(np.float) / 1.
ngc['DEC'] *= sign

del ngc['_']

sign        = np.sign(ngc['RAJ'])

ngc['_']    = np.array(ngc['RAJ']).astype(np.str)
ngc['_']    = np.array([x.replace('-', '') for x in ngc['_']])
ngc['_']    = np.array([x.zfill(8) for x in ngc['_']])

ngc['RA']   = np.array([x[-4:]   for x in np.array(ngc['_']).astype(np.str).tolist()]).astype(np.float) / 240.
ngc['RA']  += np.array([x[-6:-4] for x in np.array(ngc['_']).astype(np.str).tolist()]).astype(np.float) / 4.
ngc['RA']  += np.array([x[-8:-6] for x in np.array(ngc['_']).astype(np.str).tolist()]).astype(np.float) * 15.
ngc['RA']  *= sign

del ngc['_']

# print(ngc)

cflows      = SkyCoord(ra=ngc['RA'] * u.degree, dec=ngc['DEC'] * u.degree)
tiles       = {'mws': 66003, 'bgs': 66003, 'elg': 67230, 'lrg': 68002, 'qso': 68002}

zbests      = glob.glob('../../../andes/zbest-*')

for fname in zbests:
  dat                        = fits.open(fname)
  
  zbest                      = Table(dat['ZBEST'].data)
  zbest                      = join(zbest, Table(dat['FIBERMAP'].data), join_type='left', keys='TARGETID')
  
  catalog                    = SkyCoord(ra=zbest['TARGET_RA'] * u.degree, dec=zbest['TARGET_DEC'] * u.degree)

  idxc, idxcatalog, d2d, d3d = catalog.search_around_sky(cflows, (1.1 / 3600.) * u.deg)
  
pl.show()
