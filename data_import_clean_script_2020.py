import pandas as pd
from pandas_datareader import wb
import os
os.chdir('D:\Project Dash\medtrade')

wb_countries = wb.get_countries()
country_list = wb_countries[wb_countries['region']!='Aggregates']['name'].reset_index(drop=True)


# indicator_ids = ['EN.POP.DNST', 'SP.POP.TOTL', 'SM.POP.NETM']

# migration = wb.WorldBankReader(symbols=['SM.POP.NETM'], start=1950, end=2018, countries='all').read()
# pop_density = wb.WorldBankReader(symbols=['EN.POP.DNST'], start=1950, end=2018, countries='all').read()
# population = wb.WorldBankReader(symbols=['SP.POP.TOTL'], start=1950, end=2018, countries='all').read()

# pop_density_countries = pop_density.reset_index()#.query('country in @country_list').reset_index(drop=True)
# population_countries = population.reset_index()#.query('country in @country_list').reset_index(drop=True)
# migration_countries = migration.reset_index()#.query('country in @country_list').reset_index(drop=True)

# pop_density_merged = pd.merge(population_countries, pop_density_countries, on=['country', 'year'], how='outer')
# migration_final = (pd.merge(pop_density_merged, migration_countries, on=['country', 'year'], how='outer')
#                    .rename(columns={'SP.POP.TOTL': 'population',
#                                     'EN.POP.DNST': 'pop_density',
#                                     'SM.POP.NETM': 'net_migration'})
#                    .assign(migration_perc=lambda df: df['net_migration'].div(df['population'])))

# migration_final = pd.merge(migration_final, wb_countries, how='left', left_on='country', right_on='name')
# migration_final.drop('name', axis=1).to_csv('migration_population.csv', index=False)


#%%% 

countryname = pd.read_excel('data/CountryCodesNamesEN.xlsx')
countryname_eu = pd.read_excel('data/CountryCodesNamesEN-EU.xlsx')

imports = pd.read_excel('data/data-trade.xlsx', sheet_name='Imports').assign(year=2019).assign(type='import')
exports = pd.read_excel('data/data-trade.xlsx', sheet_name='Exports').assign(year=2019).assign(type='export')

tariff_applied = pd.read_excel('data/data-applied.xlsx',sheet_name='tariff').assign(year=2019).assign(type='tariff_applied')
tariff_rta = pd.read_excel('data/data-rta.xlsx',sheet_name='RTA').assign(year=2019).assign(type='tariff_rta')
# xxx = pd.merge(tariff_rta, countryname[['Name','ISO-3A']],  left_on='country', right_on='Name',how='left')



tariff_bound = pd.read_excel('data/data-bound.xlsx',sheet_name='bound',dtype={'Reporter':str}).assign(year=2019).assign(type='tariff_bound')
tariff_bound = pd.merge(tariff_bound,countryname[['Code','Name']],left_on='Reporter',right_on='Code' )
tariff_bound = tariff_bound.rename(columns={'Name':'country'})

tariff_bcoverage = pd.read_excel('data/data-bound.xlsx',sheet_name='bindingcoverage',dtype={'Reporter':str}).assign(year=2019).assign(type='tariff_bcoverage')
tariff_bcoverage = pd.merge(tariff_bcoverage,countryname[['Code','Name']],left_on='Reporter',right_on='Code' )
tariff_bcoverage = tariff_bcoverage.rename(columns={'Name':'country'})

eu_applied = countryname_eu[['Name']].copy().rename(columns={'Name':'country'})
eu_applied = eu_applied.assign(
                         all = 1.5,
                         medicines = 0, 
                         supplies = 3.2, 
                         equipment = 0.2, 
                         protective = 3.9,
                         year = 2019,
                         type = 'tariff_applied'
                         )
eu_bound = countryname_eu[['Name']].copy().rename(columns={'Name':'country'})
eu_bound = eu_bound.assign(
                         all = 1.9,
                         medicines = 0, 
                         supplies = 3.1, 
                         equipment = 0.9, 
                         protective = 3.7,
                         year = 2019,
                         type = 'tariff_bound'
                         )
eu_bcoverage = countryname_eu[['Name']].copy().rename(columns={'Name':'country'})
eu_bcoverage = eu_bcoverage.assign(
                         all = 100,
                         medicines = 100, 
                         supplies = 100, 
                         equipment = 100, 
                         protective = 100,
                         year = 2019,
                         type = 'tariff_bcoverage'
                         )



med_trade = tariff_applied.append(imports, sort=False)
med_trade = med_trade.append(tariff_rta, sort=False)
med_trade = med_trade.append(exports, sort=False)
med_trade = med_trade.append(tariff_bound, sort=False)
med_trade = med_trade.append(tariff_bcoverage, sort=False)
med_trade = med_trade.append(eu_applied, sort=False)
med_trade = med_trade.append(eu_bound, sort=False)
med_trade = med_trade.append(eu_bcoverage, sort=False)



country_list_wto = countryname[~countryname['ISO-3A'].isnull()]['Name'].unique().tolist()
country_list_med = med_trade['country'].unique().tolist()
country_blank = set(country_list_wto) - set(country_list_med)

# from itertools import product
# list(product(country_blank,['export','import','tariff_applied','tariff_bcoverage','tariff_bound']))
# missing = pd.DataFrame(list(product(country_blank,['export','import','tariff_applied','tariff_bcoverage','tariff_bound'])), columns=['country','type'])

# import numpy
# missing = missing.assign(
#                          all = -100,
#                          medicines = -100, 
#                          supplies = -100, 
#                          equipment = -100, 
#                          protective = -100,
#                          year = 2019
#                          )

# missing = missing.assign(
#                          all = pd.NA,
#                          medicines = pd.NA, 
#                          supplies = pd.NA, 
#                          equipment = pd.NA, 
#                          protective = pd.NA,
#                          year = 2019
#                          )


# med_trade = med_trade.append(missing, sort=False)


med_trade['country'] = med_trade['country'].str.strip()
med_trade = pd.merge(med_trade, countryname[['Name','ISO-3A']],  left_on='country', right_on='Name')



# print(eu['country'].tolist())



# med_trade.groupby('type').size()
# check_country = med_trade.groupby('country').size().index.to_list()
# wto_countryname = countryname['Name'].tolist()

# set(check_country) - set(country_list)
# set(check_country) - set(wto_countryname)

x = med_trade[med_trade['type'].str.startswith('tariff')]



med_trade = pd.merge(med_trade, wb_countries, how='left', left_on='ISO-3A', right_on='iso3c')
# migration_final1 = migration_final1.rename(columns={'name':'country',
#                                                     'All products': 'all', 
#                                                     'Medicines': 'medicines', 
#                                                     'Medical Supplies': 'supplies',
#                                                     'Medical equipment': 'equipment', 
#                                                     'Personal protective products': 'protective',
#                                                     })
# migration_final1['year'] = 2015
# migration_final1['all'] = migration_final1['all'] / 100
# migration_final1['medicines'] = migration_final1['all'] / 100
# migration_final1['supplies'] = migration_final1['all'] / 100

med_trade.loc[med_trade['ISO-3A']=='CHT','iso3c'] = 'TWN'

med_trade.loc[med_trade['type'].str.startswith('tariff'),['all', 'medicines', 'supplies', 
                    'equipment', 'protective']] = med_trade.loc[med_trade['type'].str.startswith('tariff'),
                    ['all', 'medicines', 'supplies', 'equipment', 'protective']] / 100

med_trade.loc[~med_trade['type'].str.startswith('tariff'),['all', 'medicines', 'supplies',
                    'equipment', 'protective']] = med_trade.loc[~med_trade['type'].str.startswith('tariff'),
                                                     ['all', 'medicines', 'supplies', 'equipment', 'protective']] * 1000000

med_trade.to_csv('med_trade.csv', index=False)



# print(med_trade[med_trade['region'] != 'Aggregates']['ISO-3A'].unique().tolist())


