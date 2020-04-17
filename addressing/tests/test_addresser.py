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

import unittest
from uuid import uuid4

from marketplace_addressing import addresser


class AddresserTest(unittest.TestCase):

    def test_asset_address(self):

        asset_address = addresser.make_asset_address(uuid4().hex)

        self.assertEqual(len(asset_address), 70, "The address is valid.")

        self.assertEqual(addresser.address_is(asset_address),
                         addresser.AddressSpace.ASSET,
                         "The address is correctly identified as an Asset.")

    def test_order_address(self):
        order_address = addresser.make_order_address(uuid4().hex)

        self.assertEqual(len(order_address), 70, "The address is valid.")

        self.assertEqual(addresser.address_is(order_address),
                         addresser.AddressSpace.ORDER,
                         "The address is correctly identified as an Order.")

    def test_agent_address(self):
        agent_address = addresser.make_agent_address(uuid4().hex)

        self.assertEqual(len(agent_address), 70, "The address is valid.")

        self.assertEqual(addresser.address_is(agent_address),
                         addresser.AddressSpace.AGENT,
                         "The address is correctly identified as an Agent.")

    def test_task_address(self):
        task_address = addresser.make_task_address(uuid4().hex)

        self.assertEqual(len(task_address), 70, "The address is valid.")

        self.assertEqual(addresser.address_is(task_address),
                         addresser.AddressSpace.TASK,
                         "The address is correctly identified as a Task.")
