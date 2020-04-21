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
from rethinkdb import ReqlNonExistenceError

from api.errors import ApiInternalError

r = RethinkDB()


VAL_TYPE_INT = r.expr([
    "REQUIRE_SOURCE_QUANTITIES", "REQUIRE_TARGET_QUANTITIES"
])


def fetch_latest_block_num():
    try:
        return r.table('blocks')\
            .max(index='block_num')\
            .get_field('block_num')
    except ReqlNonExistenceError:
        raise ApiInternalError('No block data found in state')


def fetch_orders(order_ids):
    return r.table('orders')\
        .get_all(r.args(order_ids), index='id')\
        .filter(lambda order: (
            fetch_latest_block_num() >= order['start_block_num'])
                & (fetch_latest_block_num() < order['end_block_num']))\
        .map(lambda order: (order['order_type'] == "").branch(
            order.without('order_type'), order))\
        .map(lambda order: (order['description'] == "").branch(
            order.without('description'), order))\
        .without('start_block_num', 'end_block_num', 'delta_id', 'agent')\
        .coerce_to('array')


def parse_rules(rules):
    return r.expr(
        {
            'rules': rules.map(lambda rule: (
                rule['value'] == bytes('', 'utf-8')).branch(
                    rule.without('value'),
                    rule.merge(
                        {
                            'value': _value_to_array(rule)
                        })))
        })


def _value_to_array(rule):
    val_array = rule['value'].coerce_to('string').split(",")
    return VAL_TYPE_INT.contains(rule['type']).branch(
        val_array.map(lambda val: val.coerce_to('number')), val_array)
