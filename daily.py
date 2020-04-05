import urllib.request
import pandas as pd
import json
d = {}


########################  Run this script to retrieve the latest information about the coronavirus from the NY Times ##########################################
urllib.request.urlretrieve('https://github.com/nytimes/covid-19-data/raw/master/us-counties.csv', 'us-counties.csv')
def setup():
    df_counties = pd.read_csv('./us-counties.csv')
    for index, row in df_counties.iterrows():
        if row['county'] + ", " + row['state'] not in d.keys():
            d[row['county'] + ", " + row['state']] = []
    
    # Construct a vector for every (county, state) of values where each one denotes a date 
    for index, row in df_counties.iterrows():
        if row['county'] + ", " + row['state'] in d.keys():
            d[row['county'] + ", " + row['state']].append( (row['date'],row['cases'],row['deaths']) )
    


setup()
with open(r'./store.json', 'w') as wf:
        json.dump(d, wf)