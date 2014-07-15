import os
import requests
import ujson as json
from flask import Flask, Response, jsonify, request, safe_join
from shapely.geometry import shape


app = Flask(__name__)
app.debug = True

# Get the list of directories from the data directory
locations_list = os.walk('data').next()[1]
# A dictionary, keyed by location/dir, with a list of types/files
# (without the file extension)
types_by_location = dict((location, [os.path.splitext(filename)[0] for filename in os.walk(os.path.join('data', location)).next()[2]])
    for location in locations_list)


@app.route('/api/v1')
def locations_route():
    return jsonify(types_by_location)


@app.route('/api/v1/<location>')
def types_route(location):
    return Response(json.dumps(types_by_location.get(location)),  mimetype='application/json')


def get_file_data(location, type):
    types_list = types_by_location.get(location)

    # Do we know about this type in this location?
    if types_list and type in types_list:
        # Build the filename
        filename = safe_join(os.path.join('data', location), type + '.json')
        # Open and read the file
        with open(filename, 'r') as myfile:
            return myfile.read()


def get_place_region(place_geojson, regions_geojson):
    place_geom = shape(place_geojson['geometry'])

    for feature in regions_geojson['features']:
        region_poly = shape(feature['geometry'])
        if region_poly.contains(place_geom):
            return feature


def update_place(place_geojson, properties):
    url = place_geojson['properties']['url'] + '?include-private'
    place_geojson['properties'].update(properties)

    resp = requests.put(url, data=json.dumps(place_geojson),
      headers={"Content-Type": "application/json", "Accept": "application/json"},
      auth=('user_here', 'pw_here'))

    return resp


@app.route('/api/v1/<location>/<type>', methods=['GET', 'POST'])
def type_route(location, type):
    geojson_str = get_file_data(location, type)

    if request.method == 'POST':
        place_geojson = json.loads(request.data)
        region_geojson = get_place_region(place_geojson, json.loads(geojson_str))
        region_attrs = region_geojson['properties']

        update_place(place_geojson, region_attrs)

        return Response(json.dumps(region_attrs),  mimetype='application/json')
    else:
        return Response(geojson_str,  mimetype='application/json')


if __name__ == '__main__':
    app.run()
