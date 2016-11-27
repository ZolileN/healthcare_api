## __author__ = 'Josh Firminger'
import pandas as pd
import os
from os.path import isfile, getsize, join

PATH = '/Users/joshfirminger/Desktop/APIs/data/cms_synpuf'
OUTPUT_PATH = '/Users/joshfirminger/Desktop/APIs/data/store'
os.chdir(PATH)

FILE_LIST = [file_ for file_ in os.listdir(PATH) if isfile(file_)]

def identify_diagnosis(data, columns, diagnosis_codes):
    for col in columns:
        if row[col] in diagnosis_codes:
            return 1
    return 0

print('reading in claims and benefits tables')
data_claimsA = pd.read_csv(FILE_LIST[1], sep= ',')
data_claimsB = pd.read_csv(FILE_LIST[2], sep= ',')

benefits_2008 = pd.read_csv(FILE_LIST[0], sep= ',')

benefits_2009 = pd.read_csv(FILE_LIST[6], sep= ',')


data_claimsA.CLM_FROM_DT = pd.to_datetime(data_claimsA.CLM_FROM_DT, format = '%Y%m%d')
data_claimsA.CLM_THRU_DT = pd.to_datetime(data_claimsA.CLM_THRU_DT, format = '%Y%m%d')
data_claimsB.CLM_FROM_DT = pd.to_datetime(data_claimsB.CLM_FROM_DT, format = '%Y%m%d')
data_claimsB.CLM_THRU_DT = pd.to_datetime(data_claimsB.CLM_THRU_DT, format = '%Y%m%d')

benefits_2008.BENE_BIRTH_DT = pd.to_datetime(benefits_2008.BENE_BIRTH_DT , format = '%Y%m%d')
benefits_2009.BENE_BIRTH_DT = pd.to_datetime(benefits_2009.BENE_BIRTH_DT , format = '%Y%m%d')

### Columns for ICD9 Diagnosis Codes ###
icd9_columns =  [u'ICD9_DGNS_CD_1', u'ICD9_DGNS_CD_2', u'ICD9_DGNS_CD_3',
                u'ICD9_DGNS_CD_4', u'ICD9_DGNS_CD_5',
                u'ICD9_DGNS_CD_6', u'ICD9_DGNS_CD_7',
                u'ICD9_DGNS_CD_8']
icd9_index = []
for col in icd9_columns:
    icd9_index.append(data_claimsA.columns.get_loc(col))

## Identify Type II Diabetes ###
base = '250'
diabetes_type_2_list = []
for val in range(0, 10):
    ## Type II Diabetes ##
    diabetes_type_2_list.append(base+str(val)+'0')
    diabetes_type_2_list.append(base+str(val)+'2')

## join 2008 and 2009 benefit tables on DESYNPUF_ID
print('join 2008 and 2009 benefit tables on DESYNPUF_ID')
list_keep = ['DESYNPUF_ID', 'SP_DIABETES']
benefits_08_09 = pd.merge(benefits_2008[list_keep], benefits_2009[list_keep], on = 'DESYNPUF_ID', how = 'inner',\
                                 suffixes=('_2008', '_2009'))

## possible dependent variable:
##  identify individuals who do not have chronic diabetes in 2008 and 2009
##  flag for type II diagnosis in 2010
no_hist_of_dbts = benefits_08_09[(benefits_08_09.SP_DIABETES_2008 != 1)&
                                 (benefits_08_09.SP_DIABETES_2009 != 1)]

## join to claims data
claims_2010_A = data_claimsA[(data_claimsA.CLM_THRU_DT >= '2010-01-01')&
                           (data_claimsA.CLM_THRU_DT <= '2010-12-31')]

claims_2010_B = data_claimsB[(data_claimsB.CLM_THRU_DT >= '2010-01-01')&
                          (data_claimsB.CLM_THRU_DT <= '2010-12-31')]

claims_2010 = pd.concat([claims_2010_A,claims_2010_B])
                           
claims_no_hist = pd.merge(claims_2010, no_hist_of_dbts, on = 'DESYNPUF_ID', how = 'inner')

print('find all type II diabetes diagnosis in 2010')
diabetes_type_2 = []
for row in claims_no_hist.itertuples():
    diabetes_type_2.append(identify_diagnosis(row, icd9_index, diabetes_type_2_list))
claims_no_hist['diabetes_type_2'] = diabetes_type_2

dep = claims_no_hist.groupby('DESYNPUF_ID').apply(lambda batch: 1 if sum(batch.diabetes_type_2) > 0 else 0)

individuals = pd.DataFrame(dep)
individuals.reset_index(level=0, inplace=True)
individuals = individuals.rename(columns={0: 'FLAG'})

print('saving output to: {}/population_flag.csv'.format(OUTPUT_PATH))
individuals.to_csv('{}/population_flag.csv'.format(OUTPUT_PATH), sep=',')
