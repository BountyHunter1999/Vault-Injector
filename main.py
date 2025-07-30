import hvac
import sys
import os
import loguru

from dotenv import load_dotenv

load_dotenv()


def get_vault_client():
    client = hvac.Client(
        url=os.getenv("VAULT_ADDR", "http://127.0.0.1:8200"),
        token=os.getenv("VAULT_TOKEN", "root"),
    )

    return client


def create_or_update_secret(client: hvac.Client, path: str, data: dict):
    res = client.secrets.kv.v2.create_or_update_secret(
        path=path,
        secret=data,
    )

    loguru.logger.info(f"Created or updated secret at {path}: {res}")


def read_data(path: str):
    def get_data(datastr: str):
        return [
            i.strip()
            for i in map(
                lambda x: x.strip().strip("|").strip("`"), datastr.strip().split(" | ")
            )
            if i
        ]

    with open(path, "r") as f:
        lines = f.readlines()

    headings = get_data(lines[0])
    data = [get_data(line) for line in lines[1:] if "------" not in line]

    return headings, data


def main():
    # client = get_vault_client()
    # print(client.__dir__())
    # create_or_update_secret(client, "test/test", {"test": "test"})

    headings, data = read_data("secrets/vault.secrets")
    print(headings)
    print(data, len(data))
    for row in data:
        print(row)


if __name__ == "__main__":
    main()
