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

import enum
import hashlib


FAMILY_NAME = 'plasma'
FAMILY_VERSION = '0.1'

NS = hashlib.sha512(FAMILY_NAME.encode('utf-8')).hexdigest()[:6]


class AgentSpace(enum.IntEnum):
    START = 0
    STOP = 1


class AssetSpace(enum.IntEnum):
    START = 1
    STOP = 50


class OrderSpace(enum.IntEnum):
    START = 50
    STOP = 125


class TaskSpace(enum.IntEnum):
    START = 125
    STOP = 200


@enum.unique
class AddressSpace(enum.IntEnum):
    AGENT = 0
    ASSET = 1
    ORDER = 2
    TASK = 3

    OTHER_FAMILY = 100


def _hash(identifier):
    return hashlib.sha512(identifier.encode()).hexdigest()


def _compress(address, start, stop):
    return "%.2X".lower() % (int(address, base=16) % (stop - start) + start)


def make_asset_address(asset_id):
    full_hash = _hash(asset_id)
    return NAMESPACE + _compress(full_hash, AssetSpace.START, AssetSpace.STOP) + full_hash[:62]

def make_agent_address(agent_id):
    full_hash = _hash(agent_id)
    return NAMESPACE + _compress(full_hash, AgentSpace.START, AgentSpace.STOP) + full_hash[:62]

def make_order_address(order_id):
    full_hash = _hash(order_id)
    return NAMESPACE + _compress(full_hash, OrderSpace.START, OrderSpace.STOP) + full_hash[:62]

def make_task_address(task_id):
    full_hash = _hash(task_id)
    return NAMESPACE + _compress(full_hash, TaskSpace.START, TaskSpace.STOP) + full_hash[:62]


def _contains(num, space):
    return space.START <= num < space.STOP


def address_is(address):
    if address[:len(NAMESPACE)] != NAMESPACE:
        return AddressSpace.OTHER_FAMILY

    infix = int(address[6:8], 16)

    if _contains(infix, AgentSpace):
        result = AddressSpace.AGENT

    elif _contains(infix, AssetSpace):
        result = AddressSpace.ASSET

    elif _contains(infix, OrderSpace):
        result = AddressSpace.ORDER

    elif _contains(infix, TaskSpace):
        result = AddressSpace.TASK

    else:
        result = AddressSpace.OTHER_FAMILY

    return result
