from sawtooth_sdk.processor.exceptions import InvalidTransaction


def handle_asset_creation(create_asset, header, state):
    """Handles creating an Asset.

    Args:
        create_asset (CreateAsset): The transaction.
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

    if state.get_asset(asset_id=create_asset.asset_id):
        raise InvalidTransaction(
            "Asset already exists with Id {}".format(create_asset.asset_id))

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