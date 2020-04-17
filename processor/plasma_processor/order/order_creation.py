from plasma_processor import common
from sawtooth_sdk.processor.exceptions import InvalidTransaction


def handle_order_creation(create_order, header, state):
    """Handles creating an Order.

    Args:
        create_order (CreateOrder): The transaction.
        header (TransactionHeader): The header of the Transaction.
        state (State): The wrapper around the context.

    Raises:
        InvalidTransaction
            - The name already exists for an Order.
            - The txn signer has an account
    """

    if not state.get_agent(public_key=header.signer_public_key):
        raise InvalidTransaction(
            "Unable to create order, signing key has no"
            " Agent: {}".format(header.signer_public_key))

    if create_order.order_id == '':
        raise InvalidTransaction('No Order ID provided')

    if state.get_order(order_id=create_order.order_id):
        raise InvalidTransaction(
            "Order already exists with Id {}".format(create_order.order_id))
    common._validate_latlng(create_order.latitude, create_order.longitude)

    state.set_order(
        public_key = header.signer_public_key,
        order_id = create_order.order_id,
        order_type = create_order.order_type,
        final = create_order.final,
        quantity = create_order.quantity,
        asset_id = create_order.asset_id,
        task_id = create_order.task_id,
        description = create_order.description,
        destination = create_order.destination,
        actual_cost = create_order.actual_cost,
        order_delivery_date = create_order.order_delivery_date,
        order_completion_date = create_order.order_completion_date,
        order_install_date = create_order.order_install_date,
        order_status = create_order.order_status,
        order_stage = create_order.order_stage,
        voided = create_order.voided,
        payment_status = create_order.payment_status,
        order_by = create_order.order_by,
        order_for = create_order.order_for,
        timestamp = create_order.timestamp)