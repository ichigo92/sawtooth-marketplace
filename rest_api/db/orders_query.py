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

import rethinkdb as r
from rethinkdb.errors import ReqlNonExistenceError

from api.errors import ApiBadRequest

from db.common import fetch_latest_block_num
# from db.common import parse_rules


async def fetch_all_order_resources(conn, query_params):
    return await r.table('orders')\
        .filter((fetch_latest_block_num() >= r.row['start_block_num'])
                & (fetch_latest_block_num() < r.row['end_block_num']))\
        .filter(query_params)\
        .map(lambda order: (order['final'] == "").branch(
            order.without('final'), order))\
        .map(lambda order: (order['description'] == "").branch(
            order.without('description'), order))\
        .map(lambda order: order.merge(
            {'quantity': order['quantity']}))\
        .map(lambda order: (order['task_id'] == "").branch(
            order.without('task_id'), order))\
        .map(lambda order: (order['actual_cost'] == "").branch(
            order,
            order.merge({'actual_cost': order['actual_cost']})))\
        .without('delta_id', 'start_block_num', 'end_block_num',
                 'description', 'task_id')\
        .coerce_to('array').run(conn)


async def fetch_order_resource(conn, order_id):
    try:
        return await r.table('orders')\
            .get_all(order_id, index='id')\
            .max('start_block_num')\
            .do(lambda offer: (offer['final'] == "").branch(
                offer.without('final'), offer))\
            .do(lambda offer: (offer['description'] == "").branch(
                offer.without('description'), offer))\
            .merge({'sourceQuantity': r.row['quantity']})\
            .do(lambda offer: (offer['quantity'] == "").branch(
                offer.without('task_id'), offer))\
            .do(lambda offer: (offer['actual_cost'] == "").branch(
                offer,
                offer.merge({'actual_cost': offer['actual_cost']})))\
            .do(lambda offer: (offer['rules'] == []).branch(
                offer, offer.merge(parse_rules(offer['rules']))))\
            .without('delta_id', 'start_block_num', 'end_block_num',
                     'description', 'task_id')\
            .run(conn)
    except ReqlNonExistenceError:
        raise ApiBadRequest("No order with the id {} exists".format(offer_id))
