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

from rethinkdb import RethinkDB
from rethinkdb.errors import ReqlNonExistenceError

from api.errors import ApiBadRequest

from db.common import fetch_orders
from db.common import fetch_latest_block_num

r = RethinkDB()


async def fetch_all_agent_resources(conn):
    return await r.table('agents')\
        .filter((fetch_latest_block_num() >= r.row['start_block_num'])
                & (fetch_latest_block_num() < r.row['end_block_num']))\
        .map(lambda agents: agents.merge(
            {'publicKey': agents['public_key']}))\
        .map(lambda account: account.merge(
            {'orders': fetch_orders(account['orders'])}))\
        .map(lambda agents: (agents['name'] == "").branch(
            agents.without('name'), agents))\
        .map(lambda agents: (agents['description'] == "").branch(
            agents.without('description'), agents))\
        .without('public_key', 'delta_id',
                 'start_block_num', 'end_block_num')\
        .coerce_to('array').run(conn)


async def fetch_agent_resource(conn, public_key, auth_key):
    try:
        return await r.table('agents')\
            .get_all(public_key, index='public_key')\
            .max('start_block_num')\
            .merge({'publicKey': r.row['public_key']})\
            .merge({'orders': fetch_orders(r.row['orders'])})\
            .do(lambda agent: (r.expr(auth_key).eq(public_key)).branch(
                agent.merge(_fetch_email(public_key)), agent))\
            .do(lambda agent: (agent['name'] == "").branch(
                agent.without('name'), agent))\
            .do(lambda agent: (agent['description'] == "").branch(
                agent.without('description'), agent))\
            .without('public_key', 'delta_id',
                     'start_block_num', 'end_block_num')\
            .run(conn)
    except ReqlNonExistenceError:
        raise ApiBadRequest(
            "No account with the public key {} exists".format(public_key))


def _fetch_email(public_key):
    return r.table('auth')\
        .get_all(public_key, index='public_key')\
        .pluck('email')\
        .coerce_to('array')[0]
