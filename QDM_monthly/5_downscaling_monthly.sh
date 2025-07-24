### Author: Hélène Genet, hgenet@alaska.edu 
### Institution: Arctic Ecosystem Modeling
### Team, Institute of Arctic Biology, University of Alaska Fairbanks 
### Date: September 23 2024 
### Description: 
### Command: $ 



########   USER SPECIFICATION   ########

### Path to directory to store the data downloaded
scriptdir='/Users/helenegenet/Helene/TEM/INPUT/production/script_final'


### AOI shapefile in EPSG:4326 (WGS84)
mask4326=' /Volumes/5TIV/PROCESSED/MASK/aoi_4326.shp'
### AOI shapefile in EPSG:6931
mask6931=' /Volumes/5TIV/PROCESSED/MASK/aoi_5k_buff_6931.shp'


### Path to directory to store the data downloaded
#indir='/Volumes/5TIII/DATA/CLIMATE/'
indir='/Volumes/5TIV/DATA/CLIMATE'


### WORLD CLIM related information
## List of variables to download
#wcvarlist=('tmin' 'tmax' 'tavg' 'prec' 'srad' 'wind' 'vapr')
wcvarlist=('tavg' 'prec' 'srad' 'vapr')
wcdir='/Volumes/5TIV/DATA/CLIMATE/WorldClim'



### ERA5 information
era5startyr='1940'
era5endyr='2025'
era5varlist=('t2m' 'd2m' 'tp' 'ssrd')
era5filelist=('data_0' 'data_0' 'data_1' 'data_1')
era5dir='/Volumes/5TIV/DATA/CLIMATE/ERA5/era5'
era5startyr=1940



### CRU-JRA related information
## CRU-JRA first and last year of the historical records
cjstartyr=1901
cjendyr=2023
## Version of the dataset
cjversion='2.5'
## Account information for CEDA FTP
usrname='hgenet'
psswrd='i6,(~Anze^9k'
## List of variables to download
#cjvarlist=('tmin' 'tmax' 'tmp' 'pre' 'dswrf' 'ugrd' 'vgrd' 'spfh' 'pres')
cjvarlist=('tmp' 'pre' 'dswrf' 'spfh' 'pres')
## Resolution in degree
cjres=0.5
## CRU-JRA directory
cjdir='/Volumes/5TIV/DATA/CLIMATE/CRU_JRA_monthly'



### CMIP-related information
## CMIP version
cmipversion='6'
## CMIP replication
rep='r1i1p1f1_gn'
## List of long and short variable name
cmipvarlist='near_surface_air_temperature,near_surface_specific_humidity,precipitation,sea_level_pressure,surface_downwelling_shortwave_radiation'
cmipvarhistlist='near_surface_air_temperature,near_surface_specific_humidity,precipitation,sea_level_pressure,surface_downwelling_shortwave_radiation'
cmipvarhistlist_sh=('near_surface_air_temperature' 'near_surface_specific_humidity' 'precipitation' 'sea_level_pressure' 'surface_downwelling_shortwave_radiation')
cmipvarlisthist_short='tas,huss,pr,psl,rsds'
cmipvarlisthist_short_sh=('tas' 'huss' 'pr' 'psl' 'rsds')
cmipvarlist_short='tas,huss,pr,psl,rsds'
cmipvarlist_short_sh=('tas' 'huss' 'pr' 'psl' 'rsds')
## List of long and short scenario name
sclist='ssp1_2_6,ssp2_4_5,ssp3_7_0,ssp5_8_5'
sclist_sh=('ssp1_2_6' 'ssp2_4_5' 'ssp3_7_0' 'ssp5_8_5')
sclist_short='ssp126,ssp245,ssp370,ssp585'
schistlist='historical'
## List of long and short cliamte model name
modlist='access_cm2,mri_esm2_0'
modlist_sh=('access_cm2' 'mri_esm2_0')
modlist_short='ACCESS-CM2,MRI-ESM2-0'
modlist_short_sh=('ACCESS-CM2' 'MRI-ESM2-0')
## start and end year of the future simulations
start_day='20150101'
end_day='21001231'
## intermetdiate start and end year for the MRI future simulations
start_day_mri='20950919'
end_day_mri='20950918'
start_mon='20150116'
end_mon='21001216'
start_mon_hist='19700116'
end_mon_hist='20141216'
cmipdir='/Volumes/5TIV/DATA/CLIMATE/CMIP'
cmipmonthdir='/Volumes/5TIV/DATA/CLIMATE/CMIP_monthly'
cmipstartyr=2015



### tiles directory path
tilesdir='/Volumes/5TIV/PROCESSED/TILES2_0'






########   PROCESSING   ########


### Boundaries in EPSG 4326
# Get shapefile layer name
filename=$(basename -- "$mask4326")
mask4326l=${filename%.*}
# Reproject the mask shapefile projected in WGS1984
ext=($(ogrinfo -so $mask4326 $mask4326l |sed -n -e '/^Extent: /p' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?'))
echo ${ext[@]}
# Include the 5 km buffer (~0.1 degree) + the resolution of the CRU_JRA dataset
ext4326=()
ext4326[0]=$(echo ${ext[0]} - 0.5 - $cjres  | bc)
ext4326[1]=$(echo ${ext[1]} - 0.5 - $cjres  | bc)
ext4326[2]=$(echo ${ext[2]} + 0.5 + $cjres  | bc)
ext4326[3]=$(echo ${ext[3]} + 0.5 + $cjres  | bc)
# Keep the bounds reasonable
if (( $(echo "${ext4326[0]} < -180.0" |bc -l) )); then
  ext4326[0]=-180.0
fi
if (( $(echo "${ext4326[1]} < -90.0" |bc -l) )); then
  ext4326[1]=-90.0
fi
if (( $(echo "${ext4326[2]} > 180.0" |bc -l) )); then
  ext4326[2]=180.0
fi
if (( $(echo "${ext4326[3]} > 90.0" |bc -l) )); then
  ext4326[3]=90.0
fi
echo 'extent of the map in EPSG 4326' ${ext4326[@]}




########## DOWNSCALING BY TILE ##########



for dir in $tilesdir/* ; do
  echo $dir
  if [ ! -f $dir'/climate_downscaling/WORLD_CLIM/wc_rsmpl.nc' ] || [ ! -f $dir'/climate_downscaling/ERA5/era5_rsmpl.nc' ] || [ ! -f $dir'/climate_downscaling/TERRA/terra_rsmpl.nc' ] || [ ! -f $dir'/climate_downscaling/CRU_JRA/cj_rsmpl.nc' ] || [ ! -d $dir'/climate_downscaling/CMIP' ]; then 
    echo "Resampling not available or incomplete"
  else
    echo 'Resampling available'
    if ( ls -A $dir"/input/historic-climate.nc" &> /dev/null ) && ( ls -A $dir"/input/projected-climate_"*".nc" &> /dev/null ); then 
      echo "Downscaling done - pass"
    else
      echo 'Downscaling starts here for '$dir'...'
      export outdir=$dir
      export mask=$dir'/input/run-mask.nc'
      export wc=$dir'/climate_downscaling/WORLD_CLIM/wc_rsmpl.nc'
      export era5=$dir'/climate_downscaling/ERA5/era5_rsmpl.nc'
      export cj=$dir'/climate_downscaling/CRU_JRA/cj_rsmpl.nc'
      export terra=$dir'/climate_downscaling/TERRA/terra_rsmpl.nc'
      export cmipoutdir=$dir'/climate_downscaling/CMIP'
      export sclist="${sclist[0]}"
      export sclist_short="${sclist_short[0]}"
      export modlist="${modlist[0]}"
      export modlist_short="${modlist_short[0]}"
      export cmipversion=$cmipversion
      export topo=$dir'/input/topo.nc'
      python3 $scriptdir'/5_downscaling_1_units.py'  
      python3 $scriptdir'/5_downscaling_2_missing.py'  
      python3 $scriptdir'/5_downscaling_3_era5_corr.py'  
      python3 $scriptdir'/5_downscaling_4_historical.py'  
      python3 $scriptdir'/5_downscaling_5_projections.py'  
      python3 $scriptdir'/5_downscaling_6_fire.py'  
      rm $dir'/input/run-mask-update.nc'
      export era5corr=$dir'/climate_downscaling/ERA5/era5_corr.nc'
      python3 $scriptdir'/5_downscaling_7_masking.py'  
    fi
  fi
done

