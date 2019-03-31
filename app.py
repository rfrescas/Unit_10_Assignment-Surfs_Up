from flask import Flask, jsonify
import datetime as dt
import numpy as np
import pandas as pd

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, distinct

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

Base.classes.keys()

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

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
           f"Available Routes:<br/>"
           f"/api/v1.0/precipitation<br/>"
           f"/api/v1.0/stations<br/>"
           f"/api/v1.0/tobs<br/>"
           f"/api/v1.0/start_date<br/>"
           f"/api/v1.0/start_date/end_date"
       )


@app.route("/api/v1.0/precipitation")
def precipitation():
       session = Session(engine)
       
       sel = [(Measurement.date).label("Date"), (Measurement.prcp).label("Percipitation")]

       max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
       max_date_dt = pd.to_datetime(max_date)

       date_year_back = max_date_dt - dt.timedelta(days=365)

       year_back_str = date_year_back.strftime("%Y-%m-%d")[0]

       year_data = session.query(*sel).\
                filter(Measurement.date >= year_back_str).\
                order_by(Measurement.date).\
                all()

       precipitation_dict = dict(year_data)

       return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
       session = Session(engine)

       active_stations = session.query(distinct(Measurement.station)).all()

       return jsonify(active_stations)

@app.route("/api/v1.0/tobs")
def tobs():
       session = Session(engine)

       max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
       max_date_dt = pd.to_datetime(max_date)

       date_year_back = max_date_dt - dt.timedelta(days=365)

       year_back_str = date_year_back.strftime("%Y-%m-%d")[0]

       year_data = session.query(Measurement.tobs).\
                filter(Measurement.date >= year_back_str).\
                order_by(Measurement.date).\
                all()

       return jsonify(year_data)

@app.route("/api/v1.0/<start_date>")
def start(start_date):
       session = Session(engine)
       
       sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
       
       result = session.query(*sel).\
              filter(Measurement.date >= start_date).\
              all()
       
       return jsonify(result)

@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end(start_date, end_date):
       session = Session(engine)
       
       sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
       
       result = session.query(*sel).\
              filter(Measurement.date >= start_date).\
              filter(Measurement.date <= end_date).\
              all()
       
       return jsonify(result)
 
if __name__ == "__main__":
   app.run(debug=True)