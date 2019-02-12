from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify, request

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

app = Flask(__name__)

@app.route("/")
def home():
    return(
        f"<b>Available Routes:</b><br/><br/>"
        f"<b>Precipitation Data</b><br/>"
        f"Dictionary using date as the key and precipitation as the value.<br/>"
        f"/api/v1.0/precipitation<br/><br/>"
        f"<b>Station Data</b><br/>"
        f"Return a JSON list of stations from the dataset.<br/>"
        f"/api/v1.0/stations<br/><br/>"
        f"<b>Temperature Data</b><br/>"
        f"Dates and temperature observations from a year from the last data point.<br/>"
        f"/api/v1.0/tobs<br/><br/>"
        f"<b>Time Based Queries</b><br/>"
        f"Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date in YYYY-MM-DD format.<br/>"
        f"/api/v1.0/[START DATE]<br/><br/>"
        f"Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range in YYYY-MM-DD format.<br/>"
        f"/api/v1.0/[START DATE]/[END DATE]"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= "2010-01-01").\
        all()
    precip = [data]
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    data = session.query(Station.name, Station.station, Station.elevation).all()
    stationlist = []
    for result in data:
        row = {}
        row['name'] = result[0]
        row['station'] = result[1]
        row['elevation'] = result[2]
        stationlist.append(row)
    return jsonify(stationlist)

@app.route("/api/v1.0/tobs")
def temps():
    """Return a list of tobs for the previous year"""
    data = session.query(Station.name, Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= "2016-08-23").\
        all()
    templist = []
    for result in data:
        row = {}
        row["Date"] = result[1]
        row["Station"] = result[0]
        row["Temperature"] = int(result[2])
        templist.append(row)
        
    return jsonify(templist)

@app.route('/api/v1.0/<start>/')
def start_temp(start):
    # get the min/avg/max
    data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    templist = []
    for result in data:
        row = {}
        row['TMIN'] = result[0]
        row['TAVG'] = result[1]
        row['TMAX'] = result[2]
        templist.append(row)
    return jsonify(templist)

@app.route('/api/v1.0/<start>/<end>')
def range_temp(start, end):
 # get the min/avg/max
    data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start, Measurement.date <= end).all()
    templist = []
    for result in data:
        row = {}
        row['TMIN'] = result[0]
        row['TAVG'] = result[1]
        row['TMAX'] = result[2]
        templist.append(row)
    return jsonify(templist)

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    
@app.route('/shutdown')
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

if __name__ == '__main__':
    app.run(debug=True)