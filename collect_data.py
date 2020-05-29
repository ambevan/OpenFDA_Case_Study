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
    for i in tnrange(50, desc='Progress'):
        url = f"https://api.fda.gov/drug/event.json?search=patient.patientagegroup:3&limit=100&skip={i*100}"
        data = get_data_from_url(url)
        all_pediatric = all_pediatric.append(data)
    return all_pediatric
