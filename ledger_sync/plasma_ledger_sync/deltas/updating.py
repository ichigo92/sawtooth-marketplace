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
# -----------------------------------------------------------------------------

import sys

from plasma_addressing.addresser import address_is
from plasma_addressing.addresser import AddressSpace


TABLE_NAMES = {
    AddressSpace.AGENT: 'agents',
    AddressSpace.ASSET: 'assets',
    AddressSpace.TASK: 'tasks',
    AddressSpace.ORDER: 'orders'
}

SECONDARY_INDEXES = {
    AddressSpace.AGENT: 'public_key',
    AddressSpace.ASSET: 'asset_id',
    AddressSpace.TASK: 'task_id',
    AddressSpace.ORDER: 'order_id'
}


def get_updater(database, block_num):
    """Returns an updater function, which can be used to update the database
    appropriately for a particular address/data combo.
    """
    return lambda adr, rsc: _update(database, block_num, adr, rsc)


def _update(database, block_num, address, resource):
    data_type = address_is(address)

    resource['start_block_num'] = block_num
    resource['end_block_num'] = sys.maxsize

    try:
        table_query = database.get_table(TABLE_NAMES[data_type])
        seconday_index = SECONDARY_INDEXES[data_type]
    except KeyError:
        raise TypeError('Unknown data type: {}'.format(data_type))

    query = table_query\
        .get_all(resource[seconday_index], index=seconday_index)\
        .filter({'end_block_num': sys.maxsize})\
        .update({'end_block_num': block_num})\
        .merge(table_query.insert(resource).without('replaced'))

    return database.run_query(query)
