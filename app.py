import numpy as np

import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

###################################
# Database setup
###################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

#Reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

###################################
# Flask setup
###################################

app = Flask(__name__)

###################################
# Flask routes
###################################

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f'<h3><font face="arial">Below are the available routes to access precipitation and temperature data of Hawaii during 2017-01-01 adn 2018-08-23:</font></h3><br/><br/>'
        f'<font face="arial">1. Precipitation data on all available dates:</font><br/>'
        f'<font color="#D35400" font face="arial">/api/v1.0/precipitation</font><br/><br/>'
        f'<font face="arial">2. The list of weather stations:</font><br/>'
        f'<font color="#D35400" font face="arial">/api/v1.0/stations</font><br/><br/>'
        f'<font face="arial">3. Temperature values recorded by the most active station across all dates:</font><br/>'
        f'<font color="#D35400" font face="arial">/api/v1.0/tobs</font><br/><br/>'
        f'<font face="arial">4. Temperature statistics during a date range with a self-selected start date:</font><br/>'
        f'<font color="#D35400" font face="arial">/api/v1.0/&lt;start&gt;</font><br/><br/>'
        f'<font face="arial">5. Temperature statistics during a date range with self-selected start and end dates:</font><br/>'
        f'<font color="#D35400" font face="arial">/api/v1.0/&lt;start&gt;/&lt;end&gt;</font><br/><br/>'
        f'<font face="arial"><i>Note: Any dates selected to run route 4 and 5 should be typed in the format of yyyy-mm-dd.</i></font><br/>'      
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query date and precipitation values
    results = session.query(Measurement.date, Measurement.prcp).all()
    
    session.close()

    # Create a dictionary from the data and append to a list of all_precipitation
    all_precipitation = []
    for date, prcp in results:
        p_dict = {}
        p_dict['date'] = date
        p_dict['precipitation'] = prcp
        all_precipitation.append(p_dict)
    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def station():
    session = Session(engine)
    results = session.query(Station.station).order_by(Station.station).all()
    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    # Get the last date in the database & the date from a year ago
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    year_ago = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Get the most active station
    most_active = session.query(Measurement.station).\
                                group_by(Measurement.station).\
                                order_by(func.count(Measurement.date).desc()).first()
    most_active_stn = most_active[0]
    
    # Query dates and temperatures of the most active station for the last year of data
    results = session.query(Measurement.date, Measurement.tobs).\
                            filter(Measurement.station == most_active_stn).\
                            filter(Measurement.date >= year_ago).all()
    session.close()

    # Create a dictionary from the data and append to a list of temp
    temp = []
    for date, tobs in results:
        t_dict = {}
        t_dict['date'] = date
        t_dict['temperature'] = tobs
        temp.append(t_dict)
    return jsonify(temp)

@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)

    # Query data for the start date
    results = session.query(func.min(Measurement.tobs),\
                            func.avg(Measurement.tobs),\
                            func.max(Measurement.tobs)).\
                            filter(Measurement.date >= start).all()
    session.close()

    # Create a dictionary from the data and append to a list of temp_start
    temp_start = []
    for result in results:
        temp_start_dict = {}
        temp_start_dict['min temp'] = result[0]
        temp_start_dict['avg temp'] = result[1]
        temp_start_dict['max temp'] = result[2]
        temp_start.append(temp_start_dict)
        return jsonify(temp_start)

@app.route("/api/v1.0/<start>/<end>")
def range(start, end):
    session = Session(engine)

    # Query data between the start and end dates
    results = session.query(func.min(Measurement.tobs),\
                            func.avg(Measurement.tobs),\
                            func.max(Measurement.tobs)).\
                            filter(Measurement.date >= start).\
                            filter(Measurement.date <= end).all()
    session.close()

    # Create a dictionary from the data and append to a list of start_end
    start_end = []
    for result in results:
        se_dict = {}
        se_dict['min temp'] = result[0]
        se_dict['avg temp'] = result[1]
        se_dict['max temp'] = result[2]
        start_end.append(se_dict)
        return jsonify(start_end)

if __name__ == "__main__":
    app.run(debug=True)