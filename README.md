# MGnify

Components
- [emgapi](https://github.com/EBI-Metagenomics/emgapi) - Django RESTful API
- [ebi-metagenomics-client](https://github.com/EBI-Metagenomics/ebi-metagenomics-client) - BackboneJS FrontEnd
- [ebi-metagenomics-webkit](https://github.com/EBI-Metagenomics/ebi-metagenomics-webkit) - FrontEnd libraries (visualizations mostly)

## Requirements

Make, Docker, Docker-Compose, nodejs.

### Setup

Clone the repo and the submodules

```
git clone --recurse-submodules git@github.com:EBI-Metagenomics/mgnify-web.git 
```

#### API DB

You can either use a db dump or an empty db.

##### Restore dump

Some manual intervention is required to populate the API database.

You need to get a dump of the MySQL database, for that refer to the documentation in confluence.

```bash
make mysql-restore /path/emg_schema_dump.sql
```

##### Empty DB

Run the django migrations to get the DB in shape

```bash
make manage migrate
```

## Running the project

To run MGnify you will need the API and the WebClient running at the same time.

The API will run using docker-compose (to run mysql, mongo and django). 

### API

```bash
make api
```

The api will be avaiable in `http://localhost:8000/metagenomics/api`

### WebClient

Install npm modules
```bash
make npm run build
```

run the webpack dev server

```bash
make client
```

The webclient will be avaiable in `http://localhost:9000/metagenomics`

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
