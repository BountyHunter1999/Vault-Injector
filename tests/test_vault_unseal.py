from vault_injector.destinations.base import DBDestination
from dotenv import load_dotenv


load_dotenv()


def test_unseal_vault():
    destination = DBDestination()
    # print("token", destination._get_token())
    # print("url", destination._get_url())

    # Seal the vault if it is not sealed to make test consistent
    if not destination.client.seal_status.get("sealed", False):
        destination.seal_vault()

    # If vault is sealed then we can't get authenticated, so we expect a VaultDown exception
    assert destination.ping() is False

    # Unseal the vault and check if we can get authenticated
    with destination:
        # destination.unseal_vault()
        assert destination.ping() is True

    assert destination.ping() is False
