SHELL := /bin/bash

.PHONY: api manage client npm mysql-restore mysql-query test-db-reset api-superuser clean update update down up _check-before-test test-api test-webkit

EMG_DB = emg
EMG_ENA_DB = ena
EMG_HOST_RESULT_PATH = emgapi/results
EMG_HOST_GENOMES_PATH = emgapi/genomes
EMG_CONTAINER_RESULT_PATH = /opt/emgapi/results
EMG_CONTAINER_GENOMES_PATH = /opt/emgapi/genomes
EMG_CONTAINER_FIXTURES_PATH = /opt/emgapi/fixtures

api: up
	docker-compose exec -w /opt/emgapi api bash manage.sh collectstatic --noinput
	docker-compose exec -w /opt/emgapi api bash manage.sh runserver 0.0.0.0:8000 --nostatic

# django manage command
manage: up
	docker-compose exec -w /opt/emgapi api bash manage.sh \
		$(filter-out $@,$(MAKECMDGOALS))


test-api:
	$(MAKE) mysql-query "DROP DATABASE emg_tests;" || echo "No emg_tests db to drop"
	#$(MAKE) mysql-query "DROP DATABASE ${EMG_ENA_DB};" || echo "No ENA db to drop"
	$(MAKE) mysql-query "CREATE DATABASE emg_tests;"
	#$(MAKE) mysql-query "CREATE DATABASE ${EMG_ENA_DB};"
	$(MAKE) mysql-query "SET GLOBAL sql_mode = 'STRICT_TRANS_TABLES';"
	docker-compose exec -w /opt/emgapi api-tests pip3 install -U git+git://github.com/EBI-Metagenomics/emg-backlog-schema.git
	docker-compose exec -w /opt/emgapi api-tests pip3 install -U git+git://github.com/EBI-Metagenomics/ena-api-handler.git
	docker-compose exec -w /opt/emgapi api-tests pip3 install -U -r requirements-test.txt
	docker-compose exec -w /opt/emgapi api-tests pip3 install "flake8==3.4" "pycodestyle==2.3.1" pep8-naming
	docker-compose exec -w /opt/emgapi api-tests pip3 install "git+git://github.com/EBI-Metagenomics/django-rest-framework-json-api@develop#egg=djangorestframework-jsonapi"
	docker-compose exec -w /opt/emgapi api-tests python3 setup.py sdist
	docker-compose exec -w /opt/emgapi api-tests pip3 install -U .
	docker-compose exec -w /opt/emgapi api-tests pip3 freeze
	docker-compose exec -w /opt/emgapi -e EMG_CONFIG=config/local-tests.yml api-tests python3 setup.py test

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

mysql-query: up
	docker-compose exec -T mysql mysql --host=0.0.0.0 \
		--user=root --port=3306 \
		--default-character-set=utf8 --comments \
		-e "$(filter-out $@,$(MAKECMDGOALS))"

test-db-reset: up
	# Start with fresh databases
	$(MAKE) mysql-query "DROP DATABASE ${EMG_DB};" || echo "No EMG db to drop"
	$(MAKE) mysql-query "DROP DATABASE ${EMG_ENA_DB};" || echo "No ENA db to drop"
	$(MAKE) mysql-query "CREATE DATABASE ${EMG_DB};"
	$(MAKE) mysql-query "CREATE DATABASE ${EMG_ENA_DB};"

	# Use ENA database dump from CI
	docker-compose exec -T mysql mysql --host=0.0.0.0 \
				--user=root --port=3306 \
				--default-character-set=utf8 --comments \
				--database=${EMG_ENA_DB} < $(filter-out $@,$(MAKECMDGOALS))/ena_db.sql

	$(MAKE) manage migrate

	# Place MYSQL fixtures from CI
	$(MAKE) mysql-query "SET FOREIGN_KEY_CHECKS = 0;"
	for fixture in $(filter-out $@,$(MAKECMDGOALS))/emg_sql_fixtures/*.sql; do \
		echo $$fixture; \
		$(MAKE) mysql-restore $$fixture; \
	done
	$(MAKE) mysql-query "SET FOREIGN_KEY_CHECKS = 1;"

	# Place results datafiles and genomes from CI
	rm -rf "${EMG_HOST_RESULT_PATH}"
	rm -rf "${EMG_HOST_GENOMES_PATH}"
	cp -R $(filter-out $@,$(MAKECMDGOALS))/emg_api_datafiles/results "${EMG_HOST_RESULT_PATH}"
	cp -R $(filter-out $@,$(MAKECMDGOALS))/emg_api_datafiles/genomes "${EMG_HOST_GENOMES_PATH}"
	mkdir -p ${EMG_HOST_RESULT_PATH}/2015/03/ERP009703/version_2.0/project-summary;
	mkdir -p ${EMG_HOST_RESULT_PATH}/2015/03/ERP009703/version_4.0/project-summary;

	touch  ${EMG_HOST_RESULT_PATH}/2015/03/ERP009703/google-map-sample-data.json;
	touch  ${EMG_HOST_RESULT_PATH}/2015/03/ERP009703/version_2.0/project-summary/BP_GO_abundances_v2.0.tsv;
	touch  ${EMG_HOST_RESULT_PATH}/2015/03/ERP009703/version_2.0/project-summary/BP_GO-slim_abundances_v2.0.tsv;
	touch  ${EMG_HOST_RESULT_PATH}/2015/03/ERP009703/version_2.0/project-summary/CC_GO_abundances_v2.0.tsv;
	touch  ${EMG_HOST_RESULT_PATH}/2015/03/ERP009703/version_2.0/project-summary/CC_GO-slim_abundances_v2.0.tsv;
	touch  ${EMG_HOST_RESULT_PATH}/2015/03/ERP009703/version_2.0/project-summary/GO_abundances_v2.0.tsv;
	touch  ${EMG_HOST_RESULT_PATH}/2015/03/ERP009703/version_2.0/project-summary/GO-slim_abundances_v2.0.tsv;
	touch  ${EMG_HOST_RESULT_PATH}/2015/03/ERP009703/version_2.0/project-summary/IPR_abundances_v2.0.tsv;
	touch  ${EMG_HOST_RESULT_PATH}/2015/03/ERP009703/version_2.0/project-summary/MF_GO_abundances_v2.0.tsv;
	touch  ${EMG_HOST_RESULT_PATH}/2015/03/ERP009703/version_2.0/project-summary/MF_GO-slim_abundances_v2.0.tsv;
	touch  ${EMG_HOST_RESULT_PATH}/2015/03/ERP009703/version_2.0/project-summary/phylum_taxonomy_abundances_v2.0.tsv;
	touch  ${EMG_HOST_RESULT_PATH}/2015/03/ERP009703/version_2.0/project-summary/taxonomy_abundances_v2.0.tsv
	touch  ${EMG_HOST_RESULT_PATH}/2015/03/ERP009703/version_4.0/project-summary/BP_GO_abundances_v4.0.tsv;
	touch  ${EMG_HOST_RESULT_PATH}/2015/03/ERP009703/version_4.0/project-summary/BP_GO-slim_abundances_v4.0.tsv;
	touch  ${EMG_HOST_RESULT_PATH}/2015/03/ERP009703/version_4.0/project-summary/CC_GO_abundances_v4.0.tsv;
	touch  ${EMG_HOST_RESULT_PATH}/2015/03/ERP009703/version_4.0/project-summary/CC_GO-slim_abundances_v4.0.tsv;
	touch  ${EMG_HOST_RESULT_PATH}/2015/03/ERP009703/version_4.0/project-summary/GO_abundances_v4.0.tsv;
	touch  ${EMG_HOST_RESULT_PATH}/2015/03/ERP009703/version_4.0/project-summary/GO-slim_abundances_v4.0.tsv;
	touch  ${EMG_HOST_RESULT_PATH}/2015/03/ERP009703/version_4.0/project-summary/IPR_abundances_v4.0.tsv;
	touch  ${EMG_HOST_RESULT_PATH}/2015/03/ERP009703/version_4.0/project-summary/LSU_diversity.tsv;
	touch  ${EMG_HOST_RESULT_PATH}/2015/03/ERP009703/version_4.0/project-summary/MF_GO_abundances_v4.0.tsv;
	touch  ${EMG_HOST_RESULT_PATH}/2015/03/ERP009703/version_4.0/project-summary/MF_GO-slim_abundances_v4.0.tsv;
	touch  ${EMG_HOST_RESULT_PATH}/2015/03/ERP009703/version_4.0/project-summary/phylum_taxonomy_abundances_LSU_v4.0.tsv;
	touch  ${EMG_HOST_RESULT_PATH}/2015/03/ERP009703/version_4.0/project-summary/phylum_taxonomy_abundances_SSU_v4.0.tsv;
	touch  ${EMG_HOST_RESULT_PATH}/2015/03/ERP009703/version_4.0/project-summary/SSU_diversity.tsv;
	touch  ${EMG_HOST_RESULT_PATH}/2015/03/ERP009703/version_4.0/project-summary/taxonomy_abundances_LSU_v4.0.tsv;
	touch  ${EMG_HOST_RESULT_PATH}/2015/03/ERP009703/version_4.0/project-summary/taxonomy_abundances_SSU_v4.0.tsv

	$(MAKE) manage "import_taxonomy ERR1022502 "${EMG_CONTAINER_RESULT_PATH}" --pipeline 4.0"
	$(MAKE) manage "import_qc ERR1022502 "${EMG_CONTAINER_RESULT_PATH}" --pipeline 4.0"
	$(MAKE) manage "import_summary ERR1022502 "${EMG_CONTAINER_RESULT_PATH}" .ipr --pipeline 4.0"
	$(MAKE) manage "import_summary ERR1022502 "${EMG_CONTAINER_RESULT_PATH}" .go_slim --pipeline 4.0"
	$(MAKE) manage "import_summary ERR1022502 "${EMG_CONTAINER_RESULT_PATH}" .go --pipeline 4.0"
	$(MAKE) manage "import_taxonomy ERR1022502 "${EMG_CONTAINER_RESULT_PATH}" --pipeline 2.0"
	$(MAKE) manage "import_qc ERR1022502 "${EMG_CONTAINER_RESULT_PATH}" --pipeline 2.0"
	$(MAKE) manage "import_summary ERR1022502 "${EMG_CONTAINER_RESULT_PATH}" .ipr --pipeline 2.0"
	$(MAKE) manage "import_summary ERR1022502 "${EMG_CONTAINER_RESULT_PATH}" .go_slim --pipeline 2.0"
	$(MAKE) manage "import_summary ERR1022502 "${EMG_CONTAINER_RESULT_PATH}" .go --pipeline 2.0"
	$(MAKE) manage "import_taxonomy ERR867655 "${EMG_CONTAINER_RESULT_PATH}" --pipeline 4.0"
	$(MAKE) manage "import_qc ERR867655 "${EMG_CONTAINER_RESULT_PATH}" --pipeline 4.0"
	$(MAKE) manage "import_summary ERR867655 "${EMG_CONTAINER_RESULT_PATH}" .ipr --pipeline 4.0"
	$(MAKE) manage "import_summary ERR867655 "${EMG_CONTAINER_RESULT_PATH}" .go_slim --pipeline 4.0"
	$(MAKE) manage "import_summary ERR867655 "${EMG_CONTAINER_RESULT_PATH}" .go --pipeline 4.0"
	$(MAKE) manage "import_taxonomy ERP104236 "${EMG_CONTAINER_RESULT_PATH}" --pipeline 4.0"
	$(MAKE) manage "import_qc ERP104236 "${EMG_CONTAINER_RESULT_PATH}" --pipeline 4.0"
	$(MAKE) manage "import_summary ERP104236 "${EMG_RESULT_PATH}" .ipr --pipeline 4.0"
	$(MAKE) manage "import_summary ERP104236 "${EMG_CONTAINER_RESULT_PATH}" .go_slim --pipeline 4.0"
	$(MAKE) manage "import_summary ERP104236 "${EMG_CONTAINER_RESULT_PATH}" .go --pipeline 4.0"
	$(MAKE) manage "import_taxonomy ERZ477576 "${EMG_CONTAINER_RESULT_PATH}" --pipeline 5.0"
	$(MAKE) manage "import_qc ERZ477576 "${EMG_CONTAINER_RESULT_PATH}" --pipeline 5.0"
	$(MAKE) manage "import_contigs ERZ477576 "${EMG_CONTAINER_RESULT_PATH}" --pipeline 5.0"
	$(MAKE) manage "import_summary ERZ477576 "${EMG_RESULT_PATH}" .ipr --pipeline 5.0"
	$(MAKE) manage "import_summary ERZ477576 "${EMG_CONTAINER_RESULT_PATH}" .go --pipeline 5.0"
	$(MAKE) manage "import_summary ERZ477576 "${EMG_CONTAINER_RESULT_PATH}" .go_slim --pipeline 5.0"
	$(MAKE) manage "import_summary ERZ477576 "${EMG_CONTAINER_RESULT_PATH}" .pfam --pipeline 5.0"
	$(MAKE) manage "import_summary ERZ477576 "${EMG_CONTAINER_RESULT_PATH}" .gprops --pipeline 5.0"
	$(MAKE) manage "import_summary ERZ477576 "${EMG_CONTAINER_RESULT_PATH}" .antismash --pipeline 5.0"

	$(MAKE) manage "import_kegg_modules ${EMG_CONTAINER_FIXTURES_PATH}/kegg_module_orthology.json"
	$(MAKE) manage "import_kegg_classes ${EMG_CONTAINER_FIXTURES_PATH}/kegg_class_orthology.json"
	$(MAKE) manage "import_cog_descriptions ${EMG_CONTAINER_FIXTURES_PATH}/cog.csv"
	$(MAKE) manage "import_genomes ${EMG_CONTAINER_GENOMES_PATH} hgut 1.0 root:Host-Associated:Human:Digestive_System:Large_intestine"

api-superuser:
	# Make a Django superuser
	echo -e "\033[0;31m ***Creating django superuser. Username ${USER}, but you need to set a password.*** \033[0m"
	$(MAKE) manage "createsuperuser --username ${USER} --email ${USER}@ebi.ac.uk"  # will prompt for password
	echo "Django admin console is at 0.0.0.0:8000/admin"

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