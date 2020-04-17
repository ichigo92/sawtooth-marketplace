from plasma_processor import common
from sawtooth_sdk.processor.exceptions import InvalidTransaction


def handle_transfer_asset(transfer_asset, header, state):
    """Handles transfering an Asset.

    Args:
        transfer_asset (TransferAsset): The transaction.
        header (TransactionHeader): The header of the Transaction.
        state (State): The wrapper around the context.

    Raises:
        InvalidTransaction
            - The name already exists for an Asset.
            - The txn signer has an account
    """

    if not state.get_agent(public_key=header.signer_public_key):
        raise InvalidTransaction(
            "Unable to create asset, signing key has no"
            " Account: {}".format(header.signer_public_key))

    if state.get_asset(asset_id=transfer_asset.asset_id):
        raise InvalidTransaction(
            "Asset already exists with Id {}".format(transfer_asset.asset_id))

    if not _validate_record_owner(signer_public_key=public_key,
                                  record=record):
        raise InvalidTransaction(
            'Transaction signer is not the owner of the record')

    state.set_asset(
        public_key = header.signer_public_key,
        latitude = create_asset.location.latitude,
        longitude = create_asset.location.longitude,
        location_name = create_asset.location.name,
        asset_id = create_asset.asset_id,
        asset_type = create_asset.asset_type,
        name = create_asset.name,
        barcode = create_asset.barcode,
        description = create_asset.description,
        planned_delivery_date = create_asset.planned_delivery_date,
        timestamp = create_asset.timestamp)

# def _transfer_record(state, public_key, payload):
#     if state.get_agent(payload.data.receiving_agent) is None:
#         raise InvalidTransaction(
#             'Agent with the public key {} does '
#             'not exist'.format(payload.data.receiving_agent))

#     record = state.get_record(payload.data.record_id)
#     if record is None:
#         raise InvalidTransaction('Record with the record id {} does not '
#                                  'exist'.format(payload.data.record_id))

#     if not _validate_record_owner(signer_public_key=public_key,
#                                   record=record):
#         raise InvalidTransaction(
#             'Transaction signer is not the owner of the record')

#     state.transfer_record(
#         receiving_agent=payload.data.receiving_agent,
#         record_id=payload.data.record_id,
#         timestamp=payload.timestamp)