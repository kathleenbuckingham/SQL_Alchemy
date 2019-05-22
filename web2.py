import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation - lists precipitation<br/>"
        f"/api/v1.0/stations - lists all weather stations in Honolulu <br/>"
        f"/api/v1.0/tobs - List of temperatures from all stations"
        f"/api/v1.0/<start> -calculates the MIN/AVG/MAX temperature for all dates greater than and equal to the start date "
        f"/api/v1.0/<start>/<end> calculates the MIN/AVG/MAX temperature for all dates less than and equal to the end date"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    precipitation = session.query(Measurement.prcp, Measurement.date).all()
       
    precp = []
    for date, prcp in precipitation:
             precipitation_dict = {}
             precipitation_dict["date"] = date
             precipitation_dict["prcp"] = prcp
             precp.append(precipitation_dict)
    return jsonify(precp)

@app.route("/api/v1.0/stations")
def stations():

    stations = session.query(Station.station).all()

    stations_list = []
    for stations in stations:
        stations_dict = {}
        stations_dict["Station"] = stations
        stations_list.append(stations_dict)

    return jsonify(stations_list)
    
@app.route("/api/v1.0/tobs")
def tobs():

    temp_data_highest_obs = session.query(Measurement.tobs).all()

    tobs_list = []
    for tobs in temp_data_highest_obs:
        tobs_dict = {}
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)


@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""

    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        # Unravel results into a 1D array and convert to a list
        temps = list(np.ravel(results))
        return jsonify(temps)

    # calculate TMIN, TAVG, TMAX with start and stop
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps)

if __name__ == '__main__':
    app.run(debug=True)