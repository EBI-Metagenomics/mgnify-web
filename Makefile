SHELL := /bin/bash

.PHONY: api manage client npm mysql-restore clean update update down up

api: up
	docker-compose exec -w /opt/emgapi api bash manage.sh runserver 0.0.0.0:8000

# django manage command
manage: up
	docker-compose exec -w /opt/emgapi api bash manage.sh \
		$(filter-out $@,$(MAKECMDGOALS))

# npm run for the webclient
client:
	source ebi-metagenomics-client/env-config.sh && \
	npm --prefix ebi-metagenomics-client run server:watch

# npm for the client
npm:
	source ebi-metagenomics-client/env-config.sh && \
	npm --prefix ebi-metagenomics-client \
		$(filter-out $@,$(MAKECMDGOALS))

mysql-restore: up
	docker-compose exec -T mysql mysql --host=0.0.0.0 \
		--user=root --port=3306 \
		--default-character-set=utf8 --comments \
		--database=emg < $(filter-out $@,$(MAKECMDGOALS))

clean:
	docker-compose down -v
	docker-compose up -d --build

update:
	docker-compose down
	docker-compose up -d

down:
	docker-compose down

up:
	docker-compose up -d
%:
	@: