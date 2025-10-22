from vault_injector.destinations.base import DBDestination
from vault_injector.destinations.models import DBTypeSecret, DBData
import os

def test_db_destination():
    destination = DBDestination()

    secret_path = "database/test"

    # Seal the vault if it is not sealed to make test consistent
    if not destination.client.seal_status.get("sealed", False):
        destination.seal_vault()

    # Test that vault is initially sealed
    assert destination.ping() is False

    # Test unsealing and setup
    with destination:
        # Vault should be unsealed now
        assert destination.ping() is True

        config = {
            # this will be the engine path
            "path": secret_path,
            "db_name": "postgres",
        }

        # Setup the database secret engine
        destination.setup(config)

        # Test adding a secret with correct path format
        data = DBTypeSecret(
            secret_path=f"{secret_path}/server1_postgres",
            db_engine="postgres",
            secret_data=DBData(
                username="test",
                password="test",
                host=os.environ.get("POSTGRES_HOST", "host.docker.internal"),
                port=5432,
                database="test_db",
                sslmode="disable",
            ),
        )
        assert destination.create_readonly_role(mount_point=secret_path, config=data) is True
