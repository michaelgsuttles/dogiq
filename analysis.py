import time
from pprint import pprint
import pandas as pd
import sys
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import re

nyc_registry = pd.read_csv('dogdata/NYC_Dog_Licensing_Dataset_2016-edit.csv')
coren = pd.read_csv('dogdata/dog_intelligence-edit.csv')
nyc_census = pd.read_csv('censusdata/ACS_16_1YR_S0201_with_ann-edit.csv') # use 2016 data
edmonton_registry = pd.read_csv('dogdata/Edmonton_Pet_Licenses_by_Neighbourhood_2018-edit.csv')
adelaide_registry = pd.read_csv('dogdata/Dog_Registrations_Adelaide_2016-edit.csv')
wiki = pd.read_csv('dogdata/wiki-edit.csv')
attrib = turcsan = pd.read_csv('dogdata/turcsan.csv')

#attrib = coren.set_index('Breed').join(turcsan.set_index('Breed'), how='inner')


# Canine attributes by AKC Groupings
wiki_pared = wiki[['Breed', 'AKC']]
akc_groups_attrib = wiki_pared.set_index('Breed').join(attrib.set_index('Breed'), how='left')
akc = akc_groups_attrib.groupby('AKC').mean()
pprint(akc)
akc_count = akc_groups_attrib.groupby('AKC').count()
pprint(akc_count)

# Make the census columns understandable
val = 'EST_'
err = 'MOE_'
age_under_5 = 'VC16'
age_5_17 = 'VC17'; age_18_24 = 'VC18'
age_25_34 = 'VC19'; age_35_44 = 'VC20'
age_45_54 = 'VC21'; age_55_64 = 'VC22'
age_65_74 = 'VC23'; age_75_over = 'VC24'



# Strip out dirty values
nyc_registry['Borough'] = nyc_registry['Borough'].map(lambda x: '' if x not in {'Brooklyn', 'Bronx', 'Staten Island', 'Manhattan', 'Queens'} else x)

nyc_attrib = nyc_registry.set_index('BreedName').join(attrib.set_index('Breed'), how='left')

nyc_attrib_t = nyc_registry.set_index('BreedName').join(turcsan.set_index('Breed'), how='left')
nyc_attrib_t_g = nyc_attrib_t.groupby('Borough').mean()
pprint(nyc_attrib_t_g)

# Adelaide
adelaide_attrib = adelaide_registry.set_index('AnimalBreed').join(attrib.set_index('Breed'), how='left')

print('Adelaide')
print(adelaide_attrib[['Calm', 'Trainable', 'Sociable', 'Bold']].mean())
print(adelaide_attrib[['Calm', 'Trainable', 'Sociable', 'Bold']].std())

# Edmonton
print('Edmonton')
edmonton_attrib = edmonton_registry.set_index('BREED').join(attrib.set_index('Breed'), how='left')
print(edmonton_attrib[['Calm', 'Trainable', 'Sociable', 'Bold']].mean())
print(edmonton_attrib[['Calm', 'Trainable', 'Sociable', 'Bold']].std())

# Which ancestral homeland has the smartest/most obedient dogs?
ancestral = wiki[['Breed', 'Origin']]

# Combining Scotland, Wales, and England as United Kingdom
ancestral['Origin'] = ancestral['Origin'].map(lambda x: 'United Kingdom' if x in {'England', 'Wales', 'Scotland'} else x)
ancestral_attrib = ancestral.set_index('Breed').join(attrib.set_index('Breed'), how='inner')

# Take cells with multiple countries and split them into separate countries
def splitDataFrameList(df,target_column,separator):
    ''' df = dataframe to split,
    target_column = the column containing the values to split
    separator = the symbol used to perform the split
    returns: a dataframe with each entry for the target column separated, with each element moved into a new row. 
    The values in the other columns are duplicated across the newly divided rows.
    Thanks to James Allen, https://gist.github.com/jlln/338b4b0b55bd6984f883
    '''
    def splitListToRows(row,row_accumulator,target_column,separator):
        split_row = row[target_column].split(separator)
        for s in split_row:
            new_row = row.to_dict()
            new_row[target_column] = s
            row_accumulator.append(new_row)
    new_rows = []
    df.apply(splitListToRows,axis=1,args = (new_rows,target_column,separator))
    new_df = pd.DataFrame(new_rows)
    return new_df

ancestral_attrib.dropna(inplace=True)
ancestral_attrib2 = splitDataFrameList(ancestral_attrib,'Origin', '/')

ancestral_attrib_group = ancestral_attrib2.groupby('Origin').mean()
pprint(ancestral_attrib_group)
ancestral_count = ancestral_attrib2.groupby('Origin').count()
pprint(ancestral_count)

wiki_breeds = set(wiki['Breed'].tolist())
coren_breeds = set(coren['Breed'].tolist())
turcsan_breeds = set(turcsan['Breed'].tolist())

print('Intersection')
print(wiki_breeds & turcsan_breeds)
print('Difference')
print(wiki_breeds - turcsan_breeds)
print(turcsan_breeds - wiki_breeds)

comparison = wiki[['Breed']]
comparison['Turcsan'] = comparison['Breed'].apply(lambda x: process.extractOne(x, list(turcsan_breeds)) if x not in turcsan_breeds else '')
comparison['Coren'] = comparison['Breed'].apply(lambda x: process.extractOne(x, list(coren_breeds)) if x not in coren_breeds else '')
comparison.to_csv('dogdata/comparisons.csv')
