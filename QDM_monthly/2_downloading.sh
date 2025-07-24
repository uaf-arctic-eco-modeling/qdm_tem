### Author: Hélène Genet, hgenet@alaska.edu 
### Institution: Arctic Eco Modeling
### Team, Institute of Arctic Biology, University of Alaska Fairbanks 
### Date: September 23 2024 
### Description: 
### Command: $ 





########   USER SPECIFICATION   ########

### Path to directory to store the data downloaded
scriptdir='/Users/helenegenet/Helene/TEM/INPUT/production/script_parallelization/'


### AOI shapefile in EPSG:6931
mask6931='/Users/helenegenet/Helene/TEM/INPUT/production/script_parallelization/inputs/aoi_5k_buff_6931_2_0.tiff'
mask4325='/Users/helenegenet/Helene/TEM/INPUT/production/script_parallelization/inputs/aoi_4326.shp'


### Path to directory to store the data downloaded
indir='/Volumes/5TIV/DATA/CLIMATE/'


### WORLD CLIM related information
## List of variables to download
#wcvarlist=('tmin' 'tmax' 'tavg' 'prec' 'srad' 'wind' 'vapr')
wcvarlist=('tavg' 'prec' 'srad' 'vapr')
wcdir='/Volumes/5TIV/DATA/CLIMATE/WorldClim'



### TERRA information
#terrastartyr='1958'
#terraendyr='2021'
#terravarlist=('ppt' 'srad' 'tmax' 'tmin' 'vap')
#terradir='/Volumes/5TIV/DATA/CLIMATE/TERRA'


### ERA5 information
era5startyr='1940'
era5endyr='2025'
era5varlist=('t2m' 'd2m' 'tp' 'ssrd')
era5filelist=('data_0' 'data_0' 'data_1' 'data_1')
era5dir='/Volumes/5TIV/DATA/CLIMATE/ERA5/era5'



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




########## DOWNLOAD AND SUMMARIZE CLIMATE DATA ##########


### CRU-JRA download and summarize daily 
## Create storage directory
if [ -d $indir'CRU_JRA' ]; then
  echo 'directory exists ... remove'
  rm -r $indir'CRU_JRA'
fi
mkdir $indir'CRU_JRA'
cd $indir'CRU_JRA'

## Download the data
cd $indir'CRU_JRA'
for y in $(seq $cjstartyr $cjendyr); do
  echo $y
  for var in "${cjvarlist[@]}"; do
    wget -r 'ftp://'$usrname':'$psswrd'@ftp.ceda.ac.uk/badc/cru/data/cru_jra/cru_jra_'$cjversion'/data/'$var'/crujra.v'$cjversion'.5d.'$var'.'$y'.365d.noc.nc.gz'
  done
done

## Move the data to the input directory
mv $indir'CRU_JRA/ftp.ceda.ac.uk/badc/cru/data/cru_jra/cru_jra_'$cjversion'/data/'*  $indir'CRU_JRA/'
rm -r $indir'CRU_JRA/ftp.ceda.ac.uk'

## Create a secondary storage directory
if [ -d $indir'CRU_JRA_daily' ]; then
  echo 'directory exists ... remove'
  rm -r $indir'CRU_JRA_daily'
fi
mkdir $indir'CRU_JRA_daily'
cd $indir'CRU_JRA_daily'

## Crop and summarize the data from 6-hourly to daily
cd $indir'CRU_JRA_daily'
for y in $(seq $cjstartyr $cjendyr); do
  echo $y
  # Loop through variables
  for var in "${cjvarlist[@]}"; do
    echo $var
#    gunzip -c $indir'CRU_JRA/'$var'/crujra.v2.5.5d.'$var'.'$y'.365d.noc.nc.gz' > $indir'CRU_JRA_daily/cj_'$var'_'$y'.nc'
    gunzip -c '/Volumes/BACKUP1/DATA/CLIMATE_DATA/CRU_JRA/dap.ceda.ac.uk/badc/cru/data/cru_jra/cru_jra_2.3/data/'$var'/crujra.v2.5.5d.'$var'.'$y'.365d.noc.nc.gz' > $indir'CRU_JRA_daily/cj_'$var'_'$y'.nc'
    # Crop the original data to area of interest
    ncks -O -h -d lat,${ext4326[1]},${ext4326[3]} $indir'CRU_JRA_daily/cj_'$var'_'$y'.nc' $indir'CRU_JRA_daily/cj_'$var'_'$y'.nc'
    # Fix missing and fill values from the attributes so they are the same across all variables
    ncatted -O -h -a eulaVlliF_,,d,c, $indir'CRU_JRA_daily/cj_'$var'_'$y'.nc' $indir'CRU_JRA_daily/cj_'$var'_'$y'.nc'
    ncatted -O -h -a _FillValue,,o,f,1.e+20 $indir'CRU_JRA_daily/cj_'$var'_'$y'.nc' $indir'CRU_JRA_daily/cj_'$var'_'$y'.nc'
    ncatted -O -h -a missing_value,,o,f,1.e+20 $indir'CRU_JRA_daily/cj_'$var'_'$y'.nc' $indir'CRU_JRA_daily/cj_'$var'_'$y'.nc'
    # Summarize 6-hourly data to daily data
    if [[ $var == 'pre' ]] || [[ $var == 'dswrf' ]] ; then
      ncra --mro -O -d time,0,,4,4 -y total $indir'CRU_JRA_daily/cj_'$var'_'$y'.nc' $indir'CRU_JRA_daily/cj_'$var'_'$y'.nc'
    else
      ncra --mro -O -d time,0,,4,4 -y avg $indir'CRU_JRA_daily/cj_'$var'_'$y'.nc' $indir'CRU_JRA_daily/cj_'$var'_'$y'.nc'
    fi
    # Append all variables into a single yearly file
    if [[ $var == "${varlist[1]}" ]] ;then
      cp $indir'CRU_JRA_daily/cj_'$var'_'$y'.nc' $indir'CRU_JRA_daily/crujra_'$y'.nc'
    else
      ncatted -O -h -a eulaVlliF_,,d,c, $indir'CRU_JRA_daily/cj_'$var'_'$y'.nc' $indir'CRU_JRA_daily/cj_'$var'_'$y'.nc'
      ncks -A -h $indir'CRU_JRA_daily/cj_'$var'_'$y'.nc' $indir'CRU_JRA_daily/crujra_'$y'.nc'
      ncatted -O -h -a eulaVlliF_,,d,c, $indir'CRU_JRA_daily/crujra_'$y'.nc' $indir'CRU_JRA_daily/crujra_'$y'.nc'
    fi
  done
  rm $indir'CRU_JRA_daily/cj_'*
done



### WORLD-CLIM data download 
## Create storage directory
if [ -d $indir'WorldClim' ]; then
  echo 'directory exists ... remove'
  rm -r $indir'WorldClim'
fi
mkdir $indir'WorldClim'
cd $indir'WorldClim'

## Download the data
# variable loop
for var in "${wcvarlist[@]}"; do
  echo $var
  wget 'https://geodata.ucdavis.edu/climate/worldclim/2_1/base/wc2.1_30s_'$var'.zip'
done

## Uncompress the data
cd $indir'WorldClim'
for f in  *.zip; do
  echo $f
  unzip $f
done


### CMIP data download 
## Create storage directory
if [ -d $indir'CMIP' ]; then
  echo 'directory exists ...'
else
  mkdir $indir'CMIP'
fi
cd $indir'CMIP'

## Install the necessary libraries
pip install cdsapi -U
pip install requests -U

## Download the data using the python script
export cmipdir=$indir'CMIP'
export cmipversion=$cmipversion
export gcm_list=${modlist[0]}
export sc_list=${sclist[0]}
export var_list_daily=${cmipvarlistdaily[0]}
export var_list_monthly=${cmipvarlistmonthly[0]}
export var_list_hist=${cmipvarlisthist[0]}
export sc_hist=${schist[0]}
python3 $scriptdir'2_download_CMIP_2_0.py'

## Uncompress the data
cd indir'CMIP'
for f in  *.zip; do
  echo $f
  unzip $f
  rm *.json *.png
done



### ERA5 data download and summarize daily 
## Create storage directory
if [ -d $indir'ERA5' ]; then
  echo 'directory exists ...'
else
  mkdir $indir'ERA5'
fi
cd $indir'ERA5'

## Install the necessary libraries
pip install cdsapi -U
pip install requests -U

## Download the data using the python script
python3 $scriptdir'2_download_ERA5_2_0.py'

## Uncompress the data
cd indir'ERA5'
for f in  *.zip; do
  echo $f
  unzip $f
  rm *.json *.png
done



## Summarize CRU-JRA and CMIP data to monthly
export indir=$indir
export cjstartyr=$cjstartyr
export cjendyr=$cjendyr
export sclist="${sclist[0]}"
export sclist_short="${sclist_short[0]}"
export modlist="${modlist[0]}"
export modlist_short="${modlist_short[0]}"
export cmipvarlist="${cmipvarlist[0]}"
export cmipvarlist_short="${cmipvarlist_short[0]}"
export start_mon=$start_mon
export end_mon=$end_mon
export start_day=$start_day
export end_day=$end_day
export start_day_mri=$start_day_mri
export end_day_mri=$end_day_mri
export version=$cmipversion
export rep=$rep

python3 $scriptdir'/2_downloading_summarize_monthly.py'







