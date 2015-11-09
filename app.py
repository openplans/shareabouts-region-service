from __future__ import print_function
import os
import requests
import ujson as json
from flask import Flask, Response, jsonify, request, safe_join, abort
from raven.contrib.flask import Sentry
from shapely.geometry import shape


def init_settings():
    try:
        app.config.from_pyfile('local_settings.py')
    except:
        print('No settings file found.')

    # Environment overrides
    access_token = os.environ.get('ACCESS_TOKEN')
    if (access_token):
        app.config['ACCESS_TOKEN'] = access_token

    Sentry(app)


# Init
app = Flask(__name__)
init_settings()

# Get the list of directories from the data directory
locations_list = next(os.walk('data'))[1]
# A dictionary, keyed by location/dir, with a list of types/files
# (without the file extension)
types_by_location = dict((location, [os.path.splitext(filename)[0] for filename in next(os.walk(os.path.join('data', location)))[2]])
    for location in locations_list)


@app.route('/api/v1')
def locations_route():
    return jsonify(types_by_location)


@app.route('/api/v1/<location>')
def types_route(location):
    if location not in locations_list:
        abort(404)

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
    else:
        return None


def get_place_region(place_geojson, regions_geojson):
    place_geom = shape(place_geojson['geometry'])

    for feature in regions_geojson['features']:
        region_poly = shape(feature['geometry'])
        if region_poly.contains(place_geom):
            return feature

    return None


def update_place(place_geojson, properties):
    url = place_geojson['properties']['url'] + '?include_private'

    # Ensure https
    if url.startswith('http://'):
        url = url.replace('http://', 'https://')

    place_geojson['properties'].update(properties)

    resp = requests.put(url, data=json.dumps(place_geojson),
      headers={"Content-Type": "application/json", "Accept": "application/json",
      "x-shareabouts-silent": "true",
      "Authorization": "Bearer " + app.config.get('ACCESS_TOKEN')})

    return resp


@app.route('/api/v1/<location>/<type>', methods=['GET', 'POST'])
def type_route(location, type):
    geojson_str = get_file_data(location, type)

    # No match for location/type
    if not geojson_str:
        abort(404)

    if request.method == 'POST':
        # Parse the place geojson
        place_geojson = json.loads(request.data)
        # Get the containing region
        region_geojson = get_place_region(place_geojson, json.loads(geojson_str))

        if region_geojson:
            region_attrs = region_geojson['properties']
            # Update the existing place (updates the API)
            resp = update_place(place_geojson, region_attrs)
            # Respond with the updated place
            return Response(resp.text,  mimetype='application/json')
        else:
            # No containing region was found
            abort(404)
    # Get the region for a simple lat/lng, via a GET
    elif request.args.get('ll'):
        ll = request.args.get('ll')

        try:
            lat, lng = ll.split(',')
        except:
            abort(400)

        # Create the geojson
        place_geojson = json.loads('{"geometry": { "type": "Point", "coordinates": [%s, %s] }}' % (lng, lat,))
        # Get the containing region

        region_geojson = get_place_region(place_geojson, json.loads(geojson_str))

        if region_geojson:
            region_attrs = region_geojson['properties']
            resp = json.dumps(region_attrs)

            callback = request.args.get('callback')
            if callback:
                resp = '%s(%s);' % (callback, resp,)

            resp = Response(resp,  mimetype='application/json')
            resp.headers['Access-Control-Allow-Origin'] = '*'
            resp.headers['Access-Control-Allow-Methods'] = 'GET,HEAD,OPTIONS'
            return resp
        else:
            abort(404)
    else:
        return Response(geojson_str,  mimetype='application/json')


if __name__ == '__main__':
    app.run()
