from sanic import Sanic
from sanic.response import json
# from sanic_mongo import Mongo
import motor.motor_asyncio
import asyncio

# Create a new connection to a single MongoDB instance at host:port.
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:8000")
# conn = AsyncIOMotorClient("mongodb://localhost:8000/zooniverseDB") 
# # Connection to a database 
db = client['zooniverseDB']

app = Sanic("My Hello, world app")

# mongo_uri = "mongodb://localhost:8000/zooniverseDB".format(
#     database='zooniverseDB',
#     port=8000,
#     host='localhost'
# )
# Mongo.SetConfig(app,test=mongo_uri)
# Mongo(app)



@app.route('/')
async def test(request):
    docs = await app.mongo['zooniverseDB'].find()
    return json({'hello': 'world'})




if __name__ == '__main__':
    app.run()
