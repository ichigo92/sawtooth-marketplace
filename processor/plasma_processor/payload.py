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
# ------------------------------------------------------------------------------

from sawtooth_sdk.processor.exceptions import InvalidTransaction

from plasma_processor.protobuf import payload_pb2


class PlasmaPayload(object):

    def __init__(self, payload):
        self._transaction = payload_pb2.PlasmaPayload()
        self._transaction.ParseFromString(payload)

    @property
    def timestamp(self):
        return self._transaction.timestamp

    def create_agent(self):
        """Returns the value set in the create_account.

        Returns:
            payload_pb2.CreateAgent
        """
        return self._transaction.create_agent

    def is_create_agent(self):

        create_agent = payload_pb2.TransactionPayload.CREATE_AGENT

        return self._transaction.payload_type == create_agent

    def create_asset(self):
        """Returns the value set in the create_asset.

        Returns:
            payload_pb2.CreateAsset
        """
        return self._transaction.create_asset

    def is_create_asset(self):

        create_asset = payload_pb2.TransactionPayload.CREATE_ASSET

        return self._transaction.payload_type == create_asset

    def update_asset(self):
        """Returns the value set in the update_asset.

        Returns:
            payload_pb2.UpdateAsset
        """
        return self._transaction.update_asset

    def is_update_asset(self):

        update_asset = payload_pb2.TransactionPayload.UPDATE_ASSET

        return self._transaction.payload_type == update_asset

    def transfer_asset(self):
        """Returns the value set in the transfer_asset.

        Returns:
            payload_pb2.TransferAsset
        """
        return self._transaction.transfer_asset

    def is_transfer_asset(self):

        transfer_asset = payload_pb2.TransactionPayload.TRANSFER_ASSET

        return self._transaction.payload_type == transfer_asset

    def create_order(self):
        """Returns the value set in the create_order.

        Returns:
            payload_pb2.CreateOrder
        """
        return self._transaction.create_order

    def is_create_order(self):

        create_order = payload_pb2.TransactionPayload.CREATE_ORDER

        return self._transaction.payload_type == create_order

    def update_order(self):
        """Returns the value set in the update_order.

        Returns:
            payload_pb2.UpdateOrder
        """
        return self._transaction.update_order

    def is_update_order(self):

        update_order = payload_pb2.TransactionPayload.UPDATE_ORDER

        return self._transaction.payload_type == update_order

    def transfer_order(self):
        """Returns the value set in the transfer_order.

        Returns:
            payload_pb2.TransferAsset
        """
        return self._transaction.transfer_order

    def is_transfer_order(self):

        transfer_order = payload_pb2.TransactionPayload.TRANSFER_ORDER

        return self._transaction.payload_type == transfer_order

    def accept_order(self):
        """Returns the value set in the accept_order.

        Returns:
            payload_pb2.AcceptOrder
        """
        return self._transaction.accept_order

    def is_accept_order(self):

        accept_order = payload_pb2.TransactionPayload.ACCEPT_ORDER

        return self._transaction.payload_type == accept_order

    def finalize_order(self):
        """Returns the value set in the finalize_order.

        Returns:
            payload_pb2.FinalizeOrder
        """
        return self._transaction.finalize_order

    def is_finalize_order(self):

        finalize_order = payload_pb2.TransactionPayload.FINALIZE_ORDER

        return self._transaction.payload_type == finalize_order

    def create_task(self):
        """Returns the value set in the create_task.

        Returns:
            payload_pb2.CreateTask
        """
        return self._transaction.create_task

    def is_create_task(self):

        create_task = payload_pb2.TransactionPayload.CREATE_TASK

        return self._transaction.payload_type == create_task

    def update_task(self):
        """Returns the value set in the update_task.

        Returns:
            payload_pb2.UpdateTask
        """
        return self._transaction.update_task

    def is_update_task(self):

        update_task = payload_pb2.TransactionPayload.UPDATE_TASK

        return self._transaction.payload_type == update_task