### Author: Hélène Genet, hgenet@alaska.edu 
### Institution: Arctic Eco Modeling
### Team, Institute of Arctic Biology, University of Alaska Fairbanks 
### Date: September 23 2024 
### Description: 
### Command: $ 


import os
import xarray as xr



indir=os.getenv('indir')
cjstartyr=os.getenv('cjstartyr')
cjendyr=os.getenv('cjendyr')
sclist=os.getenv('sclist').split(',')
sclist_short=os.getenv('sclist_short').split(',')
modlist=os.getenv('modlist').split(',')
modlist_short=os.getenv('modlist_short').split(',')
cmipvarlist=os.getenv('cmipvarlist').split(',')
cmipvarlist_short=os.getenv('cmipvarlist_short').split(',')
start_mon=os.getenv('start_mon')
end_mon=os.getenv('end_mon')
start_day=os.getenv('start_day')
end_day=os.getenv('end_day')
start_day_mri=os.getenv('start_day_mri')
end_day_mri=os.getenv('end_day_mri')
version=os.getenv('version')
rep=os.getenv('rep')





### Monthly computation of CRU-JRA

## Check output directory exists
if os.path.isdir(os.path.join(indir,'CRU_JRA_monthly')):
else:
  os.mkdir(os.path.join(indir,'CRU_JRA_monthly'))

## Monthly computation
for year in range(int(cjstartyr),int(cjendyr)+1):
	print(year)
	ds = xr.open_dataset(os.path.join(indir, 'CRU_JRA_daily', 'crujra_' + str(year) + '.nc'))
	ds = ds.sortby('time')
	dsm = ds[['tmp','pres','spfh']].resample(time='M').mean()
	dss = ds[['pre','dswrf']].resample(time='M').sum()
	dm = xr.merge([dsm, dss])
	dm.to_netcdf(os.path.join(indir, 'CRU_JRA_monthly', 'crujra_' + str(year) + '_monthly.nc'),unlimited_dims='time',format='NETCDF4', mode='w')





### Monthly computation of CMIP

## Check output directory exists
if os.path.isdir(os.path.join(indir,'CMIP_monthly')):
else:
  os.mkdir(os.path.join(indir,'CMIP_monthly'))

## Monthly computation
for i in range(len(sclist)):
  sc = sclist[i]
  sc_short = sclist_short[i]
  print(sc)
  for j in range(len(modlist)):
    mod = modlist[j]
    mod_short = modlist_short[j]
    print(mod)
    startm = int(start_mon)
    endm = int(end_mon)
    if mod == 'access_cm2':
      startd = int(start_day)
      endd = int(end_day)
    if mod == 'mri_esm2_0':
      startd1 = int(start_day)
      endd1 = int(end_day_mri)
      startd2 = int(start_day_mri)
      endd2 = int(end_day)
    for k in range(len(cmipvarlist)):
      var = cmipvarlist[k]
      var_short = cmipvarlist_short[k]
      print(var)
      print(var_short)
      if var == 'surface_downwelling_shortwave_radiation':
        ds = xr.open_dataset(os.path.join(indir,'CMIP','CMIP' + str(version) + '_' + sc + '_' + mod + '_' + var, var_short + '_Amon_' + mod_short + '_' + sc_short + '_' + rep + '_' + str(startm) + '-' + str(endm) + '.nc'))
        # this is done to harmonize the time dimension values with the other files so concatenation can occur correctly.
        dss = ds[[var_short]].resample(time='M').mean()
      else:
        if mod == 'access_cm2':
          ds = xr.open_dataset(os.path.join(indir,'CMIP','CMIP' + str(version) + '_' + sc + '_' + mod + '_' + var, var_short + '_day_' + mod_short + '_' + sc_short + '_' + rep + '_' + str(startd) + '-' + str(endd) + '.nc'))
          # if I don't do this, the resampling doesn't work, 
          ds = xr.concat([ds], dim="time")
        elif mod == 'mri_esm2_0':
          ds1 = xr.open_dataset(os.path.join(indir,'CMIP','CMIP' + str(version) + '_' + sc + '_' + mod + '_' + var, var_short + '_day_' + mod_short + '_' + sc_short + '_' + rep + '_' + str(startd1) + '-' + str(endd1) + '.nc'))
          ds2 = xr.open_dataset(os.path.join(indir,'CMIP','CMIP' + str(version) + '_' + sc + '_' + mod + '_' + var, var_short + '_day_' + mod_short + '_' + sc_short + '_' + rep + '_' + str(startd2) + '-' + str(endd2) + '.nc'))
          ds = xr.concat([ds1, ds2], dim="time")
        if var == 'precipitation':
          # convert kg.m-2.s-1 to mm.m-2
          ds['pr'] *= 24*60*60  
          dss = ds[[var_short]].resample(time='M').sum()
        else:
          dss = ds[[var_short]].resample(time='M').mean()
      if k==0:
        dm = dss
      else:
        dm = xr.merge([dm, dss])
    dm.to_netcdf(os.path.join(indir,'CMIP_monthly', 'CMIP' + str(version) + '_' + sc + '_' + mod + '_monthly' + '.nc'),unlimited_dims='time',format='NETCDF4', mode='w')





