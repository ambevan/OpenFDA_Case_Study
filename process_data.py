import pandas as pd
import numpy as np
import scipy.stats as st
from scipy.stats import chi2_contingency
from scipy.stats import chi2
import matplotlib.pyplot as plt

def z_test(series1, series2, prob):
    ''' 
    Performs a z-test comparing two distributions and determines significance
    
    Parameters:
    series1 (pandas series): the first distribution
    series2 (pandas series): the second distribution
    prob (float): the significance level to test against
    
    Returns:
    z (float): the z value
    '''
    
    # calculate sigmas and means of distributions
    sd1 = series1.std()
    sd2 = series2.std()
    mu1 = series1.mean()
    mu2 = series2.mean()
    
    # calculate z and determin critical value for significance level
    z = (mu1-mu2)/(sd1**2 + sd2**2)**0.5
    crit = st.norm.ppf(prob)
    
    # compare z to critical value
    print(f'z = {z:.3}  critical value = {crit:.3}')
    if abs(z) >= crit:
        print(f'Reject null hypothesis. Variables dependent at the {prob:.0%} confidence level.')
    else:
        print('Do not reject null hypothesis. Insufficiest evidence for dependence.')

    return z

def add_labels(ax, pivot):
    ''' 
    Adds labels to objects in a pivot plot
    '''
    p_all = ax.patches
    for i, p in enumerate(ax.patches):
        if (i % 2):
            j=int((i)/2)
            ax.annotate(f'n = {pivot.total[j]:.0f}', 
                        (p_all[j].get_x(), 
                         max(p_all[j+len(pivot)].get_height(),p_all[j].get_height()) * 1.01))

def calculate_serious_pivot(data, index):
    ''' 
    Calculates a pivot table of serious against index
    
    Parameters:
    data (dataframe): the data to pivot on
    index (str): the column name to compare to serious
    
    Returns:
    pivot_tb (dataframe): the pivot table
    '''
    
    # calculate pivot table
    pivot_tb = pd.pivot_table(data, values=['index'],  index=index, columns=['serious'], aggfunc='count')
    pivot_tb = pivot_tb[pivot_tb.notna().all(axis=1)]
    
    # calculate values at percentages
    pivot_tb['total'] = pivot_tb.sum(axis=1)
    pivot_tb.columns = ['not serious','serious','total']
    pivot_tb[['not serious %','serious %']] = pivot_tb[['not serious', 'serious']].div(pivot_tb.total, axis=0).multiply(100)

    return pivot_tb
    
def plot_serious_pivot(pivot, index, ax=None, annotate=False):
    ''' 
    Plots a pivot table as a bar chart
    
    Parameters:
    pivot (dataframe): the pivot table to plot
    index (str): the column name to compare to serious
    
    kwargs:
    ax (axes): the axes to plot on
    annotate (bool): whether to add labels to the bars
    
    Returns:
    ax (axes): the plot
    '''
    
    # get axes and plot pivot
    ax = ax or plt.gca()
    ax = pivot[['not serious %','serious %']].plot.bar(ax=ax);
    ax.set_ylabel('%');
    ax.legend(labels=['not serious', 'serious'])

    # annotate with labels if requested
    if annotate:
        add_labels(ax, pivot)
    return ax

def significance_test(table, prob):
    ''' 
    Performs a pearson chi2-test on the data
    
    Parameters:
    table (dataframe): the data on which to perform the test
    prob (float): the significance level to test against
    '''
    
    # calculate chi2 contingency table
    chi2_stat, p, dof, expected = chi2_contingency(table)

    # interpret test-statistic
    prob = prob
    critical = chi2.ppf(prob, dof)

    # print useful values 
    print(f"dof = {dof}  "
          f"probability = {prob:.3f} | "
          f"critical = {critical:.3f}   "
          f"chi2 = {chi2_stat:.3f}")
    print()

    # determine and print outcome
    if abs(chi2_stat) >= critical:
        print(f'Reject null hypothesis. Variables dependent at the {prob:.0%} confidence level.')
    else:
        print('Do not reject null hypothesis. Insufficiest evidence for dependence.')

def impute_on_mean(data, series_name):
    '''
    Replace all NaNs with mean of other data
    '''
    series_mean = data[series_name].mean()
    data[series_name].fillna(series_mean, inplace=True)
    
def map_routes(data, frac):
    '''
    Convert all drug routes that do not appear with frequency > frac to "OTHER"
    '''
    # list all routes and their relative frequencies
    freqs = data.route.value_counts(normalize=True)

    # create a dictionary for the mapping
    routes = freqs.index
    route_map = {}
    for i, freq in enumerate(freqs):
        if freq > frac:
            route_map[routes[i]] = routes[i]
        else:
            route_map[routes[i]] = 'OTHER'
            
    # create a new column to store the new categories
    data['route_summary'] = data.route.map(route_map)
    
    return data

