import numpy as np
import pandas as pd
import json
import requests
import math
from time import sleep
from tqdm.notebook import tnrange, tqdm


def create_search_url(url_base, **kwargs):
    ''' 
    Create a url which can be used to query the OpenFDA FAERS. 

    Parameters:
    url_base : the string to use as the base (beginning) of the url

    kwargs:
    count (str): the field by which the data should be counted
    limit (int): limit the number of records to return to this number
    search_key (str): the name of the field to search
    search_term (str): the string to match

    Returns:
    url (str): a string url which can be used to query the OpenFDA FAERS
    '''
    
    # construct strings for each part of the URL
    # count term, limit term, search term
    try:
        count_str = f"count={str(kwargs['count'])}"
    except:
        count_str = ""
    try:
        search_str = f"{str(kwargs['search_key'])}:{str(kwargs['search_term'])}"
    except:
        search_str = ""
    try:
        limit_str = f"limit={str(kwargs['limit'])}"
    except:
        limit_str = ""
    try:
        sort_str = f"sort={str(kwargs['sort'])}"
    except:
        sort_str = ""
        
    # construct string from component string
    if search_str == "":
        url = f"{url_base}&{count_str}&{limit_str}"
    else:
        url = f"{url_base}+AND+{search_str}&{count_str}&{limit_str}"
    
    return url


def get_data_from_url(url_base, **kwargs):
    ''' 
    Query the OpenFDA FAERS database using request 
        
    Parameters:
    url_base : the string to use as the base (beginning) of the url
    
    kwargs:
    count (str): the field by which the data should be counted
    limit (int): limit the number of records to return to this number
    search_key (str): the name of the field to search
    search_term (str): the string to match
    
    Returns:
    df (dataframe): dataframe of the collected data
    '''
        
    # create url to query with    
    url = create_search_url(url_base, **kwargs)
    
    # collect data and parse in json format
    data = requests.get(url).json()
    
    # convert data to dataframe and remove metadata
    df = pd.DataFrame(data.get("results"))

    return df



def collect_pediatric_data(n_records):
    ''' 
    Collect a sample of pediatric data with n_records using get_data_from_url
    
    Parameters:
    n_records (int): the number of records to collect
    
    Returns:
    all_pediatric (dataframe): a dataframe containing a sample of pediatric data with n_records
    '''
    
    # determine how many times to query the API
    n_iterations = math.ceil(n_records/100)
    
    # loop over requests pulling 100 records each time
    # skipping i*100 rows each time so as not to pull the same data twice
    all_pediatric = pd.DataFrame()
    for i in tnrange(n_iterations, desc='Progress'):
        url = f"https://api.fda.gov/drug/event.json?search=patient.patientagegroup:3&limit=100&skip={i*100}"
        json_data = requests.get(url).json()
        data = pd.json_normalize(json_data.get('results'))
        all_pediatric = all_pediatric.append(data)
    
    return all_pediatric

def flatten_series_list(myseries):
    '''
    Intermediate step function to flatten a series that contains lists
    
    Parameters:
    myseries (pandas series): the series to flatten
    
    Returns:
    flattened_series_df (dataframe): a dataframe containing the flattened series
    '''
    
    # create a temporary dataframe generated from unpacked list
    temp = pd.DataFrame(myseries.to_list())
    
    # recast to dataframe
    flattened_series_df = pd.DataFrame(temp.loc[:,0].to_list()) #take only first reported value 

    return flattened_series_df

def flatten_series_dict(myseries):
    '''
    Intermediate step function to flatten a series that contains dictionaries
    
    Parameters:
    myseries (pandas series): the series to flatten
    
    Returns:
    flattened_series_df (dataframe): a dataframe containing the flattened series
    '''

    # create a temporary dataframe generated from unpacked dictionary
    temp = pd.DataFrame(myseries.to_dict())
    
    # recast to dataframe
    flattened_series_df = pd.DataFrame(temp).transpose()
    for col in flattened_series_df.columns:
        flattened_series_df[col] = flattened_series_df[col].map(lambda x: x[0], na_action='ignore')
    
    return flattened_series_df


def flatten_dataframe(df):
    ''' 
    Flatten the dataframe which containes nested lists and dictionaries
    
    Parameters:
    df (dataframe): the dataframe to flatten
    
    Returns:
    flattened__df (dataframe): the flattened dataframe
    '''
    
    # list the names of columns that need unpacking
    expandable_columns = ['patient.reaction',
                         'patient.drug',
                         'openfda'
                        ]
    
    # loop over series expanding each series in turn 
    # and appending to flat dataframe
    flattened_df = df 
    for col_name in expandable_columns:
        if col_name != 'openfda':
            flat_series_df = flatten_series_list(flattened_df[col_name])
            flat_series_df.reset_index(drop=True, inplace=True)
            flattened_df = pd.concat([flattened_df,flat_series_df], axis=1, sort=False)
        else:
            flat_series_df = flatten_series_dict(flattened_df[col_name])
            flat_series_df.reset_index(drop=True, inplace=True)
            flattened_df = pd.concat([flattened_df,flat_series_df], axis=1, sort=False)
    
    assert len(df) == len(flattened_df), 'Flattening dataframe failed.'
    
    return flattened_df
        
