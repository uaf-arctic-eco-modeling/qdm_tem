import os
import xarray as xr
import pandas as pd
import numpy as np


resample_path = os.getenv('input')
var = os.getenv('var')
cmipstartyr = os.getenv('cmipstartyr')

month = list(range(1, 13, 1))
monthlength=[31,28,31,30,31,30,31,31,30,31,30,31]
first_day_of_month_noleap=[1,32,60,91,121,152,182,213,244,274,305,335]
first_day_of_month_leap=[1,33,61,92,122,153,183,214,245,275,306,336]
data = {'month': month, 'doy_noleap': first_day_of_month_noleap, 'doy_leap': first_day_of_month_leap, 'length': monthlength}
month_info = pd.DataFrame(data)



ddo = xr.open_dataset(resample_path)
dd = ddo.to_dataframe()
dd.reset_index(inplace=True)
dd = pd.melt(dd, id_vars=['y','x'], value_vars=['Band' + str(s) for s in list(range(1,1033))])
dd['timestep'] = dd['variable'].str.extract(r'(\d+)').astype(int)
dd['month'] = dd['timestep'].mod(12)
dd['month'] = dd['month'].replace(0,12)
dd = pd.merge(dd,month_info, how='outer', on='month')
dd = dd.sort_values(by=['timestep'])
dd['year'] = (np.floor((dd['timestep'] - 1)/12)+2015).astype(int)
dd['time'] = ((dd['year']-1901)*365) - 1 + dd['doy_noleap']
#dd['year'] = np.floor(dd['timestep']/12)
#dd['time'] = ((int(cmipstartyr)-1901)*365 + (np.floor(dd['timestep']/12)) * 365 + dd['doy']).astype(int)
#ddm = dd.groupby(['month'])[['value']].mean()
#ddm.reset_index(inplace=True)
#plt.plot(ddm['month'], ddm['value'])
#plt.show()
#dd[(dd['y'] == 2000.0) & (dd['x'] == -4526000.0)]
dd = dd.rename(columns={'value': var, 'x': 'lon', 'y': 'lat'})
dd = dd[['time','lat','lon',var]]
nc = dd.set_index(['time', 'lat', 'lon']).to_xarray()
nc['lat'] = nc['lat'].astype(np.single)
nc['lon'] = nc['lon'].astype(np.single)
nc[var] = nc[var].astype(np.single)
nc['time'] = nc['time'].astype(np.intc)
nc['lat'].attrs={'standard_name':'latitude','long_name':'y coordinate of projection','units':'m'}
nc['lon'].attrs={'standard_name':'longitude','long_name':'x coordinate of projection','units':'m'}
nc[var].attrs={'_FillValue': -9999.0}
### CONSIDER LEAP YEARS IN THE COUNT OF DAY SINCE REF
nc['time'].attrs={'units':'days since 1901-1-1 0:0:0','long_name':'time','calendar':'365_day','_FillValue': -9999.0}
nc.time.encoding['units'] = 'days since 1901-01-01 00:00:00'
nc.time.encoding['calendar'] = '365_day'
nc.time.encoding['long_name'] = 'time'
#nc['lambert_azimuthal_equal_area'] = ddo.lambert_azimuthal_equal_area
nc.attrs = ddo.attrs
nc.to_netcdf(resample_path,unlimited_dims='time',mode='w')


