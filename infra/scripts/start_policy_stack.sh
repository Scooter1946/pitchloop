#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
compose_file="${repo_root}/infra/pomerium/docker-compose.yml"
env_file="${repo_root}/infra/pomerium/.env"

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR docker is required to run the Pomerium data plane" >&2
  exit 1
fi

if [[ ! -f "${env_file}" ]]; then
  echo "ERROR copy infra/pomerium/.env.example to infra/pomerium/.env and fill the required values" >&2
  exit 1
fi

docker compose --env-file "${env_file}" -f "${compose_file}" up --detach --build

for attempt in $(seq 1 30); do
  health="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}unknown{{end}}' pitchloop-policy-target-1 2>/dev/null || true)"
  if [[ "${health}" == "healthy" ]]; then
    echo "READY policy_target=healthy pomerium_data_plane=started"
    exit 0
  fi
  sleep 1
done

echo "ERROR policy target did not become healthy" >&2
docker compose --env-file "${env_file}" -f "${compose_file}" ps >&2
exit 1
