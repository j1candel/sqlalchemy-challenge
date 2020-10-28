# Import Modules
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify

import numpy as np
import datetime as dt

#####################################################################################

# Creating path for database set up 
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
conn = engine.connect()

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect = True)

# Save measurement references to measurement table
measurement = Base.classes.measurement

# Save station reference to reference table 
station = Base.classes.station

#####################################################################################

# Beginning session
session = Session(engine)

# Finding the last date in the dataset 
last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()

# Finding one year prior to the last date in the dataset 
one_year_from_last_date = dt.date(2017,8,23)-dt.timedelta(days=365)

# Closing session
session.close()

#####################################################################################

# Beginning session
session = Session(engine)

station_desc = session.query(measurement.station, func.count(measurement.prcp)).\
    group_by(measurement.station).\
    order_by(func.count(measurement.prcp).desc()).all()

most_active = station_desc[0][0]

# Closing session
session.close()

#####################################################################################

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
        f'Min, Max, & Avg Temp between Date Range. Enter Date as YYYY-MM-DD<br/>'
        f'/api/v1.0/<start>/<end><br/>'
    ) 

#####################################################################################

#Defining the precipitation route
@app.route('/api/v1.0/precipitation')
def precipitation():

    # Beginning session
    session = Session(engine)

    #Querying both date and precipiation 
    results = session.query(measurement.date, measurement.prcp).all()

    # Closing session
    session.close()

    #Setting precipitaiton equal to a list
    precipitation = []

    #Putting results into a dictionary
    for result in results:
        r = {}

        r['Date'] = result[0]
        r['Precipitation'] = result[1]

        #Appending into precipitation list
        precipitation.append(r)

    #Displaying Precipiation on app
    return jsonify(precipitation)

#####################################################################################

#Defining the stations route
@app.route('/api/v1.0/stations')
def stations():

    # Beginning session
    session = Session(engine)

    #Querying both station and name 
    results = session.query(station.station, station.name).all()
    
    # Closing session
    session.close()

    #Setting stations equal to a list
    stations = []

    #Putting results into a dictionary
    for result in results:
        r = {}

        r['Station'] = result[0]
        r['Name'] = result[1]

        #Appending into stations list
        stations.append(r)
    
    #Displaying stations on app
    return jsonify(stations)

#####################################################################################

#Defining the temperature route
@app.route('/api/v1.0/tobs')
def tobs():
    
    # Beginning session
    session = Session(engine)

    # Querying both date and temperature while only taking into consideration the past
    # year and the most active station
    results = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date >= one_year_from_last_date).\
        filter(measurement.station == most_active).all()
    
    # Closing session
    session.close()

    #Setting temperature equal to a list
    temperature = []

    #Putting results into a dictionary
    for result in results:
        r = {}

        r['Date'] = result[0]
        r['Temperature'] = result[1]

        #Appending into temperature list
        temperature.append(r)

    #Displaying stations on app
    return jsonify(temperature)

#####################################################################################

#Defining the start date route
@app.route("/api/v1.0/<start>")
def start(start):

    # Beginning session
    session = Session(engine)

    # Setting the format of the date 
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')

    # The min, max, and average temperature of the the dates equal to and greater than 
    # the start date
    results = session.query(func.min(measurement.tobs),\
    func.max(measurement.tobs),\
    func.avg(measurement.tobs)).\
    filter(measurement.date >= start_date).all()

    # Closing session
    session.close()

    #Setting temperature equal to a list
    desc_temp = []

    #Putting results into a dictionary
    for result in results:
        r = {}

        r['Start_Date'] = start_date
        r['Min_Temp'] = result[0]
        r['Max_Temp'] = result[1]
        r['Avg_Temp'] = result[2]

        #Appending into descibe temperature list
        desc_temp.append(r)
    
    #Displaying stations on app
    return jsonify(desc_temp)

#####################################################################################

#Defining the start and end date route
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):

    # Beginning session
    session = Session(engine)

    # Setting the format of the date 
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')

    # The min, max, and average temperature of the the dates equal to and greater than 
    # the start date but less than or equal to the end date 
    results = session.query(func.min(measurement.tobs),\
    func.max(measurement.tobs),\
    func.avg(measurement.tobs)).\
    filter(measurement.date >= start_date).\
    filter(measurement.date <= end_date).all()

    # Closing session
    session.close()
    
    #Setting temperature equal to a list
    desc_temp = []

    #Putting results into a dictionary
    for result in results:
        
        r = {}

        r['Start_Date'] = start_date
        r['End_Date'] = end_date
        r['Min_Temp'] = result[0]
        r['Max_Temp'] = result[1]
        r['Avg_Temp'] = result[2]
        
        #Appending into descibe temperature list
        desc_temp.append(r)
    
     #Displaying stations on app
    return jsonify(desc_temp)

#run the app
if __name__ == "__main__":
    app.run(debug=True)
