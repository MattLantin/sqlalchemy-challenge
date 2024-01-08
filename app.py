# Import the dependencies.
from flask import Flask, jsonify

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Stations_Table = Base.classes.station
Measurements_Table = Base.classes.measurement


# Create our session (link) from Python to the DB
session = Session(engine)

# Date from year ago
most_recent_date = session.query(Measurements_Table.date).order_by(Measurements_Table.date.desc()).first()
one_year_ago = dt.date.fromisoformat(str(most_recent_date[0])) - dt.timedelta(days=365)
print("Date Year Ago From Latest Date:", one_year_ago)

# get the most active weather station
station_results = session.query(Measurements_Table.station, func.count(Measurements_Table.station)).\
    group_by(Measurements_Table.station).order_by(func.count(Measurements_Table.station).desc()).all()

most_active_station = str(station_results[0][0])
print("Most Active Station:", most_active_station, "\n\n")
#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")

def home():
    """Avaialble Api Routes"""

    return (
        f"Available Routes:<br/><br>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/&lt;iso_start_date&gt;<br>"
        f"/api/v1.0/&lt;iso_start_date&gt;/&lt;iso_end_date&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Precipitation of Last Year"""

    #Session
    session = Session(engine)

    #query passengers
    results = session.query(Measurements_Table.date, Measurements_Table.prcp).\
        filter(Measurements_Table.prcp != None).\
        filter(Measurements_Table.date >= one_year_ago).\
        order_by(Measurements_Table.date).all()
    
    #save query in dictionary
    precipitation_dictionary = dict()

    for result in results:
        precipitation_dictionary[str(result[0])] = float(result[1])

    #close session
    session.close()

    #return JSON
    return jsonify(precipitation_dictionary)

@app.route("/api/v1.0/stations")
def stations():
    """Return the stations in the database"""

    #create a session
    session = Session(engine)

    #query passengers
    results = session.query(Stations_Table.station, Stations_Table.name).all()

    #save query to a list of dictionaries
    station_list = [{"station_id": str(result[0]), "name": str(result[1])} for result in results]

    session.close()

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def temperature():
    """Temperature Most Active Stations"""

    #create session
    session = Session(engine)

    results = session.query(Measurements_Table.date, Measurements_Table.tobs).\
        filter(Measurements_Table.station == most_active_station).\
        filter(Measurements_Table.tobs != None).\
        filter(Measurements_Table.date >= one_year_ago).\
        order_by(Measurements_Table.date).all()
    
    # save the query to a list of dictionaries
    tobs_list = [{"date": str(result[0]), "temperature": float(result[1])} for result in results]

    session.close()

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def temperature_from(start):
    """Min, average, and max temperatures after a specific date"""

    #convert iso string to date object
    start_date = dt.date.fromisoformat(start)

    #create session to db
    session = Session(engine)

    results = session.query(func.min(Measurements_Table.tobs),\
                            func.avg(Measurements_Table.tobs),\
                            func.max(Measurements_Table.tobs)).\
                            filter(Measurements_Table.date >= start_date).all()
        
    
    tobs_list_results = [float(results[0][0]), float(results[0][1]), float(results[0][2])]

    #close session
    session.close()

    return jsonify(tobs_list_results)

@app.route("/api/v1.0/<start>/<end>")
def temperature_between(start, end):
    """Min, average, and max temperature between two dates"""
    
    # convert strings to datetime objects
    start_date = dt.date.fromisoformat(start)
    end_date = dt.date.fromisoformat(end)
    
    #create session
    session = Session(engine)
    
    #query
    results = session.query(func.min(Measurements_Table.tobs),\
                            func.avg(Measurements_Table.tobs),\
                            func.max(Measurements_Table.tobs)).\
                            filter(Measurements_Table.date >= start_date).\
                            filter(Measurements_Table.date <= end_date).all()
    tobs_list_results = [float(results[0][0]), float(results[0][1]), float(results[0][2])]
    
    # Close the session
    session.close()
    
    #return query
    return jsonify(tobs_list_results)


if __name__ == '__main__':
    app.run(debug=True, port=5002)
                                

