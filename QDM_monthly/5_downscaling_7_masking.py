import os
import xarray as xr
import pandas as pd
import numpy as np



### Import information from shell
out_path = os.getenv('outdir')
mask_path = os.getenv('mask')
wc_path = os.getenv('wc')
era5_path = os.getenv('era5corr')
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
mask_nc = xr.open_dataset(mask_path)
dd = xr.open_dataset(os.path.join(out_path,'input','historic-climate.nc'))



### DETECT PIXELS WITHOUT CLIMATE INFORMATION

## Worldclim no data
wc = xr.open_dataset(wc_path)
wc = wc.drop_vars(['lambert_azimuthal_equal_area'])
wcyx = wc.mean(dim=["time"])
#wcyx.tavg.plot()
#plt.show()
#wcyx.prec.plot()
#plt.show()
#wcyx.srad.plot()
#plt.show()
#wcyx.vapr.plot()
#plt.show()
wc['prec'] = wc['prec'].where(wc['prec'] >= 0, np.nan)
wcyx = wc.mean(dim=["time"])
wcyx['mask'] = (("lat", "lon"), np.full(wcyx.tavg.shape, 1.0))
wcyx['mask'] = wcyx['mask'].where((pd.notnull(wcyx['tavg'])) | (pd.notnull(wcyx['prec'])) | (pd.notnull(wcyx['srad'])) | (pd.notnull(wcyx['vapr'])), np.nan)


## CRU-JRA no data
cj = xr.open_dataset(cj_path)
cjyx = cj.mean(dim=["time"])
#cjyx.tmp.plot()
#plt.show()
#cjyx.pre.plot()
#plt.show()
#cjyx.dswrf.plot()
#plt.show()
#cjyx.spfh.plot()
#plt.show()
#cjyx.pres.plot()
#plt.show()
cjyx['tmp'] = cjyx['tmp'].where((cjyx['tmp'] != 0) | (cjyx['pre'] != 0) | (cjyx['dswrf'] != 0) | (cjyx['spfh'] != 0) | (cjyx['pres'] != 0), np.nan)
cjyx['pre'] = cjyx['pre'].where((pd.notnull(cjyx['tmp'])) | (cjyx['pre'] != 0) | (cjyx['dswrf'] != 0) | (cjyx['spfh'] != 0) | (cjyx['pres'] != 0), np.nan)
cjyx['dswrf'] = cjyx['dswrf'].where((pd.notnull(cjyx['tmp'])) | (pd.notnull(cjyx['pre'])) | (cjyx['dswrf'] != 0) | (cjyx['spfh'] != 0) | (cjyx['pres'] != 0), np.nan)
cjyx['spfh'] = cjyx['spfh'].where((pd.notnull(cjyx['tmp'])) | (pd.notnull(cjyx['pre'])) | (pd.notnull(cjyx['dswrf'])) | (cjyx['spfh'] != 0) | (cjyx['pres'] != 0), np.nan)
cjyx['pres'] = cjyx['pres'].where((pd.notnull(cjyx['tmp'])) | (pd.notnull(cjyx['pre'])) | (pd.notnull(cjyx['dswrf'])) | (pd.notnull(cjyx['spfh'])) | (cjyx['pres'] != 0), np.nan)
cjyx['mask'] = (("lat", "lon"), np.full(cjyx.tmp.shape, 1.0))
cjyx['mask'] = cjyx['mask'].where((pd.notnull(cjyx['tmp'])) | (pd.notnull(cjyx['pre'])) | (pd.notnull(cjyx['dswrf'])) | (pd.notnull(cjyx['spfh'])) | (pd.notnull(cjyx['pres'])), np.nan)


## ERA5 no data
era5 = xr.open_dataset(era5_path)
era5yx = era5.mean(dim=["time"])
#era5yx.t2m.plot()
#plt.show()
#era5yx.d2m.plot()
#plt.show()
#era5yx.tp.plot()
#plt.show()
#era5yx.tas_oc.plot()
#plt.show()
era5yx['tas_oc'] = era5yx['tas_oc'].where((era5yx['tas_oc'] != 0) | (era5yx['precip_mm'] != 0.0) | (era5yx['srad_wm2'] != 0) | (era5yx['vapo_kpa'] != 0), np.nan)
era5yx['precip_mm'] = era5yx['precip_mm'].where((pd.notnull(era5yx['tas_oc'])) | (era5yx['precip_mm'] != 0.0) | (pd.notnull(era5yx['srad_wm2'])) | (pd.notnull(era5yx['vapo_kpa'])), np.nan)
era5yx['srad_wm2'] = era5yx['srad_wm2'].where((pd.notnull(era5yx['tas_oc'])) | (era5yx['precip_mm'] != 0.0) | (pd.notnull(era5yx['srad_wm2'])) | (pd.notnull(era5yx['vapo_kpa'])), np.nan)
era5yx['vapo_kpa'] = era5yx['vapo_kpa'].where((pd.notnull(era5yx['tas_oc'])) | (era5yx['precip_mm'] != 0.0) | (pd.notnull(era5yx['srad_wm2'])) | (pd.notnull(era5yx['vapo_kpa'])), np.nan)
era5yx['mask'] = (("lat", "lon"), np.full(era5yx.tas_oc.shape, 1.0))
era5yx['mask'] = era5yx['mask'].where((pd.notnull(era5yx['tas_oc'])) | (pd.notnull(era5yx['precip_mm'])) | (pd.notnull(era5yx['srad_wm2'])) | (pd.notnull(era5yx['vapo_kpa'])), np.nan)


## CMIP6 no data
#cmip_access = xr.open_dataset(os.path.join(cmip_path,'CMIP6_historical_access_cm2_rsmpl.nc'))
#cmip_mri = xr.open_dataset(os.path.join(cmip_path,'CMIP6_historical_mri_esm2_0_rsmpl.nc'))
#cmip_access_yx = cmip_access.mean(dim=["time"])
#cmip_mri_yx = cmip_mri.mean(dim=["time"])
#cmip_access_yx.tas.plot()
#plt.show()
#cmip_access_yx.huss.plot()
#plt.show()
#cmip_access_yx.pr.plot()
#plt.show()
#cmip_access_yx.psl.plot()
#plt.show()
#cmip_access_yx.rsds.plot()
#plt.show()
#cmip_mri_yx.tas.plot()
#plt.show()
#cmip_mri_yx.huss.plot()
#plt.show()
#cmip_mri_yx.pr.plot()
#plt.show()
#cmip_mri_yx.psl.plot()
#plt.show()
#cmip_mri_yx.rsds.plot()
#plt.show()

## VEGETATION no data
veg = xr.open_dataset(os.path.join(out_path,'input','vegetation.nc'))
#veg.veg_class.plot()
#plt.show()
veg['mask'] = (("Y", "X"), np.full(veg.veg_class.shape, 1.0))
veg['mask'] = veg['mask'].where((pd.notnull(veg['veg_class'])), np.nan)
veg['mask'] = veg['mask'].where((veg['veg_class'] != 0.0), np.nan)


## Update the mask....
cjyx = cjyx.rename({"lat": "Y", "lon": "X", "mask": "mask_cj"})
cjyx = cjyx.drop_vars(['tmp','pre','dswrf','spfh','pres'])
wcyx = wcyx.rename({"lat": "Y", "lon": "X", "mask": "mask_wc"})
wcyx = wcyx.drop_vars(['tavg','prec','srad','vapr'])
era5yx = era5yx.rename({"lat": "Y", "lon": "X", "mask": "mask_era5"})
era5yx = era5yx.drop_vars(['tas_oc','precip_mm','srad_wm2','vapo_kpa'])
veg = veg.rename({"mask": "mask_veg"})
veg = veg.drop_vars(['lambert_azimuthal_equal_area','veg_class'])

mask_update = xr.merge([mask_nc, cjyx, wcyx, era5yx, veg])
mask_update['run'] = mask_update['run'].where((pd.notnull(mask_update['mask_cj'])), 0.0)
mask_update['run'] = mask_update['run'].where((pd.notnull(mask_update['mask_wc'])), 0.0)
mask_update['run'] = mask_update['run'].where((pd.notnull(mask_update['mask_era5'])), 0.0)
mask_update['run'] = mask_update['run'].where((pd.notnull(mask_update['mask_veg'])), 0.0)
mask_update['run'] = mask_update['run'].where((pd.notnull(mask_update['run'])), 0.0)
mask_update = mask_update.drop_vars(['mask_cj','mask_wc','mask_era5','mask_veg'])

mask_update['lat'].attrs={'standard_name':'latitude','units':'degree_north','_FillValue': 1.e+20}
mask_update['lon'].attrs={'standard_name':'longitude','units':'degree_east','_FillValue': 1.e+20}
mask_update['run'].attrs={'standard_name':'mask','units':'','grid_mapping':'albers_conical_equal_area','_FillValue': -999.0}
mask_update['Y'].attrs={'standard_name':'projection_y_coordinate','long_name':'y coordinate of projection','units':'m'}
mask_update['X'].attrs={'standard_name':'projection_x_coordinate','long_name':'x coordinate of projection','units':'m'}

#mask_update.run.plot()
#plt.show()
#mask_nc.run.plot()
#plt.show()

mask_update.to_netcdf(os.path.join(out_path,'input','run-mask-update.nc'))



### CORRECT THE FEW NEGATIVES HERE AND THERE


clmt = xr.open_dataset(os.path.join(out_path,'input','historic-climate.nc'))
runmask = xr.open_dataset(os.path.join(out_path,'input','run-mask.nc'))
# Set negative values to zero
clmt['precip'] = clmt['precip'].where(clmt['precip'] >= 0, 0)
clmt['vapor_press'] = clmt['vapor_press'].where(clmt['vapor_press'] >= 0, 0)
clmt['nirr'] = clmt['nirr'].where(clmt['nirr'] >= 0, 0)
# Replace values to missing outside of the mask
clmt = xr.merge([clmt, runmask])
clmt['tair'] = clmt['tair'].where(clmt['run'] == 1.0, -999.)
clmt['precip'] = clmt['precip'].where(clmt['run'] == 1.0, -999.)
clmt['nirr'] = clmt['nirr'].where(clmt['run'] == 1.0, -999.)
clmt['vapor_press'] = clmt['vapor_press'].where(clmt['run'] == 1.0, -999.)
clmt = clmt.drop_vars('run')
# Format the output netcdf file
clmt['lat'].attrs={'standard_name':'latitude','units':'degree_north','_FillValue': -999.0}
clmt['lon'].attrs={'standard_name':'longitude','units':'degree_east','_FillValue': -999.0}
clmt['tair'].attrs={'standard_name':'air_temperature','units':'celsius','grid_mapping':'albers_conical_equal_area','_FillValue': -999.0}
clmt['precip'].attrs={'standard_name':'precipitation_amount','units':'mm month-1','grid_mapping':'albers_conical_equal_area','_FillValue': -999.0}
clmt['nirr'].attrs={'standard_name':'downwelling_shortwave_flux_in_air','units':'W m-2','grid_mapping':'albers_conical_equal_area','_FillValue': -999.0}
clmt['vapor_press'].attrs={'standard_name':'water_vapor_pressure','units':'hPa','grid_mapping':'albers_conical_equal_area','_FillValue': -999.0}
clmt['time'].attrs={'units':'days since 1901-1-1 0:0:0','long_name':'time','calendar':'365_day'}
clmt.time.encoding['units'] = 'days since 1901-01-01 00:00:00'
clmt.time.encoding['calendar'] = '365_day'
clmt.time.encoding['long_name'] = 'time'
clmt.to_netcdf(os.path.join(out_path,'input','historic-climate_gf.nc'),unlimited_dims='time')


for mod in modlist:
    print(mod)
    for sc in sclist:
        print(sc)
		clmt = xr.open_dataset(os.path.join(out_path,'input/projected-climate_' + sc + '_' + mod + '.nc'))
		# Set negative values to zero
		clmt['precip'] = clmt['precip'].where(clmt['precip'] >= 0, 0)
		clmt['vapor_press'] = clmt['vapor_press'].where(clmt['vapor_press'] >= 0, 0)
		clmt['nirr'] = clmt['nirr'].where(clmt['nirr'] >= 0, 0)
		# Replace values to missing outside of the mask
		clmt = xr.merge([clmt, runmask])
		clmt['tair'] = clmt['tair'].where(clmt['run'] == 1.0, -999.)
		clmt['precip'] = clmt['precip'].where(clmt['run'] == 1.0, -999.)
		clmt['nirr'] = clmt['nirr'].where(clmt['run'] == 1.0, -999.)
		clmt['vapor_press'] = clmt['vapor_press'].where(clmt['run'] == 1.0, -999.)
		clmt = clmt.drop_vars('run')
		# Format the output netcdf file
		clmt['lat'].attrs={'standard_name':'latitude','units':'degree_north','_FillValue': -999.0}
		clmt['lon'].attrs={'standard_name':'longitude','units':'degree_east','_FillValue': -999.0}
		clmt['tair'].attrs={'standard_name':'air_temperature','units':'celsius','grid_mapping':'albers_conical_equal_area','_FillValue': -999.0}
		clmt['precip'].attrs={'standard_name':'precipitation_amount','units':'mm month-1','grid_mapping':'albers_conical_equal_area','_FillValue': -999.0}
		clmt['nirr'].attrs={'standard_name':'downwelling_shortwave_flux_in_air','units':'W m-2','grid_mapping':'albers_conical_equal_area','_FillValue': -999.0}
		clmt['vapor_press'].attrs={'standard_name':'water_vapor_pressure','units':'hPa','grid_mapping':'albers_conical_equal_area','_FillValue': -999.0}
		clmt['time'].attrs={'units':'days since 1901-1-1 0:0:0','long_name':'time','calendar':'365_day'}
		clmt.time.encoding['units'] = 'days since 1901-01-01 00:00:00'
		clmt.time.encoding['calendar'] = '365_day'
		clmt.time.encoding['long_name'] = 'time'
		clmt.to_netcdf(os.path.join(out_path,'input/projected-climate_' + sc + '_' + mod + '_gf.nc'),unlimited_dims='time')

