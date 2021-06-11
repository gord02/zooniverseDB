from sanic import Sanic

# allows sanic to and mongoDB to work together 
import motor.motor_asyncio
import asyncio

# Blueprint is a way to simplify the process of routing
from sanic import Blueprint
# allows for the conversion of data to json
from sanic.response import json as sanic_json
import json

# imports simple way of applying doc string through framework sanic
from sanic_openapi import doc

import requests
import chime_frb_api
from chime_frb_api import frb_master


# imports schemas
import schema


# NOTE: The URL Prefix for your backend has to be the name of the backend
# blueprint here works similar to how app is created by the flask framework enabling you to route using app.route
blueprint = Blueprint("zooniverse")
# blueprint = Blueprint("zooniverse", url_prefix="/")

# Create a new connection to a single MongoDB instance at host:port.
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:8000")

# # Connection to a database 
db = client['zooniverseDB']

# app = Sanic("My Hello, world app")
app = Sanic(__name__)
app.blueprint(blueprint)

# Accessing the CHIME/FRB databases by first generating a token
# master = chime_frb_api.frb_master.FRBMaster(username= 'gordon')
# master.API.authorize()
# auth = {"authorization": master.API.access_token}
# master.events.get_event(65540476)
# {'beam_numbers': [185, 1185, 2185, 3185],
#  'event_type': 'EXTRAGALACTIC',
#  'fpga_time': 271532193792,
#  'id': 65540476
# }
# Querying frb master for events paths
# event_path= requests.get("https://frb.chimenet.ca/frb-master/v1/events/datapaths/147503727", headers=auth)
# path = event_path.json()
# print("This is the path: ", path)

# @app.route('/')
# async def test(request):
#     try:
#         print(request)
#         # client = request.app.mongo.client
#         docs = db.events.find()

#         # await client.zooniverse.events.find()
#         # await client.zooniverse.events.insert_one(request.json)
#         return json(True)
#     except Exception as e:
#         print(str(e))
#         raise

# ====================
@app.get("/")
async def test(request):
    return json({ "hello": "world" })
@blueprint.get("/okay")
async def add_event(request):
    return 'ok'

# Stores new events in database
@app.route("/", methods=['POST'])
def addEventToDB(request):
    if request.method == "POST":
        event_path= requests.get("https://frb.chimenet.ca/frb-master/v1/events/datapaths/147503727", headers=auth)
async def test(request):
    return json({ "hello": "world" })

# display event data path
# @app.route("/", methods=['POST'])
# def addEventToDB():
#     if request.method == "POST":
#         event_path= requests.get("https://frb.chimenet.ca/frb-master/v1/events/datapaths/147503727", headers=auth)
# async def test(request):
    # return json({ "hello": "world" })
# why in this route am I adding to the database? should this be named, just add events to database?
@doc.summary("Add event to the transfer list to send to zooniverse.")
@doc.consumes(schema.Event)
@blueprint.post("/event")
async def add_event(request):
    try:

        client = request.app.mongo.client
        await client.zooniverse.events.insert_one(request.json)

        # await db.events.insert_one(request.json)

        return json(True)
    except Exception as e:
        print(str(e))
        raise


@doc.summary("Fetch event")
@doc.consumes(schema.Event)
@blueprint.get("/event/<event_no>")
async def get_event(request, event_no):
    try:
        event_path= requests.get("https://frb.chimenet.ca/frb-master/v1/events/datapaths/147503727", headers=auth)
        client = request.app.mongo.client
        items = []
        docs = db.events.find(
            # when you execute find() method it displays all fields of a document. To limit this, you need to set a list of fields with value 1 or 0. 1 is used to show the field while 0 is used to hide the fields.
            {"event": int(event_no)}, projection={"_id": 0}
        )
        async for d in docs:
            items.append(d)
        return json(items)
    except Exception as e:
        print(str(e))
        raise


@doc.summary("Fetch all events")
@doc.consumes(schema.Event)
@blueprint.get("/events")
async def fetch_all_events(request):
    try:
        client = request.app.mongo.client
        items = []
        docs = client.zooniverse.events.find({}, projection={"_id": 0})
        async for d in docs:
            items.append(d)
        return json(items)
    except Exception as e:
        print(str(e))
        raise


@doc.summary("Update event.")
@doc.consumes(schema.Event)
@blueprint.put("/event/<event_no>")
async def update_event(request, event_no):
    print(request.json)
    try:
        client = request.app.mongo.client
        client.zooniverse.events.find_one_and_update(
            {"event": int(event_no)}, {"$set": request.json}, projection={"_id": 0}
        )
        return json(True)
    except Exception as e:
        print(str(e))
        raise


@doc.summary("Delete event")
@doc.consumes(schema.Event)
@blueprint.delete("/event/<event_no>")
async def delete_event(request, event_no):
    try:
        client = request.app.mongo.client
        client.zooniverse.events.delete_one({"event": int(event_no)})
        return json(True)
    except Exception as e:
        print(str(e))
        raise


@doc.summary("Fetch events to transfer to zooniverse.")
@doc.produces([schema.Event])
@blueprint.get("/events-for-transfer")
async def fetch_events_for_transfer(request):
    try:
        client = request.app.mongo.client
        items = []
        docs = client.zooniverse.events.find(
            {"transfer_status": {"$in": ["INCOMPLETE", "FAILED"]}},
            projection={"_id": 0},
        )
        async for d in docs:
            items.append(d)
        return json(items)
    except Exception as e:
        print(str(e))
        raise


@doc.summary("Fetch events to transfer to cleanup.")
@doc.produces([schema.Event])
@blueprint.get("/events-for-cleanup")
async def fetch_events_for_cleanup(request):
    try:
        client = request.app.mongo.client
        items = []
        docs = client.zooniverse.events.find(
            {"transfer_status": "COMPLETE", "zooniverse_classification": "BAD"},
            projection={"_id": 0},
        )
        async for d in docs:
            items.append(d)
        return json(items)
    except Exception as e:
        print(str(e))
        raise


@doc.summary("Fetch events for expert verification.")
@doc.produces([schema.Event])
@blueprint.get("/events-for-experts")
async def fetch_events_for_experts(request):
    try:
        client = request.app.mongo.client
        items = []
        docs = client.zooniverse.events.find(
            {
                "zooniverse_classification": "GOOD",
                "expert_classification": "INCOMPLETE",
            },
            projection={"_id": 0},
        )
        async for d in docs:
            items.append(d)
        return json(items)
    except Exception as e:
        print(str(e))
        raise


@doc.summary("Add zooniverse classification")
@blueprint.put("/zooniverse-classification/<event_no>/<classification>")
async def zooniverse_classification(request, event_no, classification):
    assert classification.upper() in ["GOOD", "BAD", "INCOMPLETE"]
    try:
        client = request.app.mongo.client
        client.zooniverse.events.find_one_and_update(
            {"event": int(event_no)},
            {"$set": {"zooniverse_classification": classification.upper()}},
            projection={"_id": 0},
        )
        return json(True)
    except Exception as e:
        print(str(e))
        raise


@doc.summary("Add expert classification")
@blueprint.put("/expert-classification/<event_no>/<classification>")
async def expert_classification(request, event_no, classification):
    assert classification.upper() in ["GOOD", "BAD", "INCOMPLETE"]
    try:
        client = request.app.mongo.client
        client.zooniverse.events.find_one_and_update(
            {"event": int(event_no)},
            {"$set": {"expert_classification": classification.upper()}},
            projection={"_id": 0},
        )
        return json(True)
    except Exception as e:
        print(str(e))
        raise

@doc.summary("Upload zooniverse classification report")
@doc.produces([schema.ZooniverseClassificationReport])
@blueprint.post("/classifications")
async def upload_classification_report(request):
    return json("Hello from zooniverse 🦧")
# =============
# @doc.consumes(schema.Event)
@app.post("/v1/zooniverse/transfer_event")
@doc.summary("CHIME/FRB event data is being sent to server so that it can be stored in zooniverse database")
async def get_event_data_from_CHIME(request):
    try:
        req = request.json
        data_dump = json.dumps(req)
        data = json.loads(data_dump)
        event_number = data["event_number"]
        dm_value = data["dm"]
        snr_value = data["snr"]
        data_path = data["data_path"]
        return  sanic_json(True)
    #     # code to add to database here

    except Exception as error:
        print(str(error))
        return  sanic_json(False)
        raise

if __name__ == '__main__':
    app.run(debug=True)
