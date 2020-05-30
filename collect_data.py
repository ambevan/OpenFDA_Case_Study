import numpy as np
import pandas as pd
import json
import requests
import math
from time import sleep
from tqdm.notebook import tnrange, tqdm


def create_search_url(url_base, **kwargs):
    # kwargs are search_key, search_term, count and limit
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
    if search_str == "":
        url = f"{url_base}&{count_str}&{limit_str}"
    else:
        url = f"{url_base}+AND+{search_str}&{count_str}&{limit_str}"
    return url


def get_data_from_url(url_base, **kwargs):
    url = create_search_url(url_base, **kwargs)
    data = requests.get(url).json()
    return pd.DataFrame(data.get("results"))


def collect_pediatric_data(n_records):
    n_iterations = math.ceil(n_records/100)
    all_pediatric = pd.DataFrame()
    for i in tnrange(n_iterations, desc='Progress'):
        url = f"https://api.fda.gov/drug/event.json?search=patient.patientagegroup:3&limit=100&skip={i*100}"
        json_data = requests.get(url).json()
        data = pd.json_normalize(json_data.get('results'))
        all_pediatric = all_pediatric.append(data)
    return all_pediatric

def flatten_series_list(myseries):
    temp = pd.DataFrame(myseries.to_list())
    flattened_series_df = pd.DataFrame(temp.loc[:,0].to_list()) #take only first reported value 
    return flattened_series_df

def flatten_series_dict(myseries):
    temp = pd.DataFrame(myseries.to_dict())
    flattened_series_df = pd.DataFrame(temp).transpose()
    for col in flattened_series_df.columns:
        flattened_series_df[col] = flattened_series_df[col].map(lambda x: x[0], na_action='ignore')
    return flattened_series_df


def flatten_dataframe(df):
    # check for unique index
    expandable_columns = ['patient.reaction',
                         'patient.drug',
                         'openfda'
                        ]
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
        
