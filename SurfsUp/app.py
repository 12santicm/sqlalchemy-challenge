# Import the dependencies.
from flask import Flask, jsonify
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
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


# Welcome page
@app.route("/")
def welcome():
    """List all available routes."""
    return (
        f"<b>Hawaii vacations API</b><br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
        f"Example format: http://127.0.0.1:5001/api/v1.0/2017-02-01/2018-03-02"
    )

# Precipitation route

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the JSON representation of the last 12 months of precipitation data."""
    
    # Find the most recent date in the data set
    recent_date_result = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recent_date = recent_date_result.date

    # Convert recent_date to datetime
    recent_date_dt = dt.datetime.strptime(recent_date, '%Y-%m-%d')

    # Calculate the date one year from the last date in data set
    one_year_ago = recent_date_dt - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    prcp_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date).all()

    # Convert the query results to a dictionary
    prcp_dict = {date: prcp for date, prcp in prcp_data}

    return jsonify(prcp_dict)


# Stations route

@app.route("/api/v1.0/stations")

def stations():
    """Return a JSON list of stations."""
    
    # Perform a query to retrieve the station data
    return_stations = session.query(Station.station).all()

    # Convert list of tuples into normal list
    stations_list = [station[0] for station in return_stations]

    return jsonify(stations_list)


# Precipitation tobs

@app.route("/api/v1.0/tobs")

def tobs():

        most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.id).desc()).first()[0]

        # Find the most recent date in the data set
        recent_date_result = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
        recent_date = recent_date_result.date

     # Convert recent_date to datetime
        recent_date_dt = dt.datetime.strptime(recent_date, '%Y-%m-%d')
 
     # Calculate the date one year from the last date in data set
        one_year_ago = recent_date_dt - dt.timedelta(days=365)

        results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date).all()


     # Convert the query results to a list of dictionaries
        tobs_list = [{"date": date, "temperature": tobs} for date, tobs in results]

        return jsonify(tobs_list)



# Start and end route

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")

def temperature_stats(start=None, end=None):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum 
       temperature for a specified start or start-end range."""
    
    # If no end date provided, calculate stats from start date to the most recent date
    if end is None:
        end = session.query(func.max(Measurement.date)).scalar()

    # Query the temperature statistics for the given date range
    results = session.query(
        func.min(Measurement.tobs), 
        func.avg(Measurement.tobs), 
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Convert the query results to a list of dictionaries
    temp_stats = {
        "start_date": start, 
        "end_date": end,
        "min_temp": results[0][0], 
        "avg_temp": results[0][1], 
        "max_temp": results[0][2]
    }

    return jsonify(temp_stats)

if __name__ == '__main__':
    app.run(debug=True, port=5001)

