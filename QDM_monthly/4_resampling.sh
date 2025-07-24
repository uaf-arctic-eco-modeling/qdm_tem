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







########## RESAMPLING BY TILE ##########


for dir in $tilesdir/* ; do
  if [ -d $dir ]; then
    echo $dir
  fi
  
  if [ ! -d $dir'/climate_downscaling' ]; then
    mkdir $dir'/climate_downscaling'
  fi
  
  ### Compute the spatial references of the tile map
  ## Compute the extent of the original tile mask in 6931 EPSG
  msk_tile_6931_o=($(gdalinfo  $dir'/mask_6931.tiff' |sed -n -e '/^Origin = /p' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?'))
  msk_tile_6931_sz=($(gdalinfo  $dir'/mask_6931.tiff' |sed -n -e '/^Size is /p' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?'))
  msk_tile_6931_res=($(gdalinfo  $dir'/mask_6931.tiff' |sed -n -e '/^Pixel Size = /p' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?'))
  left=$(echo ${msk_tile_6931_o[0]} | bc)
  bottom=$(echo ${msk_tile_6931_o[1]}+${msk_tile_6931_res[1]}*${msk_tile_6931_sz[1]} | bc)
  top=$(echo ${msk_tile_6931_o[1]} | bc)
  right=$(echo ${msk_tile_6931_o[0]}+${msk_tile_6931_res[0]}*${msk_tile_6931_sz[0]} | bc)
  ext_tile_6931=($left $bottom $right $top)
  echo 'Sub-region extent in NSIDC EASE-Grid 2.0 North (EPSG 6931): ' ${ext_tile_6931[@]}
  
  
  ### Compute the extent of the reprojected mask with a buffer zone to prevent any gap resulting from the reprojection and croping
  msk_tile_4326_o=($(gdalinfo  $dir'/mask_4326.tiff' |sed -n -e '/^Origin = /p' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?'))
  msk_tile_4326_sz=($(gdalinfo  $dir'/mask_4326.tiff' |sed -n -e '/^Size is /p' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?'))
  msk_tile_4326_res=($(gdalinfo  $dir'/mask_4326.tiff' |sed -n -e '/^Pixel Size = /p' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?'))
  left=$(echo ${msk_tile_4326_o[0]} | bc)
  bottom=$(echo ${msk_tile_4326_o[1]}+${msk_tile_4326_res[1]}*${msk_tile_4326_sz[1]} | bc)
  top=$(echo ${msk_tile_4326_o[1]} | bc)
  right=$(echo ${msk_tile_4326_o[0]}+${msk_tile_4326_res[0]}*${msk_tile_4326_sz[0]} | bc)
  ext_tile_4326=($left $bottom $right $top)
  echo 'Sub-region extent in WGS84 (EPSG 4326): '${ext_tile_4326[@]}
  # Include the 5 km buffer (~0.1 degree) + the resolution of the CRU_JRA dataset
  ext_tile_4326_buffer=()
  ext_tile_4326_buffer[0]=$(echo ${ext_tile_4326[0]} - 3 - $cjres  | bc)
  ext_tile_4326_buffer[1]=$(echo ${ext_tile_4326[1]} - 3 - $cjres  | bc)
  ext_tile_4326_buffer[2]=$(echo ${ext_tile_4326[2]} + 3 + $cjres  | bc)
  ext_tile_4326_buffer[3]=$(echo ${ext_tile_4326[3]} + 3 + $cjres  | bc)
  # Keep the bounds reasonable
  if (( $(echo "${ext_tile_4326_buffer[0]} < -180.0" |bc -l) )); then
    ext_tile_4326_buffer[0]=-180.0
  fi
  if (( $(echo "${ext_tile_4326_buffer[1]} < -90.0" |bc -l) )); then
    ext_tile_4326_buffer[1]=-90.0
  fi
  if (( $(echo "${ext_tile_4326_buffer[2]} > 180.0" |bc -l) )); then
    ext_tile_4326_buffer[2]=180.0
  fi
  if (( $(echo "${ext_tile_4326_buffer[3]} > 90.0" |bc -l) )); then
    ext_tile_4326_buffer[3]=90.0
  fi
  echo 'Sub-region extent in WGS84 (EPSG 4326, including buffer): '${ext_tile_4326_buffer[@]}
  
  
  ### Crop and resample WorldClim reanalysis dataset
  echo 'Resampling World Clim data'
  if [ ! -d $dir'/climate_downscaling/WORLD_CLIM' ]; then
    mkdir $dir'/climate_downscaling/WORLD_CLIM'
  fi
  
  if [ ! -f $dir'/climate_downscaling/WORLD_CLIM/wc_rsmpl.nc' ]; then
    for m in {1..12}; do
      echo $m
      ## Compute day of year
      doy=$(echo $( date -j -f "%Y%m%d" 1970$(printf "%02d" $m)01 +%j ) | sed 's/^0*//')
      ## Loop through variables
      for var in "${wcvarlist[@]}"; do
        #echo $var

        gdalwarp -overwrite -co "FORMAT=NC4" -of netCDF -r average -s_srs EPSG:4326 -t_srs EPSG:6931 -tr ${msk_tile_6931_res[0]} ${msk_tile_6931_res[1]} -te ${ext_tile_6931[@]} $wcdir'/wc2.1_30s_'$var'_'$(printf "%02d" $m)'.tif' $dir'/climate_downscaling/WORLD_CLIM/tmp_'$var'_'$(printf "%02d" $m)'.nc'
        gdalwarp -overwrite -of netCDF -r average -s_srs EPSG:4326 -t_srs EPSG:6931 -tr ${msk_tile_6931_res[0]} ${msk_tile_6931_res[1]} -te ${ext_tile_6931[@]} $wcdir'/wc2.1_30s_'$var'_'$(printf "%02d" $m)'.tif' $dir'/climate_downscaling/WORLD_CLIM/tmp_'$var'_'$(printf "%02d" $m)'.nc'
        # Fix missing and fill values from the attributes so they are the same across all variables
        ncatted -O -h -a eulaVlliF_,,d,c, $dir'/climate_downscaling/WORLD_CLIM/tmp_'$var'_'$(printf "%02d" $m)'.nc' $dir'/climate_downscaling/WORLD_CLIM/tmp_'$var'_'$(printf "%02d" $m)'.nc'
        ncatted -O -h -a _FillValue,,o,f,1.e+20 $dir'/climate_downscaling/WORLD_CLIM/tmp_'$var'_'$(printf "%02d" $m)'.nc' $dir'/climate_downscaling/WORLD_CLIM/tmp_'$var'_'$(printf "%02d" $m)'.nc'
        ncatted -O -h -a missing_value,,o,f,1.e+20 $dir'/climate_downscaling/WORLD_CLIM/tmp_'$var'_'$(printf "%02d" $m)'.nc' $dir'/climate_downscaling/WORLD_CLIM/tmp_'$var'_'$(printf "%02d" $m)'.nc'
        # Rename coordinate dimensions 
        ncrename -O -h -d x,lon -d y,lat -v x,lon -v y,lat $dir'/climate_downscaling/WORLD_CLIM/tmp_'$var'_'$(printf "%02d" $m)'.nc' $dir'/climate_downscaling/WORLD_CLIM/tmp_'$var'_'$(printf "%02d" $m)'.nc'
        # Rename Band 1 to the variable name and set value for the time dimension (reset to 1 by default during transformation) to the DOY value
        ncap2 -O -h -s 'defdim("time",1); time[$time]='$doy'; '$var'[$time,$lat,$lon]=Band1' $dir'/climate_downscaling/WORLD_CLIM/tmp_'$var'_'$(printf "%02d" $m)'.nc' $dir'/climate_downscaling/WORLD_CLIM/tmp_'$var'_'$(printf "%02d" $m)'.nc'
        # Make the time dimension a record dimension for appending
        ncks -O -h --mk_rec_dmn time -x -v Band1 $dir'/climate_downscaling/WORLD_CLIM/tmp_'$var'_'$(printf "%02d" $m)'.nc' $dir'/climate_downscaling/WORLD_CLIM/tmp_'$var'_'$(printf "%02d" $m)'.nc'
        # Appending the variable files together
        if [[ $var == "${varlist[1]}" ]] ;then
          cp $dir'/climate_downscaling/WORLD_CLIM/tmp_'$var'_'$(printf "%02d" $m)'.nc' $dir'/climate_downscaling/WORLD_CLIM/wc_'$(printf "%02d" $m)'.nc'
        else
          ncks -A -h $dir'/climate_downscaling/WORLD_CLIM/tmp_'$var'_'$(printf "%02d" $m)'.nc' $dir'/climate_downscaling/WORLD_CLIM/wc_'$(printf "%02d" $m)'.nc'
        fi
        ncatted -O -h -a eulaVlliF_,,d,c, $dir'/climate_downscaling/WORLD_CLIM/wc_'$(printf "%02d" $m)'.nc' $dir'/climate_downscaling/WORLD_CLIM/wc_'$(printf "%02d" $m)'.nc'
        ncatted -O -h -a _FillValue,,o,f,1.e+20 $dir'/climate_downscaling/WORLD_CLIM/wc_'$(printf "%02d" $m)'.nc' $dir'/climate_downscaling/WORLD_CLIM/wc_'$(printf "%02d" $m)'.nc'
        ncatted -O -h -a missing_value,,o,f,1.e+20 $dir'/climate_downscaling/WORLD_CLIM/wc_'$(printf "%02d" $m)'.nc' $dir'/climate_downscaling/WORLD_CLIM/wc_'$(printf "%02d" $m)'.nc'
      done
      ncap2 -O -h -s'lat=float(lat); lon=float(lon);' $dir'/climate_downscaling/WORLD_CLIM/wc_'$(printf "%02d" $m)'.nc' $dir'/climate_downscaling/WORLD_CLIM/wc_'$(printf "%02d" $m)'.nc'
      rm $dir'/climate_downscaling/WORLD_CLIM/tmp_'*
      # Appending all the monthly outputs along the time dimension
      if [[ $m == 1 ]]; then
        cp $dir'/climate_downscaling/WORLD_CLIM/wc_'$(printf "%02d" $m)'.nc' $dir'/climate_downscaling/WORLD_CLIM/wc_rsmpl.nc'
      else 
        ncrcat -h -A $dir'/climate_downscaling/WORLD_CLIM/wc_rsmpl.nc' $dir'/climate_downscaling/WORLD_CLIM/wc_'$(printf "%02d" $m)'.nc' $dir'/climate_downscaling/WORLD_CLIM/wc_rsmpl.nc'
      fi
    done
    rm $dir'/climate_downscaling/WORLD_CLIM/wc_'??'.nc'
  fi
  
  
  ### Crop and resample CRU-JRA data
  echo 'Resampling CRU-JRA data'
  if [ ! -d $dir'/climate_downscaling/CRU_JRA' ]; then
    mkdir $dir'/climate_downscaling/CRU_JRA'
  fi
  if [ ! -f $dir'/climate_downscaling/CRU_JRA/cj_rsmpl.nc' ]; then
    for y in $(seq $cjstartyr $cjendyr); do
      ncks -O -h -d lat,${ext_tile_4326_buffer[1]},${ext_tile_4326_buffer[3]} -d lon,${ext_tile_4326_buffer[0]},${ext_tile_4326_buffer[2]} $cjdir'/crujra_'$y'_monthly.nc' $dir'/climate_downscaling/CRU_JRA/cj_'$y'.nc'
      # Fix missing and fill values from the attributes so they are the same across all variables
      ncatted -O -h -a eulaVlliF_,,d,c, $dir'/climate_downscaling/CRU_JRA/cj_'$y'.nc' $dir'/climate_downscaling/CRU_JRA/cj_'$y'.nc'
      ncatted -O -h -a _FillValue,,o,f,1.e+20 $dir'/climate_downscaling/CRU_JRA/cj_'$y'.nc' $dir'/climate_downscaling/CRU_JRA/cj_'$y'.nc'
      ncatted -O -h -a missing_value,,o,f,1.e+20 $dir'/climate_downscaling/CRU_JRA/cj_'$y'.nc' $dir'/climate_downscaling/CRU_JRA/cj_'$y'.nc'
      for var in "${cjvarlist[@]}"; do
        echo 'Year: ' $y ' Variable: ' $var
        gdalwarp -overwrite -of netCDF -r bilinear -s_srs EPSG:4326 -t_srs EPSG:6931 -tr ${msk_tile_6931_res[0]} ${msk_tile_6931_res[1]} -te ${ext_tile_6931[@]} NETCDF:$dir'/climate_downscaling/CRU_JRA/cj_'$y'.nc':$var $dir'/climate_downscaling/CRU_JRA/tmp_'$y'_'$var'.nc'
        # Reformating the resampled file
        export input=$dir'/climate_downscaling/CRU_JRA/tmp_'$y'_'$var'.nc'
        export y=$y
        export var=$var
        python3 $scriptdir'/4_resampling_crujra_2_0.py'  
        if [[ $var == "${cjvarlist[0]}" ]] ;then
          cp $dir'/climate_downscaling/CRU_JRA/tmp_'$y'_'$var'.nc' $dir'/climate_downscaling/CRU_JRA/cj_'$y'_rsmpl.nc'
          # Fix missing and fill values from the attributes so they are the same across all variables
          ncatted -O -h -a eulaVlliF_,,d,c, $dir'/climate_downscaling/CRU_JRA/cj_'$y'_rsmpl.nc' $dir'/climate_downscaling/CRU_JRA/cj_'$y'_rsmpl.nc'
          ncatted -O -h -a _FillValue,,o,f,1.e+20 $dir'/climate_downscaling/CRU_JRA/cj_'$y'_rsmpl.nc' $dir'/climate_downscaling/CRU_JRA/cj_'$y'_rsmpl.nc'
          ncatted -O -h -a missing_value,,o,f,1.e+20 $dir'/climate_downscaling/CRU_JRA/cj_'$y'_rsmpl.nc' $dir'/climate_downscaling/CRU_JRA/cj_'$y'_rsmpl.nc'
        else
          #ncks -A -h $outdir$dirname'/resampled/tmp_'$var'.nc' $outdir$dirname'/resampled/crujra.v2.4.5d.'$y'_'$(printf "%03d" $d)'.nc'
          ncks -A -h $dir'/climate_downscaling/CRU_JRA/tmp_'$y'_'$var'.nc' $dir'/climate_downscaling/CRU_JRA/cj_'$y'_rsmpl.nc'
          # Fix missing and fill values from the attributes so they are the same across all variables
          ncatted -O -h -a eulaVlliF_,,d,c, $dir'/climate_downscaling/CRU_JRA/cj_'$y'_rsmpl.nc' $dir'/climate_downscaling/CRU_JRA/cj_'$y'_rsmpl.nc'
          ncatted -O -h -a _FillValue,,o,f,1.e+20 $dir'/climate_downscaling/CRU_JRA/cj_'$y'_rsmpl.nc' $dir'/climate_downscaling/CRU_JRA/cj_'$y'_rsmpl.nc'
          ncatted -O -h -a missing_value,,o,f,1.e+20 $dir'/climate_downscaling/CRU_JRA/cj_'$y'_rsmpl.nc' $dir'/climate_downscaling/CRU_JRA/cj_'$y'_rsmpl.nc'
        fi
      done
      rm $dir'/climate_downscaling/CRU_JRA/tmp_'$y'_'*
      #done
      # Appending all the daily outputs along the time dimension
      if [[ $y == $cjstartyr ]]; then
        cp $dir'/climate_downscaling/CRU_JRA/cj_'$y'_rsmpl.nc' $dir'/climate_downscaling/CRU_JRA/cj_rsmpl.nc'
      else
        ncrcat -h -A $dir'/climate_downscaling/CRU_JRA/cj_rsmpl.nc' $dir'/climate_downscaling/CRU_JRA/cj_'$y'_rsmpl.nc' $dir'/climate_downscaling/CRU_JRA/cj_rsmpl.nc'
        ncatted -O -a history_of_appended_files,global,d,c,"" $dir'/climate_downscaling/CRU_JRA/cj_rsmpl.nc' $dir'/climate_downscaling/CRU_JRA/cj_rsmpl.nc'
        ncatted -O -h -a history,global,d,c,"" $dir'/climate_downscaling/CRU_JRA/cj_rsmpl.nc' $dir'/climate_downscaling/CRU_JRA/cj_rsmpl.nc'
      fi
    done
    rm $dir'/climate_downscaling/CRU_JRA/cj_'????'.nc' $dir'/climate_downscaling/CRU_JRA/cj_'????'_rsmpl.nc'
  fi
  
  
  ### Crop and resample to ERA5 data
  echo 'Resampling ERA5 data'
  if [ ! -d $dir'/climate_downscaling/ERA5' ]; then
    mkdir $dir'/climate_downscaling/ERA5'
  fi
  
  if [ ! -f $dir'/climate_downscaling/ERA5/era5_rsmpl.nc' ]; then
    for i in $(echo "${era5filelist[@]}" | tr ' ' '\n' | sort -u | tr '\n' ' '); do
      echo $i
      ncks -O -h -d latitude,${ext_tile_4326_buffer[1]},${ext_tile_4326_buffer[3]} -d longitude,${ext_tile_4326_buffer[0]},${ext_tile_4326_buffer[2]} $era5dir'/'$i'.nc' $dir'/climate_downscaling/ERA5/'$i'.nc'
      # Fix missing and fill values from the attributes so they are the same across all variables
      ncatted -O -h -a eulaVlliF_,,d,c, $dir'/climate_downscaling/ERA5/'$i'.nc' $dir'/climate_downscaling/ERA5/'$i'.nc'
      ncatted -O -h -a _FillValue,,o,f,1.e+20 $dir'/climate_downscaling/ERA5/'$i'.nc' $dir'/climate_downscaling/ERA5/'$i'.nc'
      ncatted -O -h -a missing_value,,o,f,1.e+20 $dir'/climate_downscaling/ERA5/'$i'.nc' $dir'/climate_downscaling/ERA5/'$i'.nc'
    done
    for i in $(seq 0 $((${#era5varlist[@]}-1))); do
      echo $i
      var="${era5varlist[$i]}"
      echo $var
      filename="${era5filelist[$i]}"
      echo $filename
      gdalwarp -overwrite -of netCDF -r bilinear -s_srs EPSG:4326 -t_srs EPSG:6931 -tr ${msk_tile_6931_res[0]} ${msk_tile_6931_res[1]} -te ${ext_tile_6931[@]} NETCDF:$dir'/climate_downscaling/ERA5/'$filename'.nc':$var $dir'/climate_downscaling/ERA5/tmp_'$var'.nc'
      # Reformating the resampled file
      export input=$dir'/climate_downscaling/ERA5/tmp_'$var'.nc'
      export var=$var
      export era5startyr=$era5startyr
      python3 $scriptdir'/4_resampling_era5_2_0.py'  
      if [[ $var == "${era5varlist[0]}" ]] ;then
        cp $dir'/climate_downscaling/ERA5/tmp_'$var'.nc' $dir'/climate_downscaling/ERA5/era5_rsmpl.nc'
        # Fix missing and fill values from the attributes so they are the same across all variables
        ncatted -O -h -a eulaVlliF_,,d,c, $dir'/climate_downscaling/ERA5/era5_rsmpl.nc' $dir'/climate_downscaling/ERA5/era5_rsmpl.nc'
        ncatted -O -h -a _FillValue,,o,f,1.e+20 $dir'/climate_downscaling/ERA5/era5_rsmpl.nc' $dir'/climate_downscaling/ERA5/era5_rsmpl.nc'
        ncatted -O -h -a missing_value,,o,f,1.e+20 $dir'/climate_downscaling/ERA5/era5_rsmpl.nc' $dir'/climate_downscaling/ERA5/era5_rsmpl.nc'
      else
        ncks -A -h $dir'/climate_downscaling/ERA5/tmp_'$var'.nc' $dir'/climate_downscaling/ERA5/era5_rsmpl.nc'
        # Fix missing and fill values from the attributes so they are the same across all variables
        ncatted -O -h -a eulaVlliF_,,d,c, $dir'/climate_downscaling/ERA5/era5_rsmpl.nc' $dir'/climate_downscaling/ERA5/era5_rsmpl.nc'
        ncatted -O -h -a _FillValue,,o,f,1.e+20 $dir'/climate_downscaling/ERA5/era5_rsmpl.nc' $dir'/climate_downscaling/ERA5/era5_rsmpl.nc'
        ncatted -O -h -a missing_value,,o,f,1.e+20 $dir'/climate_downscaling/ERA5/era5_rsmpl.nc' $dir'/climate_downscaling/ERA5/era5_rsmpl.nc'
      fi
    done
    rm $dir'/climate_downscaling/ERA5/tmp_'*'.nc' $dir'/climate_downscaling/ERA5/data_'*'.nc'
  fi
  
  
  
  ### Crop and resample CMIP data
  echo 'Resampling CMIP data'
  if [ ! -d $dir'/climate_downscaling/CMIP' ]; then
    mkdir $dir'/climate_downscaling/CMIP'
  fi
  
  if ls -A $dir"/climate_downscaling/CMIP/CMIP6_ssp"*"_rsmpl.nc" &> /dev/null; then
    echo "CMIP projection resampling already done"
  else
    for sc in ${sclist_sh[@]}; do
      for mod in ${modlist_sh[@]}; do
        echo 'sc:' $sc 'mod:' $mod
        ncks -O -h -d lat,${ext_tile_4326_buffer[1]},${ext_tile_4326_buffer[3]} -d lon,${ext_tile_4326_buffer[0]},${ext_tile_4326_buffer[2]} $cmipmonthdir'/CMIP'$cmipversion'_'$sc'_'$mod'_monthly.nc' $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_monthly.nc'
        # Fix missing and fill values from the attributes so they are the same across all variables
        ncatted -O -h -a eulaVlliF_,,d,c, $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_monthly.nc'  $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_monthly.nc'
        ncatted -O -h -a _FillValue,,o,f,1.e+20 $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_monthly.nc' $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_monthly.nc'
        ncatted -O -h -a missing_value,,o,f,1.e+20 $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_monthly.nc' $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_monthly.nc'
        for var in ${cmipvarlist_short_sh[@]}; do
          echo $var
          gdalwarp -overwrite -of netCDF -r bilinear -s_srs EPSG:4326 -t_srs EPSG:6931 -tr ${msk_tile_6931_res[0]} ${msk_tile_6931_res[1]} -te ${ext_tile_6931[@]} NETCDF:$dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_monthly.nc':$var $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_monthly_rsmpl_'$var'.nc'
          # Reformating the resampled file
          export input=$dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_monthly_rsmpl_'$var'.nc'
          export var=$var
          export cmipstartyr=$cmipstartyr
          python3 $scriptdir'/4_resampling_cmip6_2_0.py'  
          if [[ $var == "${cmipvarlist_short_sh[0]}" ]] ;then
            cp $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_monthly_rsmpl_'$var'.nc' $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_rsmpl.nc'
            # Fix missing and fill values from the attributes so they are the same across all variables
            ncatted -O -h -a eulaVlliF_,,d,c, $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_rsmpl.nc' $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_rsmpl.nc'
            ncatted -O -h -a _FillValue,,o,f,1.e+20 $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_rsmpl.nc' $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_rsmpl.nc'
            ncatted -O -h -a missing_value,,o,f,1.e+20 $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_rsmpl.nc' $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_rsmpl.nc'
          else
            ncks -A -h $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_monthly_rsmpl_'$var'.nc' $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_rsmpl.nc'
            # Fix missing and fill values from the attributes so they are the same across all variables
            ncatted -O -h -a eulaVlliF_,,d,c, $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_rsmpl.nc' $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_rsmpl.nc'
            ncatted -O -h -a _FillValue,,o,f,1.e+20 $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_rsmpl.nc' $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_rsmpl.nc'
            ncatted -O -h -a missing_value,,o,f,1.e+20 $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_rsmpl.nc' $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_rsmpl.nc'
          fi
        done
        rm $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_monthly_rsmpl_'*'.nc' $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_monthly.nc'
      done
    done
  fi
  
  sc='historical'
  
  if ls -A $dir"/climate_downscaling/CMIP/CMIP6_historical_"*"_rsmpl.nc" &> /dev/null; then
    echo "CMIP historical resampling already done"
  else
    for i in $(seq 0 $((${#modlist_sh[@]}-1))); do
      mod="${modlist_sh[$i]}"
      model="${modlist_short_sh[$i]}"
      for j in $(seq 0 $((${#cmipvarlisthist_short_sh[@]}-1))); do
        var="${cmipvarlisthist_short_sh[$j]}"
        variable="${cmipvarhistlist_sh[$j]}"
        echo 'sc:' $sc 'mod:' $mod 'model:' $model 'var:' $var 'variable:' $variable
        ncks -O -h -d lat,${ext_tile_4326_buffer[1]},${ext_tile_4326_buffer[3]} -d lon,${ext_tile_4326_buffer[0]},${ext_tile_4326_buffer[2]} $cmipdir'/CMIP'$cmipversion'_'$sc'_'$mod'_'$variable'/'$var'_Amon_'$model'_'$sc'_'$rep'_'$start_mon_hist'-'$end_mon_hist'.nc' $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_'$var'.nc'
        # Fix missing and fill values from the attributes so they are the same across all variables
        ncatted -O -h -a eulaVlliF_,,d,c, $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_'$var'.nc' $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_'$var'.nc'
        ncatted -O -h -a _FillValue,,o,f,1.e+20 $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_'$var'.nc' $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_'$var'.nc'
        ncatted -O -h -a missing_value,,o,f,1.e+20 $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_'$var'.nc' $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_'$var'.nc'
        gdalwarp -overwrite -of netCDF -r bilinear -s_srs EPSG:4326 -t_srs EPSG:6931 -tr ${msk_tile_6931_res[0]} ${msk_tile_6931_res[1]} -te ${ext_tile_6931[@]} NETCDF:$dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_'$var'.nc':$var $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_rsmpl_'$var'.nc'
        # Reformating the resampled file
        export input=$dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_rsmpl_'$var'.nc'
        export var=$var
        export cmiphiststart=$start_mon_hist
        python3 $scriptdir'/4_resampling_cmip6_hist_2_0.py'  
        if [[ $var == "${cmipvarlisthist_short_sh[0]}" ]] ;then
          cp $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_rsmpl_'$var'.nc' $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_rsmpl.nc'
          # Fix missing and fill values from the attributes so they are the same across all variables
          ncatted -O -h -a eulaVlliF_,,d,c, $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_rsmpl.nc' $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_rsmpl.nc'
          ncatted -O -h -a _FillValue,,o,f,1.e+20 $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_rsmpl.nc' $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_rsmpl.nc'
          ncatted -O -h -a missing_value,,o,f,1.e+20 $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_rsmpl.nc' $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_rsmpl.nc'
        else
          ncks -A -h $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_rsmpl_'$var'.nc' $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_rsmpl.nc'
          # Fix missing and fill values from the attributes so they are the same across all variables
          ncatted -O -h -a eulaVlliF_,,d,c, $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_rsmpl.nc' $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_rsmpl.nc'
          ncatted -O -h -a _FillValue,,o,f,1.e+20 $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_rsmpl.nc' $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_rsmpl.nc'
          ncatted -O -h -a missing_value,,o,f,1.e+20 $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_rsmpl.nc' $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_rsmpl.nc'
        fi
        rm $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_'$var'.nc' 
      done
      rm $dir'/climate_downscaling/CMIP/CMIP'$cmipversion'_'$sc'_'$mod'_rsmpl_'*'.nc' 
    done
  fi
done




















