# MGnify

## Components
- [emgapi](https://github.com/EBI-Metagenomics/emgapi) - Django RESTful API
- [ebi-metagenomics-client](https://github.com/EBI-Metagenomics/ebi-metagenomics-client) - React FrontEnd

## Other public MGnify Web repositories
These repositories are also part of the MGnify web stack, but do not form part of the core service so aren't included as submodules

- [mgnify-sourmash-component](https://github.com/EBI-Metagenomics/mgnify-sourmash-component) - web component to create Sourmash sketches in the browser
- [genome-search](https://github.com/EBI-Metagenomics/genome-search) - microservice API to perform COBS k-mer gene searches on genomes
- [sourmash-queue](https://github.com/EBI-Metagenomics/sourmash-queue) - microservice API to perform Sourmash MAG vs MAG searches 
- [blog](https://github.com/EBI-Metagenomics/blog) - GitHub-pages hosted blog and feed for the MGnify frontpage
- [EMG-docs](https://github.com/EBI-Metagenomics/EMG-docs) - source for the Sphinx-powered documentation site (ReadTheDocs)
- [notebooks](https://github.com/EBI-Metagenomics/notebooks) - MGnify Notebooks Server (Jupyter Lab)

## Requirements

Make, [Task](https://taskfile.dev/), Docker, Docker-Compose, nodejs, webpack (`npm install -g webpack`).

### Setup

Clone the repo and the submodules

```
git clone --recurse-submodules git@github.com:EBI-Metagenomics/mgnify-web.git 
```

There are **two** Docker-Compose setups available (for local development – these are NOT used in production).
The docker-compose.yml creates an environment with MySQL (not recommended for most use cases).
The lighter weight docker-compose-lite.yml create an environment backed by Sqlite.
We are migrating towards the latter option.

There is a `Makefile`, targeting the MySQL docker containers.
There is a `Taskfile.yml` targeting the Sqlite setup.
Again, the latter is recommended unless you really need to work on MySQL-specific things.

Note that MySQL is used on GitHub actions for CI, since it better matches the production setup of this API at EBI.

#### API DB

You can either use a db dump, a minimal-ish test db, or an empty db.

##### Restore dump

Some manual intervention is required to populate the API database.

You need to get a dump of the MySQL database, for that refer to the documentation in confluence.

```bash
make mysql-restore /path/emg_schema_dump.sql
```

##### Using minimal test db.
A Sqlite database is available in the `ebi-metagenomics-client/ci/testdbs` directory (because this is used in the webclient CI tests).

If you ever need to recreate this, use `task create-test-dbs`. 
This makes a minimally populated, migrated, Sqlite `emg` db, a very minimal fake `ena` Sqlite, and dumps a Mongo archive.


##### Empty DB

Run the django migrations to get the DB in shape

```bash
make manage migrate
```

##### Django admin superuser

You can add a Django superuser to the database, so you can use the Django Admin console.
In the minimal Sqlite dbs, once has been created (username/password: `emgtest`, `emgemgtesttest`).

```bash
make api-superuser
```
This picks up your local USER for username, but you set a password interactively (or set the `DJANGO_SUPERUSER_PASSWORD` env var).
Then you can log into the [Django admin console](http://0.0.0.0:8000/admin)

## Running the project

To run MGnify you will need the API and the WebClient running at the same time.

The API will run using docker-compose (to run mysql, mongo and django). 

### API (using MySQL)

```bash
make api
```

### API (using Sqlite)
```bash
task run-api
```

The api will be available in `http://localhost:8000/metagenomics/api`

### WebClient

Install npm modules
```bash
#make npm run build
```

run the webpack dev server

```bash
task run-client
```

The webclient will be available in `http://localhost:9000/metagenomics`

## API

To run any django manage command for the API:
```shell
task manage -- whatever-command
```
(note the use of ` -- ` to separate arguments for manage.py – this is a [standard Taskfile feature](https://taskfile.dev/usage/#forwarding-cli-arguments-to-commands))

e.g.
```shell
task manage -- migrate 001
```

## Tests
On GitHub, these are run by .github/workflows/test.yml in a similar-ish way.

### Client
```bash
task run-client

#(in a new terminal)
cd ebi-metagenomics-client
npx cypress run --env API_URL=http://localhost:8000/v1 # or with: -s "cypress/integration/browse.js" to run a single test
#or for an interactive testing experience:
npx cypress open --env API_URL=http://localhost:8000/v1/
```

### API
```bash
task test-api
#or for specific test/s with file/class/method name matching some string:
task test-api -- -k "PublicationAPI"
```