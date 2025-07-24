

########   USER SPECIFICATION   ########


### Script directory
scriptdir='/Users/helenegenet/Helene/TEM/INPUT/production/script'
### Path to the circumpolar mask 
mask='/Volumes/5TIV/PROCESSED/MASK/aoi_5k_buff_6931.tiff'
### Path to the land cover inputs and outputs
tilemapdir='/Volumes/5TIV/PROCESSED/TILEMAP'
tilemapdir='/Volumes/5TIV/PROCESSED/TILEMAP2_0'
### Path to the tiles
tilesdir='/Volumes/5TIV/PROCESSED/TILES2_0'




########   PROCESSING   ########


### Create in and output directories for vegetation processing
if [ -d $tilemapdir ]; then
echo 'directory exists ...'
else
mkdir $tilemapdir
fi



### Compute the spatial information of the mask 
mask_res=($(gdalinfo  $mask |sed -n -e '/^Pixel Size = /p' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?'))
mask_org=($(gdalinfo  $mask |sed -n -e '/^Origin = /p' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?'))
mask_siz=($(gdalinfo  $mask |sed -n -e '/^Size is /p' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?'))
echo $(gdalinfo  $mask |grep "PROJCRS")
mask_left=$(echo ${mask_org[0]} | bc)
mask_bottom=$(echo ${mask_org[1]}+${mask_res[1]}*${mask_siz[1]} | bc)
mask_top=$(echo ${mask_org[1]} | bc)
mask_right=$(echo ${mask_org[0]}+${mask_res[0]}*${mask_siz[0]} | bc)
mask_ext=($mask_left $mask_bottom $mask_right $mask_top)
echo 'Extent of the Mask :' ${mask_ext[@]}
echo 'Resolution of the Mask :' ${mask_res[@]}



### Tiling the topographic information and format the final input files

## The loop by pre-existing tiles (created in tilling.sh)
#dir='/Volumes/5TIV/PROCESSED/TILES/H01_V05'
for dir in $tilesdir/* ; do
  if [ -d $dir ]; then
    echo $dir
    tilename=$(basename $dir)
    gdal_polygonize.py $dir'/mask_6931.tiff' $tilemapdir'/'$tilename'.shp'
    ogrinfo $tilemapdir'/'$tilename'.shp' -sql "ALTER TABLE $tilename ADD COLUMN tile VARCHAR(50)" 
    ogrinfo $tilemapdir'/'$tilename'.shp' -dialect SQLite -sql "UPDATE $tilename set tile = '$tilename'"
    if [ -f $tilemapdir'/tilemap.shp' ]; then
      ogr2ogr -f 'ESRI Shapefile' -update -append $tilemapdir'/tilemap.shp' $tilemapdir'/'$tilename'.shp' 
    else
      ogr2ogr -f 'ESRI Shapefile' $tilemapdir'/tilemap.shp' $tilemapdir'/'$tilename'.shp'
    fi
    #rm $tilemapdir'/'$tilename*
  fi
done








