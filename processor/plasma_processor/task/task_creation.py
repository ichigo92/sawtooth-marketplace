from sawtooth_sdk.processor.exceptions import InvalidTransaction


def handle_task_creation(create_task, header, state):
    """Handles creating an Task.

    Args:
        create_task (CreateTask): The transaction.
        header (TransactionHeader): The header of the Transaction.
        state (State): The wrapper around the context.

    Raises:
        InvalidTransaction
            - The name already exists for an Task.
            - The txn signer has an account
    """

    if not state.get_agent(public_key=header.signer_public_key):
        raise InvalidTransaction(
            "Unable to create task, signing key has no"
            " Agent: {}".format(header.signer_public_key))

    if create_task.task_id == '':
        raise InvalidTransaction('No Task ID provided')

    if state.get_task(task_id=create_task.task_id):
        raise InvalidTransaction(
            "Task already exists with Id {}".format(create_task.task_id))

    state.set_order(
        public_key = header.signer_public_key,
        location = create_task.location,
        task_id = create_task.task_id,
        name = create_task.name,
        order_id = create_task.order_id,
        description = create_task.description,
        timestamp = create_task.timestamp)