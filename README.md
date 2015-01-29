Shareabouts Region Service
==========================

API for identifying and updating the region of a Shareabouts place. 

You can attach a webhook to a Shareabouts dataset. Adding the region service allows you to add location information to each submitted place, for example neighborhood or borough.

Configuring a Shareabouts dataset to use the region service
-----------------

Webhooks are configured at `API-SERVER-URL/admin/sa_api_v2/webhook/`.

Choose the dataset, event (currently `On Add` is the only option), and the URL of your region file, e.g. `https://shareabouts-region-service.herokuapp.com/api/v1/nyc/nybb`.

After this is set up, all new places in the selected dataset will be given all attributes of the region they intersect. For example, if you have `id`, `name`, and `representative` fields in the region file, those attributes will be added to the place attributes. 
