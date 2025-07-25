import os
import xarray as xr
import pandas as pd
import numpy as np

### Import information from shell
out_path = os.getenv('outdir')
mask_path = os.getenv('mask')
wc_path = os.getenv('wc')
era5_path = os.getenv('era5')
cj_path = os.getenv('cj')
terra_path = os.getenv('terra')
cmip_path = os.getenv('cmipoutdir')
sclist = os.getenv('sclist').split(',')
sclist_short = os.getenv('sclist_short').split(',')
modlist = os.getenv('modlist').split(',')
cmipversion = os.getenv('cmipversion')
topo_path = os.getenv('topo')


### Monthly information
month = list(range(1, 13, 1))
monthlength=[31,28,31,30,31,30,31,31,30,31,30,31]
first_day_of_month_noleap=[1,32,60,91,121,152,182,213,244,274,305,335]
first_day_of_month_leap=[1,33,61,92,122,153,183,214,245,275,306,336]
#data = {'month': month, 'doy_noleap': first_day_of_month_noleap, 'doy_leap': first_day_of_month_leap, 'length': monthlength}
data = {'month': month, 'doy_noleap': first_day_of_month_noleap, 'length': monthlength}
month_info = pd.DataFrame(data)





### READ DATA

dd = xr.open_dataset(os.path.join(out_path,'input','historic-climate.nc'))
#dd = xr.open_dataset('/Users/helenegenet/Helene/TEM/DVMDOSTEM/dvmdostem-input-catalog/site_extract/bnz-bog/historic-climate.nc')
ddf = dd.sel(time=dd.time.dt.month.isin([1]))
ddf = ddf.rename({'tair': 'exp_burn_mask'})
ddf.exp_burn_mask.loc[:] = 0
ddf['exp_burn_mask'] = ddf['exp_burn_mask'].astype(np.intc)
ddf = ddf.rename({'precip': 'exp_jday_of_burn'})
ddf.exp_jday_of_burn.loc[:] = 0
ddf['exp_jday_of_burn'] = ddf['exp_jday_of_burn'].astype(np.intc)
ddf = ddf.rename({'nirr': 'exp_fire_severity'})
ddf.exp_fire_severity.loc[:] = 0
ddf['exp_fire_severity'] = ddf['exp_fire_severity'].astype(np.intc)
ddf = ddf.rename({'vapor_press': 'exp_area_of_burn'})
ddf.exp_area_of_burn.loc[:] = 0
ddf['exp_area_of_burn'] = ddf['exp_area_of_burn'].astype(np.intc)
ddf.to_netcdf(os.path.join(out_path,'input','historic-explicit-no-fire.nc'),unlimited_dims='time')
#ddf.to_netcdf('/Users/helenegenet/Helene/TEM/DVMDOSTEM/dvmdostem-input-catalog/site_extract/bnz-bog/historic-explicit-no-fire.nc',unlimited_dims='time')




dd = xr.open_dataset(os.path.join(out_path,'input','projected-climate_ssp1_2_6_access_cm2.nc'))
#dd = xr.open_dataset('/Users/helenegenet/Helene/TEM/DVMDOSTEM/dvmdostem-input-catalog/site_extract/bnz-bog/projected-climate_ssp1_2_6_access_cm2.nc')
ddf = dd.sel(time=dd.time.dt.month.isin([1]))
ddf = ddf.rename({'tair': 'exp_burn_mask'})
ddf.exp_burn_mask.loc[:] = 0
ddf['exp_burn_mask'] = ddf['exp_burn_mask'].astype(np.intc)
ddf = ddf.rename({'precip': 'exp_jday_of_burn'})
ddf.exp_jday_of_burn.loc[:] = 0
ddf['exp_jday_of_burn'] = ddf['exp_jday_of_burn'].astype(np.intc)
ddf = ddf.rename({'nirr': 'exp_fire_severity'})
ddf.exp_fire_severity.loc[:] = 0
ddf['exp_fire_severity'] = ddf['exp_fire_severity'].astype(np.intc)
ddf = ddf.rename({'vapor_press': 'exp_area_of_burn'})
ddf.exp_area_of_burn.loc[:] = 0
ddf['exp_area_of_burn'] = ddf['exp_area_of_burn'].astype(np.intc)
ddf.to_netcdf(os.path.join(out_path,'input/projected-explicit-no-fire.nc'),unlimited_dims='time')
#ddf.to_netcdf('/Users/helenegenet/Helene/TEM/DVMDOSTEM/dvmdostem-input-catalog/site_extract/bnz-bog/projected-explicit-no-fire.nc',unlimited_dims='time')




