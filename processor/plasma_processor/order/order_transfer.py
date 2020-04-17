from plasma_processor import common
from sawtooth_sdk.processor.exceptions import InvalidTransaction


def handle_transfer_order(transfer_order, header, state):
    """Handles updating an Order.

    Args:
        transfer_order (TransferOrder): The transaction.
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

    if transfer_order.order_id == '':
        raise InvalidTransaction('No Order ID provided')

    order = state.get_order(order_id = transfer_order.order_id)
    if order is None:
        raise InvalidTransaction(
            "Order with Id {} does not exist".format(transfer_order.order_id))
    
    if not common._validate_record_owner(signer_public_key = public_key, order = order):
        raise InvalidTransaction('Transaction signer is not the owner of the order')


    state.transfer_order(
        receiving_agent = transfer_order.receiving_agent,
        record_id = transfer_order.record_id,
        timestamp = transfer_order.timestamp)