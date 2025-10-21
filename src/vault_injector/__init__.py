"""
Vault Injector package.
"""

from vault_injector.destinations.base import DBDestination
from dotenv import load_dotenv

load_dotenv()


def main():
    print("Hello from vault_injector")

    destination = DBDestination()
    with destination:
        print(destination.client.url)
        print(destination.client.token)
        print("seal status", destination.client.seal_status)

        print(destination.client.is_authenticated())
        # destination.

        destination.client.write(path="test/test", data={"test": "test"})
        print(destination.ping())

    print(destination.ping())

if __name__ == "__main__":
    main()
