import numpy as np
import pandas as pd


def drop_unnecessary_columns(df):
    ''' 
    Remove columns that are not wanted
    
    Parameters:
    df (dataframe): the dataframe to reduce
    
    Returns:
    df (dataframe): the reduced dataframe
    '''
    
    # list of columns to keep
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
    
    # list all columns and drop those not in keep list
    all_columns = set(df.columns)
    columns_to_drop = list(all_columns-columns_to_keep)
    df.drop(columns_to_drop, axis=1, inplace=True)
    
    return df


def fill_seriousness_nan(df):
    ''' 
    Replace NaN values with 0 in seriousness columns
    
    Parameters:
    df (dataframe): the dataframe to impute
    
    Returns:
    df (dataframe): the imputed dataframe
    '''
    
    # list seriousness columns and replace NaNs with 0s
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
    ''' 
    Remove all columns where number NaN is > perc
    
    Parameters:
    df (dataframe): the dataframe to reduce
    perc (float): the percentage threshold to drop a column
    
    Returns:
    df (dataframe): the reduced dataframe
    '''
    
    # drop columns from df where number of missing values is > perc
    threshold = len(df)*perc/100
    df = df.dropna(thresh=threshold,axis=1) 
    
    return df
    
    
def fix_data_types(df):
    ''' 
    Convert numerical fields to float
    
    Parameters:
    df (dataframe): the dataframe with incorrect types
    
    Returns:
    df (dataframe): the corrected dataframe
    '''
    
    # get list of columns to convert to float by
    # removing columns with string data from all columns
    columns = list(set(df.columns) - {'occurcountry',
                                      'reactionmeddrapt',
                                      'route'}
                  )
    df[columns] = df[columns].astype('float',errors='ignore')
   
    return df
    

def reformat_onsetage(df):
    ''' 
    Recalculate the patient age in years based on age unit
    
    Parameters:
    df (dataframe): the dataframe with inconsistent ages
    
    Returns:
    df (dataframe): the dataframe with age in years
    '''
    
    col_unit = 'patient.patientonsetageunit'
    col_age = 'patient.patientonsetage'
    col_age_year = 'patient.patientonsetageyear'
    
    # check first that there is always a unit specified for patientage
    assert df[col_unit].isna().sum() == df[col_age].isna().sum(), 'Not all patient ages have units.'

    # calculate age in years based on unit 
    # 801 = years, 802 = months
    if (df.isin([802]).any().loc[col_unit]):
        df.loc[df[col_unit]==802, col_age_year] = df.loc[df[col_unit]==802, col_age]/12
    if (df.isin([801]).any().loc[col_unit]):
        df.loc[df[col_unit]==801, col_age_year] = df.loc[df[col_unit]==801, col_age]
    
    # drop old columns to avoid confusion
    df.drop(col_unit, axis=1, inplace=True)
    df.drop(col_age, axis=1, inplace=True)

    return df


def remove_outliers(df):
    ''' 
    Remove any outliers based on patient age (>=18)
    
    Parameters:
    df (dataframe): the dataframe with outliers
    
    Returns:
    df (dataframe): the dataframe without outliers
    '''
    
    df = df[(df['patient.patientonsetageyear'] < 18) | (df['patient.patientonsetageyear'].isna())]
    
    return df  