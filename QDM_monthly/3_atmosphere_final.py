import requests
import os
import zipfile
import pandas as pd
import xarray as xr
import numpy as np

indir='/Volumes/5TIII/TEST_INPUT_SET/data'
outdir='/Volumes/5TIII/TEST_INPUT_SET/atmosphere'

indir = os.getenv('indir')
outdir = os.getenv('outdir')


#### ATMOSPHERIC CO2 AND CH4 TIME SERIES

### HISTORICAL

## PREINDUSTRIAL
# Data Source: https://agage.mit.edu/data/agage-data for CH4 concentrations and https://www.esrl.noaa.gov/gmd/dv/data/?category=Greenhouse%2BGases for atmospheric CO2
#url = 'https://www.eea.europa.eu/en/analysis/maps-and-charts/atmospheric-concentration-of-carbon-dioxide-5/@@download/file'


## CONTEMPORARY - UTQIAGVIK
# Data Source: NOAA Global Monitoring Lab Monthly In Situ averages at Barrow Atmospheric Baseline Observatory, United States
# contemporary carbon dioxide concentration
url = 'https://gml.noaa.gov/aftp/data/trace_gases/co2/in-situ/surface/nc/co2_brw_surface-insitu_1_ccgg_MonthlyData.nc'
response = requests.get(url)
with open(os.path.join(indir,'contemporary_co2.nc'), mode='wb') as file:
    file.write(response.content)

ds = xr.open_dataset(os.path.join(indir,'contemporary_co2.nc'))
cont_co2 = ds.to_dataframe()
cont_co2.reset_index(inplace=True)
cont_co2.columns
cont_co2 = cont_co2[['time','value']]
cont_co2 = cont_co2.rename(columns={'value': 'co2_ppm_utq'})

# contemporary methane concentration
url = 'https://gml.noaa.gov/aftp/data/trace_gases/ch4/in-situ/surface/nc/ch4_brw_surface-insitu_1_ccgg_MonthlyData.nc'
response = requests.get(url)
with open(os.path.join(indir,'contemporary_ch4.nc'), mode='wb') as file:
    file.write(response.content)

ds = xr.open_dataset(os.path.join(indir,'contemporary_ch4.nc'))
cont_ch4 = ds.to_dataframe()
cont_ch4.reset_index(inplace=True)
cont_ch4.columns
cont_ch4 = cont_ch4[['time','value']]
cont_ch4 = cont_ch4.rename(columns={'value': 'ch4_ppb_utq'})

#merge datasets & annual average
utq = pd.merge(cont_co2.drop_duplicates(), cont_ch4.drop_duplicates(), how = 'outer', on = ['time'])
utq['year'] = utq['time'].dt.year
utq_avg = utq.groupby(['year'])[['co2_ppm_utq','ch4_ppb_utq']].mean()
utq_avg.reset_index(inplace=True)




## CONTEMPORARY - MAUNA LOA
# Data Source: NOAA Global Monitoring Lab Monthly In Situ averages at Mauna Loa Atmospheric Baseline Observatory, United States
# contemporary carbon dioxide concentration
url = 'https://gml.noaa.gov/aftp/data/trace_gases/co2/in-situ/surface/nc/co2_mlo_surface-insitu_1_ccgg_MonthlyData.nc'
response = requests.get(url)
with open(os.path.join(indir,'contemporary_co2.nc'), mode='wb') as file:
    file.write(response.content)

ds = xr.open_dataset(os.path.join(indir,'contemporary_co2.nc'))
cont_co2 = ds.to_dataframe()
cont_co2.reset_index(inplace=True)
cont_co2.columns
cont_co2 = cont_co2[['time','value']]
cont_co2 = cont_co2.rename(columns={'value': 'co2_ppm_mlo'})

# contemporary methane concentration
url = 'https://gml.noaa.gov/aftp/data/trace_gases/ch4/in-situ/surface/nc/ch4_mlo_surface-insitu_1_ccgg_MonthlyData.nc'
response = requests.get(url)
with open(os.path.join(indir,'contemporary_ch4.nc'), mode='wb') as file:
    file.write(response.content)

ds = xr.open_dataset(os.path.join(indir,'contemporary_ch4.nc'))
cont_ch4 = ds.to_dataframe()
cont_ch4.reset_index(inplace=True)
cont_ch4.columns
cont_ch4 = cont_ch4[['time','value']]
cont_ch4 = cont_ch4.rename(columns={'value': 'ch4_ppb_mlo'})

#merge datasets & annual average
mlo = pd.merge(cont_co2.drop_duplicates(), cont_ch4.drop_duplicates(), how = 'outer', on = ['time'])
mlo['year'] = mlo['time'].dt.year
mlo_avg = mlo.groupby(['year'])[['co2_ppm_mlo','ch4_ppb_mlo']].mean()
mlo_avg.reset_index(inplace=True)





## FUTURE: https://doi.org/10.5194/gmd-13-3571-2020
url = 'https://doi.org/10.5194/gmd-13-3571-2020-supplement'
response = requests.get(url)
with open(os.path.join(indir,'Meinshausen_2020_GMD.zip'), mode='wb') as file:
    file.write(response.content)

with zipfile.ZipFile(os.path.join(indir,'Meinshausen_2020_GMD.zip'), 'r') as zip_ref:
    zip_ref.extractall(os.path.join(indir,'Meinshausen_2020_GMD'))


#Reading the historical and scenario annual averages
df = pd.ExcelFile(os.path.join(indir,'Meinshausen_2020_GMD','SUPPLEMENT_DataTables_Meinshausen_6May2020.xlsx'))
df.sheet_names
df.sheet_names[1]
hist = pd.read_excel(df, sheet_name=df.sheet_names[1], skiprows=11)
hist = hist.rename(columns={'Unnamed: 2': 'co2_ppm_north', 'Unnamed: 5': 'ch4_ppb_north','Year': 'year'})
hist = hist[['year','co2_ppm_north','ch4_ppb_north']]
df.sheet_names[4]
ssp1 = pd.read_excel(df, sheet_name=df.sheet_names[4], skiprows=11)
ssp1 = ssp1.rename(columns={'Unnamed: 2': 'co2_ppm_north', 'Unnamed: 5': 'ch4_ppb_north','Year': 'year'})
ssp1 = ssp1[['year','co2_ppm_north','ch4_ppb_north']]
df.sheet_names[5]
ssp2 = pd.read_excel(df, sheet_name=df.sheet_names[5], skiprows=11)
ssp2 = ssp2.rename(columns={'Unnamed: 2': 'co2_ppm_north', 'Unnamed: 5': 'ch4_ppb_north','Year': 'year'})
ssp2 = ssp2[['year','co2_ppm_north','ch4_ppb_north']]
df.sheet_names[6]
ssp3 = pd.read_excel(df, sheet_name=df.sheet_names[6], skiprows=11)
ssp3 = ssp3.rename(columns={'Unnamed: 2': 'co2_ppm_north', 'Unnamed: 5': 'ch4_ppb_north','Year': 'year'})
ssp3 = ssp3[['year','co2_ppm_north','ch4_ppb_north']]
df.sheet_names[11]
ssp5 = pd.read_excel(df, sheet_name=df.sheet_names[11], skiprows=11)
ssp5 = ssp5.rename(columns={'Unnamed: 2': 'co2_ppm_north', 'Unnamed: 5': 'ch4_ppb_north','Year': 'year'})
ssp5 = ssp5[['year','co2_ppm_north','ch4_ppb_north']]



## BIAS CORRECTION

# Atmospheric CO2
utq_avg[(utq_avg['year']>1973) & (utq_avg['year']<2015) & (utq_avg['co2_ppm_utq']>300)]['co2_ppm_utq'].mean()
mlo_avg[(mlo_avg['year']>1973) & (mlo_avg['year']<2015) & (mlo_avg['co2_ppm_mlo']>300)]['co2_ppm_mlo'].mean()
hist[(hist['year']>1973) & (hist['year']<2015)]['co2_ppm_north'].mean()

utq_avg[(utq_avg['year']>2014) & (utq_avg['year']<2024)& (utq_avg['co2_ppm_utq']>300)]['co2_ppm_utq'].mean()
mlo_avg[(mlo_avg['year']>2014) & (mlo_avg['year']<2024)& (mlo_avg['co2_ppm_mlo']>300)]['co2_ppm_mlo'].mean()
ssp1[(ssp1['year']>2014) & (ssp1['year']<2024)]['co2_ppm_north'].mean()
ssp2[(ssp2['year']>2014) & (ssp2['year']<2024)]['co2_ppm_north'].mean()
ssp3[(ssp3['year']>2014) & (ssp3['year']<2024)]['co2_ppm_north'].mean()
ssp5[(ssp5['year']>2014) & (ssp5['year']<2024)]['co2_ppm_north'].mean()

hist['co2_ppm_north_corr'] = hist['co2_ppm_north'] + (utq_avg[(utq_avg['year']>1973) & (utq_avg['year']<2015) & (utq_avg['co2_ppm_utq']>300)]['co2_ppm_utq'].mean() - hist[(hist['year']>1973) & (hist['year']<2015)]['co2_ppm_north'].mean())
ssp1['co2_ppm_north_corr'] = ssp1['co2_ppm_north'] + (utq_avg[(utq_avg['year']==2024) & (utq_avg['co2_ppm_utq']>300)]['co2_ppm_utq'].mean() - ssp1[(ssp1['year']==2024)]['co2_ppm_north'].mean())
ssp2['co2_ppm_north_corr'] = ssp2['co2_ppm_north'] + (utq_avg[(utq_avg['year']==2024) & (utq_avg['co2_ppm_utq']>300)]['co2_ppm_utq'].mean() - ssp2[(ssp2['year']==2024)]['co2_ppm_north'].mean())
ssp3['co2_ppm_north_corr'] = ssp3['co2_ppm_north'] + (utq_avg[(utq_avg['year']==2024) & (utq_avg['co2_ppm_utq']>300)]['co2_ppm_utq'].mean() - ssp3[(ssp3['year']==2024)]['co2_ppm_north'].mean())
ssp5['co2_ppm_north_corr'] = ssp5['co2_ppm_north'] + (utq_avg[(utq_avg['year']==2024) & (utq_avg['co2_ppm_utq']>300)]['co2_ppm_utq'].mean() - ssp5[(ssp5['year']==2024)]['co2_ppm_north'].mean())


# Atmospheric CH4
utq_avg[(utq_avg['year']>1986) & (utq_avg['year']<2015) & (utq_avg['ch4_ppb_utq']>1600)]['ch4_ppb_utq'].mean()
mlo_avg[(mlo_avg['year']>1986) & (mlo_avg['year']<2015) & (mlo_avg['ch4_ppb_mlo']>1600)]['ch4_ppb_mlo'].mean()
hist[(hist['year']>1986) & (hist['year']<2015)]['ch4_ppb_north'].mean()

utq_avg[(utq_avg['year']>2014) & (utq_avg['year']<2024)& (utq_avg['ch4_ppb_utq']>1600)]['ch4_ppb_utq'].mean()
mlo_avg[(mlo_avg['year']>2014) & (mlo_avg['year']<2024)& (mlo_avg['ch4_ppb_mlo']>1600)]['ch4_ppb_mlo'].mean()
ssp1[(ssp1['year']>2014) & (ssp1['year']<2024)]['ch4_ppb_north'].mean()
ssp2[(ssp2['year']>2014) & (ssp2['year']<2024)]['ch4_ppb_north'].mean()
ssp3[(ssp3['year']>2014) & (ssp3['year']<2024)]['ch4_ppb_north'].mean()
ssp5[(ssp5['year']>2014) & (ssp5['year']<2024)]['ch4_ppb_north'].mean()

hist['ch4_ppb_north_corr'] = hist['ch4_ppb_north'] + (utq_avg[(utq_avg['year']>1986) & (utq_avg['year']<2015) & (utq_avg['ch4_ppb_utq']>1600)]['ch4_ppb_utq'].mean() - hist[(hist['year']>1986) & (hist['year']<2015)]['ch4_ppb_north'].mean())
ssp1['ch4_ppb_north_corr'] = ssp1['ch4_ppb_north'] + (utq_avg[(utq_avg['year']==2024) & (utq_avg['ch4_ppb_utq']>1600)]['ch4_ppb_utq'].mean() - ssp1[ssp1['year']==2024]['ch4_ppb_north'].mean())
ssp2['ch4_ppb_north_corr'] = ssp2['ch4_ppb_north'] + (utq_avg[(utq_avg['year']==2024) & (utq_avg['ch4_ppb_utq']>1600)]['ch4_ppb_utq'].mean() - ssp2[ssp2['year']==2024]['ch4_ppb_north'].mean())
ssp3['ch4_ppb_north_corr'] = ssp3['ch4_ppb_north'] + (utq_avg[(utq_avg['year']==2024) & (utq_avg['ch4_ppb_utq']>1600)]['ch4_ppb_utq'].mean() - ssp3[ssp3['year']==2024]['ch4_ppb_north'].mean())
ssp5['ch4_ppb_north_corr'] = ssp5['ch4_ppb_north'] + (utq_avg[(utq_avg['year']==2024) & (utq_avg['ch4_ppb_utq']>1600)]['ch4_ppb_utq'].mean() - ssp5[ssp5['year']==2024]['ch4_ppb_north'].mean())


### MISSING VALUES OR OUTLIER OBSERVATIONS

obs = pd.merge(utq_avg, mlo_avg, how = 'outer', on = ['year'])

corr_co2 = obs[(obs['year'] > 1975) & (obs['co2_ppm_mlo']>300)]['co2_ppm_mlo'].mean() - obs[(obs['year'] > 1975) & (obs['co2_ppm_utq']>300)]['co2_ppm_utq'].mean()
corr_ch4 = obs[(obs['year'] > 1987) & (obs['ch4_ppb_mlo']>1600)]['ch4_ppb_mlo'].mean() - obs[(obs['year'] > 1987) & (obs['ch4_ppb_utq']>1600)]['ch4_ppb_utq'].mean()
obs['co2_ppm_mlo_corr'] = obs['co2_ppm_mlo'] - corr_co2
obs['ch4_ppb_mlo_corr'] = obs['ch4_ppb_mlo'] - corr_ch4

obs['co2_ppm_utq_corr'] = obs['co2_ppm_utq']
obs.loc[obs.co2_ppm_utq < 300, 'co2_ppm_utq_corr'] = obs['co2_ppm_mlo'] - corr_co2
obs['ch4_ppb_utq_corr'] = obs['ch4_ppb_utq']
obs.loc[obs.ch4_ppb_utq < 1600, 'ch4_ppb_utq_corr'] = obs['ch4_ppb_utq'] - corr_ch4



### Building time series and netcdf inputs

## Historical time series

hist1 = hist[(hist['year'] > 1900) & (hist['year'] < 1974)]
hist1 = hist1[['year','co2_ppm_north_corr']]
hist1 = hist1.rename(columns={'co2_ppm_north_corr': 'co2'})
hist2 = obs[(obs['year'] > 1973) & (obs['year'] < 2024)]
hist2 = hist2[['year','co2_ppm_utq_corr']]
hist2 = hist2.rename(columns={'co2_ppm_utq_corr': 'co2'})
historical = pd.concat([hist1,hist2], axis=0)
co2nc = historical.set_index(['year']).to_xarray()
co2nc['co2'].attrs={'standard_name':'atmospheric CO2 concentration','units':'ppm'}
co2nc['year'] = co2nc['year'].astype(np.int_)
co2nc['co2'] = co2nc['co2'].astype(np.single)
co2nc.to_netcdf(os.path.join(outdir,'co2.nc'),unlimited_dims='year')

hist1 = hist[(hist['year'] > 1900) & (hist['year'] < 1986)]
hist1 = hist1[['year','ch4_ppb_north_corr']]
hist1 = hist1.rename(columns={'ch4_ppb_north_corr': 'ch4'})
hist2 = obs[(obs['year'] > 1985) & (obs['year'] < 2024)]
hist2 = hist2[['year','ch4_ppb_utq_corr']]
hist2 = hist2.rename(columns={'ch4_ppb_utq_corr': 'ch4'})
historical = pd.concat([hist1,hist2], axis=0)
ch4nc = historical.set_index(['year']).to_xarray()
ch4nc['ch4'].attrs={'standard_name':'atmospheric CH4 concentration','units':'ppb'}
ch4nc['year'] = ch4nc['year'].astype(np.int_)
ch4nc['ch4'] = ch4nc['ch4'].astype(np.single)
ch4nc.to_netcdf(os.path.join(outdir,'ch4.nc'),unlimited_dims='year')




## Scenario time series

ssp1 = ssp1[(ssp1['year'] > 2023) & (ssp1['year'] < 2101)]
ssp1 = ssp1.rename(columns={'co2_ppm_north_corr': 'co2'})
ssp1 = ssp1.rename(columns={'ch4_ppb_north_corr': 'ch4'})
co2nc = ssp1[['year','co2']].set_index(['year']).to_xarray()
co2nc['co2'].attrs={'standard_name':'atmospheric CO2 concentration','units':'ppm'}
co2nc['year'] = co2nc['year'].astype(np.int_)
co2nc['co2'] = co2nc['co2'].astype(np.single)
co2nc.to_netcdf(os.path.join(outdir,'projected-co2_ssp1.nc'),unlimited_dims='year')
ch4nc = ssp1[['year','ch4']].set_index(['year']).to_xarray()
ch4nc['ch4'].attrs={'standard_name':'atmospheric CH4 concentration','units':'ppb'}
ch4nc['year'] = ch4nc['year'].astype(np.int_)
ch4nc['ch4'] = ch4nc['ch4'].astype(np.single)
ch4nc.to_netcdf(os.path.join(outdir,'projected-ch4_ssp1.nc'),unlimited_dims='year')


ssp2 = ssp2[(ssp2['year'] > 2023) & (ssp2['year'] < 2101)]
ssp2 = ssp2.rename(columns={'co2_ppm_north_corr': 'co2'})
ssp2 = ssp2.rename(columns={'ch4_ppb_north_corr': 'ch4'})
co2nc = ssp2[['year','co2']].set_index(['year']).to_xarray()
co2nc['co2'].attrs={'standard_name':'atmospheric CO2 concentration','units':'ppm'}
co2nc['year'] = co2nc['year'].astype(np.int_)
co2nc['co2'] = co2nc['co2'].astype(np.single)
co2nc.to_netcdf(os.path.join(outdir,'projected-co2_ssp2.nc'),unlimited_dims='year')
ch4nc = ssp2[['year','ch4']].set_index(['year']).to_xarray()
ch4nc['ch4'].attrs={'standard_name':'atmospheric CH4 concentration','units':'ppb'}
ch4nc['year'] = ch4nc['year'].astype(np.int_)
ch4nc['ch4'] = ch4nc['ch4'].astype(np.single)
ch4nc.to_netcdf(os.path.join(outdir,'projected-ch4_ssp2.nc'),unlimited_dims='year')


ssp3 = ssp3[(ssp3['year'] > 2023) & (ssp3['year'] < 2101)]
ssp3 = ssp3.rename(columns={'co2_ppm_north_corr': 'co2'})
ssp3 = ssp3.rename(columns={'ch4_ppb_north_corr': 'ch4'})
co2nc = ssp3[['year','co2']].set_index(['year']).to_xarray()
co2nc['co2'].attrs={'standard_name':'atmospheric CO2 concentration','units':'ppm'}
co2nc['year'] = co2nc['year'].astype(np.int_)
co2nc['co2'] = co2nc['co2'].astype(np.single)
co2nc.to_netcdf(os.path.join(outdir,'projected-co2_ssp3.nc'),unlimited_dims='year')
ch4nc = ssp3[['year','ch4']].set_index(['year']).to_xarray()
ch4nc['ch4'].attrs={'standard_name':'atmospheric CH4 concentration','units':'ppb'}
ch4nc['year'] = ch4nc['year'].astype(np.int_)
ch4nc['ch4'] = ch4nc['ch4'].astype(np.single)
ch4nc.to_netcdf(os.path.join(outdir,'projected-ch4_ssp3.nc'),unlimited_dims='year')


ssp5 = ssp5[(ssp5['year'] > 2023) & (ssp5['year'] < 2101)]
ssp5 = ssp5.rename(columns={'co2_ppm_north_corr': 'co2'})
ssp5 = ssp5.rename(columns={'ch4_ppb_north_corr': 'ch4'})
co2nc = ssp5[['year','co2']].set_index(['year']).to_xarray()
co2nc['co2'].attrs={'standard_name':'atmospheric CO2 concentration','units':'ppm'}
co2nc['year'] = co2nc['year'].astype(np.int_)
co2nc['co2'] = co2nc['co2'].astype(np.single)
co2nc.to_netcdf(os.path.join(outdir,'projected-co2_ssp5.nc'),unlimited_dims='year')
ch4nc = ssp5[['year','ch4']].set_index(['year']).to_xarray()
ch4nc['ch4'].attrs={'standard_name':'atmospheric CH4 concentration','units':'ppb'}
ch4nc['year'] = ch4nc['year'].astype(np.int_)
ch4nc['ch4'] = ch4nc['ch4'].astype(np.single)
ch4nc.to_netcdf(os.path.join(outdir,'projected-ch4_ssp5.nc'),unlimited_dims='year')


