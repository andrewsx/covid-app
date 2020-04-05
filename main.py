from flask import Flask, render_template, request, url_for, redirect, abort
import pandas as pd
from datetime import datetime as dt
from bokeh.plotting import figure, output_file, show
from bokeh.embed import components
from constants import ABBV_TO_STATE, METRO_AREAS
import urllib
import json
app = Flask(__name__)

@app.route('/setup', methods=['GET'])
def setup():
    d = {}
    urllib.urlretrieve('https://github.com/nytimes/covid-19-data/raw/master/us-counties.csv', 'us-counties.csv')
    df_counties = pd.read_csv('./us-counties.csv')
    for index, row in df_counties.iterrows():
        if row['county'] + ", " + row['state'] not in d.keys():
            d[row['county'] + ", " + row['state']] = []
    
    # Construct a vector for every (county, state) of values where each one denotes a date 
    for index, row in df_counties.iterrows():
        if row['county'] + ", " + row['state'] in d.keys():
            d[row['county'] + ", " + row['state']].append( (row['date'],row['cases'],row['deaths']) )
    
    with open(r'./store.json', 'w') as wf:
        json.dump(d, wf)


# Index page
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.errorhandler(404)
def page_not_found(error):
   return render_template('errors.html', error=error), 404 


# def setup():
#     flag = True
#     df_counties = pd.read_csv('./us-counties.csv')
#     for index, row in df_counties.iterrows():
#         if row['county'] + ", " + row['state'] not in d.keys():
#             d[row['county'] + ", " + row['state']] = []
    
#     # Construct a vector for every (county, state) of values where each one denotes a date 
#     for index, row in df_counties.iterrows():
#         if row['county'] + ", " + row['state'] in d.keys():
#             d[row['county'] + ", " + row['state']].append( (row['date'],row['cases'],row['deaths']) )
#     with open(r'./store.json', 'w') as wf:
#         json.dump(d, wf)
    


@app.route('/graph/<string:county>/<string:state>')
def graph(county, state):
    with open(r'./store.json', 'r') as rf:
        data = json.load(rf)
    lst_dates,lst_cases,lst_deaths = [],[],[]
    
    lst = data[county + ", " + state]
    for tup in lst:
        lst_dates.append(tup[0])
        lst_cases.append(tup[1])
        lst_deaths.append(tup[2])
    


    date_objects = [dt.strptime(date, '%Y-%m-%d').date() for date in lst_dates]

    # create a new plot with a title and axis labels
    p = figure(title="Cases in " + county + " County" + ", " + state, x_axis_label='Dates',x_axis_type="datetime")

    # add a line renderer with legend and line thickness
    p.line(date_objects, lst_cases, legend_label="Cases", line_width=2, color='blue')
    p.line(date_objects, lst_deaths, legend_label="Deaths", line_width=2, color='red')

    p.legend.location = "top_left"
    # show the results
    script, div = components(p)
    return render_template('graphs.html',script=script, div=div)

@app.route('/button', methods=["POST"])
def button():
    if request.method == "POST":
        county = request.form.get('county').strip()
        state = request.form.get('state').strip()
        # if the state has a space
        if len(state.split()) == 2:
            tokens = state.split()
            state = tokens[0][0].upper() + tokens[0][1:].lower() + tokens[1][0].upper() + tokens[1][1:].lower() 
        # state has no space
        if state[0:3].lower() == "new":
            state = state[0].upper() + state[1:3].lower() + " " + state[3].upper() + state[4:].lower()
        elif state[0:5].lower() == "north" or state[0:5].lower() == "south":
            state = state[0].upper() + state[1:5].lower() + " " + state[5].upper() + state[6:].lower()
        else:
            state = state[0].upper() + state[1:].lower()
        county = county[0].upper() + county[1:].lower()
        if len(state) == 2:
            abbv = state.upper()
            if abbv in ABBV_TO_STATE:
                state = ABBV_TO_STATE[abbv]
        print(state)
        print(county)
        # Error validation checking
        for c in county:
            if not c.isalpha() and not c.isspace():
                abort(404, "No numbers allowed")
        for c in state:
            if not c.isalpha() and not c.isspace():
                abort(404, "No numbers allowed")
                


        print("COUNTY, STATE: " , county, state)
        return redirect(url_for('graph', county=county, state=state))

@app.route('/cluster', methods=['GET'])
def cluster():
    city = request.args.get('city')
    print(city) # <-- should print 'cat', 'dog', or 'dragon'

    with open(r'./store.json', 'r') as rf:
        data = json.load(rf)

    if city in METRO_AREAS:
        lst_of_counties = METRO_AREAS[city]
        print(lst_of_counties)
        

    lst_script_divs = []
    for entity in lst_of_counties:
        [county, state] = entity.split(",")
        
        
        lst_dates,lst_cases,lst_deaths = [],[],[]
        lst = data[county.strip() + ", " + state.strip()]
        for tup in lst:
            lst_dates.append(tup[0])
            lst_cases.append(tup[1])
            lst_deaths.append(tup[2])

        date_objects = [dt.strptime(date, '%Y-%m-%d').date() for date in lst_dates]

        # create a new plot with a title and axis labels
        p = figure(title="Cases in " + county + " County" + ", " + state, x_axis_label='Dates',x_axis_type="datetime")

        # add a line renderer with legend and line thickness
        p.line(date_objects, lst_cases, legend_label="Cases", line_width=2, color='blue')
        p.line(date_objects, lst_deaths, legend_label="Deaths", line_width=2, color='red')

        p.legend.location = "top_left"
        # show the results
        script, div = components(p)
        lst_script_divs.append( (script,div) )



    return render_template('graphs.html', sections=lst_script_divs)

if __name__ == '__main__':
	app.run(host='127.0.0.1',port=8080, debug=True)