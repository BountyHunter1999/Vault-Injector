import hvac
import sys
import os
import loguru
import typer

from dotenv import load_dotenv

load_dotenv()


def get_vault_client():
    client = hvac.Client(
        url=os.getenv("VAULT_ADDR", "http://127.0.0.1:8200"),
        token=os.getenv("VAULT_TOKEN", "root"),
        verify=False,
        # url="http://127.0.0.1:8200",
        # token="root",
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


def get_value(datum: list[str], index: int, default: str = "") -> str:
    try:
        return datum[index]
    except IndexError:
        return default


def map_data_with_headings(
    headings: list[str], data: list[list[str]]
) -> dict[str, str]:
    mapped_secrets = []
    for datum in data:
        secrets = {}
        for i, heading in enumerate(headings):
            secrets[f"{heading}"] = get_value(datum, i, "")
        mapped_secrets.append(secrets)
    return mapped_secrets


def main(filepath: str):
    client = get_vault_client()
    # print(client.__dir__())
    # create_or_update_secret(client, "test/test", {"test": "test"})

    if not os.path.exists(filepath):
        typer.echo(f"File {filepath} does not exist")
        return

    if not filepath.endswith(".secrets"):
        typer.echo(f"File {filepath} is not a secrets file")
        return

    filename = os.path.basename(filepath).split(".")[0]
    typer.echo(f"Processing {filename}")

    headings, data = read_data(filepath)
    mapped_secrets = map_data_with_headings(headings, data)
    print(mapped_secrets)

    for secret in mapped_secrets:
        if "Root Password" in headings:
            create_or_update_secret(
                client,
                f"servers/{filename}/{secret[headings[0]]}",
                secret,
            )
        else:
            create_or_update_secret(
                client,
                f"credentials/{filename}/{secret[headings[0]]}: {secret[headings[1]]}",
                secret,
            )


if __name__ == "__main__":
    main()
