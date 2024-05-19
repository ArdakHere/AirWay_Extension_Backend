from flask import Flask, request, jsonify
from back_kolesa import *
from back_krisha import *

app = Flask(__name__)

@app.route('/analyze/kolesa', methods=['POST'])
def analyze_kolesa():
    data = request.json
    return jsonify("")

@app.route('/analyze/krisha', methods=['POST'])
def analyze_krisha():
    data = request.json
    coords = data.get('coords')

    result: dict = access_metrics(coords)

    parks = make_2gis_request_and_return_object_count(
        "6d76f6d4-3d4c-4164-8605-84db52d0425b",
        coords.get('lat'),
        coords.get('lon'),
        300,
        "парк")
    ev_chargers = make_2gis_request_and_return_object_count(
        "6d76f6d4-3d4c-4164-8605-84db52d0425b",
        coords.get('lat'),
        coords.get('lon'),
        300,
        "парк")

    result.update({"num_of_parks": parks, "num_of_ev_chargers": ev_chargers})

    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
