# Copyright 2018 Intel Corporation
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

import datetime
import time

from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction

from plasma_addressing import addresser

from plasma_processor.agent import agent_creation

from plasma_processor.asset import asset_creation
from plasma_processor.asset import asset_transfer
from plasma_processor.asset import asset_update

from plasma_processor.order import order_creation
from plasma_processor.order import order_update
from plasma_processor.order import order_transfer
from plasma_processor.order import order_accept
from plasma_processor.order import order_finalize

from plasma_processor.task import task_creation
from plasma_processor.task import task_update

from plasma_processor.payload import PlasmaPayload
from plasma_processor.state import PlasmaState


SYNC_TOLERANCE = 60 * 5
MAX_LAT = 90 * 1e6
MIN_LAT = -90 * 1e6
MAX_LNG = 180 * 1e6
MIN_LNG = -180 * 1e6


class PlasmaHandler(TransactionHandler):

    @property
    def family_name(self):
        return addresser.FAMILY_NAME

    @property
    def family_versions(self):
        return [addresser.FAMILY_VERSION]

    @property
    def namespaces(self):
        return [addresser.NS]

    def apply(self, transaction, context):

        payload = PlasmaPayload(transaction.payload)
        state = PlasmaState(context)

        # _validate_timestamp(payload.timestamp)

        if payload.is_create_agent():
            agent_creation.handle_agent_creation(
                payload.create_agent(),
                header = transaction.header,
                state = state)
        elif payload.is_create_asset():
            asset_creation.handle_asset_creation(
                payload.create_asset(),
                header = transaction.header,
                state = state)
        elif payload.is_update_asset():
            asset_update.handle_update_asset(
                payload.update_asset(),
                header = transaction.header,
                state = state)
        elif payload.is_transfer_asset():
            asset_transfer.handle_transfer_asset(
                payload.transfer_asset(),
                header = transaction.header,
                state = state)
        elif payload.is_create_order():
            order_creation.handle_order_creation(
                payload.create_order(),
                header = transaction.header,
                state = state)
        elif payload.is_transfer_order():
            order_transfer.handle_transfer_order(
                payload.transfer_order(),
                header = transaction.header,
                state = state)
        elif payload.is_update_order():
            order_update.handle_update_order(
                payload.update_order(),
                header = transaction.header,
                state = state)
        elif payload.is_accept_order():
            order_accept.handle_accept_order(
                payload.accept_order(),
                header = transaction.header,
                state = state)
        elif payload.is_finalize_order():
            order_finalize.handle_finalize_order(
                payload.finalize_order(),
                header = transaction.header,
                state = state)
        elif payload.is_create_task():
            task_creation.handle_task_creation(
                payload.create_task(),
                header = transaction.header,
                state = state)
        elif payload.is_update_task():
            task_update.handle_update_task(
                payload.update_task(),
                header = transaction.header,
                state = state)
        else:
            raise InvalidTransaction('Unhandled action')




def _create_record(state, public_key, payload):
    if state.get_agent(public_key) is None:
        raise InvalidTransaction('Agent with the public key {} does '
                                 'not exist'.format(public_key))

    if payload.data.record_id == '':
        raise InvalidTransaction('No record ID provided')

    if state.get_record(payload.data.record_id):
        raise InvalidTransaction('Identifier {} belongs to an existing '
                                 'record'.format(payload.data.record_id))

    _validate_latlng(payload.data.latitude, payload.data.longitude)

    state.set_record(
        public_key=public_key,
        latitude=payload.data.latitude,
        longitude=payload.data.longitude,
        record_id=payload.data.record_id,
        timestamp=payload.timestamp)


def _transfer_record(state, public_key, payload):
    if state.get_agent(payload.data.receiving_agent) is None:
        raise InvalidTransaction(
            'Agent with the public key {} does '
            'not exist'.format(payload.data.receiving_agent))

    record = state.get_record(payload.data.record_id)
    if record is None:
        raise InvalidTransaction('Record with the record id {} does not '
                                 'exist'.format(payload.data.record_id))

    if not _validate_record_owner(signer_public_key=public_key,
                                  record=record):
        raise InvalidTransaction(
            'Transaction signer is not the owner of the record')

    state.transfer_record(
        receiving_agent=payload.data.receiving_agent,
        record_id=payload.data.record_id,
        timestamp=payload.timestamp)


def _update_record(state, public_key, payload):
    record = state.get_record(payload.data.record_id)
    if record is None:
        raise InvalidTransaction('Record with the record id {} does not '
                                 'exist'.format(payload.data.record_id))

    if not _validate_record_owner(signer_public_key=public_key,
                                  record=record):
        raise InvalidTransaction(
            'Transaction signer is not the owner of the record')

    _validate_latlng(payload.data.latitude, payload.data.longitude)

    state.update_record(
        latitude=payload.data.latitude,
        longitude=payload.data.longitude,
        record_id=payload.data.record_id,
        timestamp=payload.timestamp)


def _validate_record_owner(signer_public_key, record):
    """Validates that the public key of the signer is the latest (i.e.
    current) owner of the record
    """
    latest_owner = max(record.owners, key=lambda obj: obj.timestamp).agent_id
    return latest_owner == signer_public_key


def _validate_latlng(latitude, longitude):
    if not MIN_LAT <= latitude <= MAX_LAT:
        raise InvalidTransaction('Latitude must be between -90 and 90. '
                                 'Got {}'.format(latitude/1e6))
    if not MIN_LNG <= longitude <= MAX_LNG:
        raise InvalidTransaction('Longitude must be between -180 and 180. '
                                 'Got {}'.format(longitude/1e6))


def _validate_timestamp(timestamp):
    """Validates that the client submitted timestamp for a transaction is not
    greater than current time, within a tolerance defined by SYNC_TOLERANCE

    NOTE: Timestamp validation can be challenging since the machines that are
    submitting and validating transactions may have different system times
    """
    dts = datetime.datetime.utcnow()
    current_time = round(time.mktime(dts.timetuple()) + dts.microsecond/1e6)
    if (timestamp - current_time) > SYNC_TOLERANCE:
        raise InvalidTransaction(
            'Timestamp must be less than local time.'
            ' Expected {0} in ({1}-{2}, {1}+{2})'.format(
                timestamp, current_time, SYNC_TOLERANCE))
