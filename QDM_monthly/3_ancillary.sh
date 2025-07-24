




########   USER SPECIFICATION   ########

### General information
## Script directory
scriptdir='/Users/helenegenet/Helene/TEM/INPUT/production/script_final'
## Tile directory
tiledir='/Volumes/5TIV/PROCESSED/TILES2_0'
## Path to the circumpolar mask
mask='/Volumes/5TIV/PROCESSED/MASK/aoi_5k_buff_6931.tiff'
## Target resolution in m
res=4000
## Longitudinal and latitudinal sizes of the tiles in number of pixels, npx and npy respectively.
npx=100
npy=100


### Atmospheric information
## Input directory
atmindir='/Volumes/5TIV/DATA/ATMOSPHERE'
## Output directory
atmoutdir='/Volumes/5TIV/PROCESSED/ATMOSPHERE'

### CMIP information
## CMIP list of long and short scenario name
sclist=('ssp1_2_6' 'ssp2_4_5' 'ssp3_7_0' 'ssp5_8_5')
## List of cliamte model name
modlist=('access_cm2' 'mri_esm2_0')

### Soil texture information
## Path to the topographic inputs
textindir='/Volumes/5TIV/DATA/TEXTURE'
textoutdir='/Volumes/5TIV/PROCESSED/TEXTURE'
## URL to the GMTED 7.5 arcsec resolution
urlclay='https://files.isric.org/soilgrids/latest/data_aggregated/1000m/clay/'
urlsand='https://files.isric.org/soilgrids/latest/data_aggregated/1000m/sand/'
urlsilt='https://files.isric.org/soilgrids/latest/data_aggregated/1000m/silt/'
## Coarse resolution for gapfilling
gfres=50000



### Topography information
## Path to the topographic inputs
demindir='/Volumes/5TIV/DATA/TOPO'
demoutdir='/Volumes/5TIV/PROCESSED/TOPO'
## URL to the GMTED 7.5 arcsec resolution
url='https://edcintl.cr.usgs.gov/downloads/sciweb1/shared/topo/downloads/GMTED/Grid_ZipFiles/mn75_grd.zip'



### Vegetation information
## Path to the drainage dataset
drain='/Volumes/5TIV/PROCESSED/TOPO/drainage.tif'
## Path to the land cover inputs and outputs
vegindir='/Volumes/5TIV/DATA/VEGETATION'
vegoutdir='/Volumes/5TIV/PROCESSED/VEGETATION'
## URL to the GMTED 7.5 arcsec resolution
urlworld='https://github.com/wmgeolab/geoBoundaries/raw/main/releaseData/CGAZ/geoBoundariesCGAZ_ADM1.zip'
urleco='https://storage.googleapis.com/teow2016/Ecoregions2017.zip'
## Missing value for vegetation class
missval=-9999






########   PROCESSING ATMOSPHERIC DATA   ########



export indir=$atmindir
export outdir=$atmoutdir
python3 $scriptdir'/3_atmosphere_final.py'


for dir in $tiledir/* ; do
  if [ -d $dir ]; then
    tile=$(basename $dir)
    echo $tile
    if [ -f  $dir'/input/co2.nc' ]; then
      echo 'co2.nc already exists'
    else
      cp $atmoutdir'/co2.nc' $dir'/input/'
    fi
    for sc in ${sclist[@]};do
      echo $sc
      if [ -f  $dir'/input/projected-co2_'$sc'.nc' ]; then
        echo 'co2.nc already exists'
      else
        cp $atmoutdir'/projected-co2_'$sc'.nc' $dir'/input/'
      fi
    done
  fi
done





########   FRI DUMMY FILE   ########


for dir in $tiledir/* ; do
  if [ -d $dir ]; then
    tile=$(basename $dir)
    echo $tile
    if [ -f  $dir'/input/fri-fire.nc' ]; then
      echo 'FRI file exists'
    else
      export dir=$dir
      python3 $scriptdir'/3_fri.py'
    fi
  fi
done






########   PROCESSING SOIL TEXTURE  ########



### Download and organize raw data
cd $textindir
wget -r  $urlclay -P $textindir
wget -r  $urlsand -P $textindir
wget -r  $urlsilt -P $textindir
mv $textindir/files.isric.org/soilgrids/latest/data_aggregated/1000m/* $textindir
rm -r $textindir/files.isric.org


### Compute the spatial information of the mask 

## Assess metadata of the mask raster
# Coordinates of the upper left corners
msk_all_o=($(gdalinfo  $mask |sed -n -e '/^Origin = /p' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?'))
# Size of the raster
msk_all_sz=($(gdalinfo  $mask |sed -n -e '/^Size is /p' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?'))
# Pixel resolution
msk_all_res=($(gdalinfo  $mask |sed -n -e '/^Pixel Size = /p' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?'))
# Computation of the extent of the raster
msk_all_left=$(echo ${msk_all_o[0]} | bc)
msk_all_bottom=$(echo ${msk_all_o[1]}+${msk_all_res[1]}*${msk_all_sz[1]} | bc)
msk_all_top=$(echo ${msk_all_o[1]} | bc)
msk_all_right=$(echo ${msk_all_o[0]}+${msk_all_res[0]}*${msk_all_sz[0]} | bc)
ext_all_6931=($msk_all_left $msk_all_bottom $msk_all_right $msk_all_top)
echo 'Extent of the Mask :' ${ext_all_6931[@]}


## Tiles should fall on the 0 latitude and longitude and be 100 x 100 pixels size
n=$(echo "$msk_all_left/($res*$npx)" | bc -l)
ntilesx1=$(echo "$n" | bc -l | awk -F. '{print $1}')
d=$(echo "$n - $ntilesx1" | bc -l)
if (( $(echo "$d > 0" | bc -l) )); then
  ntilesx1=$((ntilesx1 + 1))
elif (( $(echo "$d < 0" | bc -l) )); then
  ntilesx1=$((ntilesx1 - 1))
fi
left_new=$(($ntilesx1 * $res * $npx))
n=$(echo "$msk_all_right/($res*$npx)" | bc -l)
ntilesx2=$(echo "$n" | bc -l | awk -F. '{print $1}')
d=$(echo "$n - $ntilesx2" | bc -l)
if (( $(echo "$d > 0" | bc -l) )); then
  ntilesx2=$((ntilesx2 + 1))
elif (( $(echo "$d < 0" | bc -l) )); then
  ntilesx2=$((ntilesx2 - 1))
fi
right_new=$(($ntilesx2 * $res * $npx))
n=$(echo "$msk_all_bottom/($res*$npy)" | bc -l)
ntilesy1=$(echo "$n" | bc -l | awk -F. '{print $1}')
d=$(echo "$n - $ntilesy1" | bc -l)
if (( $(echo "$d > 0" | bc -l) )); then
  ntilesy1=$((ntilesy1 + 1))
elif (( $(echo "$d < 0" | bc -l) )); then
  ntilesy1=$((ntilesy1 - 1))
fi
bottom_new=$(($ntilesy1 * $res * $npy))
n=$(echo "$msk_all_top/($res*$npy)" | bc -l)
ntilesy2=$(echo "$n" | bc -l | awk -F. '{print $1}')
d=$(echo "$n - $ntilesy2" | bc -l)
if (( $(echo "$d > 0" | bc -l) )); then
  ntilesy2=$((ntilesy2 + 1))
elif (( $(echo "$d < 0" | bc -l) )); then
  ntilesy2=$((ntilesy2 - 1))
fi
top_new=$(($ntilesy2 * $res * $npy))
ext_new_6931=($left_new $bottom_new $right_new $top_new)
echo 'New extent' ${ext_new_6931[@]}


### Compute the spatial information of the texture map 
text_res=($(gdalinfo  $textindir'/clay/clay_15-30cm_mean_1000.tif' |sed -n -e '/^Pixel Size = /p' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?'))
text_org=($(gdalinfo  $textindir'/clay/clay_15-30cm_mean_1000.tif' |sed -n -e '/^Origin = /p' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?'))
text_siz=($(gdalinfo  $textindir'/clay/clay_15-30cm_mean_1000.tif' |sed -n -e '/^Size is /p' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?'))
echo $(gdalinfo  $textindir'/clay/clay_15-30cm_mean_1000.tif' |grep "PROJCRS")
text_left=$(echo ${text_org[0]} | bc)
text_bottom=$(echo ${text_org[1]}+${text_res[1]}*${text_siz[1]} | bc)
text_top=$(echo ${text_org[1]} | bc)
text_right=$(echo ${text_org[0]}+${text_res[0]}*${text_siz[0]} | bc)
text_ext=($text_left 4500000 $text_right $text_top )
echo 'Extent of the Mask :' ${text_ext[@]}
echo 'Resolution of the Mask :' ${text_res[@]}


### Crop/Averaring the texture dataset
## Cropping
## Projection information found here: https://www.isric.org/explore/soilgrids/faq-soilgrids
gdalwarp -overwrite -of GTiff -r average -s_srs '+proj=igh +datum=WGS84 +no_defs +towgs84=0,0,0' -t_srs '+proj=igh +datum=WGS84 +no_defs +towgs84=0,0,0' -tr ${text_res[0]} ${text_res[1]} -te ${text_ext[@]} $textindir'/clay/clay_15-30cm_mean_1000.tif' $textoutdir'/clay_15-30cm_mean_1000.tif'
gdalwarp -overwrite -of GTiff -r average -s_srs '+proj=igh +datum=WGS84 +no_defs +towgs84=0,0,0' -t_srs '+proj=igh +datum=WGS84 +no_defs +towgs84=0,0,0' -tr ${text_res[0]} ${text_res[1]} -te ${text_ext[@]} $textindir'/clay/clay_30-60cm_mean_1000.tif' $textoutdir'/clay_30-60cm_mean_1000.tif'
gdalwarp -overwrite -of GTiff -r average -s_srs '+proj=igh +datum=WGS84 +no_defs +towgs84=0,0,0' -t_srs '+proj=igh +datum=WGS84 +no_defs +towgs84=0,0,0' -tr ${text_res[0]} ${text_res[1]} -te ${text_ext[@]} $textindir'/clay/clay_60-100cm_mean_1000.tif' $textoutdir'/clay_60-100cm_mean_1000.tif'
gdalwarp -overwrite -of GTiff -r average -s_srs '+proj=igh +datum=WGS84 +no_defs +towgs84=0,0,0' -t_srs '+proj=igh +datum=WGS84 +no_defs +towgs84=0,0,0' -tr ${text_res[0]} ${text_res[1]} -te ${text_ext[@]} $textindir'/silt/silt_15-30cm_mean_1000.tif' $textoutdir'/silt_15-30cm_mean_1000.tif'
gdalwarp -overwrite -of GTiff -r average -s_srs '+proj=igh +datum=WGS84 +no_defs +towgs84=0,0,0' -t_srs '+proj=igh +datum=WGS84 +no_defs +towgs84=0,0,0' -tr ${text_res[0]} ${text_res[1]} -te ${text_ext[@]} $textindir'/silt/silt_30-60cm_mean_1000.tif' $textoutdir'/silt_30-60cm_mean_1000.tif'
gdalwarp -overwrite -of GTiff -r average -s_srs '+proj=igh +datum=WGS84 +no_defs +towgs84=0,0,0' -t_srs '+proj=igh +datum=WGS84 +no_defs +towgs84=0,0,0' -tr ${text_res[0]} ${text_res[1]} -te ${text_ext[@]} $textindir'/silt/silt_60-100cm_mean_1000.tif' $textoutdir'/silt_60-100cm_mean_1000.tif'
#gdalwarp -overwrite -of GTiff -r average -s_srs '+proj=igh +datum=WGS84 +no_defs +towgs84=0,0,0' -t_srs '+proj=igh +datum=WGS84 +no_defs +towgs84=0,0,0' -tr ${text_res[0]} ${text_res[1]} -te ${text_ext[@]} $textindir'/sand/sand_15-30cm_mean_1000.tif' $textoutdir'/sand_15-30cm_mean_1000.tif'
#gdalwarp -overwrite -of GTiff -r average -s_srs '+proj=igh +datum=WGS84 +no_defs +towgs84=0,0,0' -t_srs '+proj=igh +datum=WGS84 +no_defs +towgs84=0,0,0' -tr ${text_res[0]} ${text_res[1]} -te ${text_ext[@]} $textindir'/sand/sand_30-60cm_mean_1000.tif' $textoutdir'/sand_30-60cm_mean_1000.tif'
#gdalwarp -overwrite -of GTiff -r average -s_srs '+proj=igh +datum=WGS84 +no_defs +towgs84=0,0,0' -t_srs '+proj=igh +datum=WGS84 +no_defs +towgs84=0,0,0' -tr ${text_res[0]} ${text_res[1]} -te ${text_ext[@]} $textindir'/sand/sand_60-100cm_mean_1000.tif' $textoutdir'/sand_60-100cm_mean_1000.tif'

## Averaging across the three soil layers btw 15 and 100 cm
gdal_calc.py -A $textoutdir'/clay_15-30cm_mean_1000.tif' -B $textoutdir'/clay_30-60cm_mean_1000.tif' -C $textoutdir'/clay_60-100cm_mean_1000.tif' --outfile=$textoutdir'/clay.tif' --calc="((A.astype(numpy.int32) * 15 + B.astype(numpy.int32) * 30 + C.astype(numpy.int32) * 40) / (150 + 300 + 400)).astype(numpy.int32)" --NoDataValue=-9999
gdal_calc.py -A $textoutdir'/silt_15-30cm_mean_1000.tif' -B $textoutdir'/silt_30-60cm_mean_1000.tif' -C $textoutdir'/silt_60-100cm_mean_1000.tif' --outfile=$textoutdir'/silt.tif' --calc="((A.astype(numpy.int32) * 15 + B.astype(numpy.int32) * 30 + C.astype(numpy.int32) * 40) / (150 + 300 + 400)).astype(numpy.int32)" --NoDataValue=-9999
#gdal_calc.py -A $textoutdir'/clay.tif' -B $textoutdir'/silt.tif' --outfile=$textoutdir'/sand.tif' --calc="(100 - A.astype(numpy.int32)- B.astype(numpy.int32)).astype(numpy.int32)" --NoDataValue=-9999

## Transformation and resampling: 
gdalwarp -overwrite -of GTiff -r average -s_srs '+proj=igh +datum=WGS84 +no_defs +towgs84=0,0,0' -t_srs EPSG:6931 -tr ${mask_res[0]} ${mask_res[1]} -te ${ext_new_6931[@]} $textoutdir'/clay.tif' $textoutdir'/clay_6931.tif'
gdalwarp -overwrite -of GTiff -r average -s_srs '+proj=igh +datum=WGS84 +no_defs +towgs84=0,0,0' -t_srs EPSG:6931 -tr ${mask_res[0]} ${mask_res[1]} -te ${ext_new_6931[@]} $textoutdir'/silt.tif' $textoutdir'/silt_6931.tif'
#gdal_calc.py -A $textoutdir'/clay_6931.tif' -B $textoutdir'/silt_6931.tif' --outfile=$textoutdir'/sand_6931.tif' --calc="(100 - A.astype(numpy.int32)- B.astype(numpy.int32)).astype(numpy.int32)" --NoDataValue=-9999



### Gapfilling as water bodies classification might differ from the one we are using.
## from fine to coarse resolution
gdalwarp -overwrite -of GTiff -r average -s_srs EPSG:6931 -t_srs EPSG:6931 -tr ${gfres} -${gfres} -te ${ext_new_6931[@]} $textoutdir'/clay_6931.tif' $textoutdir'/clay_gf.tif'
gdalwarp -overwrite -of GTiff -r average -s_srs EPSG:6931 -t_srs EPSG:6931 -tr ${gfres} -${gfres} -te ${ext_new_6931[@]} $textoutdir'/silt_6931.tif' $textoutdir'/silt_gf.tif'
#gdalwarp -overwrite -of GTiff -r average -s_srs EPSG:6931 -t_srs EPSG:6931 -tr ${gfres} -${gfres} -te ${ext_new_6931[@]} $textoutdir'/sand_6931.tif' $textoutdir'/sand_gf.tif'
## from coarse to fine resolution
gdalwarp -overwrite -of GTiff -r near -s_srs EPSG:6931 -t_srs EPSG:6931 -tr ${mask_res[0]} ${mask_res[1]} -te ${ext_new_6931[@]} $textoutdir'/clay_gf.tif' $textoutdir'/clay_gf_d.tif'
gdalwarp -overwrite -of GTiff -r near -s_srs EPSG:6931 -t_srs EPSG:6931 -tr ${mask_res[0]} ${mask_res[1]} -te ${ext_new_6931[@]} $textoutdir'/silt_gf.tif' $textoutdir'/silt_gf_d.tif'
#gdal_calc.py -A $textoutdir'/clay_gf.tif' -B $textoutdir'/silt_gf.tif' --outfile=$textoutdir'/sand_gf.tif' --calc="(100 - A.astype(numpy.int32)- B.astype(numpy.int32)).astype(numpy.int32)" --NoDataValue=-9999

## Gapfilling

export mskpath=$(echo $mask)
export clay_org_path=$(echo $textoutdir'/clay_6931.tif')
export clay_out_path=$(echo $textoutdir'/clay_6931_gf.tif')
export clay_coarse_path=$(echo $textoutdir'/clay_gf_d.tif')
export silt_org_path=$(echo $textoutdir'/silt_6931.tif')
export silt_out_path=$(echo $textoutdir'/silt_6931_gf.tif')
export silt_coarse_path=$(echo $textoutdir'/silt_gf_d.tif')
export extent="${ext_new_6931[@]}"
export resolution="${msk_all_res[@]}"

python3 $scriptdir'/3_soil_texture_gapfilling2_0.py'    
gdal_calc.py -A $textoutdir'/clay_6931_gf.tif' -B $textoutdir'/silt_6931_gf.tif' --outfile=$textoutdir'/sand_6931_gf.tif' --calc="(100 - A.astype(numpy.int32)- B.astype(numpy.int32)).astype(numpy.int32)" --NoDataValue=-9999


### Remove heavy tiff files
rm $textoutdir'/silt_gf_d.tif' $textoutdir'/silt_gf.tif' $textoutdir'/sand_gf_d.tif' $textoutdir'/sand_gf.tif'  $textoutdir'/clay_gf_d.tif' $textoutdir'/clay_gf.tif' 

### Tiling the topographic information and format the final input files

## The loop by pre-existing tiles (created in tilling.sh)
#dir='/Volumes/5TIV/PROCESSED/TILES/H01_V05'
for dir in $tiledir/* ; do
  if [ -d $dir ]; then
    echo $dir
    # Compute the extent of the original tile mask in 6931 EPSG
    msk_tile_6931_o=($(gdalinfo  $dir'/mask_6931.tiff' |sed -n -e '/^Origin = /p' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?'))
    msk_tile_6931_sz=($(gdalinfo  $dir'/mask_6931.tiff' |sed -n -e '/^Size is /p' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?'))
    msk_tile_6931_res=($(gdalinfo  $dir'/mask_6931.tiff' |sed -n -e '/^Pixel Size = /p' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?'))
    left=$(echo ${msk_tile_6931_o[0]} | bc)
    bottom=$(echo ${msk_tile_6931_o[1]}+${msk_tile_6931_res[1]}*${msk_tile_6931_sz[1]} | bc)
    top=$(echo ${msk_tile_6931_o[1]} | bc)
    right=$(echo ${msk_tile_6931_o[0]}+${msk_tile_6931_res[0]}*${msk_tile_6931_sz[0]} | bc)
    ext_tile_6931=($left $bottom $right $top)
    echo 'Sub-region extent in NSIDC EASE-Grid 2.0 North (EPSG 6931): ' ${ext_tile_6931[@]}
    # Crop and convert the topographic information
    gdalwarp -overwrite -of netCDF -r bilinear -s_srs EPSG:6931 -t_srs EPSG:6931 -tr ${msk_tile_6931_res[0]} ${msk_tile_6931_res[1]} -te ${ext_tile_6931[@]} $textoutdir'/clay_6931_gf.tif' $dir'/clay.nc'
    gdalwarp -overwrite -of netCDF -r bilinear -s_srs EPSG:6931 -t_srs EPSG:6931 -tr ${msk_tile_6931_res[0]} ${msk_tile_6931_res[1]} -te ${ext_tile_6931[@]} $textoutdir'/silt_6931_gf.tif' $dir'/silt.nc'
    gdalwarp -overwrite -of netCDF -r bilinear -s_srs EPSG:6931 -t_srs EPSG:6931 -tr ${msk_tile_6931_res[0]} ${msk_tile_6931_res[1]} -te ${ext_tile_6931[@]} $textoutdir'/sand_6931_gf.tif' $dir'/sand.nc'
    # Merge and format the final netcdf topo.nc input file for each tile
    ncrename -O -h -v Band1,pct_clay -d x,X -d y,Y -v y,Y -v x,X $dir'/clay.nc'
    ncrename -O -h -v Band1,pct_silt -d x,X -d y,Y -v y,Y -v x,X $dir'/silt.nc'
    ncrename -O -h -v Band1,pct_sand -d x,X -d y,Y -v y,Y -v x,X $dir'/sand.nc'
    cp $dir'/clay.nc' $dir'/input/soil-texture.nc'
    ncks -A -h $dir'/silt.nc' $dir'/input/soil-texture.nc'
    ncks -A -h $dir'/sand.nc' $dir'/input/soil-texture.nc'
    # Fix missing and fill values from the attributes so they are the same across all variables
    ncatted -O -h -a eulaVlliF_,,d,c, $dir'/input/soil-texture.nc' $dir'/input/soil-texture.nc'
    ncatted -O -h -a _FillValue,,o,f,1.e+20 $dir'/input/soil-texture.nc' $dir'/input/soil-texture.nc'
    ncatted -O -h -a missing_value,,o,f,1.e+20 $dir'/input/soil-texture.nc' $dir'/input/soil-texture.nc'
    # Include lat and lon from run-mask.nc
#    ncks -O -h -v lat,lon $dir'/input/run-mask.nc' $dir'/latlon.nc'
    ncks -A -h $dir'/latlon.nc' $dir'/input/soil-texture.nc'
    # Format of variables
    ncap2 -O -h -s'pct_clay=float(pct_clay); pct_silt=float(pct_silt); pct_sand=float(pct_sand)' $dir'/input/soil-texture.nc' $dir'/input/soil-texture.nc'
    # Fix attributes of the topo.nc file
    ncatted -O -h -a long_name,pct_clay,o,c,'percent clay from Soil Grid at 1km resolution' $dir'/input/soil-texture.nc' $dir'/input/soil-texture.nc'
    ncatted -O -h -a units,pct_clay,o,c,'percent' $dir'/input/soil-texture.nc' $dir'/input/soil-texture.nc'
    ncatted -O -h -a long_name,pct_silt,o,c,'percent silt from Soil Grid at 1km resolution' $dir'/input/soil-texture.nc' $dir'/input/soil-texture.nc'
    ncatted -O -h -a units,pct_silt,o,c,'percent' $dir'/input/soil-texture.nc' $dir'/input/soil-texture.nc'
    ncatted -O -h -a long_name,pct_sand,o,c,'percent sand from 100 - clay_pct - silt_pct' $dir'/input/soil-texture.nc' $dir'/input/soil-texture.nc'
    ncatted -O -h -a units,pct_sand,o,c,'percent' $dir'/input/soil-texture.nc' $dir'/input/soil-texture.nc'
    ncatted -O -h -a long_name,lon,o,c,'x coordinate of projection' $dir'/input/soil-texture.nc' $dir'/input/soil-texture.nc'
    ncatted -O -h -a units,lon,o,c,'m' $dir'/input/soil-texture.nc' $dir'/input/soil-texture.nc'
    ncatted -O -h -a projection,lat,o,c,'EASE-Grid 2.0 North' $dir'/input/soil-texture.nc' $dir'/input/soil-texture.nc'
    ncatted -O -h -a epsg,lat,o,c,'6931' $dir'/input/soil-texture.nc' $dir'/input/soil-texture.nc'
    ncatted -O -h -a long_name,lat,o,c,'y coordinate of projection' $dir'/input/soil-texture.nc' $dir'/input/soil-texture.nc'
    ncatted -O -h -a units,lat,o,c,'m' $dir'/input/soil-texture.nc' $dir'/input/soil-texture.nc'
    ncatted -O -h -a projection,lat,o,c,'EASE-Grid 2.0 North' $dir'/input/soil-texture.nc' $dir'/input/soil-texture.nc'
    ncatted -O -h -a epsg,lat,o,c,'6931' $dir'/input/soil-texture.nc' $dir'/input/soil-texture.nc'
    # Clean directory
    rm $dir'/clay.nc' $dir'/silt.nc' $dir'/sand.nc' 
  fi
done





########   PROCESSING TOPOGRAPHIC DATA   ########


### Download and unzip raw data
cd $demindir
wget $url -P $demindir
unzip $demindir'/'*'.zip' -d $demindir
gdal_translate -of GTiff  $demindir'/mn75_grd' $demoutdir'/elevation_250m_4326.tif'


### Compute the spatial information of the DEM dataset
dem_res=($(gdalinfo  $demoutdir'/elevation_250m_4326.tif' |sed -n -e '/^Pixel Size = /p' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?'))
dem_org=($(gdalinfo  $demoutdir'/elevation_250m_4326.tif' |sed -n -e '/^Origin = /p' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?'))
dem_siz=($(gdalinfo  $demoutdir'/elevation_250m_4326.tif' |sed -n -e '/^Size is /p' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?'))

dem_left=$(echo ${dem_org[0]} | bc)
dem_bottom=$(echo ${dem_org[1]}+${dem_res[1]}*${dem_siz[1]} | bc)
dem_top=$(echo ${dem_org[1]} | bc)
dem_right=$(echo ${dem_org[0]}+${dem_res[0]}*${dem_siz[0]} | bc)
dem_ext=($dem_left 40 $dem_right $dem_top)


### Crop/Transform/Resample the elevation dataset
gdalwarp -overwrite -of GTiff -r average -s_srs EPSG:4326 -t_srs EPSG:6931 -tr ${mask_res[0]} ${mask_res[1]} -te ${ext_new_6931[@]} $demoutdir'/elevation_250m_4326.tif' $demoutdir'/elevation_4k_6931_mask.tif'
#gdalwarp -overwrite -of netCDF -r average -s_srs EPSG:4326 -t_srs EPSG:6931 -tr ${mask_res[0]} ${mask_res[1]} -te ${mask_ext[@]} $demoutdir'/elevation_250m_4326.tif' $demoutdir'/elevation_4k_6931_mask.nc'


### Compute the slope in degree and Crop/Transform/Resample the slope dataset
gdaldem slope -s 111120 $demoutdir'/elevation_250m_4326.tif' $demoutdir'/slope_250m_4326.tif' 
gdalwarp -overwrite -of GTiff -r average -s_srs EPSG:4326 -t_srs EPSG:6931 -tr ${mask_res[0]} ${mask_res[1]} -te ${ext_new_6931[@]} $demoutdir'/slope_250m_4326.tif' $demoutdir'/slope_4k_6931_mask.tif'
#gdalwarp -overwrite -of netCDF -r bilinear -s_srs EPSG:6931 -t_srs EPSG:6931 -tr ${mask_res[0]} ${mask_res[1]} -te ${mask_ext[@]} $demoutdir'/slope_4k_6931_mask.tif' $demoutdir'/slope_4k_6931_mask.nc'


### Compute the slope in degree and Crop/Transform/Resample the aspect dataset
gdaldem aspect -s 111120 $demoutdir'/elevation_250m_4326.tif' $demoutdir'/aspect_250m_4326.tif' 
gdalwarp -overwrite -of GTiff -r average -s_srs EPSG:4326 -t_srs EPSG:6931 -tr ${mask_res[0]} ${mask_res[1]} -te ${ext_new_6931[@]} $demoutdir'/aspect_250m_4326.tif' $demoutdir'/aspect_4k_6931_mask.tif'
#gdalwarp -overwrite -of netCDF -r bilinear -s_srs EPSG:6931 -t_srs EPSG:6931 -tr ${mask_res[0]} ${mask_res[1]} -te ${mask_ext[@]} $demoutdir'/aspect_4k_6931_mask.tif' $demoutdir'/aspect_4k_6931_mask.nc'


### Compute the slope in degree and Crop/Transform/Resample the topographic position index dataset
gdaldem TPI -s 111120 $demoutdir'/elevation_250m_4326.tif' $demoutdir'/tpi_250m_4326.tif' 
gdalwarp -overwrite -of GTiff -r average -s_srs EPSG:4326 -t_srs EPSG:6931 -tr ${mask_res[0]} ${mask_res[1]} -te ${ext_new_6931[@]} $demoutdir'/tpi_250m_4326.tif' $demoutdir'/tpi_4k_6931_mask.tif'
#gdalwarp -overwrite -of netCDF -r bilinear -s_srs EPSG:6931 -t_srs EPSG:6931 -tr ${mask_res[0]} ${mask_res[1]} -te ${mask_ext[@]} $demoutdir'/tpi_4k_6931_mask.tif' $demoutdir'/tpi_4k_6931_mask.nc'


### Classify the drainage class based on topography: 0: well-drained; 1: poorly-drained
gdal_calc.py -A '/Volumes/5TIV/PROCESSED/TOPO/tpi_4k_6931_mask.tif' -B '/Volumes/5TIV/PROCESSED/TOPO/slope_4k_6931_mask.tif' --outfile='/Volumes/5TIV/PROCESSED/TOPO/drainage.tif' --calc="numpy.where(((A >= -0.05) & (A <= 0.05) & (B <= 1.0)), 1, 0)" --NoDataValue=-9999


### Remove heavy tiff files
#rm $demoutdir'/elevation_250m_4326.tif' $demoutdir'/slope_250m_4326.tif' $demoutdir'/aspect_250m_4326.tif' $demoutdir'/tpi_250m_4326.tif'


### Tiling the topographic information and format the final input files

## The loop by pre-existing tiles (created in tilling.sh)
for dir in $tiledir/* ; do
  if [ -d $dir ]; then
    echo $dir
    # Compute the extent of the original tile mask in 6931 EPSG
    msk_tile_6931_o=($(gdalinfo  $dir'/mask_6931.tiff' |sed -n -e '/^Origin = /p' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?'))
    msk_tile_6931_sz=($(gdalinfo  $dir'/mask_6931.tiff' |sed -n -e '/^Size is /p' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?'))
    msk_tile_6931_res=($(gdalinfo  $dir'/mask_6931.tiff' |sed -n -e '/^Pixel Size = /p' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?'))
    left=$(echo ${msk_tile_6931_o[0]} | bc)
    bottom=$(echo ${msk_tile_6931_o[1]}+${msk_tile_6931_res[1]}*${msk_tile_6931_sz[1]} | bc)
    top=$(echo ${msk_tile_6931_o[1]} | bc)
    right=$(echo ${msk_tile_6931_o[0]}+${msk_tile_6931_res[0]}*${msk_tile_6931_sz[0]} | bc)
    ext_tile_6931=($left $bottom $right $top)
    echo 'Sub-region extent in NSIDC EASE-Grid 2.0 North (EPSG 6931): ' ${ext_tile_6931[@]}
    # Crop and convert the topographic information
    gdalwarp -overwrite -of netCDF -r bilinear -s_srs EPSG:6931 -t_srs EPSG:6931 -tr ${msk_tile_6931_res[0]} ${msk_tile_6931_res[1]} -te ${ext_tile_6931[@]} $demoutdir'/elevation_4k_6931_mask.tif' $dir'/elevation.nc'
    gdalwarp -overwrite -of netCDF -r bilinear -s_srs EPSG:6931 -t_srs EPSG:6931 -tr ${msk_tile_6931_res[0]} ${msk_tile_6931_res[1]} -te ${ext_tile_6931[@]} $demoutdir'/slope_4k_6931_mask.tif' $dir'/slope.nc'
    gdalwarp -overwrite -of netCDF -r bilinear -s_srs EPSG:6931 -t_srs EPSG:6931 -tr ${msk_tile_6931_res[0]} ${msk_tile_6931_res[1]} -te ${ext_tile_6931[@]} $demoutdir'/aspect_4k_6931_mask.tif' $dir'/aspect.nc'
    gdalwarp -overwrite -of netCDF -r bilinear -s_srs EPSG:6931 -t_srs EPSG:6931 -tr ${msk_tile_6931_res[0]} ${msk_tile_6931_res[1]} -te ${ext_tile_6931[@]} $demoutdir'/tpi_4k_6931_mask.tif' $dir'/tpi.nc'
    gdalwarp -overwrite -of netCDF -r bilinear -s_srs EPSG:6931 -t_srs EPSG:6931 -tr ${msk_tile_6931_res[0]} ${msk_tile_6931_res[1]} -te ${ext_tile_6931[@]} $demoutdir'/drainage.tif' $dir'/input/drainage.nc'
    # Merge and format the final netcdf topo.nc input file for each tile
    ncrename -O -h -v Band1,elevation -d x,X -d y,Y -v y,Y -v x,X $dir'/elevation.nc'
    ncrename -O -h -v Band1,slope -d x,X -d y,Y -v y,Y -v x,X $dir'/slope.nc'
    ncrename -O -h -v Band1,aspect -d x,X -d y,Y -v y,Y -v x,X $dir'/aspect.nc'
    ncrename -O -h -v Band1,tpi -d x,X -d y,Y -v y,Y -v x,X $dir'/tpi.nc'
    ncrename -O -h -v Band1,drainage_class -d x,X -d y,Y -v y,Y -v x,X $dir'/input/drainage.nc'
    cp $dir'/elevation.nc' $dir'/input/topo.nc'
    ncks -A -h $dir'/slope.nc' $dir'/input/topo.nc'
    ncks -A -h $dir'/aspect.nc' $dir'/input/topo.nc'
    ncks -A -h $dir'/tpi.nc' $dir'/input/topo.nc'
    # Fix missing and fill values from the attributes so they are the same across all variables
    ncatted -O -h -a eulaVlliF_,,d,c, $dir'/input/topo.nc' $dir'/input/topo.nc'
    ncatted -O -h -a _FillValue,,o,f,1.e+20 $dir'/input/topo.nc' $dir'/input/topo.nc'
    ncatted -O -h -a missing_value,,o,f,1.e+20 $dir'/input/topo.nc' $dir'/input/topo.nc'
    ncatted -O -h -a eulaVlliF_,,d,c, $dir'/input/drainage.nc' $dir'/input/drainage.nc'
    ncatted -O -h -a _FillValue,,o,f,1.e+20 $dir'/input/drainage.nc' $dir'/input/drainage.nc'
    ncatted -O -h -a missing_value,,o,f,1.e+20 $dir'/input/drainage.nc' $dir'/input/drainage.nc'
    # Include lat and lon from run-mask.nc
    ncks -O -h -v lat,lon $dir'/input/run-mask.nc' $dir'/latlon.nc'
    ncks -A -h $dir'/latlon.nc' $dir'/input/topo.nc'
    ncks -A -h $dir'/latlon.nc' $dir'/input/drainage.nc'
    # Format of variables
    ncap2 -O -h -s'elevation=double(elevation); slope=double(slope); aspect=double(aspect); tpi=double(tpi)' $dir'/input/topo.nc' $dir'/input/topo.nc'
    ncap2 -O -h -s'drainage_class=int(drainage_class);' $dir'/input/drainage.nc' $dir'/input/drainage.nc'
    # Fix attributes of the topo.nc file
    ncatted -O -h -a long_name,elevation,o,c,'elevation from GMTED 2010 at 7.5 arc-second' $dir'/input/topo.nc' $dir'/input/topo.nc'
    ncatted -O -h -a units,elevation,o,c,'m' $dir'/input/topo.nc' $dir'/input/topo.nc'
    ncatted -O -h -a long_name,slope,o,c,'slope from GMTED 2010 at 7.5 arc-second' $dir'/input/topo.nc' $dir'/input/topo.nc'
    ncatted -O -h -a units,slope,o,c,'degree' $dir'/input/topo.nc' $dir'/input/topo.nc'
    ncatted -O -h -a long_name,aspect,o,c,'aspect from GMTED 2010 at 7.5 arc-second' $dir'/input/topo.nc' $dir'/input/topo.nc'
    ncatted -O -h -a units,aspect,o,c,'degree' $dir'/input/topo.nc' $dir'/input/topo.nc'
    ncatted -O -h -a long_name,tpi,o,c,'topographic position index from GMTED 2010 at 7.5 arc-secong' $dir'/input/topo.nc' $dir'/input/topo.nc'
    ncatted -O -h -a units,tpi,o,c,'unitless' $dir'/input/topo.nc' $dir'/input/topo.nc'
    ncatted -O -h -a long_name,lon,o,c,'x coordinate of projection' $dir'/input/topo.nc' $dir'/input/topo.nc'
    ncatted -O -h -a units,lon,o,c,'m' $dir'/input/topo.nc' $dir'/input/topo.nc'
    ncatted -O -h -a projection,lat,o,c,'EASE-Grid 2.0 North' $dir'/input/topo.nc' $dir'/input/topo.nc'
    ncatted -O -h -a epsg,lat,o,c,'6931' $dir'/input/topo.nc' $dir'/input/topo.nc'
    ncatted -O -h -a long_name,lat,o,c,'y coordinate of projection' $dir'/input/topo.nc' $dir'/input/topo.nc'
    ncatted -O -h -a units,lat,o,c,'m' $dir'/input/topo.nc' $dir'/input/topo.nc'
    ncatted -O -h -a projection,lat,o,c,'EASE-Grid 2.0 North' $dir'/input/topo.nc' $dir'/input/topo.nc'
    ncatted -O -h -a epsg,lat,o,c,'6931' $dir'/input/topo.nc' $dir'/input/topo.nc'
    # Fix attributes of the drainage.nc file
    ncatted -O -h -a long_name,drainage_class,o,c,'drainage class: 0: well-drained; 1: poorly-drained' $dir'/input/drainage.nc' $dir'/input/drainage.nc'
    ncatted -O -h -a units,drainage_class,o,c,'m' $dir'/input/drainage.nc' $dir'/input/drainage.nc'
    ncatted -O -h -a _FillValue,drainage_class,o,f,1.e+20 $dir'/input/drainage.nc' $dir'/input/drainage.nc'
    ncatted -O -h -a long_name,lon,o,c,'x coordinate of projection' $dir'/input/drainage.nc' $dir'/input/drainage.nc'
    ncatted -O -h -a units,lon,o,c,'m' $dir'/input/drainage.nc' $dir'/input/drainage.nc'
    ncatted -O -h -a projection,lat,o,c,'EASE-Grid 2.0 North' $dir'/input/drainage.nc' $dir'/input/drainage.nc'
    ncatted -O -h -a epsg,lat,o,c,'6931' $dir'/input/drainage.nc' $dir'/input/drainage.nc'
    ncatted -O -h -a long_name,lat,o,c,'y coordinate of projection' $dir'/input/drainage.nc' $dir'/input/drainage.nc'
    ncatted -O -h -a units,lat,o,c,'m' $dir'/input/drainage.nc' $dir'/input/drainage.nc'
    ncatted -O -h -a projection,lat,o,c,'EASE-Grid 2.0 North' $dir'/input/drainage.nc' $dir'/input/drainage.nc'
    ncatted -O -h -a epsg,lat,o,c,'6931' $dir'/input/drainage.nc' $dir'/input/drainage.nc'
    # Clean directory
#    rm $dir'/elevation.nc' $dir'/slope.nc' $dir'/aspect.nc' $dir'/tpi.nc'
  fi
done







########   PROCESSING   ########



### Create in and output directories for vegetation processing
if [ -d $vegindir ]; then
echo 'directory exists ...'
else
mkdir $vegindir
fi

if [ -d $vegoutdir ]; then
echo 'directory exists ...'
else
mkdir $vegoutdir
fi



### Compute the spatial information of the mask 

## Assess metadata of the mask raster
# Coordinates of the upper left corners
msk_all_o=($(gdalinfo  $mask |sed -n -e '/^Origin = /p' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?'))
# Size of the raster
msk_all_sz=($(gdalinfo  $mask |sed -n -e '/^Size is /p' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?'))
# Pixel resolution
msk_all_res=($(gdalinfo  $mask |sed -n -e '/^Pixel Size = /p' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?'))
# Computation of the extent of the raster
msk_all_left=$(echo ${msk_all_o[0]} | bc)
msk_all_bottom=$(echo ${msk_all_o[1]}+${msk_all_res[1]}*${msk_all_sz[1]} | bc)
msk_all_top=$(echo ${msk_all_o[1]} | bc)
msk_all_right=$(echo ${msk_all_o[0]}+${msk_all_res[0]}*${msk_all_sz[0]} | bc)
ext_all_6931=($msk_all_left $msk_all_bottom $msk_all_right $msk_all_top)
echo 'Extent of the Mask :' ${ext_all_6931[@]}




### Download and unzip necessary datasets
cd $vegindir
wget $urlworld
wget $urleco
unzip $vegindir'/'*'.zip' -d $vegindir'raw_data/globmap/'
unzip $maskdir'raw_data/globmap/'*'.zip' -d $maskdir'raw_data/globmap/'
for z in $vegindir'/'*'.zip'; do
  unzip $z -d $vegindir
done



### Fixing geometry and Cliping to north of 40o
ogr2ogr -clipsrc -180 40 180 90 $vegoutdir'/country.shp' $vegindir'/geoBoundariesCGAZ_ADM1.shp' 
## Fixing geometry in QGIS - the command comented below doesn't work.
## qgis_process run native:fixgeometries --distance_units=meters --area_units=m2 --ellipsoid=EPSG:7030 --INPUT=/Volumes/5TIV/DATA/VEGETATION/Ecoregions2017.shp --OUTPUT=/Volumes/5TIV/DATA/VEGETATION/Ecoregions2017_fix.shp
## ogr2ogr -f "ESRI Shapefile" -overwrite -skipfailures --config SHAPE_RESTORE_SHX YES $vegindir'/Ecoregions2017_fix2.shp'  $vegindir'/Ecoregions2017.shp' 
ogr2ogr -clipsrc -180 40 180 90 $vegoutdir'/ecoreg.shp' $vegindir'/Ecoregions2017_fix2.shp' 



### Reproject the two datasets
ogr2ogr -s_srs EPSG:4326 -t_srs EPSG:6931 $vegoutdir'/country_6931.shp' $vegoutdir'/country.shp'
ogr2ogr -s_srs EPSG:4326 -t_srs EPSG:6931 $vegoutdir'/ecoreg_6931.shp' $vegoutdir'/ecoreg.shp'



### Resample and align land cover
gdalwarp -overwrite -of GTiff -r mode -s_srs EPSG:6931 -t_srs EPSG:6931 -tr ${msk_all_res[0]} ${msk_all_res[1]} -te ${ext_all_6931[@]} $vegindir'/Jan2025_TEM_Landcover2/TEM_Landcover_V4.tif' $vegoutdir'/LC_4k.tif'


### Crosswalk the classification with the list of calibrations
export cntrypath=$(echo $vegoutdir'/country_6931.shp')
export cntryrst=$(echo $vegoutdir'/country_6931.tif')
export staterst=$(echo $vegoutdir'/state_6931.tif')
export ecoregpath=$(echo $vegoutdir'/ecoreg_6931.shp')
export ecorgrst=$(echo $vegoutdir'/ecoreg_6931.tif')
export biomerst=$(echo $vegoutdir'/biome_6931.tif')
export ecobiomerst=$(echo $vegoutdir'/ecobiome_6931.tif')
export realmrst=$(echo $vegoutdir'/realm_6931.tif')
export lcpath=$(echo $vegoutdir'/LC_4k.tif')
export classpath=$(echo $vegindir'/Jan2025_TEM_Landcover2/TEMLandcoverClassDictionary.csv')
export drainpth=$(echo $drain)
export mskpath=$(echo $mask)
export subregrst=$(echo $vegoutdir'/subreg_6931.tif')
export cmtrst=$(echo $vegoutdir'/cmt_6931.tif')
export missval=$(echo $missval)
export extent="${ext_all_6931[@]}"
export resolution="${msk_all_res[@]}"

python3 $scriptdir'/3_vegetation2_0.py'


### Tiling the topographic information and format the final input files

## The loop by pre-existing tiles (created in tilling.sh)
#dir='/Volumes/5TIV/PROCESSED/TILES/H01_V05'
for dir in $tiledir/* ; do
  if [ -d $dir ]; then
    echo $dir
    # Compute the extent of the original tile mask in 6931 EPSG
    msk_tile_6931_o=($(gdalinfo  $dir'/mask_6931.tiff' |sed -n -e '/^Origin = /p' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?'))
    msk_tile_6931_sz=($(gdalinfo  $dir'/mask_6931.tiff' |sed -n -e '/^Size is /p' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?'))
    msk_tile_6931_res=($(gdalinfo  $dir'/mask_6931.tiff' |sed -n -e '/^Pixel Size = /p' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?'))
    left=$(echo ${msk_tile_6931_o[0]} | bc)
    bottom=$(echo ${msk_tile_6931_o[1]}+${msk_tile_6931_res[1]}*${msk_tile_6931_sz[1]} | bc)
    top=$(echo ${msk_tile_6931_o[1]} | bc)
    right=$(echo ${msk_tile_6931_o[0]}+${msk_tile_6931_res[0]}*${msk_tile_6931_sz[0]} | bc)
    ext_tile_6931=($left $bottom $right $top)
    echo 'Sub-region extent in NSIDC EASE-Grid 2.0 North (EPSG 6931): ' ${ext_tile_6931[@]}
    # Crop the CMT number information
    gdalwarp -overwrite -of netCDF -r bilinear -s_srs EPSG:6931 -t_srs EPSG:6931 -tr ${msk_tile_6931_res[0]} ${msk_tile_6931_res[1]} -te ${ext_tile_6931[@]} $vegoutdir'/cmt_6931.tif' $dir'/input/vegetation.nc'
    # Merge and format the final netcdf vegetation.nc input file for each tile
    ncrename -O -h -v Band1,veg_class -d x,X -d y,Y -v y,Y -v x,X $dir'/input/vegetation.nc'
    # Fix missing and fill values from the attributes so they are the same across all variables
    ncatted -O -h -a eulaVlliF_,,d,c, $dir'/input/vegetation.nc' $dir'/input/vegetation.nc'
    ncatted -O -h -a _FillValue,,o,f,1.e+20 $dir'/input/vegetation.nc' $dir'/input/vegetation.nc'
    ncatted -O -h -a missing_value,,o,f,1.e+20 $dir'/input/vegetation.nc' $dir'/input/vegetation.nc'
    # Include lat and lon from run-mask.nc
#    ncks -O -h -v lat,lon $dir'/input/run-mask.nc' $dir'/latlon.nc'
    ncks -A -h $dir'/input/run-mask.nc' $dir'/input/vegetation.nc'
    ncks -O -h -x -v run $dir'/input/vegetation.nc' $dir'/input/vegetation.nc'
    # Fix attributes of the topo.nc file
    ncatted -O -h -a long_name,veg_class,o,c,'community number' $dir'/input/vegetation.nc' $dir'/input/vegetation.nc'
    ncatted -O -h -a units,veg_class,o,c,'' $dir'/input/vegetation.nc' $dir'/input/vegetation.nc'
    ncatted -O -h -a long_name,lon,o,c,'x coordinate of projection' $dir'/input/vegetation.nc' $dir'/input/vegetation.nc'
    ncatted -O -h -a units,lon,o,c,'m' $dir'/input/vegetation.nc' $dir'/input/vegetation.nc'
    ncatted -O -h -a projection,lat,o,c,'EASE-Grid 2.0 North' $dir'/input/vegetation.nc' $dir'/input/vegetation.nc'
    ncatted -O -h -a epsg,lat,o,c,'6931' $dir'/input/vegetation.nc' $dir'/input/vegetation.nc'
    ncatted -O -h -a long_name,lat,o,c,'y coordinate of projection' $dir'/input/vegetation.nc' $dir'/input/vegetation.nc'
    ncatted -O -h -a units,lat,o,c,'m' $dir'/input/vegetation.nc' $dir'/input/vegetation.nc'
    ncatted -O -h -a projection,lat,o,c,'EASE-Grid 2.0 North' $dir'/input/vegetation.nc' $dir'/input/vegetation.nc'
    ncatted -O -h -a epsg,lat,o,c,'6931' $dir'/input/vegetation.nc' $dir'/input/vegetation.nc'
    ncatted -O -h -a missing_value,lon,o,f,1.e+20 $dir'/input/vegetation.nc' $dir'/input/vegetation.nc'
    ncatted -O -h -a _FillValue,lon,o,f,1.e+20 $dir'/input/vegetation.nc' $dir'/input/vegetation.nc'
    ncatted -O -h -a missing_value,lat,o,f,1.e+20 $dir'/input/vegetation.nc' $dir'/input/vegetation.nc'
    ncatted -O -h -a _FillValue,lat,o,f,1.e+20 $dir'/input/vegetation.nc' $dir'/input/vegetation.nc'
    ncatted -O -h -a missing_value,veg_class,o,s,$missval $dir'/input/vegetation.nc' $dir'/input/vegetation.nc'
    ncatted -O -h -a _FillValue,veg_class,o,s,$missval $dir'/input/vegetation.nc' $dir'/input/vegetation.nc'
#    ncatted -O -h -a missing_value,lambert_azimuthal_equal_area,o,c,"missing" $dir'/input/vegetation.nc' $dir'/input/vegetation.nc'
#    ncatted -O -h -a _FillValue,lambert_azimuthal_equal_area,o,c,"missing" $dir'/input/vegetation.nc' $dir'/input/vegetation.nc'
    ncatted -O -h -a missing_value,lambert_azimuthal_equal_area,d,, $dir'/input/vegetation.nc' $dir'/input/vegetation.nc'
    ncatted -O -h -a _FillValue,lambert_azimuthal_equal_area,d,, $dir'/input/vegetation.nc' $dir'/input/vegetation.nc'
  fi
done












































