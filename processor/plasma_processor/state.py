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

from plasma_addressing import addresser

from plasma_processor.protobuf import agent_pb2
from plasma_processor.protobuf import asset_pb2
from plasma_processor.protobuf import order_pb2
from plasma_processor.protobuf import task_pb2
from plasma_processor.protobuf import role_pb2


class PlasmaState(object):
    def __init__(self, context, timeout=2):
        self._context = context
        self._timeout = timeout
        self._state_entries = []

    def get_agent(self, public_key):
        address = addresser.make_agent_address(agent_id = public_key)
        self._state_entries.extend(self._context.get_state(
            addresses=[address],
            timeout=self._timeout))
        
        container = _get_agent_container(self._state_entries, address)
        agent = None
        try:
            agent = _get_agent_from_container(container, public_key)
        except KeyError:
            # We are fine with returning None for an agent that doesn't
            # exist in state.
            pass
        return agent


    def set_agent(self, public_key, name, description, role, orders,timestamp):
        """Creates a new agent in state

        Args:
            public_key (str): The public key of the agent
            name (str): The human-readable name of the agent
            description (str): Description about the agent
            role (Role): Role assigned to the agent
            orders (str): Array of orders related to this agent
            timestamp (int): Unix UTC timestamp of when the agent was created
        """
        # agent = agent_pb2.Agent(
        #     public_key=public_key, name=name, timestamp=timestamp)
        # container = agent_pb2.AgentContainer()
        # state_entries = self._context.get_state(
        #     addresses=[address], timeout=self._timeout)
        # if state_entries:
        #     container.ParseFromString(state_entries[0].data)

        # container.entries.extend([agent])
        # data = container.SerializeToString()

        # updated_state = {}
        # updated_state[address] = data
        # self._context.set_state(updated_state, timeout=self._timeout)

        address = addresser.make_agent_address(agent_id = public_key)

        container = _get_agent_container(self._state_entries, address)

        try:
            agent = _get_agent_from_container(container, public_key)

        except KeyError:
            agent = container.entries.add()
        
        agent.public_key = public_key
        agent.name = name
        agent.description = description

        # TODO: Fix Role

        agent.role.type = role
        agent.timestamp = timestamp

        for order in orders:
            agent.orders.append(order)

        state_entries_send = {}
        state_entries_send[address] = container.SerializeToString()
        return self._context.set_state(state_entries_send, self._timeout)


    def add_orders_to_agent(self, public_key, order_ids):
        address = addresser.make_agent_address(agent_id = public_key)

        container = _get_agent_container(self._state_entries, address)

        try:
            agent = _get_agent_from_container(container, public_key)
        except KeyError:
            agent = container.entries.add()

        agent.orders.extend(order_ids)

        state_entries_send = {}
        state_entries_send[address] = container.SerializeToString()
        return self._context.set_state(state_entries_send, self._timeout)

    def get_asset(self, asset_id):
        """Gets the agent associated with the asset_id

        Args:
            asset_id (str): The id of the asset

        Returns:
            asset_pb2.Asset: Asset with the provided asset_id
        """
        address = addresser.make_asset_address(asset_id = asset_id)

        self._state_entries.extend(self._context.get_state(
            addresses=[address],
            timeout = self._timeout))

        return self._get_asset(address = address, asset_id = asset_id)

    def _get_asset(self, address, asset_id):

        container = _get_asset_container(self._state_entries, address)

        asset = None
        try:
            asset = _get_asset_from_container(container, asset_id)
        except KeyError:
            # We are fine with returning None for an asset that doesn't exist
            pass
        return asset

    def set_asset(self,
                  public_key,
                  latitude,
                  longitude,
                  location_name,
                  asset_id,
                  asset_type,
                  name,
                  barcode,
                  description,
                  planned_delivery_date,
                  timestamp):
        """Creates a new asset in state

        Args:
            public_key (str): The public key of the agent creating the asset
            latitude (int): Initial latitude of the asset
            longitude (int): Initial latitude of the asset
            location_name (str): Name of the location
            asset_id (str): Unique ID of the asset
            asset_type (str): Type of the asset
            name (str): Name of the asset
            description (str): Description of the asset
            barcode (str): Barcode for physical tracking of asset
            planned_deliver_date (int): Expected delivery date
            timestamp (int): Unix UTC timestamp of when the agent was created
        """
        address = addresser.make_asset_address(asset_id)

        container = _get_asset_container(self._state_entries, address)
        try:
            asset = _get_asset_from_container(container, asset_id)
        except KeyError:
            asset = container.entries.add()

        owner = asset_pb2.Asset.Owner(
            agent_id=public_key,
            timestamp=timestamp)
        location = asset_pb2.Asset.Location(
            latitude=latitude,
            longitude=longitude,
            name=location_name,
            timestamp=timestamp)

        planned_dates = asset_pb2.Asset.PlannedDates(
            planned_delivery_date=planned_delivery_date)

        manufacturer = asset_pb2.Asset.Manufacturer(
            agent_id=public_key,
            timestamp=timestamp)

        asset.asset_id = asset_id
        asset.asset_type = asset_type
        asset.name = name
        asset.owners.extend([owner])
        asset.locations.extend([location])
        asset.barcode = barcode
        asset.description = description
        asset.planned_dates = planned_dates
        asset.manufacturer = manufacturer

        state_entries_send = {}
        state_entries_send[address] = container.SerializeToString()
        return self._context.set_state(state_entries_send, self._timeout)


    def get_order(self, identifier):
        """Gets the record associated with the identifier

        Args:
            identifier (str): The id of the order i.e. order_id

        Returns:
            record_pb2.Record: Record with the provided identifier
        """
        address = addresser.make_order_address(order_id = identifier)

        self._state_entries.extend(self._context.get_state(
            addresses = [address],
            timeout = self._timeout))

        return self._get_order(address = address, identifier = identifier)

    def _get_order(self, address, identifier):

        container = _get_order_container(self._state_entries, address)
        order = None
        try:
            order = _get_order_from_container(container, identifier)
        except KeyError:
            # We are fine with returning None
            pass

        return order

    def set_order(self,
                  public_key,
                  order_id,
                  order_type,
                  final,
                  quantity,
                  asset_id,
                  task_id,
                  description,
                  destination,
                  actual_cost,
                  cost_paid,
                  order_delivery_date,
                  order_completion_date,
                  order_install_date,
                  order_status,
                  order_stage,
                  voided,
                  payment_status,
                  order_by,
                  order_for,
                  timestamp):
        """Creates a new order in state

        Args:
            public_key (str): The public key of the agent creating the record
            order_id (str): Unique ID of the order
            timestamp (int): Unix UTC timestamp of when the agent was created
        """
        address = addresser.make_order_address(order_id = identifier)
        container = _get_order_container(self._state_entries, address)

        try:
            order = _get_order_from_container(container, identifier)

        except KeyError:
            order = container.entries.add()

        owner = record_pb2.Record.Owner(
            agent_id=public_key,
            timestamp=timestamp)
        order_dates = record_pb2.Record.OrderDates(
            order_completion_date=order_completion_date,
            order_delivery_date=order_delivery_date,
            order_install_date=order_install_date)

        order.order_id = identifier
        order.owners = [owner]
        order.order_type = order_type
        order.final = final
        order.quantity = quantity
        order.task_id = task_id
        order.description = description
        order.destination = destination
        order.actual_cost = actual_cost
        order.cost_paid = cost_paid
        order.order_dates = order_dates
        order.order_status = order_status
        order.order_stage = order_stage
        order.voided = voided
        order.payment_status = payment_status
        order.order_by = order_by
        order.order_for = order_for

        state_entries_send = {}
        state_entries_send[address] = container.SerializeToString()
        return self._context.set_state(state_entries_send, self._timeout)

    def transfer_order(self, receiving_agent, identifier, timestamp):
        
        address = addresser.make_order_address(identifier)
        container = _get_order_container(self._state_entries, address)

        try:
            order = _get_order_from_container(container, identifier)

        except KeyError:
            order = container.entries.add()

        owner = order_pb2.Order.Owner(
            agent_id=receiving_agent,
            timestamp=timestamp)
        
        state_entries_send = {}
        state_entries_send[address] = container.SerializeToString()
        return self._context.set_state(state_entries_send, self._timeout)

    def update_order(self, latitude, longitude, identifier, timestamp):
        
        address = addresser.make_order_address(identifier)
        container = _get_order_container(self._state_entries, address)

        try:
            order = _get_order_from_container(container, identifier)
        
        except KeyError:
            order = container.entries.add()

        location = record_pb2.Record.Location(
            latitude=latitude,
            longitude=longitude,
            timestamp=timestamp)
        
        state_entries_send = {}
        state_entries_send[address] = container.SerializeToString()
        return self._context.set_state(state_entries_send, self._timeout)


    def get_task(self, identifier):
        """Gets the task associated with the identifier

        Args:
            identifier (str): The id of the task

        Returns:
            task_pb2.Task: Task with the provided identifier
        """
        address = addresser.make_task_address(task_id = identifier)
        
        self._state_entries.extend(self._context.get_state(
            addresses = [address],
            timeout = self._timeout))
        

        return self._get_task(address = address, identifier = identifier)

    def _get_task(self, address, identifier):

        container = _get_task_container(self._state_entries, address)

        task = None

        try:
            task = _get_task_from_container(container, identifier)

        except KeyError:
            # Fine with returning None
            pass

        return task


    def set_task(self,
                 public_key,
                 location,
                 task_id,
                 name,
                 order_id,
                 description,
                 timestamp):
        """Creates a new task in state

        Args:
            public_key (str): The public key of the agent creating the task
            latitude (int): Initial latitude of the task
            longitude (int): Initial latitude of the task
            task_id (str): Unique ID of the task
            timestamp (int): Unix UTC timestamp of when the agent was created
        """
        address = addresser.make_task_address(task_id)
        container = _get_task_container(self._state_entries, address)

        try:
            task = _get_task_from_container(container, identifier)
        except KeyError:
            task = container.entries.add()


        owner = task_pb2.Task.Owner(
            agent_id=public_key,
            timestamp=timestamp)

        task.task_id=task_id
        task.name=name
        task.owner=owner
        task.description=description
        task.location=location
        task.order_id=order_id
        task.timestamp=timestamp

        state_entries_send = {}
        state_entries_send[address] = container.SerializeToString()
        return self._context.set_state(state_entries_send, self._timeout)

# TODO: Add other methods

def _find_in_state(state_entries, address):
    for entry in state_entries:
        if entry.address == address:
            return entry
    raise KeyError("Address {} not found in state".format(address))


def _get_agent_container(state_entries, address):
    try:
        entry = _find_in_state(state_entries, address)
        container = agent_pb2.AgentContainer()
        container.ParseFromString(entry.data)
    except KeyError:
        container = agent_pb2.AgentContainer()

    return container

def _get_agent_from_container(container, identifier):
    for agent in container.entries:
        if agent.public_key == identifier:
            return agent
    raise KeyError(
        "Agent with id {} is not in container".format(identifier))


def _get_asset_container(state_entries, address):
    try:
        entry = _find_in_state(state_entries, address)
        container = asset_pb2.AssetContainer()
        container.ParseFromString(entry.data)
    except KeyError:
        container = asset_pb2.AssetContainer()
    return container

def _get_asset_from_container(container, asset_id):
    for asset in container.entries:
        if asset.asset_id == asset_id:
            return asset
    raise KeyError(
        "Asset with asset_id {} is not in container".format(asset_id))


def _get_order_container(state_entries, address):
    try:
        entry = _find_in_state(state_entries, address)
        container = order_pb2.OfferContainer()
        container.ParseFromString(entry.data)
    except KeyError:
        container = order_pb2.OrderContainer()

    return container

def _get_order_from_container(container, order_id):
    for order in container.entries:
        if order.order_id == order_id:
            return order
    raise KeyError(
        "Order with id {} is not in container".format(order_id))


def _get_task_container(state_entries, address):
    try:
        entry = _find_in_state(state_entries, address)
        container = task_pb2.TaskContainer()
        container.ParseFromString(entry.data)
    except KeyError:
        container = task_pb2.TaskContainer()

    return container

def _get_task_from_container(container, holding_id):
    for task in container.entries:
        if task.task_id == task_id:
            return task
    raise KeyError(
        "Holding with id {} is not in container".format(task_id))