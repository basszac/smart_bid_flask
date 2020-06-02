from flask import Flask
from flask_restplus import Resource, Api, fields
import redis
import os
import json

app = Flask(__name__)
api = Api(
    app,
    version='1.0',
    title='SmartBid API',
    description='Back end for the SmartBid application',
)

ns = api.namespace('v1', description='Application operations')

todo = api.model('CustomerData', {
    'entity_id': fields.String(
        readonly=True,
        description="The entity's unique identifier"
    ),
    'data': fields.String(
        required=True,
        description='The data payload')
})

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_DB = os.getenv('REDIS_DB')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

assert REDIS_HOST and REDIS_PORT and REDIS_DB and REDIS_PASSWORD

r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD
)


@ns.route('/customer/<string:entity_id>')
class CustomerData(Resource):
    def get(self, entity_id):
        '''Retrieve an entity's data from the database'''
        redis_payload = r.get(entity_id)
        if redis_payload:
            decoded = redis_payload.decode()

            return json.loads(decoded)
        else:
            api.abort(404, f"Entity '{ entity_id }' doesn't exist")

    @ns.expect(todo)
    @ns.response(201, 'Entity entered')
    def post(self, entity_id):
        '''Create a new entity (or modify existing) and add data'''
        r.set(entity_id, json.dumps(api.payload))
        return entity_id, 201

    @ns.response(204, 'Entity deleted')
    def delete(self, entity_id):
        '''Delete all data for an entity'''
        r.delete(entity_id)
        return entity_id, 204


@ns.route('/list_entities')
class EntityList(Resource):
    def get(self):
        '''List all entities in the database'''
        keys = r.keys()
        decoded_list = []
        for i in keys:
            decoded_list.append(i.decode())
        return decoded_list
