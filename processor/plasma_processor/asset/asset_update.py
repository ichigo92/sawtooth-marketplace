from palsma_processor import common
from sawtooth_sdk.processor.exceptions import InvalidTransaction


def handle_update_asset(update_asset, header, state):
    """Handles transfering an Asset.

    Args:
        update_asset (UpdateAsset): The transaction.
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

    asset = state.get_asset(asset_id=update_asset.asset_id)
    
    if asset is None:
        raise InvalidTransaction(
            "Asset with the asset Id {} does not exist".format(update_asset.asset_id))

    if not common._validate_asset_owner(signer_public_key=public_key,
                                  asset = asset):
        raise InvalidTransaction(
            'Transaction signer is not the owner of the asset')

    common._validate_latlng(update_asset.latitude, update_asset.longitude)

    # state.set_asset(
    #     public_key = header.signer_public_key,
    #     latitude = create_asset.location.latitude,
    #     longitude = create_asset.location.longitude,
    #     location_name = create_asset.location.name,
    #     asset_id = create_asset.asset_id,
    #     asset_type = create_asset.asset_type,
    #     name = create_asset.name,
    #     barcode = create_asset.barcode,
    #     description = create_asset.description,
    #     planned_delivery_date = create_asset.planned_delivery_date,
    #     timestamp = create_asset.timestamp)

# def _update_record(state, public_key, payload):
#     record = state.get_record(payload.data.record_id)
#     if record is None:
#         raise InvalidTransaction('Record with the record id {} does not '
#                                  'exist'.format(payload.data.record_id))

#     if not _validate_record_owner(signer_public_key=public_key,
#                                   record=record):
#         raise InvalidTransaction(
#             'Transaction signer is not the owner of the record')

#     _validate_latlng(payload.data.latitude, payload.data.longitude)

#     state.update_record(
#         latitude=payload.data.latitude,
#         longitude=payload.data.longitude,
#         record_id=payload.data.record_id,
#         timestamp=payload.timestamp)