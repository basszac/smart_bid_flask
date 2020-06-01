from flask import Flask
from flask_restplus import Resource, Api, fields
import redis
import os
import json

app = Flask(__name__)
api = Api(app, version='1.0', title='SmartBid API',
    description='Back end for the SmartBid application',
)

ns = api.namespace('v1', description='Application operations')

todo = api.model('CustomerData', {
    'customer_id': fields.String(readonly=True, description='The customer unique identifier'),
    'data': fields.String(required=True, description='The data payload')
})

r = redis.Redis(
    host='redis',
    port=6379,
    db=0
)

@ns.route('/customer/<string:entity_id>')
class CustomerData(Resource):
    def get(self, entity_id):
        redis_payload = r.get(entity_id)
        decoded = redis_payload.decode()

        return json.loads(decoded)

    @ns.expect(todo)
    def post(self, entity_id):
        r.set(entity_id, json.dumps(api.payload))


