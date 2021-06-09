# MGnify

Components
- [emgapi](https://github.com/EBI-Metagenomics/emgapi) - Django RESTful API
- [ebi-metagenomics-client](https://github.com/EBI-Metagenomics/ebi-metagenomics-client) - BackboneJS FrontEnd
- [ebi-metagenomics-webkit](https://github.com/EBI-Metagenomics/ebi-metagenomics-webkit) - FrontEnd libraries (visualizations mostly)

## Requirements

Make, Docker, Docker-Compose, nodejs, webpack (`npm install -g webpack`).

### Setup

Clone the repo and the submodules

```
git clone --recurse-submodules git@github.com:EBI-Metagenomics/mgnify-web.git 
```

#### API DB

You can either use a db dump, a minimal-ish test db, or an empty db.

##### Restore dump

Some manual intervention is required to populate the API database.

You need to get a dump of the MySQL database, for that refer to the documentation in confluence.

```bash
make mysql-restore /path/emg_schema_dump.sql
```

##### Reset to a minimal test db.
This uses the fixtures and SQL dumps from the `ebi-metagenomics-client` CI (tests).

Those fixtures/SQL dumps/datafiles should already be in place in the client submodule of this repo.

WARNING: If this isn’t your first time using it, you’ll lose any existing data from the mysql container.

```bash
make test-db-reset
```

##### Empty DB

Run the django migrations to get the DB in shape

```bash
make manage migrate
```

##### Django admin superuser

You can add a Django superuser to the database, so you can use the Django Admin console.

```bash
make api-superuser
```
This picks up your local USER for username, but you set a password interactively (or set the `DJANGO_SUPERUSER_PASSWORD` env var).
Then you can log into the [Django admin console](http://0.0.0.0:8000/admin)

## Running the project

To run MGnify you will need the API and the WebClient running at the same time.

The API will run using docker-compose (to run mysql, mongo and django). 

### API

```bash
make api
```

The api will be available in `http://localhost:8000/metagenomics/api`

### WebClient

Install npm modules
```bash
make npm run build
```

run the webpack dev server

```bash
make client
```

The webclient will be available in `http://localhost:9000/metagenomics`

## API

To run any django manage command for the API:
```
make manage <django-command>
```

## WebClient

To run the webclient npm tasks
```
make npm run <npm task> 
```
