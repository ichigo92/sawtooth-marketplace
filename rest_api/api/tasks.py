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

from uuid import uuid4

from sanic import Blueprint
from sanic import response

from api import common
from api import messaging
from api.authorization import authorized

from plasma_transaction import transaction_creation


TASKS_BP = Blueprint('tasks')


@TASKS_BP.post('tasks')
@authorized()
async def create_task(request):
    """Creates a new Holding for the authorized Account"""
    required_fields = ['name']
    common.validate_fields(required_fields, request.json)

    task = _create_task_dict(request)
    signer = await common.get_signer(request)

    batches, batch_id = transaction_creation.create_task(
        txn_key=signer,
        batch_key=request.app.config.SIGNER,
        identifier=task['task_id'],
        name=task.get('name'),
        description=task.get('description'),
        order_id=task['order_id'],
        quantity=task['quantity'])

    await messaging.send(
        request.app.config.VAL_CONN,
        request.app.config.TIMEOUT,
        batches)

    await messaging.check_batch_status(request.app.config.VAL_CONN, batch_id)

    return response.json(holding)


def _create_task_dict(request):
    keys = ['name', 'description', 'order_id', 'location']
    body = request.json

    task = {k: body[k] for k in keys if body.get(k) is not None}

    # if holding.get('quantity') is None:
    #     holding['quantity'] = 0

    task['task_id'] = str(uuid4())

    return task
