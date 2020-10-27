#Import Modules
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify

import numpy as np
import datetime as dt

#####################################################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
conn = engine.connect()

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect = True)

# Save measurement references to measurement table
measurement = Base.classes.measurement

#Save station reference to reference table 
station = Base.classes.station

#####################################################################################

session = Session(engine)

#Finding the last date in the dataset 
last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()

one_year_from_last_date = dt.date(2017,8,23)-dt.timedelta(days=365)

session.close()

#####################################################################################

session = Session(engine)

descending_order = session.query(measurement.station, func.count(measurement.prcp)).\
    group_by(measurement.station).\
    order_by(func.count(measurement.prcp).desc()).all()

most_active = descending_order[0][0]

session.close()

#####################################################################################

most_active
#Creating the app
app = Flask(__name__)

#Defining the flask route
@app.route('/')
def home():
    #List of all available api routes
    return(
        f'Hello! Take a Look at Hawaii Weather<br/>'
        f'The following are the available routes:<br/>'
        f'<br/>'
        f'Precipitation with Dates:<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'<br/>'
        f'Stations with Names:<br/>'
        f'/api/v1.0/stations<br/>'
        f'<br/>'
        f'Most Active Station: Dates and Temperature:<br/>'
        f'/api/v1.0/tobs<br/>'
        f'<br/>'
        f'Min, Max, & Avg Temp for any Start Date. Enter Date as YYYY-MM-DD. <br/>'
        f'/api/v1.0/<start><br/>'
        f'<br/>'
        f'Min, Max, & Avg Temp between Date Range<br/>'
        f'/api/v1.0/<start>/<end><br/>'
    ) 

#####################################################################################

#Defining the precipitation route
@app.route('/api/v1.0/precipitation')
def precipitation():

    session = Session(engine)

    results = session.query(measurement.date, measurement.prcp).all()

    session.close()

    precipitation = []

    for result in results:
        r = {}

        r['Date'] = result[0]
        r['Precipitation'] = result[1]

        precipitation.append(r)

    return jsonify(precipitation)

#####################################################################################

@app.route('/api/v1.0/stations')
def stations():

    session = Session(engine)

    results = session.query(station.station, station.name).all()

    session.close()

    stations = []

    for result in results:
        r = {}

        r['Station'] = result[0]
        r['Name'] = result[1]

        stations.append(r)
    
    return jsonify(stations)

#####################################################################################

@app.route('/api/v1.0/tobs')
def tobs():
    
    session = Session(engine)

    results = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date >= one_year_from_last_date).\
        filter(measurement.station == most_active).all()
    
    session.close()

    temperature = []

    for result in results:
        r = {}

        r['Date'] = result[0]
        r['Temperature'] = result[1]

        temperature.append(r)

    return jsonify(temperature)

#####################################################################################

@app.route("/api/v1.0/<start>")
def start(start):

    session = Session(engine)

    start_date = dt.datetime.strptime(start, '%Y-%m-%d')

    results = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).filter(measurement.date >= start_date).all()

    session.close()

    desc_temp = []

    for result in results:
        
        r = {}

        r['Start_Date'] = start_date
        r['Min_Temp'] = result[0]
        r['Max_Temp'] = result[1]
        r['Avg_Temp'] = result[2]

        desc_temp.append(r)

    return jsonify(desc_temp)

#####################################################################################

#run the app
if __name__ == "__main__":
    app.run(debug=True)