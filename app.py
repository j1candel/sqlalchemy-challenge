#Import Modules
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify

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

#Creating the app
app = Flask(__name__)

#Defining the flask route
@app.route("/")
def home():
    #List of all available api routes
    return(
        f'Hello! Take a Look at Hawaii Weather<br/>'
        f'The following are the available routes:<br/>'
        f'<br/>'
        f'Precipitation With Dates:<br/>'
        f'/api/v1.0/precipitation'
    ) 

#Defining the precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)

    results = session.query(measurement.date, measurement.prcp).all()

    session.close()

    precipitation = []

    for result in results:
        r = {}

        r[result[0]] = result[1]

        precipitation.append(r)

    return jsonify(precipitation)

#run the app
if __name__ == "__main__":
    app.run(debug=True)