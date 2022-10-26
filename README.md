# MGnify

## Components
- [emgapi](https://github.com/EBI-Metagenomics/emgapi) - Django RESTful API
- [ebi-metagenomics-client](https://github.com/EBI-Metagenomics/ebi-metagenomics-client) - React FrontEnd
- [sourmash-queue](https://github.com/EBI-Metagenomics/sourmash-queue) - microservice API to perform Sourmash MAG vs MAG searches 


## Other public MGnify Web repositories
These repositories are also part of the MGnify web stack, but  aren't included as submodules (yet)
- [mgnify-sourmash-component](https://github.com/EBI-Metagenomics/mgnify-sourmash-component) - web component to create Sourmash sketches in the browser. Published on NPM.
  - See [npm link](https://docs.npmjs.com/cli/v8/commands/npm-link) for the nice way to work on this locally too.
- [genome-search](https://github.com/EBI-Metagenomics/genome-search) - microservice API to perform COBS k-mer gene searches on genomes
- [blog](https://github.com/EBI-Metagenomics/blog) - GitHub-pages hosted blog and feed for the MGnify frontpage
- [EMG-docs](https://github.com/EBI-Metagenomics/EMG-docs) - source for the Sphinx-powered documentation site (ReadTheDocs)
- [notebooks](https://github.com/EBI-Metagenomics/notebooks) - MGnify Notebooks Server (Jupyter Lab)

## Requirements

[Task](https://taskfile.dev/), Docker, Docker-Compose, nodejs, webpack (`npm install -g webpack`).

## Setup

Clone the repo and the submodules

```
git clone --recurse-submodules git@github.com:EBI-Metagenomics/mgnify-web.git 
```

Docker-compose is used for local development – it is NOT used in production.
The docker-compose.yml creates an environment with SQlite for the EMG database.
Additional docker-compose files extend this:
- docker-compose-api-test.yml extends the API service with the test dependencies and env vars.
- docker-compose-mysql.yml adds a MySQL service and switches the API's config file for one set up for MySQL.
  - You won't normally need this, unless you need to test MySQL-specific things.

To use the extra docker-compose files, run docker commands like: `docker compose -f docker-compose.yml docker-compose-mysql.yml ...`.

There is a `Taskfile.yml` with tasks for most common development needs like running the services, tests, and managing test databases.
There are currently no tasks to help with the mysql setup.

Note that MySQL is used on GitHub actions for CI, to match the production setup of this API at EBI.

#### API DB

You can either use a db dump, a minimal-ish test db, or an empty db.

##### Using minimal test db.
A Sqlite database is available in the `ebi-metagenomics-client/ci/testdbs` directory (because this is used in the webclient CI tests).

If you ever need to recreate this, use `task create-test-dbs`. 
This makes a minimally populated, migrated, Sqlite `emg` db, a very minimal fake `ena` Sqlite, and dumps a Mongo archive.

There is a Mongo DB dump to go alongside this option. Restore it with:
```bash
task restore-mongo-test-db
```

##### Empty DB

Run the django migrations to get the DB in shape

```bash
task manage -- migrate
```

##### Restore dump

Some manual intervention is required to populate the API database with a production DB dump.
You need to get a dump of the MySQL database, for that refer to the documentation in confluence (EBI-only).
Use the MySQL setup, and pipe the dump files into MySQL – the dump files will `INSERT` commands.


##### Django admin superuser

You can add a Django superuser to the database, so you can use the Django Admin console.
In the minimal Sqlite dbs, one has been created (username/password: `emgtest`, `emgemgtesttest`).

```bash
task manage -- createsuperuser
```
Then you can log into the [Django admin console](http://127.0.0.1:8000/admin)

## Running the project

To run MGnify you will need the API and the WebClient running at the same time.

The API will run using docker-compose (to run the databases and django etc). 

### API (using Sqlite, **recommended**)
```bash
task run-api
```

If you need to use the MySQL backend instead, you would run:
```bash
docker compose -f docker-compose.yml -f docker-compose-mysql.yml up -d
task manage -- collectstatic
task manage -- runserver 0.0.0.0:8000
```

Either way the api will be available in `http://localhost:8000/metagenomics/api`

### WebClient

Install npm modules
```bash
npm install
```

run the webpack dev server (and API, DBs etc via docker compose):
```bash
task run-client
```

The webclient will be available in `http://localhost:9000/metagenomics`

### Sourmash search
To work on the Sourmash (MAG) search, build a minimal index in the `sourmash-queue` service:
```shell
task create-sourmash-test-index
```
Flower (a dashboard for the Celery queue system) is running, browse to [5555](http://127.0.0.1:5555) to see it.
To debug the worker: `docker attach mgnify-web-sourmash-queue-1`.


## Managing the API

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
