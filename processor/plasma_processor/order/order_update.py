from plasma_processor import common
from sawtooth_sdk.processor.exceptions import InvalidTransaction


def handle_update_order(update_order, header, state):
    """Handles updating an Order.

    Args:
        update_order (UpdateOrder): The transaction.
        header (TransactionHeader): The header of the Transaction.
        state (State): The wrapper around the context.

    Raises:
        InvalidTransaction
            - The name already exists for an Order.
            - The txn signer has an account
    """

    if not state.get_agent(public_key=header.signer_public_key):
        raise InvalidTransaction(
            "Unable to update order, signing key has no"
            " Agent: {}".format(header.signer_public_key))

    if update_order.order_id == '':
        raise InvalidTransaction('No Order ID provided')

    order = state.get_order(order_id=update_order.order_id)
    if order is None:
        raise InvalidTransaction(
            "Order with Id {} does not exist".format(update_order.order_id))
    
    if not common._validate_record_owner(signer_public_key = public_key, order = order):
        raise InvalidTransaction('Transaction signer is not the owner of the order')


    common._validate_latlng(update_order.latitude, update_order.longitude)

    state.update_order(
        latitude = update_order.latitude,
        longitude = update_order.longitude,
        order_id = update_order.order_id,
        timestamp = update_order.timestamp)