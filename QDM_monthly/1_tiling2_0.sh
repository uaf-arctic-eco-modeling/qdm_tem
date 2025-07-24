

########   USER SPECIFICATION   ########


### Script directory
scriptdir='/Users/helenegenet/Helene/TEM/INPUT/production/script_final'
### Output directory
outdir='/Volumes/5TIV/PROCESSED/TILES2_0'
if [ -d $outdir ]; then
  echo "Directory exists."
else
  mkdir -p $outdir
fi
### Target resolution in m
res=4000
### Path to the mask
mask='/Volumes/5TIV/PROCESSED/MASK/aoi_5k_buff_6931.tiff'
### Longitudinal and latitudinal sizes of the tiles in number of pixels, npx and npy respectively.
npx=100
npy=100






########   PROCESSING   ########



## Assess metadata of the mask raster
# Coordinates of the upper left corners
msk_all_o=($(gdalinfo  $mask |sed -n -e '/^Origin = /p' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?'))
echo ${msk_all_o[@]}
# Size of the raster
msk_all_sz=($(gdalinfo  $mask |sed -n -e '/^Size is /p' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?'))
echo ${msk_all_sz[@]}
# Pixel resolution
msk_all_res=($(gdalinfo  $mask |sed -n -e '/^Pixel Size = /p' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?'))
echo ${msk_all_res[@]}
# Computation of the extent of the raster
msk_all_left=$(echo ${msk_all_o[0]} | bc)
msk_all_bottom=$(echo ${msk_all_o[1]}+${msk_all_res[1]}*${msk_all_sz[1]} | bc)
msk_all_top=$(echo ${msk_all_o[1]} | bc)
msk_all_right=$(echo ${msk_all_o[0]}+${msk_all_res[0]}*${msk_all_sz[0]} | bc)
ext_all_6931=($msk_all_left $msk_all_bottom $msk_all_right $msk_all_top)
echo ${ext_all_6931[@]}


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

ntilesx=$((${ntilesx1#-}+${ntilesx2#-}))
ntilesy=$((${ntilesy1#-}+${ntilesy2#-}))
echo 'Total number of tiles - vertical:' $ntilesy ' horizontal:' $ntilesx

### Tiling
modx=$(echo $((${msk_all_sz[0]} % $npx)) | bc)
mody=$(echo $((${msk_all_sz[1]} % $npy)) | bc)

## Loop through tiles to select the ones that includes active cells and produce the mask for each of these tiles
for h in $(seq 1 $(printf '%.0f\n' ${ntilesx}));do
  for v in $(seq 1 $(printf '%.0f\n' ${ntilesy}));do
    echo "H: "$h" V: "$v 
    # 1- Compute the extent of the tile
    # Horizontal indices
    h0=$(($h-1))
    xmin=$(echo $left_new+$npx*$h0*${msk_all_res[0]} | bc)
    if [[ $h == $(printf '%.0f\n' ${ntilesx}) ]]; then
      xmax=$(echo $right_new | bc)
    else	
      xmax=$(echo $xmin+$npx*${msk_all_res[0]} | bc)
    fi
    # Vertical indices
    v0=$(($v-1))
    ymin=$(echo $bottom_new+$npy*$v0*${msk_all_res[0]} | bc)
    if [[ $v == $(printf '%.0f\n' ${ntilesy}) ]]; then
      ymax=$(echo $top_new | bc)
    else	
      ymax=$(echo $ymin+$npy*${msk_all_res[0]} | bc)
    fi
    # Tile extent
    ext_tile_6931=($xmin $ymin $xmax $ymax)
    echo ${ext_tile_6931[@]}
    # 2- check that the mask has active pixels in the tile
    # Crop the subregion from the mask raster
    gdalwarp -overwrite -of netCDF -r bilinear -s_srs EPSG:6931 -t_srs EPSG:6931 -tr ${msk_all_res[0]} ${msk_all_res[1]} -te ${ext_tile_6931[@]} $mask $outdir'/tmp.nc'
    ncrename -O -h -v Band1,active $outdir'/tmp.nc'
    ncwa -O -h -v active -a x,y -y total $outdir'/tmp.nc' $outdir'/tmp2.nc'
    check=$(ncdump $outdir'/tmp2.nc' | sed -n -e '/^ active = /p' | grep -Eo '[+-]?[0-9]+([.][0-9]+[ee][+-][0-9]+)?')
    if [ "${check%.*}" -ge "1" ]; then
      # Create a tile directory
      dirname='H'$(printf "%0"$(echo "${#ntilex}")"d" $h)'_V'$(printf "%0"$(echo "${#ntiley}")"d" $v)
      mkdir $outdir'/'$dirname
      # Crop the mask to entire rows or columns of NAs from the mask
      ext_tile_6931=($(python3 $scriptdir'/1_tiling2_0_croping.py' $outdir'/tmp.nc' ${msk_all_res[0]} | tr -d '[],'))
      echo ${ext_tile_6931[@]}
      gdalwarp -overwrite -of GTiff -r bilinear -s_srs EPSG:6931 -t_srs EPSG:6931 -tr ${msk_all_res[0]} ${msk_all_res[1]} -te ${ext_tile_6931[@]} $mask $outdir'/'$dirname'/mask_6931.tiff'
      # Create the runmask
      if [ -d $outdir'/'$dirname'/input' ]; then
        echo "Directory exists."
      else
        mkdir -p $outdir'/'$dirname'/input'
      fi
      gdalwarp -overwrite -of netCDF -r bilinear -s_srs EPSG:6931 -t_srs EPSG:6931 -tr ${msk_all_res[0]} ${msk_all_res[1]} -te ${ext_tile_6931[@]} $mask $outdir'/'$dirname'/input/run-mask.nc'
      ncrename -O -h -v Band1,run -d x,X -d y,Y -v y,Y -v x,X $outdir'/'$dirname'/input/run-mask.nc'
      python3 $scriptdir'/1_tiling2_0_runmask_formating.py' $outdir'/'$dirname'/input/run-mask.nc'
      # Convert the projection of the mask to the projection of the one for CRU-JRA
      gdalwarp -overwrite -of GTiff -r bilinear -s_srs EPSG:6931 -t_srs EPSG:4326 $outdir'/'$dirname'/mask_6931.tiff' $outdir'/'$dirname'/mask_4326.tiff'
    fi
    rm $outdir'/tmp.nc' $outdir'/tmp2.nc'
  done
done








