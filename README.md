# MGnify

Components
- [emgapi](https://github.com/EBI-Metagenomics/emgapi) - Django RESTful API
- [ebi-metagenomics-client](https://github.com/EBI-Metagenomics/ebi-metagenomics-client) - BackboneJS FrontEnd
- [ebi-metagenomics-webkit](https://github.com/EBI-Metagenomics/ebi-metagenomics-webkit) - FrontEnd libraries (visualizations mostly)

## Requirements

Make, Docker and Docker-Compose.

### Setup

Clone the repo and the submodules

```
git clone --recurse-submodules <repo>
```

Some manual intervention is required to populate the API database.

You need to get a dump of the MySQL database, for that refer to the documentation in confluence.

```bash
make mysql-restore /path/emg_schema_dump.sql
```

## Running the project

To run MGnify you will need the API and the WebClient running at the same time.

The API will run using docker-compose (to run mysql, mongo and django). 

### API

```bash
make api
```

### WebClient

```bash
make client
```

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