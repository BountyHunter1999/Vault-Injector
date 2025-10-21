.PHONY: run tests

start-vault:
	docker run -d -e 'VAULT_DEV_LISTEN_ADDRESS=0.0.0.0:8200' -e 'VAULT_DEV_ROOT_TOKEN_ID=root' -p 8200:8200 hashicorp/vault:1.20

run:
	uv run v-inject

tests:
	uv run pytest

get-unseal-keys:
	docker compose exec vault sh -c "VAULT_ADDR=http://127.0.0.1:8200 vault operator init" >> secrets/vault/vault-unseal-keys.txt