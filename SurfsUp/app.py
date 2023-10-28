# Import the dependencies.

import datetime as dt
import numpy as np
import pandas as pd

from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

#################################################

# Homepage Setup
app = Flask(__name__)

@app.route("/")
def home():
    return (
        "Welcome to the Climate App API!<br/><br/>"
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/start<br/>"
        "/api/v1.0/start/end"
    )

##################################

# Create the SQLAlchemy engine and establish a connection to the database
engine = create_engine("sqlite:///SurfsUp/Resources/hawaii.sqlite")

# Create a session to interact with the database
session = Session(engine)


# Reflect the database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# Define the Measurement table
Measurement = Base.classes.measurement
Station = Base.classes.station


# Precipitation route creation
@app.route("/api/v1.0/precipitation")
def precipitation():
   
    
    # Calculated the date one year from the last date in the dataset
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d")
    one_year_ago = most_recent_date - dt.timedelta(days=365)
    
    # A query to retrieve the last 12 months of precipitation data
    precipitation_data = session.query(Measurement.date, Measurement.prcp)\
        .filter(Measurement.date >= one_year_ago).all()

    session.close()
    
    # Created a dictionary with date as the key and prcp as the value
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precipitation_dict)

# Station route creation
@app.route("/api/v1.0/stations")
def stations():
    # Create a session to interact with the database
    session = Session(engine)
    
    # Query to retrieve the list of stations
    station_data = session.query(Station.station, Station.name).all()

    session.close()

    # Create a list of station data as dictionaries
    station_list = [{"Station ID": station, "Station Name": name} for station, name in station_data]

    return jsonify(station_list)


# Tobs route creation 

@app.route("/api/v1.0/tobs")
def tobs():
    # Create a session to interact with the database
    session = Session(engine)
    
    # Calculate the most active station
    active_stations = session.query(Measurement.station, func.count(Measurement.id))\
        .group_by(Measurement.station)\
        .order_by(func.count(Measurement.id).desc())\
        .all()

    most_active_station = active_stations[0][0]

    # Calculated the date one year from the last date in the dataset
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d")
    one_year_ago = most_recent_date - dt.timedelta(days=365)
    
    # A query to retrieve temperature observations for the previous year from the most-active station
    temperature_data = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.station == most_active_station, Measurement.date >= one_year_ago).all()

    session.close()
    
    # Created a list of temperature observations as dictionaries
    temperature_list = [{"Date": date, "Temperature": tobs} for date, tobs in temperature_data]

    return jsonify(temperature_list)


# Start/End Route creation

# Define the /api/v1.0/<start> route
@app.route("/api/v1.0/<start>")
def temperature_stats_start(start):
    # Create a session to interact with the database
    session = Session(engine)
    
    # Query to retrieve temperature statistics (TMIN, TAVG, TMAX) for dates greater than or equal to the start date
    temperature_stats = session.query(
        func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.date >= start).all()

    session.close()

    # Create a list of temperature statistics as dictionaries
    statistics_list = [
        {"Start Date": start, "TMIN": tmin, "TAVG": tavg, "TMAX": tmax}
        for tmin, tavg, tmax in temperature_stats]

    return jsonify(statistics_list)

# Define the /api/v1.0/<start>/<end> route
@app.route("/api/v1.0/<start>/<end>")
def temperature_stats_range(start, end):
    # Create a session to interact with the database
    session = Session(engine)
    
    # Query to retrieve temperature statistics (TMIN, TAVG, TMAX) for the specified date range
    temperature_stats = session.query(
        func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.date >= start, Measurement.date <= end).all()

    session.close()

    # Create a list of temperature statistics as dictionaries
    statistics_list = [
        {"Start Date": start, "End Date": end, "TMIN": tmin, "TAVG": tavg, "TMAX": tmax}
        for tmin, tavg, tmax in temperature_stats]

    return jsonify(statistics_list)


if __name__ == "__main__":
    app.run(debug=True)