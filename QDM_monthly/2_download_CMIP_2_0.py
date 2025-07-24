### Author: Hélène Genet, hgenet@alaska.edu 
### Institution: Arctic Eco Modeling
### Team, Institute of Arctic Biology, University of Alaska Fairbanks 
### Date: September 23 2024 
### Description: 
### Command: $ 


import cdsapi
import requests
import os



### storage directory
cmipdir = '/Volumes/5TIV/DATA/CLIMATE/CMIP_hist'
### CMIP version
cmipversion = '6'
### List of models
gcmlist = ['access_cm2','mri_esm2_0']
### List of historical scenario
schist = ['historical']
### List of variables
varlisthistorical=('near_surface_air_temperature','near_surface_specific_humidity','near_surface_wind_speed','precipitation','sea_level_pressure','surface_downwelling_shortwave_radiation')


cmipdir = os.getenv('cmipdir')
### CMIP version
cmipversion = os.getenv('cmipversion')
### List of models
gcmlist = os.getenv('gcm_list').split(',')
### List of scenarios
sclist = os.getenv('sc_list').split(',')
### List of historical scenario
schist = os.getenv('sc_hist').split(',')
### List of variables
varlistdaily = os.getenv('var_list_daily').split(',')
varlistmonthly = os.getenv('var_list_monthly').split(',')
varlisthistorical = os.getenv('var_list_hist').split(',')



### This suite of download is part of the model comparison with historical climate product to document model selection. 

c = cdsapi.Client()

for sc in sclist:
    print(sc)
    for gcm in gcmlist:
        print(gcm)
        for var in varlistdaily:
            print(var)
            c.retrieve(
                str('projections-cmip' + cmipversion),
                {
                    'format': 'zip',
                    'temporal_resolution': 'daily',
                    'experiment': sc,
                    'variable': var,
                    'year': ['2015', '2016', '2017',
                        '2018', '2019', '2020',
                        '2021', '2022', '2023',
                        '2024', '2025', '2026',
                        '2027', '2028', '2029',
                        '2030', '2031', '2032',
                        '2033', '2034', '2035',
                        '2036', '2037', '2038',
                        '2039', '2040', '2041',
                        '2042', '2043', '2044',
                        '2045', '2046', '2047',
                        '2048', '2049', '2050',
                        '2051', '2052', '2053',
                        '2054', '2055', '2056',
                        '2057', '2058', '2059',
                        '2060', '2061', '2062',
                        '2063', '2064', '2065',
                        '2066', '2067', '2068',
                        '2069', '2070', '2071',
                        '2072', '2073', '2074',
                        '2075', '2076', '2077',
                        '2078', '2079', '2080',
                        '2081', '2082', '2083',
                        '2084', '2085', '2086',
                        '2087', '2088', '2089',
                        '2090', '2091', '2092',
                        '2093', '2094', '2095',
                        '2096', '2097', '2098',
                        '2099', '2100'],
                    'month': ['01', '02', '03',
                        '04', '05', '06',
                        '07', '08', '09',
                        '10', '11', '12'],
                    'day': ['01', '02', '03',
                        '04', '05', '06',
                        '07', '08', '09',
                        '10', '11', '12',
                        '13', '14', '15',
                        '16', '17', '18',
                        '19', '20', '21',
                        '22', '23', '24',
                        '25', '26', '27',
                        '28', '29', '30',
                        '31'],
                    'area': [90, -180, 30,180],
                    'model': gcm,
                },
                os.path.join(cmipdir,'CMIP' + cmipversion + '_' + sc + '_' + gcm + '_' + var + '.zip'))



import cdsapi

for sc in schist:
    print(sc)
    for gcm in gcmlist:
        print(gcm)
        for var in varlisthistorical:
            print(var)
            dataset = str('projections-cmip' + cmipversion)
            request = {
                "temporal_resolution": "monthly",
                "experiment": sc,
                "variable": var,
                "model": gcm,
                "month": [
                    "01", "02", "03",
                    "04", "05", "06",
                    "07", "08", "09",
                    "10", "11", "12"
                ],
                "year": ['1970', '1971', '1972',
                    '1973', '1974', '1975',
                    '1976', '1977', '1978',
                    '1979', '1980', '1981',
                    '1982', '1983', '1984',
                    '1985', '1986', '1987',
                    '1988', '1989', '1990',
                    '1991', '1992', '1993',
                    '1994', '1995', '1996',
                    '1997', '1998', '1999',
                    '2000', '2001', '2002', 
                    '2003', '2004', '2005', 
                    '2006', '2007', '2008', 
                    '2009', '2010', '2011', 
                    '2012', '2013', '2014'],
                "area": [90, -180, 30, 180]
            }
            client = cdsapi.Client()
            client.retrieve(dataset, request, os.path.join(cmipdir,'CMIP' + cmipversion + '_' + sc + '_' + gcm + '_' + var + '.zip'))

