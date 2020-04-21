# Copyright 2017 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

import bcrypt

from itsdangerous import BadSignature

from sanic import Blueprint
from sanic import response

from sawtooth_signing import CryptoFactory

from api.authorization import authorized
from api import common
from api import messaging
from api.errors import ApiBadRequest
from api.errors import ApiInternalError

from db import agents_query
from db import auth_query

from plasma_transaction import transaction_creation


AGENTS_BP = Blueprint('agents')


@AGENTS_BP.post('agents')
async def create_agent(request):
    """Creates a new Agent and corresponding authorization token"""
    required_fields = ['email', 'password']
    common.validate_fields(required_fields, request.json)

    private_key = request.app.config.CONTEXT.new_random_private_key()
    signer = CryptoFactory(request.app.config.CONTEXT).new_signer(private_key)
    public_key = signer.get_public_key().as_hex()

    auth_entry = _create_auth_dict(
        request, public_key, private_key.as_hex())
    await auth_query.create_auth_entry(request.app.config.DB_CONN, auth_entry)

    agent = _create_agent_dict(request.json, public_key)

    batches, batch_id = transaction_creation.create_agent(
        txn_key=signer,
        batch_key=request.app.config.SIGNER,
        name=agent.get('name'),
        description=agent.get('description'))

    await messaging.send(
        request.app.config.VAL_CONN,
        request.app.config.TIMEOUT,
        batches)

    try:
        await messaging.check_batch_status(
            request.app.config.VAL_CONN, batch_id)
    except (ApiBadRequest, ApiInternalError) as err:
        await auth_query.remove_auth_entry(
            request.app.config.DB_CONN, request.json.get('email'))
        raise err

    token = common.generate_auth_token(
        request.app.config.SECRET_KEY,
        agent.get('email'),
        public_key)

    return response.json(
        {
            'authorization': token,
            'agent': agent
        })


@AGENTS_BP.get('agents')
async def get_all_agents(request):
    """Fetches complete details of all Agents in state"""
    agent_resources = await agents_query.fetch_all_agent_resources(
        request.app.config.DB_CONN)
    return response.json(agent_resources)


@AGENTS_BP.get('agents/<key>')
async def get_agent(request, key):
    """Fetches the details of particular Agent in state"""
    try:
        auth_key = common.deserialize_auth_token(
            request.app.config.SECRET_KEY,
            request.token).get('public_key')
    except (BadSignature, TypeError):
        auth_key = None
    agent_resource = await agents_query.fetch_agent_resource(
        request.app.config.DB_CONN, key, auth_key)
    return response.json(agent_resource)


@AGENTS_BP.patch('agents')
@authorized()
async def update_agent_info(request):
    """Updates auth information for the authorized agent"""
    token = common.deserialize_auth_token(
        request.app.config.SECRET_KEY, request.token)

    update = {}
    if request.json.get('password'):
        update['hashed_password'] = bcrypt.hashpw(
            bytes(request.json.get('password'), 'utf-8'), bcrypt.gensalt())
    if request.json.get('email'):
        update['email'] = request.json.get('email')

    if update:
        updated_auth_info = await auth_query.update_auth_info(
            request.app.config.DB_CONN,
            token.get('email'),
            token.get('public_key'),
            update)
        new_token = common.generate_auth_token(
            request.app.config.SECRET_KEY,
            updated_auth_info.get('email'),
            updated_auth_info.get('publicKey'))
    else:
        updated_auth_info = await agents_query.fetch_agent_resource(
            request.app.config.DB_CONN,
            token.get('public_key'),
            token.get('public_key'))
        new_token = request.token

    return response.json(
        {
            'authorization': new_token,
            'agent': updated_auth_info
        })


def _create_agent_dict(body, public_key):
    keys = ['name', 'description', 'email']

    agent = {k: body[k] for k in keys if body.get(k) is not None}

    agent['publicKey'] = public_key
    agent['orders'] = []

    return agent


def _create_auth_dict(request, public_key, private_key):
    auth_entry = {
        'public_key': public_key,
        'email': request.json['email']
    }

    auth_entry['encrypted_private_key'] = common.encrypt_private_key(
        request.app.config.AES_KEY, public_key, private_key)
    auth_entry['hashed_password'] = bcrypt.hashpw(
        bytes(request.json.get('password'), 'utf-8'), bcrypt.gensalt())

    return auth_entry
