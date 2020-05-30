import numpy as np
import pandas as pd


def drop_unnecessary_columns(df):
    columns_to_keep = {'occurcountry',
                           'patient.patientsex',
                           'patient.patientonsetage',
                           'patient.patientonsetageunit',
                           'primarysource.qualification',
                           'route',
                           'reporttype',
                           'serious',
                           'seriousnesscongenitalanomali',
                           'seriousnessother',
                           'seriousnesshospitalization',
                           'seriousnesslifethreatening',
                           'seriousnessdeath',
                           'seriousnessdisabling',
                           'reactionmeddrapt',
                           'reactionoutcome'}
    all_columns = set(df.columns)
    columns_to_drop = list(all_columns-columns_to_keep)
    df.drop(columns_to_drop, axis=1, inplace=True)
    return df


def fill_seriousness_nan(df):
    seriousness_list = [   'seriousnesscongenitalanomali',
                           'seriousnessother',
                           'seriousnesshospitalization',
                           'seriousnesslifethreatening',
                           'seriousnessdeath',
                           'seriousnessdisabling'
                       ]
    df[seriousness_list] = df[seriousness_list].fillna(0)
    return df


def remove_nan_columns(df,perc):
    # drop columns from df where number of missing values is > perc
    threshold = len(df)*perc/100
    df = df.dropna(thresh=threshold,axis=1) 
    return df
    
    
def fix_data_types(df):
    columns = list(set(df.columns) - {'occurcountry',
                                      'patient.patientonsetageunit',
                                      'reactionmeddrapt',
                                      'route'}
                  )
    df[columns] = df[columns].astype('float',errors='ignore')
    return df
    

def reformat_onsetage(df):
    col_unit = 'patient.patientonsetageunit'
    col_age = 'patient.patientonsetage'
    col_age_year = 'patient.patientonsetageyear'
    
    # check first that there is always a unit specified for patientage
    assert df[col_unit].isna().sum() == df[col_age].isna().sum(), 'Not all patient ages have units.'

    df.loc[df[col_unit]==802, col_age_year] = df.loc[df[col_unit]==802, col_age]/12
    df.loc[df[col_unit]==801, col_age_year] = df.loc[df[col_unit]==801, col_age]
    
    df.drop(col_unit, axis=1, inplace=True)
    df.drop(col_age, axis=1, inplace=True)
    return df


def remove_outliers(df):
    df = df[(df['patient.patientonsetageyear'] < 18) | (df['patient.patientonsetageyear'].isna())]
    return df  