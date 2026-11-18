# MGnify web development

## Components

- [emgapi-v2](https://github.com/EBI-Metagenomics/emgapi-v2/) provides the API.
- [ebi-metagenomics-client](https://github.com/EBI-Metagenomics/ebi-metagenomics-client) provides the React client.

## Requirements

Install Git, [Task](https://taskfile.dev/), Docker Compose, Node.js, and npm.
Use the Node.js version required by the client.
See `emgapi/README.md` for API requirements and optional local credentials.

## Setup

```sh
git submodule update --init --recursive
task client:install
task dev-init
```

`task dev-init` creates local client settings and runs `task api:make-dev-data`.
It resets the development database.
It also requests a password for the `emgdev` admin account (just for local development).

Local client settings reside in `overrides/client/config.json` and `overrides/client/config.private.json`.
Both files use `http://localhost:8000/` for `api_v2`.
Both files use `http://localhost:8000/services/branchwater/` for `api_branchwater`.
Other settings come from the corresponding client config files.
The parent Vite config redirects the client imports to these local files.

`task client:configure` refreshes these copies without database setup.
`task client:run` also refreshes these copies.

## Run the full stack

```sh
task run
```

This task starts the complete upstream Docker stack and the client in parallel.
It includes the local Slurm and Prefect services.
It opens both pages in your browser during startup.
You may need to refresh the pages if the servers are still starting and you see 404s.

- Client: <http://localhost:9000/metagenomics/>
- API: <http://localhost:8000/>
- Django admin: <http://localhost:8000/admin/> (`emgdev` and the password you set earlier)

Use Ctrl+C to end the foreground tasks.
Use `task stop` to remove the API containers.

## Run individual components

```sh
task client:run
# API stack without Slurm:
task api:run-api-only
# Complete upstream stack, including local Slurm and Prefect:
task api:run
```

The parent includes the upstream API Taskfile under the `api` namespace.
API tasks use `emgapi/` as their working directory.
The Compose project name is `emgapiv2`, matching the upstream development database volume.
The legacy parent Compose files are unused by these tasks.

## Other tasks

```sh
task --list
task api:manage -- migrate
task api:test -- -k study
task client:build
task client:test -- --spec cypress/e2e/example.cy.js
```

Client tests require a running client and the appropriate test fixtures.
