def impute_on_mean(data, series_name):
    series_mean = data[series_name].mean()
    data[series_name].fillna(series_mean, inplace=True)
    
def map_routes(data, frac):
    freqs = data.route.value_counts(normalize=True)
    routes = freqs.index
    route_map = {}
    for i, freq in enumerate(freqs):
        if freq > frac:
            route_map[routes[i]] = routes[i]
        else:
            route_map[routes[i]] = 'OTHER'
    data['route_summary'] = data.route.map(route_map)
    return data