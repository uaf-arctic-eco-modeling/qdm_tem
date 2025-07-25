
import os
import xarray as xr
import numpy as np


indir = os.getenv('dir')



### Concatenate the yearly downscaled datasets

ds = xr.open_dataset(os.path.join(indir, 'input','run-mask.nc'))
df = ds.to_dataframe()
df.reset_index(inplace=True)
fri = df.drop('run', axis=1)
fri['fri'] = 2000
fri['fri_severity'] = 0
fri['fri_jday_of_burn'] = 0
fri['fri_area_of_burn'] = 0
fri_nc = fri.set_index(['Y', 'X']).to_xarray()
fri_nc['lat'] = fri_nc['lat'].astype(np.single)
fri_nc['lon'] = fri_nc['lon'].astype(np.single)
fri_nc['fri'] = fri_nc['fri'].astype(np.intc)
fri_nc['fri_severity'] = fri_nc['fri_severity'].astype(np.intc)
fri_nc['fri_jday_of_burn'] = fri_nc['fri_jday_of_burn'].astype(np.intc)
fri_nc['fri_area_of_burn'] = fri_nc['fri_area_of_burn'].astype(np.intc)
fri_nc['lat'].attrs={'standard_name':'latitude','units':'degree_north'}
fri_nc['lon'].attrs={'standard_name':'longitude','units':'degree_east'}
fri_nc['Y'].attrs={'standard_name':'projection_y_coordinate','long_name':'y coordinate of projection','units':'m'}
fri_nc['X'].attrs={'standard_name':'projection_x_coordinate','long_name':'x coordinate of projection','units':'m'}
fri_nc['fri'].attrs={'standard_name':'fire_return_interval','units':'yrs','grid_mapping':'albers_conical_equal_area','_FillValue': -999.0}
fri_nc['fri_jday_of_burn'].attrs={'standard_name':'fri_jday_of_burn','units':'doy','grid_mapping':'albers_conical_equal_area','_FillValue': -999.0}
fri_nc['fri_area_of_burn'].attrs={'standard_name':'fri_area_of_burn','units':'','grid_mapping':'albers_conical_equal_area','_FillValue': -999.0}
fri_nc.to_netcdf(os.path.join(indir, 'input','fri-fire.nc'))
