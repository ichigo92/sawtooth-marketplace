from sawtooth_sdk.processor.exceptions import InvalidTransaction


def handle_agent_creation(create_agent, header, state):
    """Handles creating an Agent.

    Args:
        create_agent (CreateAgent): The transaction.
        header (TransactionHeader): The header of the Transaction.
        state (State): The wrapper around the Context.

    Raises:
        InvalidTransaction
            - The public key already exists for an Agent.
    """

    if state.get_agent(public_key=header.signer_public_key):
        raise InvalidTransaction("Agent with public key {} already "
                                 "exists".format(header.signer_public_key))

    state.set_agent(
        public_key = header.signer_public_key,
        name = create_agent.name,
        description = create_agent.description,
        role = create_agent.role,
        timestamp=create_agent.timestamp)



# def _create_agent(state, public_key, payload):
#     if state.get_agent(public_key):
#         raise InvalidTransaction('Agent with the public key {} already '
#                                  'exists'.format(public_key))
#     state.set_agent(
#         public_key=public_key,
#         name=payload.data.name,
#         description = None,
#         role = None,
#         timestamp=payload.timestamp)