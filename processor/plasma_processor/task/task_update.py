from plasma_processor import common
from sawtooth_sdk.processor.exceptions import InvalidTransaction


def handle_update_task(update_task, header, state):
    """Handles updating an Order.

    Args:
        update_task (UpdateTask): The transaction.
        header (TransactionHeader): The header of the Transaction.
        state (State): The wrapper around the context.

    Raises:
        InvalidTransaction
            - The name already exists for an Task.
            - The txn signer has an account
    """

    if not state.get_agent(public_key=header.signer_public_key):
        raise InvalidTransaction(
            "Unable to update task, signing key has no"
            " Agent: {}".format(header.signer_public_key))

    if update_task.task_id == '':
        raise InvalidTransaction('No Task ID provided')

    task = state.get_task(task_id=update_task.task_id)
    if task is None:
        raise InvalidTransaction(
            "Task with Id {} does not exist".format(update_task.task_id))
    
    if not common._validate_task_owner(signer_public_key = public_key, task = task):
        raise InvalidTransaction('Transaction signer is not the owner of the task')


    # common._validate_latlng(update_task.latitude, update_task.longitude)

    # state.update_task(
    #     latitude = update_task.latitude,
    #     longitude = update_task.longitude,
    #     order_id = update_task.order_id,
    #     timestamp = update_task.timestamp)