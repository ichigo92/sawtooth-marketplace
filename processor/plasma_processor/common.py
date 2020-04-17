from sawtooth_sdk.processor.exceptions import InvalidTransaction


SYNC_TOLERANCE = 60 * 5
MAX_LAT = 90 * 1e6
MIN_LAT = -90 * 1e6
MAX_LNG = 180 * 1e6
MIN_LNG = -180 * 1e6


def _validate_order_owner(signer_public_key, order):
    """Validates that the public key of the signer is the latest (i.e.
    current) owner of the order
    """
    latest_owner = max(order.owners, key=lambda obj: obj.timestamp).agent_id
    return latest_owner == signer_public_key

def _validate_asset_owner(signer_public_key, asset):
    """Validates that the public key of the signer is the latest (i.e.
    current) owner of the asset
    """
    latest_owner = max(asset.owners, key=lambda obj: obj.timestamp).agent_id
    return latest_owner == signer_public_key

def _validate_task_owner(signer_public_key, task):
    """Validates that the public key of the signer is the latest (i.e.
    current) owner of the task
    """
    latest_owner = max(task.owners, key=lambda obj: obj.timestamp).agent_id
    return latest_owner == signer_public_key


def _validate_latlng(latitude, longitude):
    if not MIN_LAT <= latitude <= MAX_LAT:
        raise InvalidTransaction('Latitude must be between -90 and 90. '
                                 'Got {}'.format(latitude/1e6))
    if not MIN_LNG <= longitude <= MAX_LNG:
        raise InvalidTransaction('Longitude must be between -180 and 180. '
                                 'Got {}'.format(longitude/1e6))


def _validate_timestamp(timestamp):
    """Validates that the client submitted timestamp for a transaction is not
    greater than current time, within a tolerance defined by SYNC_TOLERANCE

    NOTE: Timestamp validation can be challenging since the machines that are
    submitting and validating transactions may have different system times
    """
    dts = datetime.datetime.utcnow()
    current_time = round(time.mktime(dts.timetuple()) + dts.microsecond/1e6)
    if (timestamp - current_time) > SYNC_TOLERANCE:
        raise InvalidTransaction(
            'Timestamp must be less than local time.'
            ' Expected {0} in ({1}-{2}, {1}+{2})'.
