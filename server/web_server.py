from flask import Flask, send_from_directory, request
from flask_restful import Resource, Api
from os.path import join

import sys
import sqlite3


def get_sensor_data(node, sensor, since_time=None, limit=500):
    with sqlite3.connect('data.db') as conn:
        cur = conn.cursor()
        limit = min(500, limit)

        condition = f"WHERE node = '{node}' and sensor = '{sensor}'"
        if since_time is not None:
            condition += f" and timestamp > {since_time}"

        rows = list(cur.execute(
            f"SELECT * FROM sensor_data " + condition +
            f"ORDER BY timestamp DESC LIMIT {limit}"))
        return rows


def get_threat_data(node, threat, min_level=None, since_time=None, limit=500):
    with sqlite3.connect('data.db') as conn:
        cur = conn.cursor()
        limit = min(500, limit)

        condition = f"WHERE node = '{node}' and threat = '{threat}'"

        if since_time is not None:
            condition += f" and timestamp > {since_time}"

        if min_level is not None:
            condition += f" and new_level >= {min_level}"

        rows = list(cur.execute(
            f"SELECT * FROM threats " + condition +
            f"ORDER BY timestamp DESC LIMIT {limit}"))
        return rows


class Node(Resource):
    def get(self, node, sensor, time=None, limit=1):
        return list(
            map(lambda row: {
                "timestamp": row[0],
                "value": row[1]
            }, get_sensor_data(node, sensor, since_time=time, limit=limit)))


class Threat(Resource):
    def get(self, node = None, threat = None, min_level=None, time=None, limit=1):
        return list(
            map(lambda row: {
                "timestamp": row[0],
                "node": row[1],
                "threat": row[2],
                "old_level": row[3],
                "new_level": row[4]
            }, get_threat_data(node, threat, min_level=min_level, since_time=time, limit=limit)))


# main route

def create_app():
    app = Flask(__name__, static_folder="../client/dist", static_url_path="")
    api = Api(app)

    api.add_resource(Node,
                     "/api/sensor/<string:node>/<string:sensor>/",
                     "/api/sensor/<string:node>/<string:sensor>/limit:<int:limit>",
					 "/api/sensor/<string:node>/<string:sensor>/since:<int:time>",
					 "/api/sensor/<string:node>/<string:sensor>/since:<int:time>/limit:<int:limit>")
	
	api.add_resource(Threat,
                     "/api/threat/limit:<int:limit>",
                     "/api/threat/minlevel:<int:min_level>/limit:<int:limit>",
                     "/api/threat/<string:node>/<string:threat>/",
                     "/api/threat/<string:node>/<string:threat>/limit:<int:limit>",
                     "/api/threat/<string:node>/<string:threat>/minlevel:<int:min_level>/",
                     "/api/threat/<string:node>/<string:threat>/minlevel:<int:min_level>/limit:<int:limit>",
                     "/api/threat/<string:node>/<string:threat>/since:<int:time>",
					 "/api/threat/<string:node>/<string:threat>/since:<int:time>/limit:<int:limit>",
					 "/api/threat/<string:node>/<string:threat>/since:<int:time>/minlevel:<int:min_level>/",
					 "/api/threat/<string:node>/<string:threat>/since:<int:time>/minlevel:<int:min_level>/limit:<int:limit>")

    return app


app = create_app()


@app.route('/')
def index():
    return app.send_static_file('index.html')


if __name__ == "__main__":
    app.run(debug=True)

#    host='0.0.0.0', port=80, debug=False
