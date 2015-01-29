Shareabouts Region Service
==========================

API for identifying and updating the region of a Shareabouts place. 

You can attach a webhook to a Shareabouts dataset. Adding the region service allows you to add location information to each submitted place, for example neighborhood or borough.

Deploy 
----------------

This repo contains the necessary files to deploy the region service on Heroku. 


Uploading regions 
------------------

To add a new region, prepare a geojson file with the `.json` file extension. QGIS can export shapefiles to geojson. Make sure the file is projected as WGS (lat/lon), not a local projection in different units.

Add the file to a city directory in your local repo of the region service. Deploy to production.

Check that the file is deployed by visiting the endpoint in your browser. If the file is in `/data/nyc/districts.json`, visit `region-service-url/api/v1/city/districts`.

Configuring a Shareabouts dataset to use the region service
-----------------

Webhooks are configured at `API-SERVER-URL/admin/sa_api_v2/webhook/`.

Choose the dataset, event (currently `On Add` is the only option), and the URL of your region file, e.g. `https://shareabouts-region-service.herokuapp.com/api/v1/nyc/nybb`.

After this is set up, all new places in the selected dataset will be given all attributes of the region they intersect. For example, if you have `id`, `name`, and `representative` fields in the region file, those attributes will be added to the place attributes. 
